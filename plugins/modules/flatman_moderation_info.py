#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 MrMEEE
# MIT License

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
module: flatman_moderation_info
short_description: List flat-manager moderation requests
version_added: 1.0.0
description:
  - Lists the moderation requests known to a flat-manager-django server, optionally narrowed to one application.
  - Wraps the C(/api/v2/moderation/apps) and C(/api/v2/moderation/apps/<app_id>) endpoints.
  - Requires an API token belonging to an administrator.
author:
  - MrMEEE (@MrMEEE)
extends_documentation_fragment:
  - mrmeee.flatman.flatman
  - mrmeee.flatman.flatman.attributes_info
options:
  app_id:
    description:
      - Return only the moderation requests belonging to this application ID.
    type: str
  status:
    description:
      - Return only the moderation requests in this state.
      - The filtering is done by the module, because the endpoint has no status query parameter.
    type: str
    choices: [pending, approved, rejected]
seealso:
  - module: mrmeee.flatman.flatman_moderation_request
  - module: mrmeee.flatman.flatman_moderation_review
'''

EXAMPLES = r'''
- name: List every moderation request
  mrmeee.flatman.flatman_moderation_info:
    url: https://flatman.example.com
    api_token: "{{ flatman_admin_token }}"
  register: moderation

- name: List the pending requests of a single application
  mrmeee.flatman.flatman_moderation_info:
    url: https://flatman.example.com
    api_token: "{{ flatman_admin_token }}"
    app_id: org.example.Editor
    status: pending
  register: pending

- name: Show how many requests are still waiting for a decision
  ansible.builtin.debug:
    msg: "{{ pending.moderation_requests | length }} requests pending"
'''

RETURN = r'''
moderation_requests:
  description: The matching moderation requests.
  returned: always
  type: list
  elements: dict
  sample:
    - id: 17
      app_id: org.example.Editor
      status: pending
      reason: New maintainer took over the project
      review_comment: ''
      created_at: '2026-01-14T09:12:44.512000+00:00'
      reviewed_at: null
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.mrmeee.flatman.plugins.module_utils.flatman import (
    flatman_argument_spec,
    run_module,
)

APPS_PATH = '/api/v2/moderation/apps'


def main():
    argument_spec = flatman_argument_spec()
    argument_spec.update(
        app_id=dict(type='str'),
        status=dict(type='str', choices=['pending', 'approved', 'rejected']),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    def handler(client):
        params = module.params
        if params['app_id']:
            path = '%s/%s' % (APPS_PATH, params['app_id'])
        else:
            path = APPS_PATH

        requests = client.get(path)
        if params['status']:
            requests = [item for item in requests if item.get('status') == params['status']]

        module.exit_json(changed=False, moderation_requests=requests)

    run_module(module, handler)


if __name__ == '__main__':
    main()
