#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 MrMEEE
# MIT License

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
module: flatman_app_pick
short_description: Manage curated app selections on flat-manager
version_added: 1.0.0
description:
  - Creates, updates and deletes the dated editorial app selections exposed by the Flathub compatible API.
  - Creates use C(POST /api/v2/app-picks/admin/curated-app-selections), updates use
    C(PUT /api/v2/app-picks/admin/curated-app-selections/<id>) and deletions use the matching C(DELETE).
  - The admin endpoint is used for every kind of selection because it is the only create endpoint that takes
    an explicit O(kind), so a single code path covers app of the day, app of the week and curated selections.
  - All of these endpoints require an API token belonging to an administrator.
author:
  - MrMEEE (@MrMEEE)
extends_documentation_fragment:
  - mrmeee.flatman.flatman
  - mrmeee.flatman.flatman.attributes
options:
  id:
    description:
      - Numeric ID of an existing selection.
      - When omitted, an existing selection is looked up by O(app_id), O(kind) and O(date), which together
        are unique on the server.
    type: int
  app_id:
    description:
      - Application ID (the Flatpak package ID) that is being picked.
      - Required to create a selection, and required together with O(kind) and O(date) to look one up.
      - The application must already be published.
    type: str
  kind:
    description:
      - Kind of editorial selection, taken from the server side choices.
    type: str
    choices: [day, week, curated]
  date:
    description:
      - ISO date the selection is shown on, for example C(2026-02-14).
    type: str
  title:
    description:
      - Editorial title shown with the selection. Defaults to an empty string on the server.
    type: str
  description:
    description:
      - Editorial description shown with the selection. Defaults to an empty string on the server.
    type: str
  rank:
    description:
      - Ordering rank within a single date. Defaults to V(0) on the server.
    type: int
  state:
    description:
      - Whether the selection should exist or not.
    type: str
    choices: [present, absent]
    default: present
seealso:
  - module: mrmeee.flatman.flatman_app_pick_info
'''

EXAMPLES = r'''
- name: Pick an application as app of the day
  mrmeee.flatman.flatman_app_pick:
    url: https://flatman.example.com
    api_token: "{{ flatman_admin_token }}"
    app_id: org.example.Editor
    kind: day
    date: '2026-02-14'
    title: Editor
    description: A fast plain text editor

- name: Reorder a known curated selection
  mrmeee.flatman.flatman_app_pick:
    url: https://flatman.example.com
    api_token: "{{ flatman_admin_token }}"
    id: 42
    rank: 1

- name: Remove an app of the week selection
  mrmeee.flatman.flatman_app_pick:
    url: https://flatman.example.com
    api_token: "{{ flatman_admin_token }}"
    app_id: org.example.Game
    kind: week
    date: '2026-02-09'
    state: absent
'''

RETURN = r'''
app_pick:
  description: The app pick selection as returned by the API after the change.
  returned: when O(state=present)
  type: dict
  sample:
    id: 42
    app_id: org.example.Editor
    name: Editor
    kind: day
    date: '2026-02-14'
    title: Editor
    description: A fast plain text editor
    rank: 0
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.mrmeee.flatman.plugins.module_utils.flatman import (
    flatman_argument_spec,
    run_module,
)

ADMIN_PATH = '/api/v2/app-picks/admin/curated-app-selections'


def find_current(client, params):
    if params['id'] is not None:
        for item in client.get(ADMIN_PATH):
            if item.get('id') == params['id']:
                return item
        return None

    if not (params['app_id'] and params['kind'] and params['date']):
        return None

    for item in client.get(ADMIN_PATH):
        if (item.get('app_id') == params['app_id']
                and item.get('kind') == params['kind']
                and str(item.get('date')) == params['date']):
            return item
    return None


def main():
    argument_spec = flatman_argument_spec()
    argument_spec.update(
        id=dict(type='int'),
        app_id=dict(type='str'),
        kind=dict(type='str', choices=['day', 'week', 'curated']),
        date=dict(type='str'),
        title=dict(type='str'),
        description=dict(type='str'),
        rank=dict(type='int'),
        state=dict(type='str', default='present', choices=['present', 'absent']),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_one_of=[['id', 'app_id']],
    )

    def handler(client):
        params = module.params
        state = params['state']
        current = find_current(client, params)

        if state == 'absent':
            if current is None:
                module.exit_json(changed=False, diff={})
            diff = client.make_diff(current, {})
            if not module.check_mode:
                client.delete('%s/%s' % (ADMIN_PATH, current['id']))
            module.exit_json(changed=True, app_pick=current, diff=diff)

        desired = dict(
            app_id=params['app_id'],
            kind=params['kind'],
            date=params['date'],
            title=params['title'],
            description=params['description'],
            rank=params['rank'],
        )
        payload = dict((k, v) for k, v in desired.items() if v is not None)

        if current is None:
            for required in ('app_id', 'kind', 'date'):
                if payload.get(required) is None:
                    module.fail_json(msg='app_id, kind and date are required to create an app pick')
            diff = client.make_diff({}, payload)
            if module.check_mode:
                module.exit_json(changed=True, app_pick=payload, diff=diff)
            created = client.post(ADMIN_PATH, data=payload)
            module.exit_json(changed=True, app_pick=created, diff=client.make_diff({}, created))

        changes = client.diff_fields(current, payload)
        # app_id cannot be changed through the detail endpoint, so it never drives an update.
        changes.pop('app_id', None)
        if not changes:
            module.exit_json(changed=False, app_pick=current, diff={})

        preview = dict(current)
        preview.update(changes)
        diff = client.make_diff(current, preview)
        if module.check_mode:
            module.exit_json(changed=True, app_pick=preview, diff=diff)

        updated = client.put('%s/%s' % (ADMIN_PATH, current['id']), data=changes)
        module.exit_json(changed=True, app_pick=updated, diff=client.make_diff(current, updated))

    run_module(module, handler)


if __name__ == '__main__':
    main()
