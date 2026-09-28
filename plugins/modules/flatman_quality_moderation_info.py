#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 MrMEEE
# MIT License

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
module: flatman_quality_moderation_info
short_description: Gather quality moderation information from flat-manager
version_added: 1.0.0
description:
  - Reads the quality moderation status of a single application, or one of the aggregated quality reports.
  - Wraps the read-only C(/api/v2/quality-moderation) endpoints, which do not require authentication.
author:
  - MrMEEE (@MrMEEE)
extends_documentation_fragment:
  - mrmeee.flatman.flatman
  - mrmeee.flatman.flatman.attributes_info
options:
  app_id:
    description:
      - Application ID to read the quality status for, using C(/api/v2/quality-moderation/<app_id>/status).
      - Mutually exclusive with O(report).
    type: str
  report:
    description:
      - Aggregated quality report to fetch.
      - V(status) returns the instance wide counters from C(/api/v2/quality-moderation/status).
      - V(stats-by-category) returns a mapping of branch to application count.
      - V(passing-apps) returns the applications whose quality status is C(passing).
      - V(failed-by-guideline) returns the failing applications together with the guidelines they failed.
      - V(app-pick-recommendations) returns applications recommended for an editorial pick.
      - Mutually exclusive with O(app_id).
    type: str
    choices:
      - status
      - stats-by-category
      - passing-apps
      - failed-by-guideline
      - app-pick-recommendations
seealso:
  - module: mrmeee.flatman.flatman_quality_moderation
  - module: mrmeee.flatman.flatman_moderation_info
'''

EXAMPLES = r'''
- name: Read the quality status of a single application
  mrmeee.flatman.flatman_quality_moderation_info:
    url: https://flatman.example.com
    app_id: org.example.Editor
  register: app_quality

- name: Fail when the application is not a fullscreen application
  ansible.builtin.assert:
    that: app_quality.quality.fullscreen

- name: List every application that passes quality moderation
  mrmeee.flatman.flatman_quality_moderation_info:
    url: https://flatman.example.com
    report: passing-apps
  register: passing
'''

RETURN = r'''
quality:
  description:
    - The quality data returned by the selected endpoint.
    - A dict for O(app_id), O(report=status) and O(report=stats-by-category).
    - A list of dicts for O(report=passing-apps), O(report=failed-by-guideline) and
      O(report=app-pick-recommendations).
  returned: always
  type: raw
  sample:
    id: org.example.Editor
    status: passing
    fullscreen: false
    guidelines: []
    review_comment: ''
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.mrmeee.flatman.plugins.module_utils.flatman import (
    flatman_argument_spec,
    run_module,
)

BASE_PATH = '/api/v2/quality-moderation'

REPORT_PATHS = {
    'status': '%s/status' % BASE_PATH,
    'stats-by-category': '%s/stats-by-category' % BASE_PATH,
    'passing-apps': '%s/passing-apps' % BASE_PATH,
    'failed-by-guideline': '%s/failed-by-guideline' % BASE_PATH,
    'app-pick-recommendations': '%s/app-pick-recommendations' % BASE_PATH,
}


def main():
    argument_spec = flatman_argument_spec()
    argument_spec.update(
        app_id=dict(type='str'),
        report=dict(
            type='str',
            choices=[
                'status',
                'stats-by-category',
                'passing-apps',
                'failed-by-guideline',
                'app-pick-recommendations',
            ],
        ),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        mutually_exclusive=[['app_id', 'report']],
        required_one_of=[['app_id', 'report']],
    )

    def handler(client):
        params = module.params
        if params['app_id']:
            path = '%s/%s/status' % (BASE_PATH, params['app_id'])
        else:
            path = REPORT_PATHS[params['report']]
        module.exit_json(changed=False, quality=client.get(path))

    run_module(module, handler)


if __name__ == '__main__':
    main()
