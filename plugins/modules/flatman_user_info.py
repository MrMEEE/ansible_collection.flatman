#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 MrMEEE
# MIT License

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
module: flatman_user_info
short_description: Gather information about flat-manager users
version_added: 1.0.0
description:
  - Retrieve one or more user records from a flat-manager-django server.
  - Can also return the user the supplied API token belongs to.
author:
  - MrMEEE (@MrMEEE)
extends_documentation_fragment:
  - mrmeee.flatman.flatman
  - mrmeee.flatman.flatman.attributes_info
options:
  username:
    description:
      - Return only the user with this exact login name.
    type: str
  id:
    description:
      - Return only the user with this numeric ID.
    type: int
  search:
    description:
      - Free text search across username, email, first name and last name.
    type: str
  me:
    description:
      - Return only the user the API token authenticates as, using the C(/api/users/me/) endpoint.
      - Mutually exclusive with O(username) and O(id).
    type: bool
    default: false
seealso:
  - module: mrmeee.flatman.flatman_user
  - module: mrmeee.flatman.flatman_user_profile_info
'''

EXAMPLES = r'''
- name: List every user
  mrmeee.flatman.flatman_user_info:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
  register: all_users

- name: Look up a single user by name
  mrmeee.flatman.flatman_user_info:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    username: jdoe
  register: jdoe

- name: Show who the token belongs to
  mrmeee.flatman.flatman_user_info:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    me: true
  register: whoami

- name: Print the authenticated username
  ansible.builtin.debug:
    msg: "Authenticated as {{ whoami.users[0].username }}"
'''

RETURN = r'''
users:
  description: The matching users. Contains at most one element when O(me=true), O(id) or O(username) is set.
  returned: always
  type: list
  elements: dict
  sample:
    - id: 7
      username: jdoe
      email: jdoe@example.com
      first_name: Jane
      last_name: Doe
      is_local: true
      created_at: "2026-01-14T09:21:00Z"
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.mrmeee.flatman.plugins.module_utils.flatman import (
    flatman_argument_spec,
    run_module,
)

COLLECTION_PATH = '/api/users/'


def main():
    argument_spec = flatman_argument_spec()
    argument_spec.update(
        username=dict(type='str'),
        id=dict(type='int'),
        search=dict(type='str'),
        me=dict(type='bool', default=False),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        mutually_exclusive=[['id', 'username'], ['me', 'username'], ['me', 'id']],
    )

    def handler(client):
        params = module.params

        if params['me']:
            found = client.get_or_none('%sme/' % COLLECTION_PATH)
            users = [found] if found else []
        elif params['id'] is not None:
            found = client.get_or_none('%s%s/' % (COLLECTION_PATH, params['id']))
            users = [found] if found else []
        else:
            query = dict(search=params['search'] or params['username'])
            users = client.get_all(COLLECTION_PATH, params=query)
            if params['username']:
                users = [u for u in users if u.get('username') == params['username']]

        module.exit_json(changed=False, users=users)

    run_module(module, handler)


if __name__ == '__main__':
    main()
