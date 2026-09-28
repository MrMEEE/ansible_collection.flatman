#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 MrMEEE
# MIT License

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
module: flatman_moderation_request
short_description: Submit a moderation review request for a flat-manager application
version_added: 1.0.0
description:
  - Submits a moderation review request for an application.
  - Wraps the C(/api/v2/moderation/submit_review_request) endpoint.
  - Requires an API token belonging to an administrator.
author:
  - MrMEEE (@MrMEEE)
extends_documentation_fragment:
  - mrmeee.flatman.flatman
  - mrmeee.flatman.flatman.attributes
options:
  app_id:
    description:
      - Application ID (the Flatpak package ID) to open a moderation request for.
    type: str
    required: true
  reason:
    description:
      - Free form reason stored on the moderation request.
    type: str
  force:
    description:
      - Submit a new request even when the application already has a request in the C(pending) state.
      - By default the existing requests are listed first and the submission is skipped when one is pending.
    type: bool
    default: false
seealso:
  - module: mrmeee.flatman.flatman_moderation_info
  - module: mrmeee.flatman.flatman_moderation_review
'''

EXAMPLES = r'''
- name: Request moderation for an application
  mrmeee.flatman.flatman_moderation_request:
    url: https://flatman.example.com
    api_token: "{{ flatman_admin_token }}"
    app_id: org.example.Editor
    reason: New maintainer took over the project

- name: Always submit a fresh request, even when one is still pending
  mrmeee.flatman.flatman_moderation_request:
    url: https://flatman.example.com
    api_token: "{{ flatman_admin_token }}"
    app_id: org.example.Editor
    reason: Re-submitted after the metadata fix
    force: true
'''

RETURN = r'''
moderation_request:
  description:
    - The moderation request created by this task.
    - When an existing pending request was reused, that request is returned instead.
  returned: success
  type: dict
  sample:
    id: 17
    status: pending
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.mrmeee.flatman.plugins.module_utils.flatman import (
    flatman_argument_spec,
    run_module,
)

SUBMIT_PATH = '/api/v2/moderation/submit_review_request'
APPS_PATH = '/api/v2/moderation/apps'


def main():
    argument_spec = flatman_argument_spec()
    argument_spec.update(
        app_id=dict(type='str', required=True),
        reason=dict(type='str'),
        force=dict(type='bool', default=False),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    def handler(client):
        params = module.params
        app_id = params['app_id']

        if not params['force']:
            existing = client.get('%s/%s' % (APPS_PATH, app_id))
            pending = [item for item in existing if item.get('status') == 'pending']
            if pending:
                module.exit_json(changed=False, moderation_request=pending[0], diff={})

        payload = {'app_id': app_id}
        if params['reason'] is not None:
            payload['reason'] = params['reason']

        if module.check_mode:
            module.exit_json(changed=True, moderation_request=payload, diff={})

        created = client.post(SUBMIT_PATH, data=payload)
        module.exit_json(changed=True, moderation_request=created, diff={})

    run_module(module, handler)


if __name__ == '__main__':
    main()
