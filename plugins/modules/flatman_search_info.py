#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 MrMEEE
# MIT License

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
module: flatman_search_info
short_description: Search published flat-manager applications
version_added: 1.0.0
description:
  - Search the published application catalogue by ID, name, summary or developer name.
  - Wraps the C(/api/v2/search) endpoint, which is queried with a POST request carrying a JSON body.
  - This endpoint is public, so O(api_token) is optional.
author:
  - MrMEEE (@MrMEEE)
extends_documentation_fragment:
  - mrmeee.flatman.flatman
  - mrmeee.flatman.flatman.attributes_info
options:
  query:
    description:
      - The search string, sent to the server as the C(query) key of the request body.
      - Matched case insensitively against application ID, package name, summary and developer name.
    type: str
    required: true
seealso:
  - module: mrmeee.flatman.flatman_app_info
  - module: mrmeee.flatman.flatman_collection_info
'''

EXAMPLES = r'''
- name: Search for editors
  mrmeee.flatman.flatman_search_info:
    url: https://flatman.example.com
    query: editor
  register: results

- name: Show the matching application IDs
  ansible.builtin.debug:
    msg: "{{ results.apps | map(attribute='id') | list }}"

- name: Find everything published by one developer
  mrmeee.flatman.flatman_search_info:
    url: https://flatman.example.com
    query: Example Inc
  register: by_developer
'''

RETURN = r'''
apps:
  description: The applications matching the search query.
  returned: always
  type: list
  elements: dict
  sample:
    - id: org.example.Editor
      name: Example Editor
      summary: A small text editor
      developer: Example Inc
      verified: true
      version: 1.2.3
      branch: stable
      arch: x86_64
      repository: stable
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.mrmeee.flatman.plugins.module_utils.flatman import (
    flatman_argument_spec,
    run_module,
)


def main():
    argument_spec = flatman_argument_spec()
    argument_spec.update(
        query=dict(type='str', required=True),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    def handler(client):
        apps = client.post('/api/v2/search', data=dict(query=module.params['query']), expect=(200,))
        module.exit_json(changed=False, apps=apps or [])

    run_module(module, handler)


if __name__ == '__main__':
    main()
