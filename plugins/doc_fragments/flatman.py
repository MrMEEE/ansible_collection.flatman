# -*- coding: utf-8 -*-
# Copyright (c) 2026 MrMEEE
# MIT License

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class ModuleDocFragment(object):

    DOCUMENTATION = r'''
options:
  url:
    description:
      - Base URL of the flat-manager-django instance, for example C(https://flatman.example.com).
      - May also be set with the E(FLATMAN_URL) environment variable.
    type: str
    required: true
  api_token:
    description:
      - API token used for authentication, sent in an C(Authorization) header of the form C(Token <api_token>).
      - Create one in the web UI under your user profile, or with the C(createapitoken) management command.
      - May also be set with the E(FLATMAN_API_TOKEN) environment variable.
      - Not required for the public read-only C(/api/v2) endpoints.
    type: str
  validate_certs:
    description:
      - Whether to validate the TLS certificate of the flat-manager server.
      - May also be set with the E(FLATMAN_VALIDATE_CERTS) environment variable.
    type: bool
    default: true
  timeout:
    description:
      - Socket timeout in seconds for each individual HTTP request.
    type: int
    default: 30
  include_names:
    description:
      - Add best-effort human-readable companion fields for related resource IDs in returned records.
      - Original numeric IDs are retained. Set to C(false) to skip the extra lookup requests.
    type: bool
    default: true
  client_cert:
    description:
      - Path to a PEM formatted client certificate used for mutual TLS.
    type: path
  client_key:
    description:
      - Path to the PEM formatted private key matching O(client_cert).
    type: path
requirements:
  - ansible-core >= 2.15
'''

    ATTRIBUTES = r'''
attributes:
  check_mode:
    description: Can run in C(check_mode) and return the changes that would be made.
    support: full
  diff_mode:
    description: Returns details on what has changed (or would have changed) when C(--diff) is used.
    support: full
'''

    ATTRIBUTES_INFO = r'''
attributes:
  check_mode:
    description: This module makes no changes, so it fully supports C(check_mode).
    support: full
  diff_mode:
    description: This module makes no changes, so it never reports a diff.
    support: N/A
'''
