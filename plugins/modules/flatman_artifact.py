#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 MrMEEE
# MIT License

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
module: flatman_artifact
short_description: Manage flat-manager build artifacts
version_added: 1.0.0
description:
  - Register, update and delete build artifact records on a flat-manager-django server.
  - Wraps the C(/api/artifacts/) endpoint.
author:
  - MrMEEE (@MrMEEE)
extends_documentation_fragment:
  - mrmeee.flatman.flatman
  - mrmeee.flatman.flatman.attributes
options:
  filename:
    description:
      - Name of the artifact file, for example C(org.example.MyApp.flatpak).
      - Together with O(build_id) this forms the unique key used for idempotency.
    type: str
    required: true
  build_id:
    description:
      - Numeric ID of the build the artifact belongs to.
      - Required when the artifact has to be created, and used to narrow the search server side.
    type: int
  file_path:
    description:
      - Path of the artifact file on the flat-manager server.
    type: str
  file_size:
    description:
      - Size of the artifact file in bytes.
    type: int
  checksum:
    description:
      - Checksum of the artifact file, normally a SHA256 hex digest.
    type: str
  state:
    description:
      - Whether the artifact record should exist or not.
    type: str
    choices: [present, absent]
    default: present
notes:
  - This module only manages the artifact metadata record. The file itself has to be placed on the
    server by other means, because the API offers no multipart upload that this collection can use.
  - The owning build is written as C(build_id) but is not returned by the API, so O(build_id)
    is never compared for idempotency.
seealso:
  - module: mrmeee.flatman.flatman_artifact_info
  - module: mrmeee.flatman.flatman_build_info
'''

EXAMPLES = r'''
- name: Register a bundle produced by build 48
  mrmeee.flatman.flatman_artifact:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    build_id: 48
    filename: org.example.MyApp.flatpak
    file_path: /var/lib/flat-manager/artifacts/48/org.example.MyApp.flatpak
    file_size: 48271360
    checksum: 4a3b1c8d9e0f1a2b3c4d5e6f708192a3b4c5d6e7f8091a2b3c4d5e6f70819200

- name: Correct the recorded size of an artifact
  mrmeee.flatman.flatman_artifact:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    build_id: 48
    filename: org.example.MyApp.flatpak
    file_size: 48271872

- name: Remove an artifact record
  mrmeee.flatman.flatman_artifact:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    build_id: 48
    filename: org.example.MyApp.flatpak
    state: absent
'''

RETURN = r'''
artifact:
  description: The artifact as returned by the API after the change.
  returned: when O(state=present)
  type: dict
  sample:
    id: 91
    filename: org.example.MyApp.flatpak
    file_path: /var/lib/flat-manager/artifacts/48/org.example.MyApp.flatpak
    file_size: 48271360
    checksum: 4a3b1c8d9e0f1a2b3c4d5e6f708192a3b4c5d6e7f8091a2b3c4d5e6f70819200
    uploaded_at: '2026-04-11T09:31:02Z'
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.mrmeee.flatman.plugins.module_utils.flatman import (
    flatman_argument_spec,
    run_module,
)

COLLECTION_PATH = '/api/artifacts/'


def main():
    argument_spec = flatman_argument_spec()
    argument_spec.update(
        filename=dict(type='str', required=True),
        build_id=dict(type='int'),
        file_path=dict(type='str'),
        file_size=dict(type='int'),
        checksum=dict(type='str', no_log=False),
        state=dict(type='str', default='present', choices=['present', 'absent']),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[['state', 'present', ['build_id']]],
    )

    def handler(client):
        params = module.params
        state = params['state']

        query = dict(build=params['build_id'])
        current = client.find_one(COLLECTION_PATH, 'filename', params['filename'], params=query)

        if state == 'absent':
            changed, dummy, diff = client.ensure(COLLECTION_PATH, current, {}, state='absent')
            module.exit_json(changed=changed, diff=diff)

        desired = dict(
            filename=params['filename'],
            build_id=params['build_id'],
            file_path=params['file_path'],
            file_size=params['file_size'],
            checksum=params['checksum'],
        )

        comparable = None
        if current is not None:
            comparable = dict(current)
            # build_id is write-only, so it must not create a diff.
            comparable['build_id'] = params['build_id']

        changed, artifact, diff = client.ensure(COLLECTION_PATH, comparable, desired)
        module.exit_json(changed=changed, artifact=artifact, diff=diff)

    run_module(module, handler)


if __name__ == '__main__':
    main()
