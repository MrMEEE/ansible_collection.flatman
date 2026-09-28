#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 MrMEEE
# MIT License

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
module: flatman_year_in_review_info
short_description: Gather the flat-manager year in review summary
version_added: 1.0.0
description:
  - Retrieve the aggregated activity summary of a single calendar year.
  - Wraps the C(/api/v2/year-in-review/<year>) endpoint.
  - This endpoint is public, so O(api_token) is optional.
author:
  - MrMEEE (@MrMEEE)
extends_documentation_fragment:
  - mrmeee.flatman.flatman
  - mrmeee.flatman.flatman.attributes_info
options:
  year:
    description:
      - The calendar year to summarise, for example C(2026).
    type: int
    required: true
seealso:
  - module: mrmeee.flatman.flatman_app_stats_info
  - module: mrmeee.flatman.flatman_usage_info
'''

EXAMPLES = r'''
- name: Gather the summary of last year
  mrmeee.flatman.flatman_year_in_review_info:
    url: https://flatman.example.com
    year: 2025
  register: review

- name: Show how many applications were added
  ansible.builtin.debug:
    msg: "{{ review.year_in_review.apps_added }} applications added in 2025"

- name: Gather the summary of the current year
  mrmeee.flatman.flatman_year_in_review_info:
    url: https://flatman.example.com
    year: "{{ '%Y' | ansible.builtin.strftime | int }}"
  register: current_review
'''

RETURN = r'''
year_in_review:
  description: The aggregated activity summary of the requested year.
  returned: always
  type: dict
  sample:
    year: 2025
    apps_added: 42
    apps_updated: 128
    usage_observations: 10432
    unique_clients: 517
    generated_at: '2026-01-02T08:00:00+00:00'
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.mrmeee.flatman.plugins.module_utils.flatman import (
    flatman_argument_spec,
    run_module,
)


def main():
    argument_spec = flatman_argument_spec()
    argument_spec.update(
        year=dict(type='int', required=True),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    def handler(client):
        review = client.get('/api/v2/year-in-review/%s' % module.params['year'])
        module.exit_json(changed=False, year_in_review=review)

    run_module(module, handler)


if __name__ == '__main__':
    main()
