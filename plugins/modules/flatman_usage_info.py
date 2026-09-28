#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 MrMEEE
# MIT License

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
module: flatman_usage_info
short_description: Gather popular application usage from flat-manager
version_added: 1.0.0
description:
  - Retrieve the published applications ranked by the number of unique clients that reported using them.
  - Wraps the C(/api/v2/usage/popular) endpoint.
  - This endpoint is public, so O(api_token) is optional.
author:
  - MrMEEE (@MrMEEE)
extends_documentation_fragment:
  - mrmeee.flatman.flatman
  - mrmeee.flatman.flatman.attributes_info
options:
  days:
    description:
      - Size of the reporting window in days.
      - The server clamps this value to the range 1 to 365, so smaller or larger values are silently adjusted.
      - The value actually used is reported in RV(days).
    type: int
    default: 30
seealso:
  - module: mrmeee.flatman.flatman_app_stats_info
  - module: mrmeee.flatman.flatman_collection_info
'''

EXAMPLES = r'''
- name: Gather usage over the default 30 day window
  mrmeee.flatman.flatman_usage_info:
    url: https://flatman.example.com
  register: usage

- name: Gather usage over the last year
  mrmeee.flatman.flatman_usage_info:
    url: https://flatman.example.com
    days: 365
  register: yearly_usage

- name: Show the ten most used applications
  ansible.builtin.debug:
    msg: "{{ usage.apps[:10] | map(attribute='app_id') | list }}"
'''

RETURN = r'''
days:
  description: The reporting window actually used by the server, after clamping to the range 1 to 365.
  returned: always
  type: int
  sample: 30
apps:
  description: The applications with usage in the window, ordered by unique clients and then by observations.
  returned: always
  type: list
  elements: dict
  sample:
    - app_id: org.example.App
      unique_clients: 87
      observations: 431
    - app_id: org.example.Editor
      unique_clients: 12
      observations: 54
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.mrmeee.flatman.plugins.module_utils.flatman import (
    flatman_argument_spec,
    run_module,
)


def main():
    argument_spec = flatman_argument_spec()
    argument_spec.update(
        days=dict(type='int', default=30),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    def handler(client):
        result = client.get('/api/v2/usage/popular', params=dict(days=module.params['days']))
        module.exit_json(
            changed=False,
            days=result.get('days'),
            apps=result.get('apps') or [],
        )

    run_module(module, handler)


if __name__ == '__main__':
    main()
