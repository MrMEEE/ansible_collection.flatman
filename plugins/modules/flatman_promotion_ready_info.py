#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 MrMEEE
# MIT License

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
module: flatman_promotion_ready_info
short_description: List published Flatpak builds and External versions ready to promote
version_added: 1.2.0
description:
  - Query the server-calculated promotion eligibility for published Flatpak builds and External versions.
  - Each result is one eligible source and target repository pair.
  - Repository-chain prerequisites and existing promotion records are evaluated by the server.
author:
  - MrMEEE (@MrMEEE)
extends_documentation_fragment:
  - mrmeee.flatman.flatman
  - mrmeee.flatman.flatman.attributes_info
options:
  kind:
    description: Limit results to Flatpak builds, External versions, or both.
    type: str
    choices: [both, build, external]
    default: both
  build_id:
    description: Restrict candidates to this published build-history ID.
    type: int
  external_ref_id:
    description: Restrict candidates to this External definition ID.
    type: int
  external_ref_version_id:
    description: Restrict candidates to this immutable External version ID.
    type: int
  repository:
    description:
      - Restrict candidates to this target repository name.
      - Mutually exclusive with O(target_repo_id).
    type: str
  target_repo_id:
    description:
      - Restrict candidates to this target repository ID.
      - Mutually exclusive with O(repository).
    type: int
notes:
  - Requires the token promotion API and promotion permission for the source organisation.
  - Results are an eligibility snapshot; another request can change eligibility before a promotion is submitted.
seealso:
  - module: mrmeee.flatman.flatman_promotion
  - module: mrmeee.flatman.flatman_promotion_batch
'''

EXAMPLES = r'''
- name: List every Flatpak and External promotion currently ready
  mrmeee.flatman.flatman_promotion_ready_info:
    url: https://flatman.example.com
    api_token: "{{ flatman_api_token }}"
  register: ready

- name: List targets ready for build 48
  mrmeee.flatman.flatman_promotion_ready_info:
    url: https://flatman.example.com
    api_token: "{{ flatman_api_token }}"
    kind: build
    build_id: 48
'''

RETURN = r'''
ready_promotions:
  description: Eligible source/target pairs. IDs remain available alongside readable names.
  returned: always
  type: list
  elements: dict
  sample:
    - kind: build
      build_id: 19
      build_number: 7
      package_id: 3
      package_identifier: org.example.App
      package_name: Example App
      source_repo_id: 2
      source_repo_name: testing
      target_repo_id: 10
      target_repo_name: stable
count:
  description: Number of eligible source/target pairs.
  returned: always
  type: int
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.mrmeee.flatman.plugins.module_utils.flatman import (
    flatman_argument_spec,
    run_module,
)


def main():
    spec = flatman_argument_spec()
    spec.update(
        kind=dict(type='str', default='both', choices=['both', 'build', 'external']),
        build_id=dict(type='int'),
        external_ref_id=dict(type='int'),
        external_ref_version_id=dict(type='int'),
        repository=dict(type='str'),
        target_repo_id=dict(type='int'),
    )
    module = AnsibleModule(
        argument_spec=spec,
        supports_check_mode=True,
        mutually_exclusive=[['repository', 'target_repo_id']],
        required_by={'external_ref_version_id': ['external_ref_id']},
    )

    def handler(client):
        params = module.params
        target_id = params['target_repo_id']
        if params['repository']:
            target_id = client.resolve(
                '/api/repositories/', 'name', params['repository'], 'Repository')['id']

        candidates = []
        if params['kind'] in ('both', 'build'):
            candidates.extend(client.get_all('/api/promotions/available/'))
        if params['kind'] in ('both', 'external'):
            candidates.extend(client.get_all('/api/external-ref-promotions/available/'))
        if params['build_id'] is not None:
            candidates = [item for item in candidates if item.get('kind') != 'build'
                          or item.get('build_id') == params['build_id']]
        if params['external_ref_id'] is not None:
            candidates = [item for item in candidates if item.get('kind') != 'external'
                          or item.get('external_ref_id') == params['external_ref_id']]
        if params['external_ref_version_id'] is not None:
            candidates = [item for item in candidates if item.get('kind') != 'external'
                          or item.get('external_ref_version_id') == params['external_ref_version_id']]
        if target_id is not None:
            candidates = [item for item in candidates if item.get('target_repo_id') == target_id]
        module.exit_json(changed=False, ready_promotions=candidates, count=len(candidates))

    run_module(module, handler)


if __name__ == '__main__':
    main()
