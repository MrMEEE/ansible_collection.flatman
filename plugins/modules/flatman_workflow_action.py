#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 MrMEEE
# MIT License

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
module: flatman_workflow_action
short_description: Run actions in the expanded token workflow router
version_added: 1.2.0
description:
  - Dispatch an explicitly supported resource/action pair as a JSON POST.
  - Supports BuildStream, release lifecycle, RPM, access membership and maintenance workflows.
  - Uses the server web workflow field names for O(data), including nested route IDs.
author:
  - MrMEEE (@MrMEEE)
extends_documentation_fragment:
  - mrmeee.flatman.flatman
attributes:
  check_mode:
    description: Validates arguments without dispatching any action, including read actions.
    support: full
  diff_mode:
    description: Imperative actions do not return a diff.
    support: N/A
options:
  resource:
    description: Router resource owning the action.
    type: str
    required: true
    choices:
      - gpg-keys
      - ldap-sources
      - flatpak-remotes
      - external-refs
      - packages
      - repositories
      - builds
      - promotions
      - external-ref-promotions
      - bst-promotions
      - bst-sources
      - clients
      - permission-groups
      - site-config
      - rpm-packages
      - rpm-builds
      - rpm-distributions
      - rpm-repositories
      - satellite-servers
  action:
    description:
      - Action name. Only pairs listed in the collection workflow guide are accepted.
      - C(delete), C(unpublish), pruning and toggles can be destructive.
    type: str
    required: true
    choices:
      - renew
      - test-connection
      - test-search
      - scan-spec-files
      - scan-branches
      - toggle
      - bulk-import
      - unpublish
      - retry
      - republish
      - check-upstream
      - check-available
      - update-metadata
      - recommit
      - delete
      - cancel
      - bst-promote
      - build
      - force-rebuild
      - integrity-check
      - assign-organisations
      - lockdown
      - memberships
      - cleanup
      - sync-repositories
      - check-external-updates
      - scan-available-versions
      - scan-upstream-versions
      - repair-permissions
      - scan-orphaned-refs
      - prune-orphaned-ref
      - prune-orphaned-refs
      - build-with-number
      - toggle-repository
      - signing-key
      - assign-destination
      - repush
      - logs
      - sync
      - sync-repos
      - fetch-organisations
      - fetch-products
      - fetch-repositories
  id:
    description: Numeric source ID. Required for detail actions and forbidden for collection actions.
    type: int
  data:
    description:
      - JSON workflow body using upstream form/JSON names.
      - Nested identifiers such as C(repo_pk) or C(dist_pk) belong here.
      - Put credentials in O(secret_data), not ordinary fields.
    type: dict
    default: {}
  secret_data:
    description:
      - Credential fields merged into O(data) and protected with C(no_log).
      - Must not duplicate fields in O(data).
      - Only include secrets here; ordinary IDs belong in O(data).
    type: dict
    default: {}
notes:
  - Requires a server with the expanded token workflow router.
  - Actions are imperative, not convergent, and never automatically retried or polled.
  - Read/report actions return C(changed=false), even though the router uses POST for them.
  - Other actions return C(changed=true) when successfully dispatched.
  - Version checks may update cached server fields even though reported as read actions.
  - Use C(flatman_resource_info) to poll the affected record or inspect C(error_message).
  - Prefer dedicated promotion and External action modules when their idempotency/wait support is needed.
  - Use task-level C(no_log=true) for workflows containing credentials.
  - GPG renewal takes C(key_lifetime) as C("0"), C(1y), C(2y), C(5y), or C(10y), recalculated from today.
  - LDAP tests require C(hostname); search also requires C(base_dn) and C(search_username).
  - LDAP tests accept connection settings and optional C(source_pk) to reuse a saved bind password.
  - RPM discovery requires C(url); spec discovery accepts C(branch), defaulting to C(main).
  - LDAP tests and RPM discovery return C(changed=false); LDAP C(ok=false) responses fail the task.
'''

EXAMPLES = r'''
- name: Build a BuildStream source
  mrmeee.flatman.flatman_workflow_action:
    resource: bst-sources
    action: build
    id: 12

- name: Inspect orphaned refs without pruning them
  mrmeee.flatman.flatman_workflow_action:
    resource: site-config
    action: scan-orphaned-refs

- name: Discover RPM spec files without changing a package
  mrmeee.flatman.flatman_workflow_action:
    resource: rpm-packages
    action: scan-spec-files
    timeout: 180
    data:
      url: https://github.com/example/app-rpm.git
      branch: main
  register: discovered_specs
'''

RETURN = r'''
result:
  description: Raw workflow response, or an empty dictionary in check mode.
  returned: always
  type: dict
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.mrmeee.flatman.plugins.module_utils.flatman import flatman_argument_spec, run_module
from ansible_collections.mrmeee.flatman.plugins.module_utils.router import (
    ACTION_ROUTES,
    ACTIONS,
    check_response,
    resource_path,
    workflow_payload,
)


def main():
    spec = flatman_argument_spec()
    spec.update(
        resource=dict(type='str', required=True, choices=sorted(ACTION_ROUTES)),
        action=dict(type='str', required=True, choices=ACTIONS),
        id=dict(type='int'),
        data=dict(type='dict', default={}),
        secret_data=dict(type='dict', default={}, no_log=True),
    )
    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)
    params = module.params
    payload = workflow_payload(module)
    contract = ACTION_ROUTES[params['resource']].get(params['action'])
    if contract is None:
        module.fail_json(msg='Unsupported resource/action pair')
    detail, read_only, required = contract
    if detail != (params['id'] is not None):
        module.fail_json(msg='id is required for detail actions and forbidden for collection actions')
    if params['id'] is not None and params['id'] <= 0:
        module.fail_json(msg='id must be positive')
    for key in required:
        if key not in payload or not payload[key]:
            module.fail_json(msg='data.%s is required for this action' % key)

    def handler(client):
        if module.check_mode:
            module.exit_json(changed=not read_only, result={})
        path = resource_path(params['resource'])
        if detail:
            path += '%s/' % params['id']
        result = check_response(client.post('%s%s/' % (path, params['action']), data=payload))
        module.exit_json(changed=not read_only, result=result)

    run_module(module, handler)


if __name__ == '__main__':
    main()
