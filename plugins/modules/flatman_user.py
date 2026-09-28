#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 MrMEEE
# MIT License

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
module: flatman_user
short_description: Manage flat-manager user accounts
version_added: 1.0.0
description:
  - Create, update and delete user records on a flat-manager-django server.
  - Wraps the C(/api/users/) endpoint.
author:
  - MrMEEE (@MrMEEE)
extends_documentation_fragment:
  - mrmeee.flatman.flatman
  - mrmeee.flatman.flatman.attributes
options:
  username:
    description:
      - Login name of the user. Used as the unique key for idempotency.
    type: str
    required: true
  state:
    description:
      - Whether the user should exist or not.
    type: str
    choices: [present, absent]
    default: present
  email:
    description:
      - Email address of the user.
    type: str
  first_name:
    description:
      - Given name of the user.
    type: str
  last_name:
    description:
      - Family name of the user.
    type: str
  is_local:
    description:
      - Whether this is a locally managed account rather than one provided by an external identity source.
    type: bool
notes:
  - This module manages user records only. The API serializer exposes no password field, so a
    password cannot be set or changed here. Set local passwords through the web UI or a Django
    management command on the server.
  - Creating, updating and deleting users requires an administrator API token. Read access only
    requires an authenticated token.
  - Creating a user also creates an empty user profile on the server through a post-save signal.
seealso:
  - module: mrmeee.flatman.flatman_user_info
  - module: mrmeee.flatman.flatman_user_profile
  - module: mrmeee.flatman.flatman_token
'''

EXAMPLES = r'''
- name: Create a local maintainer account
  mrmeee.flatman.flatman_user:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    username: jdoe
    email: jdoe@example.com
    first_name: Jane
    last_name: Doe
    is_local: true

- name: Update the email address of an existing user
  mrmeee.flatman.flatman_user:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    username: jdoe
    email: jane.doe@example.com

- name: Remove a user that left the project
  mrmeee.flatman.flatman_user:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    username: olduser
    state: absent
'''

RETURN = r'''
user:
  description: The user as returned by the API after the change.
  returned: when O(state=present)
  type: dict
  sample:
    id: 7
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
        username=dict(type='str', required=True),
        state=dict(type='str', default='present', choices=['present', 'absent']),
        email=dict(type='str'),
        first_name=dict(type='str'),
        last_name=dict(type='str'),
        is_local=dict(type='bool'),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    def handler(client):
        params = module.params
        state = params['state']
        current = client.find_one(COLLECTION_PATH, 'username', params['username'],
                                  params=dict(search=params['username']))

        if state == 'absent':
            changed, _obj, diff = client.ensure(COLLECTION_PATH, current, {}, state='absent')
            module.exit_json(changed=changed, diff=diff)

        desired = dict(
            username=params['username'],
            email=params['email'],
            first_name=params['first_name'],
            last_name=params['last_name'],
            is_local=params['is_local'],
        )

        changed, user, diff = client.ensure(COLLECTION_PATH, current, desired)
        module.exit_json(changed=changed, user=user, diff=diff)

    run_module(module, handler)


if __name__ == '__main__':
    main()
