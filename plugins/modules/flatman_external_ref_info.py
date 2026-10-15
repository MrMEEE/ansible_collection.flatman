#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 MrMEEE
# MIT License

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
module: flatman_external_ref_info
short_description: Gather External refs and their versions
version_added: 1.1.0
description:
  - Read External refs, including versions, logs and publication status, from C(/api/external-refs/).
  - Requires a server with the token-authenticated External workflow API.
author:
  - MrMEEE (@MrMEEE)
extends_documentation_fragment:
  - mrmeee.flatman.flatman
  - mrmeee.flatman.flatman.attributes_info
options:
  id:
    description: Return only the External ref with this numeric ID.
    type: int
  repository:
    description:
      - Filter by repository name.
      - Mutually exclusive with O(repository_id).
    type: str
  repository_id:
    description:
      - Filter by numeric repository ID.
      - Mutually exclusive with O(repository).
    type: int
  remote_id:
    description: Filter by numeric upstream remote ID.
    type: int
  ref:
    description: Filter by full OSTree ref, for example C(app/org.example.App/x86_64/stable).
    type: str
  status:
    description: Filter by External ref state.
    type: str
  search:
    description: Search the ref and display name.
    type: str
notes:
  - When O(id) is supplied, list filters are ignored.
seealso:
  - module: mrmeee.flatman.flatman_external_ref_action
'''

EXAMPLES = r'''
- name: Find External apps in testing
  mrmeee.flatman.flatman_external_ref_info:
    repository: testing
  register: externals

- name: Inspect an External and its published versions
  mrmeee.flatman.flatman_external_ref_info:
    id: 12
  register: external
'''

RETURN = r'''
external_refs:
  description: Matching External refs including their versions and logs.
  returned: always
  type: list
  elements: dict
  sample:
    - id: 12
      ref: app/org.example.App/x86_64/stable
      status: published
      versions: []
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.mrmeee.flatman.plugins.module_utils.flatman import (
    flatman_argument_spec,
    run_module,
)

COLLECTION_PATH = '/api/external-refs/'


def main():
    argument_spec = flatman_argument_spec()
    argument_spec.update(
        id=dict(type='int'),
        repository=dict(type='str'),
        repository_id=dict(type='int'),
        remote_id=dict(type='int'),
        ref=dict(type='str'),
        status=dict(type='str'),
        search=dict(type='str'),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        mutually_exclusive=[['repository', 'repository_id']],
    )

    def handler(client):
        params = module.params
        if params['id'] is not None:
            found = client.get_or_none('%s%s/' % (COLLECTION_PATH, params['id']))
            refs = [found] if found else []
        else:
            repository_id = params['repository_id']
            if params['repository']:
                repository_id = client.resolve(
                    '/api/repositories/', 'name', params['repository'], 'Repository')['id']
            refs = client.get_all(COLLECTION_PATH, params=dict(
                repository=repository_id,
                remote=params['remote_id'],
                ref=params['ref'],
                status=params['status'],
                search=params['search'],
            ))
        module.exit_json(changed=False, external_refs=refs)

    run_module(module, handler)


if __name__ == '__main__':
    main()
