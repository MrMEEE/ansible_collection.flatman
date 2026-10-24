#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 MrMEEE
# MIT License

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
module: flatman_promotion_batch
short_description: Promote all currently eligible Flatpak builds or External versions
version_added: 1.2.0
description:
  - Discover server-eligible Flatpak build and External version promotions and submit them sequentially.
  - V(target) sends every currently eligible candidate to one selected repository.
  - V(all_ready) promotes to all repositories currently eligible in the release chain.
  - With O(wait=true), refresh eligibility after each completed round to discover newly unlocked child repositories.
author:
  - MrMEEE (@MrMEEE)
extends_documentation_fragment:
  - mrmeee.flatman.flatman
attributes:
  check_mode:
    description: Reports the current plan without submitting any promotions.
    support: full
  diff_mode:
    description: Returns the planned source and target pairs when C(--diff) is used.
    support: partial
options:
  mode:
    description: Promote to one selected target or advance through every eligible repository in the chain.
    type: str
    choices: [target, all_ready]
    default: target
  kind:
    description: Limit the batch to Flatpak builds, External versions, or both.
    type: str
    choices: [both, build, external]
    default: both
  repository:
    description:
      - Target repository name; required with O(mode=target).
      - Mutually exclusive with O(target_repo_id).
    type: str
  target_repo_id:
    description:
      - Target repository ID; required with O(mode=target).
      - Mutually exclusive with O(repository).
    type: int
  wait:
    description: Wait for each promotion and refresh eligibility to traverse release chains.
    type: bool
    default: true
  wait_timeout:
    description: Maximum seconds to wait for each promotion.
    type: int
    default: 1800
  wait_interval:
    description: Seconds between promotion status checks.
    type: int
    default: 10
  max_promotions:
    description: Safety limit on promotions submitted in one invocation.
    type: int
    default: 500
notes:
  - Eligibility and parent-chain prerequisites are calculated and enforced by the server.
  - V(all_ready) with O(wait=false) submits only the current readiness snapshot. Run again after jobs finish to continue the chain.
  - Check mode predicts only the current readiness snapshot; it cannot predict targets unlocked by future promotions.
  - Eligibility can change between listing and dispatch if another actor promotes the same source.
  - Requires promotion permission and organisation access to each source.
seealso:
  - module: mrmeee.flatman.flatman_promotion_ready_info
  - module: mrmeee.flatman.flatman_promotion
'''

EXAMPLES = r'''
- name: Promote all currently-ready items to stable
  mrmeee.flatman.flatman_promotion_batch:
    url: https://flatman.example.com
    api_token: "{{ flatman_api_token }}"
    mode: target
    repository: stable
    kind: both
    wait: true

- name: Promote all Flatpak builds and Externals through the release chain
  mrmeee.flatman.flatman_promotion_batch:
    url: https://flatman.example.com
    api_token: "{{ flatman_api_token }}"
    mode: all_ready
    kind: both
    wait: true

- name: Preview currently-ready promotions
  mrmeee.flatman.flatman_promotion_batch:
    url: https://flatman.example.com
    api_token: "{{ flatman_api_token }}"
    mode: all_ready
  check_mode: true
'''

RETURN = r'''
promotions:
  description: Dispatched promotion records with readable source and target names.
  returned: always
  type: list
  elements: dict
  sample:
    - kind: build
      build_id: 19
      package_name: Example App
      target_repo_id: 10
      target_repo_name: stable
      promotion_id: 31
      status: promoted
planned_promotions:
  description: Currently eligible source/target pairs returned in check mode.
  returned: in check mode
  type: list
  elements: dict
count:
  description: Number of promotions dispatched.
  returned: always
  type: int
remaining_ready:
  description: Candidates left when the safety limit or non-waiting mode stops the batch.
  returned: always
  type: list
  elements: dict
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.mrmeee.flatman.plugins.module_utils.flatman import (
    FlatManagerError,
    flatman_argument_spec,
    run_module,
)
from ansible_collections.mrmeee.flatman.plugins.module_utils.workflows import (
    validate_wait,
)


