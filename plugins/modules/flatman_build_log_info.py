#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 MrMEEE
# MIT License

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
module: flatman_build_log_info
short_description: Fetch the build log of a flat-manager build or package
version_added: 1.0.0
description:
  - Retrieve the log lines produced by a build.
  - Wraps the C(/api/builds/<id>/logs/) and C(/api/packages/<id>/logs/) endpoints.
author:
  - MrMEEE (@MrMEEE)
extends_documentation_fragment:
  - mrmeee.flatman.flatman
  - mrmeee.flatman.flatman.attributes_info
options:
  build_id:
    description:
      - Numeric ID of the build whose log should be fetched.
      - Exactly one of O(build_id), O(package_id) and O(package_pk) is required.
    type: int
  package_id:
    description:
      - Flatpak application ID of the package whose log should be fetched, for example
        C(org.example.MyApp).
      - Exactly one of O(build_id), O(package_id) and O(package_pk) is required.
    type: str
  package_pk:
    description:
      - Numeric ID of the package whose log should be fetched.
      - Exactly one of O(build_id), O(package_id) and O(package_pk) is required.
    type: int
  level:
    description:
      - Return only log entries with this level, for example C(info) or C(error).
      - The filtering happens on the controller, because the endpoint has no level filter.
    type: str
  limit:
    description:
      - Return only the last given number of log entries, after O(level) filtering.
    type: int
notes:
  - Both log endpoints allow unauthenticated access, so O(api_token) is optional for this module.
  - Resolving O(package_id) to a numeric ID does require an authenticated request against
    C(/api/packages/), so use O(package_pk) or O(build_id) when no token is available.
seealso:
  - module: mrmeee.flatman.flatman_build_info
  - module: mrmeee.flatman.flatman_package_action
'''

EXAMPLES = r'''
- name: Fetch the full log of one build
  mrmeee.flatman.flatman_build_log_info:
    url: https://flatman.example.com
    build_id: 48
  register: buildlog

- name: Show the last 20 log lines of a package
  mrmeee.flatman.flatman_build_log_info:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    package_id: org.example.MyApp
    limit: 20
  register: tail

- name: Collect only the error lines of a build
  mrmeee.flatman.flatman_build_log_info:
    url: https://flatman.example.com
    build_id: 48
    level: error
  register: errors
'''

RETURN = r'''
logs:
  description: The matching log entries, oldest first.
  returned: always
  type: list
  elements: dict
  sample:
    - id: 981
      message: Cloning https://github.com/example/org.example.MyApp
      level: info
      timestamp: '09:12:44'
build:
  description:
    - The metadata the log endpoint returns alongside the log entries, without the log entries
      themselves.
    - Empty when the endpoint returns a bare list of log entries.
  returned: always
  type: dict
  sample:
    build_number: 7
    package_id: org.example.MyApp
    status: published
    total_logs: 213
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.mrmeee.flatman.plugins.module_utils.flatman import (
    flatman_argument_spec,
    run_module,
)

BUILD_PATH = '/api/builds/'
PACKAGE_PATH = '/api/packages/'


def main():
    argument_spec = flatman_argument_spec()
    argument_spec.update(
        build_id=dict(type='int'),
        package_id=dict(type='str'),
        package_pk=dict(type='int'),
        level=dict(type='str'),
        limit=dict(type='int'),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        mutually_exclusive=[['build_id', 'package_id', 'package_pk']],
        required_one_of=[['build_id', 'package_id', 'package_pk']],
    )

    def handler(client):
        params = module.params

        if params['build_id'] is not None:
            path = '%s%s/logs/' % (BUILD_PATH, params['build_id'])
        else:
            package_pk = params['package_pk']
            if package_pk is None:
                package_pk = client.resolve(
                    PACKAGE_PATH, 'package_id', params['package_id'], 'Package')['id']
            path = '%s%s/logs/' % (PACKAGE_PATH, package_pk)

        response = client.get(path)

        if isinstance(response, list):
            logs = response
            meta = {}
        else:
            logs = response.get('logs') or []
            meta = dict((k, v) for k, v in response.items() if k != 'logs')

        if params['level']:
            logs = [entry for entry in logs if entry.get('level') == params['level']]
        if params['limit'] is not None and params['limit'] >= 0:
            logs = logs[-params['limit']:] if params['limit'] else []

        module.exit_json(changed=False, logs=logs, build=meta)

    run_module(module, handler)


if __name__ == '__main__':
    main()
