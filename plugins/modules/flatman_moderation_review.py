#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 MrMEEE
# MIT License

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
module: flatman_moderation_review
short_description: Approve or reject a flat-manager moderation request
version_added: 1.0.0
description:
  - Records a review decision on an existing moderation request.
  - Wraps the C(/api/v2/moderation/requests/<request_id>/review) endpoint.
  - Requires an API token belonging to an administrator.
author:
  - MrMEEE (@MrMEEE)
extends_documentation_fragment:
  - mrmeee.flatman.flatman
  - mrmeee.flatman.flatman.attributes
options:
  request_id:
    description:
      - Numeric ID of the moderation request to review.
    type: int
    required: true
  status:
    description:
      - Decision to record on the moderation request.
      - The server rejects any other value, even though the model also knows the initial C(pending) state.
    type: str
    required: true
    choices: [approved, rejected]
  comment:
    description:
      - Review comment stored on the moderation request, sent as the C(comment) body key.
      - The server stores an empty comment when this is omitted.
    type: str
seealso:
  - module: mrmeee.flatman.flatman_moderation_info
  - module: mrmeee.flatman.flatman_moderation_request
'''

EXAMPLES = r'''
- name: Approve a moderation request
  mrmeee.flatman.flatman_moderation_review:
    url: https://flatman.example.com
    api_token: "{{ flatman_admin_token }}"
    request_id: 17
    status: approved
    comment: Metadata and screenshots look good

- name: Reject every pending request for an application
  mrmeee.flatman.flatman_moderation_review:
    url: https://flatman.example.com
    api_token: "{{ flatman_admin_token }}"
    request_id: "{{ item.id }}"
    status: rejected
    comment: Superseded by a newer submission
  loop: "{{ pending.moderation_requests }}"
'''

RETURN = r'''
moderation_request:
  description: The moderation request after the review decision was applied.
  returned: success
  type: dict
  sample:
    id: 17
    status: approved
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.mrmeee.flatman.plugins.module_utils.flatman import (
    flatman_argument_spec,
    run_module,
)

APPS_PATH = '/api/v2/moderation/apps'
REVIEW_PATH = '/api/v2/moderation/requests/%s/review'


def main():
    argument_spec = flatman_argument_spec()
    argument_spec.update(
        request_id=dict(type='int', required=True),
        status=dict(type='str', required=True, choices=['approved', 'rejected']),
        comment=dict(type='str'),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    def handler(client):
        params = module.params
        request_id = params['request_id']
        wanted = params['status']

        current = None
        for item in client.get(APPS_PATH):
            if item.get('id') == request_id:
                current = item
                break
        if current is None:
            module.fail_json(msg='Moderation request %s not found' % request_id)

        if current.get('status') == wanted:
            module.exit_json(changed=False, moderation_request=current, diff={})

        after = dict(current)
        after['status'] = wanted
        if params['comment'] is not None:
            after['review_comment'] = params['comment']
        diff = client.make_diff(current, after)

        if module.check_mode:
            module.exit_json(changed=True, moderation_request=after, diff=diff)

        payload = {'status': wanted}
        if params['comment'] is not None:
            payload['comment'] = params['comment']
        reviewed = client.post(REVIEW_PATH % request_id, data=payload)
        module.exit_json(changed=True, moderation_request=reviewed, diff=diff)

    run_module(module, handler)


if __name__ == '__main__':
    main()
