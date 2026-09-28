#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 MrMEEE
# MIT License

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
module: flatman_token_info
short_description: Gather information about flat-manager repository access tokens
version_added: 1.0.0
description:
  - Retrieve one or more repository scoped access tokens from a flat-manager-django server.
  - Wraps the C(/api/tokens/) endpoint.
author:
  - MrMEEE (@MrMEEE)
extends_documentation_fragment:
  - mrmeee.flatman.flatman
  - mrmeee.flatman.flatman.attributes_info
options:
  name:
    description:
      - Return only the token with this exact name.
    type: str
  id:
    description:
      - Return only the token with this numeric ID.
    type: int
  repository:
    description:
      - Restrict the result to tokens of the repository with this name.
      - Mutually exclusive with O(repository_id).
    type: str
  repository_id:
    description:
      - Restrict the result to tokens of the repository with this numeric ID.
      - Mutually exclusive with O(repository).
    type: int
  token_type:
    description:
      - Restrict the result to tokens granting this kind of access.
    type: str
    choices: [upload, download, admin]
  is_active:
    description:
      - Restrict the result to tokens with this active flag.
    type: bool
notes:
  - B(These tokens are not enforced by the server yet.) The flat-manager-django server
    stores repository tokens but no code path validates an incoming request against them,
    so the values returned here currently grant no access.
  - Repository tokens are not the same thing as the O(api_token) used to talk to the API.
    That one is a user scoped Django REST Framework token and cannot be read from this
    endpoint.
  - Every returned token carries its secret value, so use C(no_log) on tasks that
    register the result.
seealso:
  - module: mrmeee.flatman.flatman_token
'''

EXAMPLES = r'''
- name: List the active upload tokens of the stable repository
  mrmeee.flatman.flatman_token_info:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    repository: stable
    token_type: upload
    is_active: true
  register: upload_tokens
  no_log: true

- name: Fail when the CI token is missing
  ansible.builtin.assert:
    that: upload_tokens.tokens | selectattr('name', 'equalto', 'ci-upload') | list | length == 1
    fail_msg: The ci-upload token is not present

- name: Look up a single token by ID
  mrmeee.flatman.flatman_token_info:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    id: 11
  register: one_token
  no_log: true
'''

RETURN = r'''
tokens:
  description:
    - The matching tokens.
    - Each entry contains the secret C(token) value, so treat the result as sensitive.
  returned: always
  type: list
  elements: dict
  sample:
    - id: 11
      name: ci-upload
      token_type: upload
      token: VALUE_SPECIFIED_IN_NO_LOG_PARAMETER
      expires_at: "2027-01-31T23:59:59Z"
      is_active: true
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.mrmeee.flatman.plugins.module_utils.flatman import (
    flatman_argument_spec,
    run_module,
)

COLLECTION_PATH = '/api/tokens/'
REPOSITORY_PATH = '/api/repositories/'


def main():
    argument_spec = flatman_argument_spec()
    argument_spec.update(
        name=dict(type='str'),
        id=dict(type='int'),
        repository=dict(type='str'),
        repository_id=dict(type='int'),
        token_type=dict(type='str', choices=['upload', 'download', 'admin'], no_log=False),
        is_active=dict(type='bool'),
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
            module.exit_json(changed=False, tokens=[found] if found else [])

        repository_id = params['repository_id']
        if params['repository']:
            repository_id = client.resolve(
                REPOSITORY_PATH, 'name', params['repository'], 'Repository')['id']

        query = dict(
            repository=repository_id,
            token_type=params['token_type'],
            is_active=params['is_active'],
        )
        tokens = client.get_all(COLLECTION_PATH, params=query)
        if params['name']:
            tokens = [t for t in tokens if t.get('name') == params['name']]

        module.exit_json(changed=False, tokens=tokens)

    run_module(module, handler)


if __name__ == '__main__':
    main()
