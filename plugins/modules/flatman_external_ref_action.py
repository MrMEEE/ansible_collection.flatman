#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 MrMEEE
# MIT License

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
module: flatman_external_ref_action
short_description: Pull or publish an existing External ref
version_added: 1.1.0
description:
  - Queue token-authenticated actions under C(/api/external-refs/).
  - Pull fetches from the configured remote and queues publication to the source repository.
  - Publish queues publication of an already-pulled ref.
author:
  - MrMEEE (@MrMEEE)
extends_documentation_fragment:
  - mrmeee.flatman.flatman
attributes:
  check_mode:
    description: Validates the current ref without dispatching or polling.
    support: full
  diff_mode:
    description: Imperative actions do not return a diff.
    support: N/A
options:
  id:
    description: Numeric ID of an existing External ref.
    type: int
    required: true
  action:
    description: Action to queue.
    type: str
    required: true
    choices: [pull, publish]
  wait:
    description: Poll until the External ref is published, failing on a failed or cancelled state.
    type: bool
    default: false
  wait_timeout:
    description: Maximum polling duration in seconds. Must be positive.
    type: int
    default: 600
  wait_interval:
    description: Seconds between polls. Must be positive.
    type: int
    default: 5
notes:
  - Pull is imperative and always reports changed when queued, even for a published ref.
  - Publish skips an already-published ref and otherwise requires the pulled state.
  - Pull rejects refs that are pulling or publishing, or have no configured remote.
  - Check mode validates the current ref but never queues or polls an action.
  - Requires a server with the token-authenticated External workflow API and appropriate user permissions.
seealso:
  - module: mrmeee.flatman.flatman_external_ref_info
  - module: mrmeee.flatman.flatman_promotion
'''

EXAMPLES = r'''
- name: Pull and publish an External from its configured remote
  mrmeee.flatman.flatman_external_ref_action:
    id: 12
    action: pull
    wait: true
    wait_timeout: 1800

- name: Publish an already-pulled External
  mrmeee.flatman.flatman_external_ref_action:
    id: 12
    action: publish
    wait: true
'''

RETURN = r'''
result:
  description: Action response, or an empty dictionary when skipped or in check mode.
  returned: always
  type: dict
external_ref:
  description: Ref at completion when waiting, otherwise the ref read before dispatch.
  returned: always
  type: dict
  sample:
    id: 12
    status: published
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.mrmeee.flatman.plugins.module_utils.flatman import (
    flatman_argument_spec,
    run_module,
)
from ansible_collections.mrmeee.flatman.plugins.module_utils.workflows import (
    validate_wait,
    wait_argument_spec,
)


def main():
    argument_spec = flatman_argument_spec()
    argument_spec.update(wait_argument_spec())
    argument_spec.update(
        id=dict(type='int', required=True),
        action=dict(type='str', required=True, choices=['pull', 'publish']),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    validate_wait(module)

    def handler(client):
        params = module.params
        path = '/api/external-refs/%s/' % params['id']
        external = client.get(path)
        action = params['action']
        if action == 'publish':
            if external['status'] == 'published':
                module.exit_json(changed=False, result={}, external_ref=external)
            if external['status'] != 'pulled':
                module.fail_json(msg='External ref must be pulled before publishing', external_ref=external)
        else:
            if external['status'] in ('pulling', 'publishing'):
                module.fail_json(msg='External pull or publish already in progress', external_ref=external)
            if external.get('remote') is None:
                module.fail_json(msg='No remote configured for External ref', external_ref=external)

        result = {}
        if not module.check_mode:
            result = client.post('%s%s/' % (path, action), expect=(202,))
            if params['wait']:
                external = client.wait_for(
                    path, 'status', ['published'], fail_values=['failed', 'cancelled'],
                    timeout=params['wait_timeout'], interval=params['wait_interval'],
                )
        module.exit_json(changed=True, result=result, external_ref=external)

    run_module(module, handler)


if __name__ == '__main__':
    main()
