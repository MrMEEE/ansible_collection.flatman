#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 MrMEEE
# MIT License

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
module: flatman_status_info
short_description: Gather the version and health status of a flat-manager server
version_added: 1.0.0
description:
  - Query the running version of a flat-manager-django server through C(/api/version/).
  - Query the service health flag through the Flathub compatible C(/api/v2/status) endpoint.
author:
  - MrMEEE (@MrMEEE)
extends_documentation_fragment:
  - mrmeee.flatman.flatman
  - mrmeee.flatman.flatman.attributes_info
options: {}
notes:
  - Both endpoints allow anonymous access, so O(api_token) is optional. This makes the module
    useful as a readiness check before any credentials have been provisioned.
seealso:
  - module: mrmeee.flatman.flatman_repository_info
'''

EXAMPLES = r'''
- name: Check that the server is up and report its version
  mrmeee.flatman.flatman_status_info:
    url: https://flatman.example.com
  register: flatman_status

- name: Show the running version
  ansible.builtin.debug:
    msg: "flat-manager {{ flatman_status.version }} built {{ flatman_status.build_date }}"

- name: Wait until the service reports itself healthy
  mrmeee.flatman.flatman_status_info:
    url: https://flatman.example.com
  register: health
  until: health.status == 'ok'
  retries: 30
  delay: 5
'''

RETURN = r'''
version:
  description: Version string reported by the server.
  returned: always
  type: str
  sample: 1.0.29
build_date:
  description: Build date reported by the server.
  returned: always
  type: str
  sample: "2026-09-22"
status:
  description: Health flag reported by the C(/api/v2/status) endpoint.
  returned: always
  type: str
  sample: ok
server:
  description: The raw responses of both endpoints, keyed by endpoint name.
  returned: always
  type: dict
  contains:
    version:
      description: Raw body of the C(/api/version/) response.
      returned: always
      type: dict
      sample:
        version: 1.0.29
        build_date: "2026-09-22"
    status:
      description: Raw body of the C(/api/v2/status) response.
      returned: always
      type: dict
      sample:
        status: ok
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.mrmeee.flatman.plugins.module_utils.flatman import (
    flatman_argument_spec,
    run_module,
)

VERSION_ENDPOINT = '/api/version/'
STATUS_ENDPOINT = '/api/v2/status'


def as_dict(value):
    return value if isinstance(value, dict) else {}


def main():
    module = AnsibleModule(
        argument_spec=flatman_argument_spec(),
        supports_check_mode=True,
    )

    def handler(client):
        version_body = as_dict(client.get(VERSION_ENDPOINT))
        status_body = as_dict(client.get(STATUS_ENDPOINT))

        module.exit_json(
            changed=False,
            version=version_body.get('version'),
            build_date=version_body.get('build_date'),
            status=status_body.get('status'),
            server=dict(version=version_body, status=status_body),
        )

    run_module(module, handler)


if __name__ == '__main__':
    main()