def main():
    spec = flatman_argument_spec()
    spec.update(
        mode=dict(type='str', default='target', choices=['target', 'all_ready']),
        kind=dict(type='str', default='both', choices=['both', 'build', 'external']),
        repository=dict(type='str'),
        target_repo_id=dict(type='int'),
        wait=dict(type='bool', default=True),
        wait_timeout=dict(type='int', default=1800),
        wait_interval=dict(type='int', default=10),
        max_promotions=dict(type='int', default=500),
    )
    module = AnsibleModule(
        argument_spec=spec,
        supports_check_mode=True,
        mutually_exclusive=[['repository', 'target_repo_id']],
    )
    validate_wait(module)
    if module.params['mode'] == 'target' and not (
        module.params['repository'] or module.params['target_repo_id']
    ):
        module.fail_json(msg='mode=target requires repository or target_repo_id')
    if module.params['max_promotions'] < 1:
        module.fail_json(msg='max_promotions must be positive')

    def handler(client):
        params = module.params
        target_id = params['target_repo_id']
        if params['repository']:
            target_id = client.resolve(
                '/api/repositories/', 'name', params['repository'], 'Repository')['id']

        def get_candidates():
            found = []
            if params['kind'] in ('both', 'build'):
                found.extend(client.get_all('/api/promotions/available/'))
            if params['kind'] in ('both', 'external'):
                found.extend(client.get_all('/api/external-ref-promotions/available/'))
            if target_id is not None:
                found = [item for item in found if item.get('target_repo_id') == target_id]
            return found

        dispatched = []
        handled = set()
        while len(dispatched) < params['max_promotions']:
            candidates = get_candidates()
            candidates = [item for item in candidates if _candidate_key(item) not in handled]
            if module.check_mode:
                module.exit_json(changed=bool(candidates), promotions=[], planned_promotions=candidates,
                                 count=0, remaining_ready=candidates)
            if not candidates:
                break

            for item in candidates:
                if len(dispatched) >= params['max_promotions']:
                    break
                key = _candidate_key(item)
                if key in handled:
                    continue
                handled.add(key)
                if item['kind'] == 'build':
                    source_path = '/api/builds/%s/' % item['build_id']
                    promotion_collection = '/api/promotions/'
                    payload = {'target_repo_id': item['target_repo_id']}
                else:
                    source_path = '/api/external-refs/%s/' % item['external_ref_id']
                    promotion_collection = '/api/external-ref-promotions/'
                    payload = {
                        'target_repo_id': item['target_repo_id'],
                        'external_ref_version_id': item['external_ref_version_id'],
                    }
                try:
                    response = client.post('%spromote/' % source_path, data=payload, expect=(202,))
                    promotion_id = response['promotion_id']
                    promotion_path = '%s%s/' % (promotion_collection, promotion_id)
                    promotion = client.get(promotion_path)
                    if params['wait'] and promotion.get('status') != 'promoted':
                        promotion = client.wait_for(
                            promotion_path, 'status', ['promoted'], fail_values=['failed'],
                            timeout=params['wait_timeout'], interval=params['wait_interval'],
                        )
                except FlatManagerError as exc:
                    module.fail_json(msg='Promotion failed: %s' % exc.msg, promotions=dispatched,
                                     count=len(dispatched), remaining_ready=get_candidates())
                dispatched_item = dict(item)
                dispatched_item.update(promotion_id=promotion_id, status=promotion.get('status'))
                dispatched.append(dispatched_item)

            if not params['wait']:
                break

        module.exit_json(changed=bool(dispatched), promotions=dispatched, count=len(dispatched),
                         remaining_ready=get_candidates())

    run_module(module, handler)


def _candidate_key(item):
    return (
        item.get('kind'), item.get('build_id'), item.get('external_ref_id'),
        item.get('external_ref_version_id'), item.get('target_repo_id'),
    )


if __name__ == '__main__':
    main()
