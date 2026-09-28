#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 MrMEEE
# MIT License

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
module: flatman_package
short_description: Manage flat-manager Flatpak packages
version_added: 1.0.0
description:
  - Create, update and delete package definitions on a flat-manager-django server.
  - Wraps the C(/api/packages/) endpoint.
  - A package holds the build configuration (git source, branch, architecture) and the current build state.
author:
  - MrMEEE (@MrMEEE)
extends_documentation_fragment:
  - mrmeee.flatman.flatman
  - mrmeee.flatman.flatman.attributes
options:
  package_id:
    description:
      - Flatpak application ID in reverse DNS notation, for example C(org.example.MyApp).
      - Used as the unique key for idempotency.
    type: str
    required: true
  state:
    description:
      - Whether the package should exist or not.
    type: str
    choices: [present, absent]
    default: present
  package_name:
    description:
      - Human readable name of the package, for example C(My Application).
    type: str
  version:
    description:
      - Version number of the package.
      - Normally extracted from the manifest for git based packages.
    type: str
  git_repo_url:
    description:
      - URL of the git repository holding the Flatpak manifest.
    type: str
  git_branch:
    description:
      - Git branch to build from.
    type: str
  branch:
    description:
      - Flatpak branch the package is published to, for example C(stable) or C(beta).
    type: str
  arch:
    description:
      - Architecture the package is built for, for example C(x86_64).
    type: str
  status:
    description:
      - Build state of the package.
      - Normally managed by the server; set it only to force a package back to a given state.
    type: str
    choices:
      - pending
      - building
      - built
      - committing
      - committed
      - publishing
      - published
      - failed
      - cancelled
  repository:
    description:
      - Name of the repository the package belongs to.
      - Mutually exclusive with O(repository_id).
    type: str
  repository_id:
    description:
      - Numeric ID of the repository the package belongs to.
      - Mutually exclusive with O(repository).
    type: int
  dependencies:
    description:
      - Flatpak SDK and runtime dependencies detected for this package.
    type: dict
  error_message:
    description:
      - Error message stored on the package.
      - Set it to an empty string to clear a previous failure message.
    type: str
notes:
  - The API returns the repository as a nested object while it is written as C(repository_id), so the
    nested value is unpacked before comparison to keep the module idempotent.
seealso:
  - module: mrmeee.flatman.flatman_package_info
  - module: mrmeee.flatman.flatman_package_action
  - module: mrmeee.flatman.flatman_repository
'''

EXAMPLES = r'''
- name: Create a git based package in the stable repository
  mrmeee.flatman.flatman_package:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    package_id: org.example.MyApp
    package_name: My Application
    repository: stable
    git_repo_url: https://github.com/example/org.example.MyApp
    git_branch: main
    branch: stable
    arch: x86_64

- name: Move a package to the beta branch
  mrmeee.flatman.flatman_package:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    package_id: org.example.MyApp
    repository_id: 3
    branch: beta

- name: Delete a retired package
  mrmeee.flatman.flatman_package:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    package_id: org.example.OldApp
    state: absent
'''

RETURN = r'''
package:
  description: The package as returned by the API after the change.
  returned: when O(state=present)
  type: dict
  sample:
    id: 12
    package_id: org.example.MyApp
    package_name: My Application
    version: 1.4.2
    branch: stable
    arch: x86_64
    status: published
    git_repo_url: https://github.com/example/org.example.MyApp
    git_branch: main
    build_number: 7
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.mrmeee.flatman.plugins.module_utils.flatman import (
    flatman_argument_spec,
    run_module,
)

COLLECTION_PATH = '/api/packages/'
REPOSITORY_PATH = '/api/repositories/'

STATUS_CHOICES = [
    'pending',
    'building',
    'built',
    'committing',
    'committed',
    'publishing',
    'published',
    'failed',
    'cancelled',
]


def main():
    argument_spec = flatman_argument_spec()
    argument_spec.update(
        package_id=dict(type='str', required=True),
        state=dict(type='str', default='present', choices=['present', 'absent']),
        package_name=dict(type='str'),
        version=dict(type='str'),
        git_repo_url=dict(type='str'),
        git_branch=dict(type='str'),
        branch=dict(type='str'),
        arch=dict(type='str'),
        status=dict(type='str', choices=STATUS_CHOICES),
        repository=dict(type='str'),
        repository_id=dict(type='int'),
        dependencies=dict(type='dict'),
        error_message=dict(type='str'),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        mutually_exclusive=[['repository', 'repository_id']],
    )

    def handler(client):
        params = module.params
        state = params['state']
        current = client.find_one(COLLECTION_PATH, 'package_id', params['package_id'])

        if state == 'absent':
            changed, dummy, diff = client.ensure(COLLECTION_PATH, current, {}, state='absent')
            module.exit_json(changed=changed, diff=diff)

        repository_id = params['repository_id']
        if params['repository']:
            repository_id = client.resolve(
                REPOSITORY_PATH, 'name', params['repository'], 'Repository')['id']

        desired = dict(
            package_id=params['package_id'],
            package_name=params['package_name'],
            version=params['version'],
            git_repo_url=params['git_repo_url'],
            git_branch=params['git_branch'],
            branch=params['branch'],
            arch=params['arch'],
            status=params['status'],
            repository_id=repository_id,
            dependencies=params['dependencies'],
            error_message=params['error_message'],
        )

        comparable = None
        if current is not None:
            comparable = dict(current)
            # repository_id is write-only; the API returns it nested under repository.
            comparable['repository_id'] = (current.get('repository') or {}).get('id')

        changed, package, diff = client.ensure(COLLECTION_PATH, comparable, desired)
        module.exit_json(changed=changed, package=package, diff=diff)

    run_module(module, handler)


if __name__ == '__main__':
    main()
