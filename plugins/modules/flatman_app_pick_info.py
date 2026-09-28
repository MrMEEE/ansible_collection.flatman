#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 MrMEEE
# MIT License

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
module: flatman_app_pick_info
short_description: Read curated app selections from flat-manager
version_added: 1.0.0
description:
  - Reads the dated editorial app selections exposed by the Flathub compatible API.
  - Wraps the C(/api/v2/app-picks) endpoints.
author:
  - MrMEEE (@MrMEEE)
extends_documentation_fragment:
  - mrmeee.flatman.flatman
  - mrmeee.flatman.flatman.attributes_info
options:
  scope:
    description:
      - Which set of app picks to read.
      - V(app-of-the-day) reads C(/api/v2/app-picks/app-of-the-day), or the dated variant when O(date) is set.
      - V(app-of-the-week) reads C(/api/v2/app-picks/app-of-the-week), which always uses the current date.
      - V(apps-of-the-week) reads C(/api/v2/app-picks/apps-of-the-week/<date>).
      - V(curated) reads C(/api/v2/app-picks/curated-app-selections/<date>).
      - V(admin-selections) reads C(/api/v2/app-picks/admin/curated-app-selections) and needs an
        administrator token. Set O(id) to pick a single selection out of that list.
      - V(admin-apps-of-the-week) reads C(/api/v2/app-picks/admin/apps-of-the-week/<date>) and needs an
        administrator token.
      - V(themes) reads C(/api/v2/app-picks/admin/curated-app-selection-themes) and needs an
        administrator token.
    type: str
    required: true
    choices:
      - app-of-the-day
      - app-of-the-week
      - apps-of-the-week
      - curated
      - admin-selections
      - admin-apps-of-the-week
      - themes
  date:
    description:
      - ISO date to read the selections for, for example C(2026-02-14).
      - Required for O(scope=apps-of-the-week), O(scope=curated) and O(scope=admin-apps-of-the-week),
        because their URL contains the date.
      - Optional for O(scope=app-of-the-day), where it switches to the dated endpoint.
    type: str
  id:
    description:
      - Return only the selection with this numeric ID.
      - Only meaningful with O(scope=admin-selections), because the detail endpoint itself is write only,
        so the filtering is done by the module.
    type: int
seealso:
  - module: mrmeee.flatman.flatman_app_pick
'''

EXAMPLES = r'''
- name: Read today's app of the day
  mrmeee.flatman.flatman_app_pick_info:
    url: https://flatman.example.com
    scope: app-of-the-day
  register: today

- name: Read the apps of the week for a given week
  mrmeee.flatman.flatman_app_pick_info:
    url: https://flatman.example.com
    scope: apps-of-the-week
    date: '2026-02-09'
  register: this_week

- name: Read every curated selection as an administrator
  mrmeee.flatman.flatman_app_pick_info:
    url: https://flatman.example.com
    api_token: "{{ flatman_admin_token }}"
    scope: admin-selections
  register: selections
'''

RETURN = r'''
app_picks:
  description:
    - The matching app pick selections.
    - For O(scope=themes) the entries are theme objects with C(id), C(name) and C(description) keys.
    - When O(id) is used the list holds at most the single matching selection.
  returned: always
  type: list
  elements: dict
  sample:
    - id: 42
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

BASE_PATH = '/api/v2/app-picks'

DATED_SCOPES = ['apps-of-the-week', 'curated', 'admin-apps-of-the-week']


def scope_path(scope, date):
    if scope == 'app-of-the-day':
        if date:
            return '%s/app-of-the-day/%s' % (BASE_PATH, date)
        return '%s/app-of-the-day' % BASE_PATH
    if scope == 'app-of-the-week':
        return '%s/app-of-the-week' % BASE_PATH
    if scope == 'apps-of-the-week':
        return '%s/apps-of-the-week/%s' % (BASE_PATH, date)
    if scope == 'curated':
        return '%s/curated-app-selections/%s' % (BASE_PATH, date)
    if scope == 'admin-selections':
        return '%s/admin/curated-app-selections' % BASE_PATH
    if scope == 'admin-apps-of-the-week':
        return '%s/admin/apps-of-the-week/%s' % (BASE_PATH, date)
    return '%s/admin/curated-app-selection-themes' % BASE_PATH


def main():
    argument_spec = flatman_argument_spec()
    argument_spec.update(
        scope=dict(
            type='str',
            required=True,
            choices=[
                'app-of-the-day',
                'app-of-the-week',
                'apps-of-the-week',
                'curated',
                'admin-selections',
                'admin-apps-of-the-week',
                'themes',
            ],
        ),
        date=dict(type='str'),
        id=dict(type='int'),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[('scope', scope, ('date',)) for scope in DATED_SCOPES],
    )

    def handler(client):
        params = module.params
        app_picks = client.get(scope_path(params['scope'], params['date']))
        if params['id'] is not None:
            app_picks = [item for item in app_picks if item.get('id') == params['id']]
        module.exit_json(changed=False, app_picks=app_picks)

    run_module(module, handler)


if __name__ == '__main__':
    main()
