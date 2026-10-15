#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 MrMEEE
# MIT License

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
module: flatman_resource
short_description: Manage resources in the expanded token API
version_added: 1.2.0
description:
  - Manage supported resources through their router endpoints using JSON or web-form field names.
  - Identify an existing record by numeric ID or an exact, unique field match.
  - Only fields supplied in O(data) are reconciled; lists are compared order-insensitively.
author:
  - MrMEEE (@MrMEEE)
extends_documentation_fragment:
  - mrmeee.flatman.flatman
attributes:
  check_mode:
    description: Reads existing records and predicts changes without sending mutations.
    support: full
  diff_mode:
    description: Payloads may contain credentials, so no diff is returned.
    support: N/A
options:
  resource:
    description: Router resource to manage. Supported operations vary by resource.
    type: str
    required: true
    choices:
      - flatpak-remotes
      - organisations
      - bst-sources
      - clients
      - permission-groups
      - ldap-sources
      - ldap-group-mappings
      - rpm-packages
      - rpm-builds
      - rpm-distributions
      - satellite-servers
      - satellite-repositories
      - rpm-destinations
      - user-roles
      - permission-grants
      - group-permissions
      - site-config
      - external-refs
  id:
    description:
      - Numeric ID of an existing record. Mutually exclusive with O(match).
      - A missing ID cannot be used to create a new resource.
    type: int
  match:
    description:
      - Nonempty exact identity fields used to find a unique record.
      - On creation these fields are included in the payload.
      - Use readable fields, not credentials, for identity.
    type: dict
  data:
    description:
      - Desired JSON or web-form fields. Use numeric IDs for related resources.
      - Write-only fields cannot be compared and cause a write on every run when supplied.
      - Put credentials in O(secret_data), not ordinary fields or identity.
    type: dict
    default: {}
  secret_data:
    description:
      - Write-only credential fields merged into O(data) and protected with C(no_log).
      - Must not duplicate fields in O(data).
      - Only include secrets here; ordinary IDs belong in O(data) to keep returned IDs usable.
    type: dict
    default: {}
  state:
    description: Whether the resource should exist.
    type: str
    choices: [present, absent]
    default: present
notes:
  - Requires the expanded token router and suitable workflow/organisation permissions.
  - External refs may auto-queue a pull on creation according to upstream settings.
  - Unsupported create, update or delete operations fail explicitly.
  - Client, RPM build and destination resources only support deletion here.
  - Satellite servers and repositories support creation and deletion but not update.
  - Site configuration supports updates only; use O(id) from C(flatman_resource_info).
  - Responses from web-form adapters are acknowledgements, not resource records. The module rereads after writes.
  - Use task-level C(no_log=true) when managing site settings or credentials.
'''

EXAMPLES = r'''
- name: Configure an upstream Flatpak remote
  mrmeee.flatman.flatman_resource:
    resource: flatpak-remotes
    match:
      name: flathub
    data:
      url: https://dl.flathub.org/repo/
      is_active: true
      priority: 1

- name: Create an External definition
  mrmeee.flatman.flatman_resource:
    resource: external-refs
    match:
      repository: 2
      ref: app/org.example.App/x86_64/stable
    data:
      remote: 1
      display_name: Example App
'''

RETURN = r'''
resource:
  description: Current resource, predicted fields in check mode, or an empty dictionary after deletion.
  returned: always
  type: dict
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.mrmeee.flatman.plugins.module_utils.flatman import flatman_argument_spec, run_module
from ansible_collections.mrmeee.flatman.plugins.module_utils.router import (
    RESOURCE_OPERATIONS,
    check_response,
    field_changes,
    find_resource,
    resource_path,
    workflow_payload,
)

MANAGED_RESOURCES = sorted(key for key, operations in RESOURCE_OPERATIONS.items() if operations)


def main():
    spec = flatman_argument_spec()
    spec.update(
        resource=dict(type='str', required=True, choices=MANAGED_RESOURCES),
        id=dict(type='int'),
        match=dict(type='dict'),
        data=dict(type='dict', default={}),
        secret_data=dict(type='dict', default={}, no_log=True),
        state=dict(type='str', default='present', choices=['present', 'absent']),
    )
    module = AnsibleModule(
        argument_spec=spec, supports_check_mode=True,
        mutually_exclusive=[['id', 'match']], required_one_of=[['id', 'match']],
    )

    def handler(client):
        params = module.params
        payload = workflow_payload(module)
        identity = params['match']
        if identity is not None and not identity:
            module.fail_json(msg='match must contain identity fields')
        path = resource_path(params['resource'])
        pk = params['id']
        current = (client.get_or_none('%s%s/' % (path, pk)) if pk is not None
                   else find_resource(client, path, identity))
        desired = dict(identity or {})
        desired.update(payload)
        if identity and field_changes(client, desired, identity):
            module.fail_json(msg='data must not conflict with match identity fields')
        if params['state'] == 'absent':
            operation = 'delete'
            changed = current is not None
        else:
            operation = 'create' if current is None else 'update'
            changed = current is None or bool(field_changes(client, current, desired))
        if not changed:
            module.exit_json(changed=False, resource=current or {})
        if operation not in RESOURCE_OPERATIONS[params['resource']].split():
            module.fail_json(msg='%s does not support %s' % (params['resource'], operation))
        if current is None and pk is not None and operation == 'create':
            module.fail_json(msg='Resource ID not found; use match to create a record')
        if module.check_mode:
            preview = dict(current or {})
            preview.update(desired)
            module.exit_json(changed=True, resource={} if operation == 'delete' else preview)
        if operation == 'delete':
            check_response(client.delete('%s%s/' % (path, current['id'])))
            module.exit_json(changed=True, resource={})
        if operation == 'create':
            response = check_response(client.post(path, data=desired, expect=(200, 201, 202)))
        else:
            response = check_response(client.patch('%s%s/' % (path, current['id']), data=desired))
        result_id = current['id'] if current else response.get('id')
        updated = (client.get('%s%s/' % (path, result_id)) if result_id is not None
                   else find_resource(client, path, identity))
        if updated is None:
            module.fail_json(msg='Mutation acknowledged but the resource could not be read back')
        readable = dict((key, value) for key, value in desired.items() if key in updated)
        if field_changes(client, updated, readable):
            module.fail_json(msg='Mutation acknowledged but requested readable fields were not applied')
        module.exit_json(changed=True, resource=updated)

    run_module(module, handler)


if __name__ == '__main__':
    main()
