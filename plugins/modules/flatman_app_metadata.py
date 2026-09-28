#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 MrMEEE
# MIT License

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
module: flatman_app_metadata
short_description: Manage the public Flathub metadata of a flat-manager application
version_added: 1.0.0
description:
  - Update the cached public metadata that the Flathub compatible C(/api/v2) API exposes for an application.
  - Wraps the C(/api/v2/appstream/<app_id>/metadata) endpoint.
  - This endpoint requires an administrator API token, unlike the read-only C(/api/v2) endpoints.
author:
  - MrMEEE (@MrMEEE)
extends_documentation_fragment:
  - mrmeee.flatman.flatman
  - mrmeee.flatman.flatman.attributes
options:
  app_id:
    description:
      - Application ID of the package, for example C(org.example.App).
    type: str
    required: true
  summary:
    description:
      - Short one line summary of the application.
    type: str
  description:
    description:
      - Long form description of the application.
    type: str
  homepage:
    description:
      - Homepage URL of the application.
    type: str
  icon_url:
    description:
      - URL of the application icon.
    type: str
  screenshots:
    description:
      - Screenshot entries stored verbatim in the metadata.
      - Each element may be a plain URL string or a dictionary, depending on your conventions.
    type: list
    elements: raw
  developer_name:
    description:
      - Name of the developer or vendor of the application.
    type: str
  categories:
    description:
      - Categories the application belongs to.
      - Replaces the existing list when specified.
    type: list
    elements: str
  keywords:
    description:
      - Search keywords for the application.
      - Replaces the existing list when specified.
    type: list
    elements: str
  is_verified:
    description:
      - Whether the application is marked as verified.
    type: bool
  is_mobile:
    description:
      - Whether the application is marked as suitable for mobile form factors.
    type: bool
seealso:
  - module: mrmeee.flatman.flatman_app_info
  - module: mrmeee.flatman.flatman_search_info
'''

EXAMPLES = r'''
- name: Publish metadata for an application
  mrmeee.flatman.flatman_app_metadata:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    app_id: org.example.App
    summary: A small example application
    developer_name: Example Inc
    homepage: https://example.com/app
    categories:
      - Utility
      - Development

- name: Mark an application as verified and mobile friendly
  mrmeee.flatman.flatman_app_metadata:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    app_id: org.example.App
    is_verified: true
    is_mobile: true

- name: Replace the screenshot list
  mrmeee.flatman.flatman_app_metadata:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    app_id: org.example.App
    screenshots:
      - https://example.com/app/shot1.png
      - https://example.com/app/shot2.png
'''

RETURN = r'''
app:
  description:
    - The public application entry after the change, in the same shape as C(/api/v2/appstream/<app_id>).
    - In check mode this is the locally computed preview of the entry.
  returned: always
  type: dict
  sample:
    id: org.example.App
    name: Example App
    summary: A small example application
    description: A slightly longer description.
    homepage: https://example.com/app
    icon_url: https://example.com/app/icon.png
    screenshots: []
    developer: Example Inc
    categories:
      - Utility
    keywords:
      - example
    verified: true
    mobile: false
    version: 1.2.3
    branch: stable
    arch: x86_64
    repository: stable
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.mrmeee.flatman.plugins.module_utils.flatman import (
    flatman_argument_spec,
    run_module,
)

# Metadata field name sent to the API -> key used in the public appstream response.
FIELD_MAP = {
    'summary': 'summary',
    'description': 'description',
    'homepage': 'homepage',
    'icon_url': 'icon_url',
    'screenshots': 'screenshots',
    'developer_name': 'developer',
    'categories': 'categories',
    'keywords': 'keywords',
    'is_verified': 'verified',
    'is_mobile': 'mobile',
}


def main():
    argument_spec = flatman_argument_spec()
    argument_spec.update(
        app_id=dict(type='str', required=True),
        summary=dict(type='str'),
        description=dict(type='str'),
        homepage=dict(type='str'),
        icon_url=dict(type='str'),
        screenshots=dict(type='list', elements='raw'),
        developer_name=dict(type='str'),
        categories=dict(type='list', elements='str'),
        keywords=dict(type='list', elements='str', no_log=False),
        is_verified=dict(type='bool'),
        is_mobile=dict(type='bool'),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    def handler(client):
        params = module.params
        app_id = params['app_id']

        current = client.get_or_none('/api/v2/appstream/%s' % app_id)
        if current is None:
            module.fail_json(msg='Application %r not found' % app_id)

        desired = dict((field, params[field]) for field in FIELD_MAP if params[field] is not None)
        comparable = dict((field, current.get(public)) for field, public in FIELD_MAP.items())

        changes = client.diff_fields(comparable, desired)
        if not changes:
            module.exit_json(changed=False, app=current, diff={})

        preview = dict(current)
        for field, value in changes.items():
            preview[FIELD_MAP[field]] = value

        if module.check_mode:
            module.exit_json(changed=True, app=preview, diff=client.make_diff(current, preview))

        updated = client.put('/api/v2/appstream/%s/metadata' % app_id, data=changes)
        module.exit_json(changed=True, app=updated, diff=client.make_diff(current, updated))

    run_module(module, handler)


if __name__ == '__main__':
    main()
