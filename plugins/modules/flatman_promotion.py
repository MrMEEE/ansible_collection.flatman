#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 MrMEEE
# MIT License

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
module: flatman_promotion
short_description: Promote a Flatpak build or External version to another repository
version_added: 1.1.0
description:
  - Queue a promotion through the token API and optionally wait until it completes.
  - Reuses pending, promoting or promoted records for the same source and target.
  - Failed Flatpak promotions are retried by the server; failed External promotions are queued anew.
author:
  - MrMEEE (@MrMEEE)
extends_documentation_fragment:
  - mrmeee.flatman.flatman
attributes:
  check_mode:
    description: Predicts changes from source and promotion records without dispatching or polling.
    support: full
  diff_mode:
    description: Promotion actions do not return a diff.
    support: N/A
options:
  build_id:
    description:
      - Numeric build history ID, not a package ID or build attempt number.
      - Exactly one of O(build_id) and O(external_ref_id) is required.
    type: int
  external_ref_id:
    description:
      - Numeric External ref ID.
      - Exactly one of O(build_id) and O(external_ref_id) is required.
    type: int
  external_ref_version_id:
    description:
      - Published version belonging to O(external_ref_id).
      - When omitted, the latest published version by pull time and ID is selected.
      - Only valid with O(external_ref_id).
    type: int
  repository:
    description:
      - Target repository name.
      - Exactly one of O(repository) and O(target_repo_id) is required.
    type: str
  target_repo_id:
    description:
      - Numeric target repository ID.
      - Exactly one of O(repository) and O(target_repo_id) is required.
    type: int
  wait:
    description: Poll the new or existing promotion until promoted, failing on a failed state.
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
  - Requires a server with the token-authenticated promotion API and appropriate user permissions.
  - The server enforces active child targets and completion of prerequisite parent promotions.
  - Check mode reads source and promotion records but never dispatches or polls.
  - Target eligibility for a new promotion is validated by the server on dispatch, not in check mode.
  - Configure External refs through the server web interface; this module does not create them.
seealso:
  - module: mrmeee.flatman.flatman_promotion_info
  - module: mrmeee.flatman.flatman_external_ref_info
  - module: mrmeee.flatman.flatman_build_info
'''

EXAMPLES = r'''
- name: Promote an exact published Flatpak build to stable
  mrmeee.flatman.flatman_promotion:
    build_id: 48
    repository: stable
    wait: true

- name: Promote an exact External version to stable
  mrmeee.flatman.flatman_promotion:
    external_ref_id: 12
    external_ref_version_id: 7
    repository: stable
    wait: true
'''

RETURN = r'''
promotion:
  description: New or reused promotion record, or the predicted fields in check mode.
  returned: always
  type: dict
  sample:
    id: 10
    build: 48
    target_repo: 3
    status: promoted
result:
  description: Raw dispatch response, or an empty dictionary when reused or in check mode.
  returned: always
  type: dict
'''

from datetime import datetime

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
        build_id=dict(type='int'),
        external_ref_id=dict(type='int'),
        external_ref_version_id=dict(type='int'),
        repository=dict(type='str'),
        target_repo_id=dict(type='int'),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        mutually_exclusive=[['build_id', 'external_ref_id'], ['repository', 'target_repo_id']],
        required_one_of=[['build_id', 'external_ref_id'], ['repository', 'target_repo_id']],
        required_by={'external_ref_version_id': ['external_ref_id']},
    )
    validate_wait(module)

    def handler(client):
        params = module.params
        target = params['target_repo_id']
        if params['repository']:
            target = client.resolve('/api/repositories/', 'name', params['repository'], 'Repository')['id']
        payload = dict(target_repo_id=target)
        query = dict(target_repo=target)
        if params['build_id'] is not None:
            source_path = '/api/builds/%s/' % params['build_id']
            source = client.get(source_path)
            if source['status'] != 'published':
                module.fail_json(msg='Build must be published before promoting')
            path = '/api/promotions/'
            query['build'] = params['build_id']
        else:
            source_path = '/api/external-refs/%s/' % params['external_ref_id']
            source = client.get(source_path)
            versions = [v for v in source['versions'] if v['status'] == 'published']
            version_id = params['external_ref_version_id']
            if version_id is not None:
                versions = [v for v in versions if v['id'] == version_id]
            if not versions:
                module.fail_json(msg='No matching published version belongs to this External ref')
            version = max(versions, key=lambda v: (
                datetime.fromisoformat(v['pulled_at'].replace('Z', '+00:00')), v['id']))
            payload['external_ref_version_id'] = version['id']
            path = '/api/external-ref-promotions/'
            query.update(external_ref=params['external_ref_id'], external_ref_version=version['id'])

        candidates = client.get_all(path, params=query)
        current = next((p for p in candidates
                        if all(p.get(key) == value for key, value in query.items())
                        and p['status'] in ('pending', 'promoting', 'promoted')), None)
        changed = current is None
        result = {}
        if changed:
            if module.check_mode:
                current = dict(query, status='pending')
            else:
                result = client.post('%spromote/' % source_path, data=payload, expect=(202,))
                current = client.get('%s%s/' % (path, result['promotion_id']))
        if params['wait'] and not module.check_mode and current['status'] != 'promoted':
            current = client.wait_for(
                '%s%s/' % (path, current['id']), 'status', ['promoted'], fail_values=['failed'],
                timeout=params['wait_timeout'], interval=params['wait_interval'],
            )
        module.exit_json(changed=changed, promotion=current, result=result)

    run_module(module, handler)


if __name__ == '__main__':
    main()
