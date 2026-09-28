#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 MrMEEE
# MIT License

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
module: flatman_app_info
short_description: Gather information about published flat-manager applications
version_added: 1.0.0
description:
  - Retrieve the public application catalogue from the Flathub compatible C(/api/v2) API.
  - Wraps the C(/api/v2/appstream) endpoints, optionally enriched with summary, addon and fullscreen data.
  - These endpoints are public, so O(api_token) is optional.
author:
  - MrMEEE (@MrMEEE)
extends_documentation_fragment:
  - mrmeee.flatman.flatman
  - mrmeee.flatman.flatman.attributes_info
options:
  app_id:
    description:
      - Return only the application with this ID, for example C(org.example.App).
      - When omitted, every published application is returned.
    type: str
  sort:
    description:
      - Sort order requested from the server.
      - Only honoured when O(app_id) is not set, because the single application form takes no query parameters.
    type: str
    choices: [alphabetical, recent, recently-updated]
  include:
    description:
      - Extra sub-resources to fetch for the requested application.
      - Only honoured when O(app_id) is set.
      - V(summary) adds a C(summary) key, V(addon) adds an C(addons) key and V(fullscreen) adds an C(is_fullscreen) key.
    type: list
    elements: str
    choices: [summary, addon, fullscreen]
seealso:
  - module: mrmeee.flatman.flatman_app_metadata
  - module: mrmeee.flatman.flatman_app_stats_info
  - module: mrmeee.flatman.flatman_search_info
'''

EXAMPLES = r'''
- name: List every published application
  mrmeee.flatman.flatman_app_info:
    url: https://flatman.example.com
  register: catalogue

- name: List applications ordered by last update
  mrmeee.flatman.flatman_app_info:
    url: https://flatman.example.com
    sort: recently-updated
  register: recent_apps

- name: Fetch one application with all extra data
  mrmeee.flatman.flatman_app_info:
    url: https://flatman.example.com
    app_id: org.example.App
    include:
      - summary
      - addon
      - fullscreen
  register: app
'''

RETURN = r'''
apps:
  description:
    - The matching applications.
    - Contains at most one element when O(app_id) is set, and is empty when that application does not exist.
  returned: always
  type: list
  elements: dict
  sample:
    - id: org.example.App
      name: Example App
      summary: A small example application
      developer: Example Inc
      categories:
        - Utility
      verified: true
      mobile: false
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
        app_id=dict(type='str'),
        sort=dict(type='str', choices=['alphabetical', 'recent', 'recently-updated']),
        include=dict(type='list', elements='str', choices=['summary', 'addon', 'fullscreen']),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    def handler(client):
        params = module.params
        app_id = params['app_id']

        if not app_id:
            apps = client.get('/api/v2/appstream', params=dict(sort=params['sort']))
            module.exit_json(changed=False, apps=apps or [])

        app = client.get_or_none('/api/v2/appstream/%s' % app_id)
        if app is None:
            module.exit_json(changed=False, apps=[])

        include = params['include'] or []
        if 'summary' in include:
            app['summary'] = client.get_or_none('/api/v2/summary/%s' % app_id)
        if 'addon' in include:
            app['addons'] = client.get_or_none('/api/v2/addon/%s' % app_id) or []
        if 'fullscreen' in include:
            app['is_fullscreen'] = client.get_or_none('/api/v2/is-fullscreen-app/%s' % app_id)

        module.exit_json(changed=False, apps=[app])

    run_module(module, handler)


if __name__ == '__main__':
    main()
