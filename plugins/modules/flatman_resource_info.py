#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 MrMEEE
# MIT License

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
module: flatman_resource_info
short_description: Inspect resources in the expanded token API
version_added: 1.2.0
description:
  - Read resources from the expanded router, including BuildStream, access control, RPM and server configuration.
  - Returns a consistent list even for the singleton site configuration and workflow catalogue.
  - Follows pagination and optionally selects exact field values locally.
author:
  - MrMEEE (@MrMEEE)
extends_documentation_fragment:
  - mrmeee.flatman.flatman
  - mrmeee.flatman.flatman.attributes_info
options:
  resource:
    description: Router resource to read.
    type: str
    required: true
    choices:
      - gpg-keys
      - flatpak-remotes
      - organisations
      - bst-sources
      - bst-promotions
      - clients
      - permission-groups
      - ldap-sources
      - ldap-group-mappings
      - rpm-packages
      - rpm-builds
      - rpm-distributions
      - rpm-repositories
      - satellite-servers
      - satellite-repositories
      - rpm-destinations
      - rpm-signing-keys
      - user-roles
      - permission-grants
      - group-permissions
      - site-config
      - external-refs
      - packages
      - repositories
      - builds
      - promotions
      - external-ref-promotions
      - workflows
  id:
    description: Numeric detail ID. Mutually exclusive with O(match).
    type: int
  match:
    description: Exact returned field values to select locally, not fuzzy search parameters.
    type: dict
    default: {}
notes:
  - Requires a server with the expanded token workflow router.
  - Site configuration can contain sensitive settings. Use task-level C(no_log=true) when inspecting it.
  - C(workflows) supports list reads only and returns the server action catalogue.
'''

EXAMPLES = r'''
- name: Find active Flatpak remotes
  mrmeee.flatman.flatman_resource_info:
    resource: flatpak-remotes
    match:
      is_active: true
  register: remotes

- name: Discover server workflow endpoints
  mrmeee.flatman.flatman_resource_info:
    resource: workflows
  register: catalogue
'''

RETURN = r'''
resources:
  description: Matching resource records, or a single configuration/catalogue dictionary.
  returned: always
  type: list
  elements: dict
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.mrmeee.flatman.plugins.module_utils.flatman import flatman_argument_spec, run_module
from ansible_collections.mrmeee.flatman.plugins.module_utils.router import INFO_RESOURCES, matches, resource_path


def main():
    spec = flatman_argument_spec()
    spec.update(
        resource=dict(type='str', required=True, choices=INFO_RESOURCES),
        id=dict(type='int'),
        match=dict(type='dict', default={}),
    )
    module = AnsibleModule(argument_spec=spec, supports_check_mode=True, mutually_exclusive=[['id', 'match']])

    def handler(client):
        params = module.params
        path = resource_path(params['resource'])
        if params['id'] is not None:
            if params['resource'] == 'workflows':
                module.fail_json(msg='The workflow catalogue has no detail endpoint')
            found = client.get_or_none('%s%s/' % (path, params['id']))
            records = [found] if found is not None else []
        elif params['resource'] in ('site-config', 'workflows'):
            records = [client.get(path)]
        else:
            records = client.get_all(path)
        records = [item for item in records if matches(client, item, params['match'])]
        module.exit_json(changed=False, resources=records)

    run_module(module, handler)


if __name__ == '__main__':
    main()
