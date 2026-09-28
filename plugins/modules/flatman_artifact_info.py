#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 MrMEEE
# MIT License

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
module: flatman_artifact_info
short_description: Gather information about flat-manager build artifacts
version_added: 1.0.0
description:
  - Retrieve one or more build artifact records from a flat-manager-django server.
  - Wraps the C(/api/artifacts/) endpoint.
author:
  - MrMEEE (@MrMEEE)
extends_documentation_fragment:
  - mrmeee.flatman.flatman
  - mrmeee.flatman.flatman.attributes_info
options:
  id:
    description:
      - Return only the artifact with this numeric ID.
    type: int
  build_id:
    description:
      - Return only artifacts belonging to the build with this numeric ID.
    type: int
  filename:
    description:
      - Return only the artifact with this exact filename.
    type: str
  search:
    description:
      - Free text search across the artifact filename.
    type: str
seealso:
  - module: mrmeee.flatman.flatman_artifact
  - module: mrmeee.flatman.flatman_build_info
'''

EXAMPLES = r'''
- name: List every artifact
  mrmeee.flatman.flatman_artifact_info:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
  register: artifacts

- name: List the artifacts of one build
  mrmeee.flatman.flatman_artifact_info:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    build_id: 48
  register: build_artifacts

- name: Show the total size of the artifacts of a build
  ansible.builtin.debug:
    msg: "{{ build_artifacts.artifacts | map(attribute='file_size') | sum }} bytes"
'''

RETURN = r'''
artifacts:
  description: The matching artifacts.
  returned: always
  type: list
  elements: dict
  sample:
    - id: 91
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
        id=dict(type='int'),
        build_id=dict(type='int'),
        filename=dict(type='str'),
        search=dict(type='str'),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        mutually_exclusive=[['id', 'filename']],
    )

    def handler(client):
        params = module.params

        if params['id'] is not None:
            found = client.get_or_none('%s%s/' % (COLLECTION_PATH, params['id']))
            artifacts = [found] if found else []
        else:
            query = dict(build=params['build_id'], search=params['search'])
            artifacts = client.get_all(COLLECTION_PATH, params=query)
            if params['filename']:
                artifacts = [a for a in artifacts if a.get('filename') == params['filename']]

        module.exit_json(changed=False, artifacts=artifacts)

    run_module(module, handler)


if __name__ == '__main__':
    main()
