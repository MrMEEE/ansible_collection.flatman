#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 MrMEEE
# MIT License

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
module: flatman_user_profile
short_description: Manage flat-manager user profiles
version_added: 1.0.0
description:
  - Create, update and delete the profile attached to a flat-manager user.
  - Wraps the C(/api/profiles/) endpoint.
author:
  - MrMEEE (@MrMEEE)
extends_documentation_fragment:
  - mrmeee.flatman.flatman
  - mrmeee.flatman.flatman.attributes
options:
  user:
    description:
      - Login name of the user whose profile is managed.
      - Mutually exclusive with O(user_id). One of the two is required.
    type: str
  user_id:
    description:
      - Numeric ID of the user whose profile is managed.
      - Mutually exclusive with O(user). One of the two is required.
    type: int
  state:
    description:
      - Whether the profile should exist or not.
    type: str
    choices: [present, absent]
    default: present
  bio:
    description:
      - Free form biography text shown on the profile page.
    type: str
  phone:
    description:
      - Contact phone number.
    type: str
  organization:
    description:
      - Organisation or company the user belongs to.
    type: str
notes:
  - The server already creates one empty profile automatically whenever a user is created, so in
    practice this module updates that profile rather than creating a new one.
  - A user can only have one profile, so the owning user is the natural key. Addressing a user
    that already has a profile updates it instead of failing.
  - Changing or deleting a profile requires an administrator API token.
seealso:
  - module: mrmeee.flatman.flatman_user
  - module: mrmeee.flatman.flatman_user_profile_info
'''

EXAMPLES = r'''
- name: Fill in the profile of an existing user
  mrmeee.flatman.flatman_user_profile:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    user: jdoe
    bio: Flatpak packager and release manager
    organization: Example Inc
    phone: "+45 12 34 56 78"

- name: Update only the organisation, addressing the user by ID
  mrmeee.flatman.flatman_user_profile:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    user_id: 7
    organization: Example Foundation

- name: Delete the profile of a decommissioned account
  mrmeee.flatman.flatman_user_profile:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    user: olduser
    state: absent
'''

RETURN = r'''
user_profile:
  description: The profile as returned by the API after the change.
  returned: when O(state=present)
  type: dict
  sample:
    id: 12
    user:
      id: 7
      username: jdoe
      email: jdoe@example.com
    bio: Flatpak packager and release manager
    phone: "+45 12 34 56 78"
    organization: Example Inc
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.mrmeee.flatman.plugins.module_utils.flatman import (
    flatman_argument_spec,
    run_module,
)

COLLECTION_PATH = '/api/profiles/'
USER_PATH = '/api/users/'


def profile_matches(profile, username, user_id):
    user = profile.get('user') or {}
    if username is not None:
        return user.get('username') == username
    return str(user.get('id')) == str(user_id)


def find_profile(client, username, user_id):
    for profile in client.get_all(COLLECTION_PATH):
        if profile_matches(profile, username, user_id):
            return profile
    return None


def main():
    argument_spec = flatman_argument_spec()
    argument_spec.update(
        user=dict(type='str'),
        user_id=dict(type='int'),
        state=dict(type='str', default='present', choices=['present', 'absent']),
        bio=dict(type='str'),
        phone=dict(type='str'),
        organization=dict(type='str'),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        mutually_exclusive=[['user', 'user_id']],
        required_one_of=[['user', 'user_id']],
    )

    def handler(client):
        params = module.params
        state = params['state']
        current = find_profile(client, params['user'], params['user_id'])

        if state == 'absent':
            changed, dummy, diff = client.ensure(COLLECTION_PATH, current, {}, state='absent')
            module.exit_json(changed=changed, diff=diff)

        user_id = params['user_id']
        if params['user']:
            user_id = client.resolve(
                USER_PATH, 'username', params['user'], 'User',
                params=dict(search=params['user']))['id']

        desired = dict(
            user_id=user_id,
            bio=params['bio'],
            phone=params['phone'],
            organization=params['organization'],
        )

        comparable = None
        if current is not None:
            comparable = dict(current)
            # user_id is write-only; the API returns it nested under user.
            comparable['user_id'] = (current.get('user') or {}).get('id')

        changed, profile, diff = client.ensure(COLLECTION_PATH, comparable, desired)
        module.exit_json(changed=changed, user_profile=profile, diff=diff)

    run_module(module, handler)


if __name__ == '__main__':
    main()
