#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 MrMEEE
# MIT License

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
module: flatman_gpg_key
short_description: Manage flat-manager GPG signing keys
version_added: 1.0.0
description:
  - Create, update and delete GPG key records on a flat-manager-django server.
  - Can also ask the server to generate a brand new key pair, or import an existing one.
  - Wraps the C(/api/gpg-keys/) endpoint and its C(generate) and C(import_key) actions.
author:
  - MrMEEE (@MrMEEE)
extends_documentation_fragment:
  - mrmeee.flatman.flatman
  - mrmeee.flatman.flatman.attributes
options:
  name:
    description:
      - Name of the key. Used as the unique key for idempotency.
    type: str
    required: true
  state:
    description:
      - V(present) manages a key record through plain CRUD.
      - V(absent) deletes the key.
      - V(generated) asks the server to create a new key pair, but only when no key with
        this name exists yet. Generating is not repeatable, so the existence check is
        what makes this option safe to run more than once.
      - V(imported) uploads an existing key pair, but only when no key with this name
        exists yet.
    type: str
    choices: [present, absent, generated, imported]
    default: present
  email:
    description:
      - Email address associated with the key.
      - Required by the server when O(state=generated) or O(state=imported).
    type: str
  comment:
    description:
      - Comment embedded in the generated key user ID.
      - Only used when O(state=generated).
    type: str
  key_length:
    description:
      - Size in bits of the generated RSA key.
      - Only used when O(state=generated).
    type: int
    default: 4096
  key_id:
    description:
      - Short GPG key ID. Normally filled in by the server.
    type: str
  fingerprint:
    description:
      - Full GPG fingerprint. Normally filled in by the server.
    type: str
  public_key:
    description:
      - ASCII armored public key.
      - Required when O(state=imported).
    type: str
  private_key:
    description:
      - ASCII armored private key, used only when O(state=imported).
      - Never returned by the API once stored.
    type: str
  passphrase:
    description:
      - Passphrase protecting O(private_key), used only when O(state=imported).
    type: str
  passphrase_hint:
    description:
      - Free form reminder of where the passphrase is kept.
    type: str
  is_active:
    description:
      - Whether the key is active.
    type: bool
seealso:
  - module: mrmeee.flatman.flatman_gpg_key_info
  - module: mrmeee.flatman.flatman_repository
'''

EXAMPLES = r'''
- name: Generate a signing key if the server does not have one yet
  mrmeee.flatman.flatman_gpg_key:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    name: release-signing-key
    email: release@example.com
    comment: Example release signing key
    key_length: 4096
    state: generated
  register: signing_key
  no_log: true

- name: Import an existing key pair
  mrmeee.flatman.flatman_gpg_key:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    name: legacy-signing-key
    email: legacy@example.com
    public_key: "{{ lookup('file', 'legacy.pub.asc') }}"
    private_key: "{{ lookup('file', 'legacy.sec.asc') }}"
    passphrase: "{{ vaulted_legacy_passphrase }}"
    state: imported

- name: Retire a key without deleting it
  mrmeee.flatman.flatman_gpg_key:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    name: legacy-signing-key
    is_active: false
'''

RETURN = r'''
gpg_key:
  description:
    - The GPG key as returned by the API after the change.
    - When a key has just been generated the server may include a C(private_key) member.
      That member is only available in the response of the generate action and can never
      be read back afterwards, so store it somewhere safe and use C(no_log) on the task.
  returned: when O(state) is V(present), V(generated) or V(imported)
  type: dict
  sample:
    id: 2
    name: release-signing-key
    email: release@example.com
    key_id: A1B2C3D4E5F60718
    fingerprint: 1234567890ABCDEF1234567890ABCDEF12345678
    public_key: "-----BEGIN PGP PUBLIC KEY BLOCK-----"
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
        name=dict(type='str', required=True),
        state=dict(type='str', default='present',
                   choices=['present', 'absent', 'generated', 'imported']),
        email=dict(type='str'),
        comment=dict(type='str'),
        key_length=dict(type='int', default=4096, no_log=False),
        key_id=dict(type='str', no_log=False),
        fingerprint=dict(type='str'),
        public_key=dict(type='str', no_log=False),
        private_key=dict(type='str', no_log=True),
        passphrase=dict(type='str', no_log=True),
        passphrase_hint=dict(type='str', no_log=False),
        is_active=dict(type='bool'),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[
            ['state', 'generated', ['email']],
            ['state', 'imported', ['email', 'public_key']],
        ],
    )

    def handler(client):
        params = module.params
        state = params['state']
        current = client.find_one(COLLECTION_PATH, 'name', params['name'])

        if state == 'absent':
            changed, dummy, diff = client.ensure(COLLECTION_PATH, current, {}, state='absent')
            module.exit_json(changed=changed, diff=diff)

        if state in ('generated', 'imported'):
            if current is not None:
                module.exit_json(changed=False, gpg_key=current)

            if state == 'generated':
                action = '%sgenerate/' % COLLECTION_PATH
                payload = dict(
                    name=params['name'],
                    email=params['email'],
                    comment=params['comment'] or '',
                    key_length=params['key_length'],
                )
            else:
                action = '%simport_key/' % COLLECTION_PATH
                payload = dict(
                    name=params['name'],
                    email=params['email'],
                    public_key=params['public_key'],
                    private_key=params['private_key'] or '',
                    passphrase=params['passphrase'],
                )
                payload = dict((k, v) for k, v in payload.items() if v is not None)

            if module.check_mode:
                module.exit_json(changed=True, gpg_key=dict(name=params['name']),
                                 diff=client.make_diff({}, payload))

            created = client.post(action, data=payload, expect=(200, 201))
            module.exit_json(changed=True, gpg_key=created,
                             diff=client.make_diff({}, created))

        desired = dict(
            name=params['name'],
            email=params['email'],
            key_id=params['key_id'],
            fingerprint=params['fingerprint'],
            public_key=params['public_key'],
            passphrase_hint=params['passphrase_hint'],
            is_active=params['is_active'],
        )

        changed, gpg_key, diff = client.ensure(COLLECTION_PATH, current, desired)
        module.exit_json(changed=changed, gpg_key=gpg_key, diff=diff)

    run_module(module, handler)


if __name__ == '__main__':
    main()
