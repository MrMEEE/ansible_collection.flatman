#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 MrMEEE
# MIT License

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
module: flatman_gpg_key_info
short_description: Gather information about flat-manager GPG keys
version_added: 1.0.0
description:
  - Retrieve one or more GPG key records from a flat-manager-django server.
  - Optionally fetch the ASCII armored public key of every returned key.
  - Private key material is never exposed by the API and is therefore never returned.
author:
  - MrMEEE (@MrMEEE)
extends_documentation_fragment:
  - mrmeee.flatman.flatman
  - mrmeee.flatman.flatman.attributes_info
options:
  name:
    description:
      - Return only the key with this exact name.
    type: str
  id:
    description:
      - Return only the key with this numeric ID.
    type: int
  email:
    description:
      - Return only keys with this exact email address.
    type: str
  search:
    description:
      - Free text search across name, email, key ID and fingerprint.
    type: str
  include:
    description:
      - Extra sub-resources to fetch for every returned key.
      - V(public_key) merges the result of the C(public_key) action into each key.
    type: list
    elements: str
    choices: [public_key]
seealso:
  - module: mrmeee.flatman.flatman_gpg_key
'''

EXAMPLES = r'''
- name: List all GPG keys
  mrmeee.flatman.flatman_gpg_key_info:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
  register: keys

- name: Fetch one key including its armored public key
  mrmeee.flatman.flatman_gpg_key_info:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    name: release-signing-key
    include:
      - public_key
  register: signing_key

- name: Write the public key to disk
  ansible.builtin.copy:
    content: "{{ signing_key.gpg_keys[0].public_key }}"
    dest: /etc/pki/example-release.asc
    mode: "0644"
'''

RETURN = r'''
gpg_keys:
  description: The matching GPG keys.
  returned: always
  type: list
  elements: dict
  sample:
    - id: 2
      name: release-signing-key
      email: release@example.com
      key_id: A1B2C3D4E5F60718
      fingerprint: 1234567890ABCDEF1234567890ABCDEF12345678
      is_active: true
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.mrmeee.flatman.plugins.module_utils.flatman import (
    flatman_argument_spec,
    run_module,
)

COLLECTION_PATH = '/api/gpg-keys/'


def main():
    argument_spec = flatman_argument_spec()
    argument_spec.update(
        name=dict(type='str'),
        id=dict(type='int'),
        email=dict(type='str'),
        search=dict(type='str'),
        include=dict(type='list', elements='str', choices=['public_key']),
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
            gpg_keys = [found] if found else []
        else:
            gpg_keys = client.get_all(COLLECTION_PATH, params=dict(search=params['search']))
            if params['name']:
                gpg_keys = [k for k in gpg_keys if k.get('name') == params['name']]
            if params['email']:
                gpg_keys = [k for k in gpg_keys if k.get('email') == params['email']]

        if 'public_key' in include:
            for gpg_key in gpg_keys:
                gpg_key.update(client.get('%s%s/public_key/' % (COLLECTION_PATH, gpg_key['id'])))

        module.exit_json(changed=False, gpg_keys=gpg_keys)

    run_module(module, handler)


if __name__ == '__main__':
    main()
