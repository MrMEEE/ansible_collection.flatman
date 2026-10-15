# -*- coding: utf-8 -*-
# Copyright (c) 2026 MrMEEE
# MIT License

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.mrmeee.flatman.plugins.module_utils.flatman import FlatManagerError


# Operations are explicit: several workflow viewsets expose methods that return 405.
RESOURCE_OPERATIONS = {
    'flatpak-remotes': 'create update delete',
    'organisations': 'create update delete',
    'bst-sources': 'create update delete',
    'bst-promotions': '',
    'clients': 'delete',
    'permission-groups': 'create update delete',
    'ldap-sources': 'create update delete',
    'ldap-group-mappings': 'create update delete',
    'rpm-packages': 'create update delete',
    'rpm-builds': 'delete',
    'rpm-distributions': 'create update delete',
    'rpm-repositories': '',
    'satellite-servers': 'create delete',
    'satellite-repositories': 'create delete',
    'rpm-destinations': 'delete',
    'rpm-signing-keys': '',
    'user-roles': 'create update delete',
    'permission-grants': 'create update delete',
    'group-permissions': 'create update delete',
    'site-config': 'update',
    'external-refs': 'create update delete',
}

# Tuple values: (requires detail ID, read-only, required body identifiers).
ACTION_ROUTES = {
    'gpg-keys': {'renew': (True, False, ('key_lifetime',))},
    'ldap-sources': {
        'test-connection': (False, True, ('hostname',)),
        'test-search': (False, True, ('hostname', 'base_dn', 'search_username')),
    },
    'flatpak-remotes': {'toggle': (True, False, ())},
    'external-refs': {
        'bulk-import': (False, False, ('repository_id', 'remote_id', 'refs')),
        'unpublish': (True, False, ()),
    },
    'packages': {
        'retry': (True, False, ()),
        'republish': (True, False, ()),
        'check-upstream': (True, True, ()),
        'check-available': (True, True, ()),
    },
    'repositories': {'update-metadata': (True, False, ())},
    'builds': {
        'unpublish': (True, False, ()),
        'recommit': (True, False, ()),
        'delete': (True, False, ()),
        'cancel': (True, False, ()),
        'bst-promote': (True, False, ('target_repo_id',)),
    },
    'promotions': {'retry': (True, False, ()), 'delete': (True, False, ())},
    'external-ref-promotions': {'retry': (True, False, ()), 'delete': (True, False, ())},
    'bst-promotions': {'retry': (True, False, ()), 'delete': (True, False, ())},
    'bst-sources': {
        'build': (True, False, ()),
        'retry': (True, False, ()),
        'force-rebuild': (True, False, ()),
        'integrity-check': (False, True, ()),
    },
    'clients': {'assign-organisations': (True, False, ()), 'lockdown': (True, False, ())},
    'permission-groups': {'memberships': (True, False, ())},
    'site-config': dict((name, (False, False, ())) for name in (
        'cleanup', 'sync-repositories', 'check-external-updates', 'scan-available-versions',
        'scan-upstream-versions', 'repair-permissions', 'scan-orphaned-refs',
        'prune-orphaned-ref', 'prune-orphaned-refs',
    )),
    'rpm-packages': {
        'scan-spec-files': (False, True, ('url',)),
        'scan-branches': (False, True, ('url',)),
        'build': (True, False, ()),
        'build-with-number': (True, False, ()),
        'check-upstream': (True, True, ()),
        'check-available': (True, True, ()),
        'toggle-repository': (True, False, ('repo_pk',)),
        'signing-key': (True, False, ('dist_pk',)),
        'assign-destination': (True, False, ()),
    },
    'rpm-builds': {
        'retry': (True, False, ()), 'repush': (True, False, ()),
        'cancel': (True, False, ()), 'logs': (True, True, ()),
    },
    'rpm-distributions': {
        'sync': (False, False, ()), 'toggle': (True, False, ()), 'sync-repos': (True, False, ()),
    },
    'rpm-repositories': {'toggle': (True, False, ())},
    'satellite-servers': dict((name, (False, True, ())) for name in (
        'fetch-organisations', 'fetch-products', 'fetch-repositories',
    )),
}

INFO_RESOURCES = sorted(set(RESOURCE_OPERATIONS) | set(ACTION_ROUTES) | {'workflows'})
ACTIONS = sorted(set(action for actions in ACTION_ROUTES.values() for action in actions))


def workflow_payload(module):
    data = dict(module.params['data'])
    secrets = module.params['secret_data']
    if set(data).intersection(secrets):
        module.fail_json(msg='data and secret_data must not contain the same field')
    data.update(secrets)

    def protect(value, sensitive=False):
        if isinstance(value, dict):
            for key, item in value.items():
                secret = sensitive or any(part in key.lower() for part in (
                    'password', 'passphrase', 'token', 'secret', 'private_key', 'api_key', 'admin_pass',
                ))
                protect(item, secret)
        elif isinstance(value, list):
            for item in value:
                protect(item, sensitive)
        elif sensitive and value is not None and not isinstance(value, bool):
            module.no_log_values.add(str(value))

    protect(data)
    return data


def resource_path(resource):
    return '/api/%s/' % resource


def check_response(response):
    """Web adapters may report workflow errors in a successful HTTP response."""
    if not isinstance(response, dict):
        raise FlatManagerError('Expected a JSON object from workflow endpoint', body=response)
    if (
        response.get('errors') or response.get('error') or response.get('ok') is False
        or response.get('status') in ('error', 'failed')
    ):
        raise FlatManagerError('Workflow reported an error', body=response)
    return response


def field_changes(client, current, desired):
    changes = client.diff_fields(current, desired)
    for key, value in desired.items():
        if value is None and (key not in current or current[key] is not None):
            changes[key] = None
    return changes


def matches(client, record, identity):
    return all(key in record for key in identity) and not field_changes(client, record, identity)


def find_resource(client, path, identity):
    candidates = [
        item for item in client.get_all(path)
        if matches(client, item, identity)
    ]
    if len(candidates) > 1:
        raise FlatManagerError('Resource identity matches multiple records; use id or a more specific match')
    return candidates[0] if candidates else None
