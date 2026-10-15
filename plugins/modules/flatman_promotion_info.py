#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 MrMEEE
# MIT License

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
module: flatman_promotion_info
short_description: Gather Flatpak or External promotion status
version_added: 1.1.0
description:
  - Read promotion records through the token API, including completion status and errors.
author:
  - MrMEEE (@MrMEEE)
extends_documentation_fragment:
  - mrmeee.flatman.flatman
  - mrmeee.flatman.flatman.attributes_info
options:
  kind:
    description: Select Flatpak build or External version promotion records.
    type: str
    choices: [build, external]
    default: build
  id:
    description: Return only this numeric promotion ID. List filters are ignored.
    type: int
  build_id:
    description: Filter by numeric build history ID. Only valid with O(kind=build).
    type: int
  external_ref_id:
    description: Filter by External ref ID. Only valid with O(kind=external).
    type: int
  external_ref_version_id:
    description: Filter by External version ID. Only valid with O(kind=external).
    type: int
  repository:
    description:
      - Filter by target repository name.
      - Mutually exclusive with O(target_repo_id).
    type: str
  target_repo_id:
    description:
      - Filter by numeric target repository ID.
      - Mutually exclusive with O(repository).
    type: int
  status:
    description: Filter by promotion state.
    type: str
    choices: [pending, promoting, promoted, failed]
notes:
  - Requires a server with the token-authenticated promotion API and appropriate user permissions.
seealso:
  - module: mrmeee.flatman.flatman_promotion
'''

EXAMPLES = r'''
- name: Find completed build promotions to stable
  mrmeee.flatman.flatman_promotion_info:
    repository: stable
    status: promoted

- name: Inspect an External promotion
  mrmeee.flatman.flatman_promotion_info:
    kind: external
    id: 10
  register: promotion
'''

RETURN = r'''
promotions:
  description: Matching promotion records.
  returned: always
  type: list
  elements: dict
  sample:
    - id: 10
      target_repo: 3
      status: promoted
      error_message: ''
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.mrmeee.flatman.plugins.module_utils.flatman import (
    flatman_argument_spec,
    run_module,
)


def main():
    argument_spec = flatman_argument_spec()
    argument_spec.update(
        kind=dict(type='str', default='build', choices=['build', 'external']),
        id=dict(type='int'),
        build_id=dict(type='int'),
        external_ref_id=dict(type='int'),
        external_ref_version_id=dict(type='int'),
        repository=dict(type='str'),
        target_repo_id=dict(type='int'),
        status=dict(type='str', choices=['pending', 'promoting', 'promoted', 'failed']),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        mutually_exclusive=[['repository', 'target_repo_id']],
    )
    params = module.params
    invalid = ['build_id'] if params['kind'] == 'external' else ['external_ref_id', 'external_ref_version_id']
    for key in invalid:
        if params[key] is not None:
            module.fail_json(msg='%s is not valid for kind=%s' % (key, params['kind']))

    def handler(client):
        path = '/api/promotions/' if params['kind'] == 'build' else '/api/external-ref-promotions/'
        if params['id'] is not None:
            found = client.get_or_none('%s%s/' % (path, params['id']))
            promotions = [found] if found else []
        else:
            target = params['target_repo_id']
            if params['repository']:
                target = client.resolve('/api/repositories/', 'name', params['repository'], 'Repository')['id']
            query = dict(target_repo=target, status=params['status'])
            if params['kind'] == 'build':
                query['build'] = params['build_id']
            else:
                query.update(external_ref=params['external_ref_id'],
                             external_ref_version=params['external_ref_version_id'])
            promotions = client.get_all(path, params=query)
        module.exit_json(changed=False, promotions=promotions)

    run_module(module, handler)


if __name__ == '__main__':
    main()
