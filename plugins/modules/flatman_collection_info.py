#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 MrMEEE
# MIT License

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
module: flatman_collection_info
short_description: Browse flat-manager application collections and feeds
version_added: 1.0.0
description:
  - Retrieve the curated application collections and feeds of the Flathub compatible C(/api/v2) API.
  - Wraps the C(/api/v2/collection) and C(/api/v2/feed) endpoints.
  - These endpoints are public, so O(api_token) is optional.
author:
  - MrMEEE (@MrMEEE)
extends_documentation_fragment:
  - mrmeee.flatman.flatman
  - mrmeee.flatman.flatman.attributes_info
options:
  collection:
    description:
      - Which collection to retrieve.
      - V(popular) and V(trending) rank applications by unique clients seen in the last 30 days.
      - V(recently-added) and V(new) are equivalent and order by creation date.
      - V(category), V(developer), V(keyword) and V(keywords) list names when O(value) is not set.
      - V(keyword) and V(keywords) always return the full keyword list and ignore O(value).
      - V(feed) retrieves C(/api/v2/feed/<value>) and therefore requires O(value).
    type: str
    required: true
    choices:
      - popular
      - trending
      - recently-added
      - new
      - recently-updated
      - verified
      - mobile
      - alphabetical
      - category
      - developer
      - keyword
      - keywords
      - feed
  value:
    description:
      - The category name, developer name or feed name to look up.
      - Required when O(collection=feed) or when O(subcategories=true).
      - Valid feed names are C(new) and C(recently-updated).
    type: str
  subcategories:
    description:
      - Retrieve the subcategories of O(value) instead of its applications.
      - Only meaningful together with O(collection=category) and a O(value).
    type: bool
    default: false
seealso:
  - module: mrmeee.flatman.flatman_app_info
  - module: mrmeee.flatman.flatman_search_info
'''

EXAMPLES = r'''
- name: Get the most popular applications
  mrmeee.flatman.flatman_collection_info:
    url: https://flatman.example.com
    collection: popular
  register: popular

- name: List every known category
  mrmeee.flatman.flatman_collection_info:
    url: https://flatman.example.com
    collection: category
  register: categories

- name: Get the applications of one developer
  mrmeee.flatman.flatman_collection_info:
    url: https://flatman.example.com
    collection: developer
    value: Example Inc
  register: by_developer

- name: Read the new applications feed
  mrmeee.flatman.flatman_collection_info:
    url: https://flatman.example.com
    collection: feed
    value: new
  register: feed
'''

RETURN = r'''
items:
  description:
    - The contents of the requested collection.
    - A list of application dictionaries for the application collections and feeds.
    - A list of plain strings for the name listings, that is O(collection=category), O(collection=developer),
      O(collection=keyword) and O(collection=keywords) without a O(value), and for subcategory lookups.
  returned: always
  type: list
  elements: raw
  sample:
    - id: org.example.App
      name: Example App
      summary: A small example application
      developer: Example Inc
      verified: true
      version: 1.2.3
      repository: stable
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.mrmeee.flatman.plugins.module_utils.flatman import (
    flatman_argument_spec,
    run_module,
)

COLLECTION_CHOICES = [
    'popular',
    'trending',
    'recently-added',
    'new',
    'recently-updated',
    'verified',
    'mobile',
    'alphabetical',
    'category',
    'developer',
    'keyword',
    'keywords',
    'feed',
]


def build_path(collection, value, subcategories):
    if collection == 'feed':
        return '/api/v2/feed/%s' % value
    if collection == 'category':
        if not value:
            return '/api/v2/collection/category'
        if subcategories:
            return '/api/v2/collection/category/%s/subcategories' % value
        return '/api/v2/collection/category/%s' % value
    if collection == 'developer':
        if not value:
            return '/api/v2/collection/developer'
        return '/api/v2/collection/developer/%s' % value
    return '/api/v2/collection/%s' % collection


def main():
    argument_spec = flatman_argument_spec()
    argument_spec.update(
        collection=dict(type='str', required=True, choices=COLLECTION_CHOICES),
        value=dict(type='str'),
        subcategories=dict(type='bool', default=False),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[
            ('collection', 'feed', ['value']),
            ('subcategories', True, ['value']),
        ],
    )

    def handler(client):
        params = module.params
        path = build_path(params['collection'], params['value'], params['subcategories'])
        items = client.get(path)
        module.exit_json(changed=False, items=items or [])

    run_module(module, handler)


if __name__ == '__main__':
    main()
