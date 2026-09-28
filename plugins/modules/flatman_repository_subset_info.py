#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 MrMEEE
# MIT License

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
module: flatman_repository_subset_info
short_description: Gather information about flat-manager repository subsets
version_added: 1.0.0
description:
  - Retrieve one or more repository subsets from a flat-manager-django server.
  - Wraps the C(/api/repository-subsets/) endpoint.
author:
  - MrMEEE (@MrMEEE)
extends_documentation_fragment:
  - mrmeee.flatman.flatman
  - mrmeee.flatman.flatman.attributes_info
options:
  name:
    description:
      - Return only the subset with this exact name.
    type: str
  id:
    description:
      - Return only the subset with this numeric ID.
    type: int
  repository:
    description:
      - Restrict the result to subsets of the repository with this name.
      - Mutually exclusive with O(repository_id).
    type: str
  repository_id:
    description:
      - Restrict the result to subsets of the repository with this numeric ID.
      - Mutually exclusive with O(repository).
    type: int
  search:
    description:
      - Free text search across subset name and collection ID.
    type: str
seealso:
  - module: mrmeee.flatman.flatman_repository_subset
  - module: mrmeee.flatman.flatman_repository_info
'''

EXAMPLES = r'''
- name: List every subset on the server
  mrmeee.flatman.flatman_repository_subset_info:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
  register: all_subsets

- name: List the subsets of the stable repository
  mrmeee.flatman.flatman_repository_subset_info:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    repository: stable
  register: stable_subsets

- name: Show the collection IDs of the stable subsets
  ansible.builtin.debug:
    msg: "{{ stable_subsets.repository_subsets | map(attribute='collection_id') | list }}"
'''

RETURN = r'''
repository_subsets:
  description: The matching repository subsets.
  returned: always
  type: list
  elements: dict
  sample:
    - id: 7
      name: apps
      collection_id: org.example.Stable.Apps
      base_url: https://cdn.example.com/stable/apps
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.mrmeee.flatman.plugins.module_utils.flatman import (
    flatman_argument_spec,
    run_module,
)

COLLECTION_PATH = '/api/repository-subsets/'
REPOSITORY_PATH = '/api/repositories/'


def main():
    argument_spec = flatman_argument_spec()
    argument_spec.update(
        name=dict(type='str'),
        id=dict(type='int'),
        repository=dict(type='str'),
        repository_id=dict(type='int'),
        search=dict(type='str'),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        mutually_exclusive=[['repository', 'repository_id'], ['id', 'name']],
    )

    def handler(client):
        params = module.params

        if params['id'] is not None:
            found = client.get_or_none('%s%s/' % (COLLECTION_PATH, params['id']))
            module.exit_json(changed=False, repository_subsets=[found] if found else [])

        repository_id = params['repository_id']
        if params['repository']:
            repository_id = client.resolve(
                REPOSITORY_PATH, 'name', params['repository'], 'Repository')['id']

        query = dict(repository=repository_id, search=params['search'])
        subsets = client.get_all(COLLECTION_PATH, params=query)
        if params['name']:
            subsets = [s for s in subsets if s.get('name') == params['name']]

        module.exit_json(changed=False, repository_subsets=subsets)

    run_module(module, handler)


if __name__ == '__main__':
    main()
