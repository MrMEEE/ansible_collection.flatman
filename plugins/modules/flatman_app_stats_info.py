#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 MrMEEE
# MIT License

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
module: flatman_app_stats_info
short_description: Gather flat-manager application statistics
version_added: 1.0.0
description:
  - Retrieve global catalogue statistics, or the statistics of a single published application.
  - Wraps the C(/api/v2/stats/) endpoints.
  - These endpoints are public, so O(api_token) is optional.
author:
  - MrMEEE (@MrMEEE)
extends_documentation_fragment:
  - mrmeee.flatman.flatman
  - mrmeee.flatman.flatman.attributes_info
options:
  app_id:
    description:
      - Return the statistics of this application only, for example C(org.example.App).
      - When omitted, server wide catalogue counters are returned instead.
    type: str
seealso:
  - module: mrmeee.flatman.flatman_app_info
  - module: mrmeee.flatman.flatman_usage_info
'''

EXAMPLES = r'''
- name: Get global catalogue statistics
  mrmeee.flatman.flatman_app_stats_info:
    url: https://flatman.example.com
  register: totals

- name: Show how many applications are published
  ansible.builtin.debug:
    msg: "{{ totals.stats.apps }} applications in {{ totals.stats.repositories }} repositories"

- name: Get statistics for a single application
  mrmeee.flatman.flatman_app_stats_info:
    url: https://flatman.example.com
    app_id: org.example.App
  register: app_stats
'''

RETURN = r'''
stats:
  description:
    - Global counters when O(app_id) is not set, otherwise the statistics of that application.
    - Empty when the requested application does not exist.
  returned: always
  type: dict
  sample:
    app_id: org.example.App
    builds: 12
    build_number: 12
    version: 1.2.3
    updated_at: '2026-01-05T09:15:00+00:00'
    usage:
      observations: 431
      unique_clients: 87
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
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    def handler(client):
        app_id = module.params['app_id']
        if app_id:
            stats = client.get_or_none('/api/v2/stats/%s' % app_id) or {}
        else:
            stats = client.get('/api/v2/stats/')
        module.exit_json(changed=False, stats=stats)

    run_module(module, handler)


if __name__ == '__main__':
    main()
