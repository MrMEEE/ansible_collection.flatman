#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 MrMEEE
# MIT License

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
module: flatman_package_info
short_description: Gather information about flat-manager packages
version_added: 1.0.0
description:
  - Retrieve one or more packages from a flat-manager-django server.
  - Wraps the C(/api/packages/) endpoint.
author:
  - MrMEEE (@MrMEEE)
extends_documentation_fragment:
  - mrmeee.flatman.flatman
  - mrmeee.flatman.flatman.attributes_info
options:
  package_id:
    description:
      - Return only the package with this exact Flatpak application ID.
    type: str
  id:
    description:
      - Return only the package with this numeric ID.
    type: int
  status:
    description:
      - Filter packages by build state.
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
      - Name of the repository to filter on.
      - Mutually exclusive with O(repository_id).
    type: str
  repository_id:
    description:
      - Numeric ID of the repository to filter on.
      - Mutually exclusive with O(repository).
    type: int
  arch:
    description:
      - Filter packages by architecture, for example C(x86_64).
    type: str
  branch:
    description:
      - Filter packages by Flatpak branch, for example C(stable).
    type: str
  search:
    description:
      - Free text search across the application ID and the package name.
    type: str
  full:
    description:
      - Whether to return the complete build history embedded in every package.
      - The API embeds every build together with all of its log lines, which makes the response very
        large; when this is V(false) the C(builds) key is removed from each result.
      - The C(latest_build) key is always kept.
    type: bool
    default: false
seealso:
  - module: mrmeee.flatman.flatman_package
  - module: mrmeee.flatman.flatman_build_info
'''

EXAMPLES = r'''
- name: List every package
  mrmeee.flatman.flatman_package_info:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
  register: packages

- name: Find failed packages in the stable repository
  mrmeee.flatman.flatman_package_info:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    repository: stable
    status: failed
  register: broken

- name: Fetch one package including its full build history
  mrmeee.flatman.flatman_package_info:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    package_id: org.example.MyApp
    full: true
  register: myapp
'''

RETURN = r'''
packages:
  description: The matching packages.
  returned: always
  type: list
  elements: dict
  sample:
    - id: 12
      package_id: org.example.MyApp
      package_name: My Application
      version: 1.4.2
      branch: stable
      arch: x86_64
      status: published
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
        package_id=dict(type='str'),
        id=dict(type='int'),
        status=dict(type='str', choices=STATUS_CHOICES),
        repository=dict(type='str'),
        repository_id=dict(type='int'),
        arch=dict(type='str'),
        branch=dict(type='str'),
        search=dict(type='str'),
        full=dict(type='bool', default=False),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        mutually_exclusive=[['id', 'package_id'], ['repository', 'repository_id']],
    )

    def handler(client):
        params = module.params

        if params['id'] is not None:
            found = client.get_or_none('%s%s/' % (COLLECTION_PATH, params['id']))
            packages = [found] if found else []
        else:
            repository_id = params['repository_id']
            if params['repository']:
                repository_id = client.resolve(
                    REPOSITORY_PATH, 'name', params['repository'], 'Repository')['id']

            query = dict(
                status=params['status'],
                repository=repository_id,
                arch=params['arch'],
                branch=params['branch'],
                search=params['search'],
            )
            packages = client.get_all(COLLECTION_PATH, params=query)
            if params['package_id']:
                packages = [p for p in packages if p.get('package_id') == params['package_id']]

        if not params['full']:
            for package in packages:
                package.pop('builds', None)

        module.exit_json(changed=False, packages=packages)

    run_module(module, handler)


if __name__ == '__main__':
    main()
