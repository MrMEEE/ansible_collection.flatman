#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 MrMEEE
# MIT License

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
module: flatman_git_branch_info
short_description: List the branches of a remote Git repository known to flat-manager
version_added: 1.0.0
description:
  - Ask a flat-manager-django server to list the heads of a remote Git repository.
  - Wraps the C(/api/git-branches/) endpoint, which runs C(git ls-remote) on the server.
author:
  - MrMEEE (@MrMEEE)
extends_documentation_fragment:
  - mrmeee.flatman.flatman
  - mrmeee.flatman.flatman.attributes_info
options:
  repo_url:
    description:
      - URL of the remote Git repository to inspect, as the server would clone it.
    type: str
    required: true
notes:
  - This endpoint allows anonymous access, so O(api_token) is optional.
  - The server applies a short timeout to the remote lookup. If the remote cannot be reached in
    time it returns the fallback list C(['main', 'master']) instead of an error.
seealso:
  - module: mrmeee.flatman.flatman_package
'''

EXAMPLES = r'''
- name: List the branches of a manifest repository
  mrmeee.flatman.flatman_git_branch_info:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    repo_url: https://github.com/example/org.example.App.git
  register: branches

- name: Fail early when the expected release branch is missing
  ansible.builtin.assert:
    that: "'stable' in branches.branches"
    fail_msg: The manifest repository has no stable branch

- name: Query anonymously without a token
  mrmeee.flatman.flatman_git_branch_info:
    url: https://flatman.example.com
    repo_url: https://gitlab.example.com/apps/org.example.Tool.git
  register: tool_branches
'''

RETURN = r'''
branches:
  description: Sorted branch names reported by the server.
  returned: always
  type: list
  elements: str
  sample:
    - beta
    - main
    - stable
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.mrmeee.flatman.plugins.module_utils.flatman import (
    flatman_argument_spec,
    run_module,
)

ENDPOINT = '/api/git-branches/'


def main():
    argument_spec = flatman_argument_spec()
    argument_spec.update(
        repo_url=dict(type='str', required=True),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    def handler(client):
        response = client.get(ENDPOINT, params=dict(repo_url=module.params['repo_url']))
        branches = response.get('branches') if isinstance(response, dict) else None
        module.exit_json(changed=False, branches=branches or [])

    run_module(module, handler)


if __name__ == '__main__':
    main()
