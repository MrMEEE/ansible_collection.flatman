#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 MrMEEE
# MIT License

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
module: flatman_repository_info
short_description: Gather information about flat-manager repositories
version_added: 1.0.0
description:
  - Retrieve one or more repositories from a flat-manager-django server.
  - Optionally include the builds and subsets belonging to each repository.
author:
  - MrMEEE (@MrMEEE)
extends_documentation_fragment:
  - mrmeee.flatman.flatman
  - mrmeee.flatman.flatman.attributes_info
options:
  name:
    description:
      - Return only the repository with this exact name.
    type: str
  id:
    description:
      - Return only the repository with this numeric ID.
    type: int
  collection_id:
    description:
      - Filter repositories by OSTree collection ID.
    type: str
  is_active:
    description:
      - Filter repositories by their active flag.
    type: bool
  search:
    description:
      - Free text search across name, description and collection ID.
    type: str
  include:
    description:
      - Extra sub-resources to fetch for every returned repository.
      - V(builds) adds a C(builds) key, V(subsets) refreshes the C(subsets) key.
    type: list
    elements: str
    choices: [builds, subsets]
seealso:
  - module: mrmeee.flatman.flatman_repository
'''

EXAMPLES = r'''
- name: List all repositories
  mrmeee.flatman.flatman_repository_info:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
  register: repos

- name: Fetch one repository including its builds
  mrmeee.flatman.flatman_repository_info:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    name: stable
    include:
      - builds
  register: stable

- name: Show how many builds the stable repository has
  ansible.builtin.debug:
    msg: "{{ stable.repositories[0].builds | length }} builds"
'''

RETURN = r'''
repositories:
  description: The matching repositories.
  returned: always
  type: list
  elements: dict
  sample:
    - id: 3
      name: stable
      collection_id: org.example.Stable
      is_active: true
      build_count: 42
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.mrmeee.flatman.plugins.module_utils.flatman import (
    flatman_argument_spec,
    run_module,
)

COLLECTION_PATH = '/api/repositories/'


def main():
    argument_spec = flatman_argument_spec()
    argument_spec.update(
        name=dict(type='str'),
        id=dict(type='int'),
        collection_id=dict(type='str'),
        is_active=dict(type='bool'),
        search=dict(type='str'),
        include=dict(type='list', elements='str', choices=['builds', 'subsets']),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        mutually_exclusive=[['id', 'name']],
    )

    def handler(client):
        params = module.params
        include = params['include'] or []

        if params['id'] is not None:
            found = client.get_or_none('%s%s/' % (COLLECTION_PATH, params['id']))
            repositories = [found] if found else []
        else:
            query = dict(
                collection_id=params['collection_id'],
                is_active=params['is_active'],
                search=params['search'],
            )
            repositories = client.get_all(COLLECTION_PATH, params=query)
            if params['name']:
                repositories = [r for r in repositories if r.get('name') == params['name']]

        for repository in repositories:
            if 'builds' in include:
                repository['builds'] = client.get_all('%s%s/builds/' % (COLLECTION_PATH, repository['id']))
            if 'subsets' in include:
                repository['subsets'] = client.get_all('%s%s/subsets/' % (COLLECTION_PATH, repository['id']))

        module.exit_json(changed=False, repositories=repositories)

    run_module(module, handler)


if __name__ == '__main__':
    main()
