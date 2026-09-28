#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 MrMEEE
# MIT License

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
module: flatman_repository
short_description: Manage flat-manager Flatpak/OSTree repositories
version_added: 1.0.0
description:
  - Create, update and delete repositories on a flat-manager-django server.
  - Wraps the C(/api/repositories/) endpoint.
author:
  - MrMEEE (@MrMEEE)
extends_documentation_fragment:
  - mrmeee.flatman.flatman
  - mrmeee.flatman.flatman.attributes
options:
  name:
    description:
      - Name of the repository. Used as the unique key for idempotency.
    type: str
    required: true
  state:
    description:
      - Whether the repository should exist or not.
    type: str
    choices: [present, absent]
    default: present
  collection_id:
    description:
      - OSTree collection ID advertised by this repository, for example C(org.example.Repo).
    type: str
  description:
    description:
      - Free form description of the repository.
    type: str
  gpg_key:
    description:
      - Name of the GPG key used to sign commits in this repository.
      - Mutually exclusive with O(gpg_key_id).
    type: str
  gpg_key_id:
    description:
      - Numeric ID of the GPG key used to sign commits in this repository.
      - Mutually exclusive with O(gpg_key).
    type: int
  parent_repos:
    description:
      - Names or numeric IDs of the parent repositories this repository inherits from.
      - Replaces the existing list when specified.
    type: list
    elements: raw
  is_active:
    description:
      - Whether the repository is active.
    type: bool
seealso:
  - module: mrmeee.flatman.flatman_repository_info
  - module: mrmeee.flatman.flatman_repository_subset
  - module: mrmeee.flatman.flatman_gpg_key
'''

EXAMPLES = r'''
- name: Create a stable repository signed with an existing key
  mrmeee.flatman.flatman_repository:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    name: stable
    collection_id: org.example.Stable
    description: Production Flatpak repository
    gpg_key: release-signing-key
    is_active: true

- name: Chain beta on top of stable
  mrmeee.flatman.flatman_repository:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    name: beta
    collection_id: org.example.Beta
    parent_repos:
      - stable

- name: Remove a retired repository
  mrmeee.flatman.flatman_repository:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    name: old-testing
    state: absent
'''

RETURN = r'''
repository:
  description: The repository as returned by the API after the change.
  returned: when O(state=present)
  type: dict
  sample:
    id: 3
    name: stable
    collection_id: org.example.Stable
    description: Production Flatpak repository
    repo_path: /var/lib/flat-manager/repos/stable
    is_active: true
    build_count: 42
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.mrmeee.flatman.plugins.module_utils.flatman import (
    flatman_argument_spec,
    run_module,
)

COLLECTION_PATH = '/api/repositories/'


def resolve_repo_ids(client, values):
    ids = []
    for value in values:
        if isinstance(value, int) or (isinstance(value, str) and value.isdigit()):
            ids.append(int(value))
        else:
            ids.append(client.resolve(COLLECTION_PATH, 'name', value, 'Repository')['id'])
    return ids


def main():
    argument_spec = flatman_argument_spec()
    argument_spec.update(
        name=dict(type='str', required=True),
        state=dict(type='str', default='present', choices=['present', 'absent']),
        collection_id=dict(type='str'),
        description=dict(type='str'),
        gpg_key=dict(type='str', no_log=False),
        gpg_key_id=dict(type='int'),
        parent_repos=dict(type='list', elements='raw'),
        is_active=dict(type='bool'),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        mutually_exclusive=[['gpg_key', 'gpg_key_id']],
    )

    def handler(client):
        params = module.params
        state = params['state']
        current = client.find_one(COLLECTION_PATH, 'name', params['name'])

        if state == 'absent':
            changed, obj, diff = client.ensure(COLLECTION_PATH, current, {}, state='absent')
            module.exit_json(changed=changed, diff=diff)

        gpg_key_id = params['gpg_key_id']
        if params['gpg_key']:
            gpg_key_id = client.resolve('/api/gpg-keys/', 'name', params['gpg_key'], 'GPG key')['id']

        desired = dict(
            name=params['name'],
            collection_id=params['collection_id'],
            description=params['description'],
            gpg_key_id=gpg_key_id,
            is_active=params['is_active'],
        )
        if params['parent_repos'] is not None:
            desired['parent_repos'] = resolve_repo_ids(client, params['parent_repos'])

        comparable = None
        if current is not None:
            comparable = dict(current)
            # gpg_key_id is write-only; the API returns it nested under gpg_key.
            comparable['gpg_key_id'] = (current.get('gpg_key') or {}).get('id')

        changed, repository, diff = client.ensure(COLLECTION_PATH, comparable, desired)
        module.exit_json(changed=changed, repository=repository, diff=diff)

    run_module(module, handler)


if __name__ == '__main__':
    main()
