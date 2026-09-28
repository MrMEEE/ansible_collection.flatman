#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 MrMEEE
# MIT License

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
module: flatman_user_profile_info
short_description: Gather information about flat-manager user profiles
version_added: 1.0.0
description:
  - Retrieve one or more user profiles from a flat-manager-django server.
  - Wraps the C(/api/profiles/) endpoint.
author:
  - MrMEEE (@MrMEEE)
extends_documentation_fragment:
  - mrmeee.flatman.flatman
  - mrmeee.flatman.flatman.attributes_info
options:
  user:
    description:
      - Return only the profile belonging to the user with this login name.
    type: str
  user_id:
    description:
      - Return only the profile belonging to the user with this numeric ID.
    type: int
  id:
    description:
      - Return only the profile with this numeric profile ID, fetched from the detail endpoint.
    type: int
notes:
  - The profile serializer exposes C(user) as a nested read-only object, so filtering by
    O(user) or O(user_id) is done on the nested user object
    after the list has been retrieved.
seealso:
  - module: mrmeee.flatman.flatman_user_profile
  - module: mrmeee.flatman.flatman_user_info
'''

EXAMPLES = r'''
- name: List every user profile
  mrmeee.flatman.flatman_user_profile_info:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
  register: profiles

- name: Fetch the profile of a single user
  mrmeee.flatman.flatman_user_profile_info:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    user: jdoe
  register: jdoe_profile

- name: Show the organisation of that user
  ansible.builtin.debug:
    msg: "{{ jdoe_profile.user_profiles[0].organization }}"
'''

RETURN = r'''
user_profiles:
  description: The matching user profiles.
  returned: always
  type: list
  elements: dict
  sample:
    - user:
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


def main():
    argument_spec = flatman_argument_spec()
    argument_spec.update(
        user=dict(type='str'),
        user_id=dict(type='int'),
        id=dict(type='int'),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        mutually_exclusive=[['user', 'user_id'], ['id', 'user'], ['id', 'user_id']],
    )

    def handler(client):
        params = module.params

        if params['id'] is not None:
            found = client.get_or_none('%s%s/' % (COLLECTION_PATH, params['id']))
            profiles = [found] if found else []
        else:
            profiles = client.get_all(COLLECTION_PATH)
            if params['user']:
                profiles = [p for p in profiles
                            if (p.get('user') or {}).get('username') == params['user']]
            elif params['user_id'] is not None:
                profiles = [p for p in profiles
                            if str((p.get('user') or {}).get('id')) == str(params['user_id'])]

        module.exit_json(changed=False, user_profiles=profiles)

    run_module(module, handler)


if __name__ == '__main__':
    main()
