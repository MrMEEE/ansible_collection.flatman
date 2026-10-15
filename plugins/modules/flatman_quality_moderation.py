#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 MrMEEE
# MIT License

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
module: flatman_quality_moderation
short_description: Perform quality moderation actions on a flat-manager application
description:
  - Marks an application as a fullscreen application or opens a quality review request for it.
  - Wraps the C(/api/v2/quality-moderation/<app_id>/fullscreen) and
    C(/api/v2/quality-moderation/<app_id>/request-review) endpoints.
  - Both actions require an API token belonging to an administrator.
author:
  - MrMEEE (@MrMEEE)
extends_documentation_fragment:
  - mrmeee.flatman.flatman
  - mrmeee.flatman.flatman.attributes
options:
  app_id:
    description:
      - Application ID (the Flatpak package ID) the action applies to.
    type: str
    required: true
  action:
    description:
      - V(fullscreen) flags the application as a fullscreen application. This action is idempotent - the
        current quality status is read first and the write is skipped when the flag is already set.
      - V(request-review) creates a new moderation request for the application. This action is imperative,
        so it always reports a change outside of check mode.
      - V(reject-pending-reviews) rejects all pending review requests for the application.
    type: str
    required: true
    choices: [fullscreen, request-review, reject-pending-reviews]
    version_added: 1.0.0
  reason:
    description:
      - Reason recorded on the moderation request, sent as the C(reason) body key.
      - Only used with O(action=request-review). The server defaults it to C(Quality review requested).
    type: str
notes:
  - V(reject-pending-reviews) rejects all pending requests through DELETE on the request-review endpoint.
  - This bulk action was added in collection version 1.2.0 and reports changed when dispatched.
seealso:
  - module: mrmeee.flatman.flatman_quality_moderation_info
  - module: mrmeee.flatman.flatman_moderation_request
'''

EXAMPLES = r'''
- name: Flag an application as a fullscreen application
  mrmeee.flatman.flatman_quality_moderation:
    url: https://flatman.example.com
    api_token: "{{ flatman_admin_token }}"
    app_id: org.example.Game
    action: fullscreen

- name: Ask for a quality review of an application
  mrmeee.flatman.flatman_quality_moderation:
    url: https://flatman.example.com
    api_token: "{{ flatman_admin_token }}"
    app_id: org.example.Editor
    action: request-review
    reason: Screenshots were refreshed for the 2.0 release

- name: Flag several games as fullscreen applications
  mrmeee.flatman.flatman_quality_moderation:
    url: https://flatman.example.com
    api_token: "{{ flatman_admin_token }}"
    app_id: "{{ item }}"
    action: fullscreen
  loop:
    - org.example.Game
    - org.example.Racer
'''

RETURN = r'''
result:
  description:
    - The raw API response.
    - For O(action=fullscreen) this is the fullscreen state of the application. When the flag was already
      set no request is sent and the current quality status is returned instead.
    - For O(action=request-review) this is the newly created moderation request.
  returned: success
  type: dict
  sample:
    app_id: org.example.Game
    fullscreen: true
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.mrmeee.flatman.plugins.module_utils.flatman import (
    flatman_argument_spec,
    run_module,
)

BASE_PATH = '/api/v2/quality-moderation'


def main():
    argument_spec = flatman_argument_spec()
    argument_spec.update(
        app_id=dict(type='str', required=True),
        action=dict(type='str', required=True, choices=['fullscreen', 'request-review', 'reject-pending-reviews']),
        reason=dict(type='str'),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    def handler(client):
        params = module.params
        app_id = params['app_id']
        action = params['action']

        if action == 'reject-pending-reviews':
            if not module.check_mode:
                client.delete('%s/%s/request-review' % (BASE_PATH, app_id))
            module.exit_json(changed=True, result={}, diff={})

        if action == 'fullscreen':
            current = client.get('%s/%s/status' % (BASE_PATH, app_id))
            if current.get('fullscreen') is True:
                module.exit_json(changed=False, result=current, diff={})
            after = dict(current)
            after['fullscreen'] = True
            diff = client.make_diff(current, after)
            if module.check_mode:
                module.exit_json(changed=True, result=after, diff=diff)
            result = client.post('%s/%s/fullscreen' % (BASE_PATH, app_id))
            module.exit_json(changed=True, result=result, diff=diff)

        payload = {}
        if params['reason'] is not None:
            payload['reason'] = params['reason']
        if module.check_mode:
            module.exit_json(changed=True, result=payload, diff={})
        result = client.post('%s/%s/request-review' % (BASE_PATH, app_id), data=payload)
        module.exit_json(changed=True, result=result, diff={})

    run_module(module, handler)


if __name__ == '__main__':
    main()
