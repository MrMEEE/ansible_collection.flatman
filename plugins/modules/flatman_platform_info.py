#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 MrMEEE
# MIT License

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
module: flatman_platform_info
short_description: Gather the platforms and runtimes known to flat-manager
version_added: 1.0.0
description:
  - Retrieve the architectures and runtimes used by the published applications.
  - Wraps the C(/api/v2/platforms) and C(/api/v2/runtimes) endpoints.
  - These endpoints are public, so O(api_token) is optional.
author:
  - MrMEEE (@MrMEEE)
extends_documentation_fragment:
  - mrmeee.flatman.flatman
  - mrmeee.flatman.flatman.attributes_info
seealso:
  - module: mrmeee.flatman.flatman_app_info
  - module: mrmeee.flatman.flatman_app_stats_info
'''

EXAMPLES = r'''
- name: Gather the supported platforms and runtimes
  mrmeee.flatman.flatman_platform_info:
    url: https://flatman.example.com
  register: platforms

- name: Fail when x86_64 is not published
  ansible.builtin.assert:
    that: "'x86_64' in platforms.platforms"

- name: Show the runtimes in use
  ansible.builtin.debug:
    var: platforms.runtimes
'''

RETURN = r'''
platforms:
  description: The sorted architectures of every published package.
  returned: always
  type: list
  elements: str
  sample:
    - aarch64
    - x86_64
runtimes:
  description: The sorted runtimes declared by the dependencies of every published package.
  returned: always
  type: list
  elements: str
  sample:
    - org.freedesktop.Platform/x86_64/23.08
    - org.gnome.Platform/x86_64/45
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.mrmeee.flatman.plugins.module_utils.flatman import (
    flatman_argument_spec,
    run_module,
)


def main():
    module = AnsibleModule(
        argument_spec=flatman_argument_spec(),
        supports_check_mode=True,
    )

    def handler(client):
        platforms = client.get('/api/v2/platforms')
        runtimes = client.get('/api/v2/runtimes')
        module.exit_json(changed=False, platforms=platforms or [], runtimes=runtimes or [])

    run_module(module, handler)


if __name__ == '__main__':
    main()
