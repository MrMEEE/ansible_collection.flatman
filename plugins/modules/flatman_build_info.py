#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 MrMEEE
# MIT License

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
module: flatman_build_info
short_description: Gather information about flat-manager build history records
version_added: 1.0.0
description:
  - Retrieve build history records from a flat-manager-django server.
  - Wraps the read only C(/api/builds/) endpoint.
author:
  - MrMEEE (@MrMEEE)
extends_documentation_fragment:
  - mrmeee.flatman.flatman
  - mrmeee.flatman.flatman.attributes_info
options:
  id:
    description:
      - Return only the build with this numeric ID.
    type: int
  package:
    description:
      - Flatpak application ID of the package whose builds should be returned, for example
        C(org.example.MyApp).
      - Mutually exclusive with O(package_pk).
    type: str
  package_pk:
    description:
      - Numeric ID of the package whose builds should be returned.
      - Mutually exclusive with O(package).
    type: int
  status:
    description:
      - Filter builds by state.
    type: str
    choices:
      - building
      - built
      - committing
      - committed
      - publishing
      - published
      - failed
      - cancelled
  build_number:
    description:
      - Return only the build with this build attempt number.
    type: int
  search:
    description:
      - Free text search across the application ID and the package name of the owning package.
    type: str
  full:
    description:
      - Whether to return the complete log output embedded in every build.
      - The API embeds every log line of a build, which makes the response very large; when this is
        V(false) the C(logs) key is removed from each result.
    type: bool
    default: false
seealso:
  - module: mrmeee.flatman.flatman_build_log_info
  - module: mrmeee.flatman.flatman_package_info
'''

EXAMPLES = r'''
- name: List every build
  mrmeee.flatman.flatman_build_info:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
  register: builds

- name: List the failed builds of one package
  mrmeee.flatman.flatman_build_info:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    package: org.example.MyApp
    status: failed
  register: failures

- name: Fetch build attempt number 7 including its logs
  mrmeee.flatman.flatman_build_info:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    package: org.example.MyApp
    build_number: 7
    full: true
  register: attempt
'''

RETURN = r'''
builds:
  description: The matching build history records.
  returned: always
  type: list
  elements: dict
  sample:
    - id: 48
      package_id: 12
      package_package_id: org.example.MyApp
      package_name: My Application
      repository_name: stable
      build_number: 7
      version: 1.4.2
      status: published
      commit_hash: 4a3b1c8d9e0f1a2b3c4d5e6f708192a3b4c5d6e7
      started_at: '2026-04-11T09:12:44Z'
      completed_at: '2026-04-11T09:31:02Z'
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.mrmeee.flatman.plugins.module_utils.flatman import (
    flatman_argument_spec,
    run_module,
)

COLLECTION_PATH = '/api/builds/'
PACKAGE_PATH = '/api/packages/'

STATUS_CHOICES = [
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
        id=dict(type='int'),
        package=dict(type='str'),
        package_pk=dict(type='int'),
        status=dict(type='str', choices=STATUS_CHOICES),
        build_number=dict(type='int'),
        search=dict(type='str'),
        full=dict(type='bool', default=False),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        mutually_exclusive=[['package', 'package_pk']],
    )

    def handler(client):
        params = module.params

        if params['id'] is not None:
            found = client.get_or_none('%s%s/' % (COLLECTION_PATH, params['id']))
            builds = [found] if found else []
        else:
            package_pk = params['package_pk']
            if params['package']:
                package_pk = client.resolve(
                    PACKAGE_PATH, 'package_id', params['package'], 'Package')['id']

            query = dict(
                package=package_pk,
                status=params['status'],
                build_number=params['build_number'],
                search=params['search'],
            )
            builds = client.get_all(COLLECTION_PATH, params=query)

        if not params['full']:
            for build in builds:
                build.pop('logs', None)

        module.exit_json(changed=False, builds=builds)

    run_module(module, handler)


if __name__ == '__main__':
    main()
