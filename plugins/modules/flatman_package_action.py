#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 MrMEEE
# MIT License

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
module: flatman_package_action
short_description: Run build actions on a flat-manager package
version_added: 1.0.0
description:
  - Trigger the imperative actions exposed by the C(/api/packages/) endpoint, such as starting,
    cancelling, committing or publishing a build.
  - Optionally wait until the package reaches a terminal build state.
author:
  - MrMEEE (@MrMEEE)
extends_documentation_fragment:
  - mrmeee.flatman.flatman
  - mrmeee.flatman.flatman.attributes
options:
  package_id:
    description:
      - Flatpak application ID of the package to act on, for example C(org.example.MyApp).
      - Mutually exclusive with O(id); exactly one of the two is required.
    type: str
  id:
    description:
      - Numeric ID of the package to act on.
      - Mutually exclusive with O(package_id); exactly one of the two is required.
    type: int
  action:
    description:
      - The action to perform on the package.
      - V(start) queues a git based build, and only works while the package is pending.
      - V(cancel) marks a running build as cancelled.
      - V(commit) commits a built package into the OSTree repository.
      - V(publish) publishes a committed package.
      - V(build_ref) registers an OSTree ref and commit pair for the package.
      - V(missing_objects) asks the server which OSTree objects are still missing.
    type: str
    required: true
    choices: [start, cancel, commit, publish, build_ref, missing_objects]
  ref:
    description:
      - Full OSTree ref, for example C(app/org.example.MyApp/x86_64/stable).
      - Required when O(action=build_ref).
    type: str
  commit:
    description:
      - OSTree commit hash to associate with O(ref).
      - Required when O(action=build_ref).
    type: str
  wanted:
    description:
      - OSTree object names to check for.
      - Only used when O(action=missing_objects); the request is sent as a POST when this is given
        and as a GET otherwise.
    type: list
    elements: str
  wait:
    description:
      - Whether to poll the package until it reaches a terminal build state.
      - Only applies to O(action=start), O(action=commit) and O(action=publish).
    type: bool
    default: false
  wait_timeout:
    description:
      - Maximum number of seconds to wait when O(wait=true).
    type: int
    default: 600
  wait_interval:
    description:
      - Number of seconds between polls when O(wait=true).
    type: int
    default: 5
notes:
  - The actions V(start), V(cancel), V(commit), V(publish) and V(build_ref) are imperative
    operations, so this module always reports a change for them. V(missing_objects) is read only and
    never reports a change.
  - The C(upload) action of the API is not implemented, because uploading artifacts requires a
    multipart request body which the collection HTTP client does not support.
seealso:
  - module: mrmeee.flatman.flatman_package
  - module: mrmeee.flatman.flatman_package_info
  - module: mrmeee.flatman.flatman_build_log_info
'''

EXAMPLES = r'''
- name: Start a build and wait for it to finish
  mrmeee.flatman.flatman_package_action:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    package_id: org.example.MyApp
    action: start
    wait: true
    wait_timeout: 3600
  register: build

- name: Publish a committed package
  mrmeee.flatman.flatman_package_action:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    id: 12
    action: publish
    wait: true

- name: Ask which OSTree objects are still missing
  mrmeee.flatman.flatman_package_action:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    package_id: org.example.MyApp
    action: missing_objects
    wanted:
      - 4a3b1c8d9e0f1a2b3c4d5e6f708192a3b4c5d6e7f8091a2b3c4d5e6f70819200
  register: missing
'''

RETURN = r'''
result:
  description: The raw body returned by the API for the requested action.
  returned: always
  type: dict
  sample:
    status: Build started manually
    package_id: org.example.MyApp
package:
  description: The package as returned by the API once it reached a terminal state.
  returned: when O(wait=true) and O(action) is V(start), V(commit) or V(publish)
  type: dict
  sample:
    id: 12
    package_id: org.example.MyApp
    status: published
    build_number: 7
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.mrmeee.flatman.plugins.module_utils.flatman import (
    flatman_argument_spec,
    run_module,
)

COLLECTION_PATH = '/api/packages/'

FAIL_STATUSES = ['failed', 'cancelled']

# Terminal states per action, derived from the Package status choices.
DONE_STATUSES = dict(
    start=['built', 'committed', 'published'],
    commit=['committed', 'published'],
    publish=['published'],
)

CHANGING_ACTIONS = ['start', 'cancel', 'commit', 'publish', 'build_ref']


def main():
    argument_spec = flatman_argument_spec()
    argument_spec.update(
        package_id=dict(type='str'),
        id=dict(type='int'),
        action=dict(
            type='str',
            required=True,
            choices=['start', 'cancel', 'commit', 'publish', 'build_ref', 'missing_objects'],
        ),
        ref=dict(type='str'),
        commit=dict(type='str'),
        wanted=dict(type='list', elements='str'),
        wait=dict(type='bool', default=False),
        wait_timeout=dict(type='int', default=600),
        wait_interval=dict(type='int', default=5),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        mutually_exclusive=[['package_id', 'id']],
        required_one_of=[['package_id', 'id']],
        required_if=[['action', 'build_ref', ['ref', 'commit']]],
    )

    def handler(client):
        params = module.params
        action = params['action']
        changed = action in CHANGING_ACTIONS

        if module.check_mode:
            module.exit_json(changed=changed, result={})

        pk = params['id']
        if pk is None:
            pk = client.resolve(
                COLLECTION_PATH, 'package_id', params['package_id'], 'Package')['id']

        detail_path = '%s%s/' % (COLLECTION_PATH, pk)
        action_path = '%s%s/' % (detail_path, action)

        if action == 'build_ref':
            result = client.post(action_path, data=dict(ref=params['ref'], commit=params['commit']))
        elif action == 'missing_objects':
            if params['wanted'] is not None:
                result = client.post(action_path, data=dict(wanted=params['wanted']))
            else:
                result = client.get(action_path)
        else:
            result = client.post(action_path)

        if params['wait'] and action in DONE_STATUSES:
            package = client.wait_for(
                detail_path,
                'status',
                DONE_STATUSES[action],
                fail_values=FAIL_STATUSES,
                timeout=params['wait_timeout'],
                interval=params['wait_interval'],
            )
            module.exit_json(changed=changed, result=result, package=package)

        module.exit_json(changed=changed, result=result)

    run_module(module, handler)


if __name__ == '__main__':
    main()
