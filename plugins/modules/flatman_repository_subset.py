#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 MrMEEE
# MIT License

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
module: flatman_repository_subset
short_description: Manage flat-manager repository subsets
version_added: 1.0.0
description:
  - Create, update and delete repository subsets on a flat-manager-django server.
  - A subset is a partial mirror of a repository with its own collection ID and base URL.
  - Wraps the C(/api/repository-subsets/) endpoint.
author:
  - MrMEEE (@MrMEEE)
extends_documentation_fragment:
  - mrmeee.flatman.flatman
  - mrmeee.flatman.flatman.attributes
options:
  name:
    description:
      - Name of the subset.
      - Together with the owning repository this forms the unique key used for idempotency.
    type: str
    required: true
  repository:
    description:
      - Name of the repository owning the subset.
      - Mutually exclusive with O(repository_id).
    type: str
  repository_id:
    description:
      - Numeric ID of the repository owning the subset.
      - Mutually exclusive with O(repository).
    type: int
  collection_id:
    description:
      - OSTree collection ID advertised by this subset, for example C(org.example.Repo.Stable).
    type: str
  base_url:
    description:
      - Base URL clients use to reach this subset.
    type: str
  state:
    description:
      - Whether the subset should exist or not.
    type: str
    choices: [present, absent]
    default: present
notes:
  - The owning repository is written as C(repository_id) but is not returned by the API, so the
    module filters the list endpoint server side by repository ID and then matches O(name) locally.
seealso:
  - module: mrmeee.flatman.flatman_repository_subset_info
  - module: mrmeee.flatman.flatman_repository
'''

EXAMPLES = r'''
- name: Create a stable subset of the main repository
  mrmeee.flatman.flatman_repository_subset:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    repository: stable
    name: apps
    collection_id: org.example.Stable.Apps
    base_url: https://cdn.example.com/stable/apps

- name: Point an existing subset at a new CDN
  mrmeee.flatman.flatman_repository_subset:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    repository_id: 3
    name: apps
    base_url: https://cdn2.example.com/stable/apps

- name: Remove a subset
  mrmeee.flatman.flatman_repository_subset:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    repository: stable
    name: legacy
    state: absent
'''

RETURN = r'''
repository_subset:
  description: The repository subset as returned by the API after the change.
  returned: when O(state=present)
  type: dict
  sample:
    id: 7
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
        name=dict(type='str', required=True),
        repository=dict(type='str'),
        repository_id=dict(type='int'),
        collection_id=dict(type='str'),
        base_url=dict(type='str'),
        state=dict(type='str', default='present', choices=['present', 'absent']),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        mutually_exclusive=[['repository', 'repository_id']],
        required_one_of=[['repository', 'repository_id']],
    )

    def handler(client):
        params = module.params

        repository_id = params['repository_id']
        if params['repository']:
            repository_id = client.resolve(
                REPOSITORY_PATH, 'name', params['repository'], 'Repository')['id']

        current = client.find_one(
            COLLECTION_PATH, 'name', params['name'], params=dict(repository=repository_id))

        if params['state'] == 'absent':
            changed, dummy, diff = client.ensure(COLLECTION_PATH, current, {}, state='absent')
            module.exit_json(changed=changed, diff=diff)

        desired = dict(
            name=params['name'],
            repository_id=repository_id,
            collection_id=params['collection_id'],
            base_url=params['base_url'],
        )

        comparable = None
        if current is not None:
            comparable = dict(current)
            # repository_id is write-only, but it is known from the filter above.
            comparable['repository_id'] = repository_id

        changed, subset, diff = client.ensure(COLLECTION_PATH, comparable, desired)
        module.exit_json(changed=changed, repository_subset=subset, diff=diff)

    run_module(module, handler)


if __name__ == '__main__':
    main()
