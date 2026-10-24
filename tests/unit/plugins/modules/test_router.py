# Copyright (c) 2026 MrMEEE
# MIT License

import json
import unittest
from unittest.mock import MagicMock, patch

from ansible.module_utils import basic
from ansible_collections.mrmeee.flatman.plugins.module_utils import flatman, router
from ansible_collections.mrmeee.flatman.plugins.modules import (
    flatman_quality_moderation,
    flatman_resource,
    flatman_resource_info,
    flatman_workflow_action,
)


class ModuleResult(Exception):
    def __init__(self, failed, result):
        self.failed = failed
        self.result = result


def exit_json(self, **kwargs):
    raise ModuleResult(False, kwargs)


def fail_json(self, **kwargs):
    raise ModuleResult(True, kwargs)


def unchanged_display_names(value, resource=None):
    return value


class RouterTests(unittest.TestCase):
    def setUp(self):
        self.client = MagicMock()
        self.client.diff_fields.side_effect = flatman.FlatManagerClient.diff_fields
        self.client.add_display_names.side_effect = unchanged_display_names
        self.client.get_all.return_value = []

    def run_module(self, module, params, failed=False, check=False):
        args = dict(url='https://flatman.example.com', **params)
        args['_ansible_check_mode'] = check
        with patch.object(basic, '_ANSIBLE_ARGS', json.dumps({'ANSIBLE_MODULE_ARGS': args}).encode()), \
                patch.object(basic, '_ANSIBLE_PROFILE', 'legacy', create=True), \
                patch.object(basic.AnsibleModule, 'exit_json', exit_json), \
                patch.object(basic.AnsibleModule, 'fail_json', fail_json), \
                patch.object(flatman, 'FlatManagerClient', return_value=self.client):
            with self.assertRaises(ModuleResult) as caught:
                module.main()
        self.assertEqual(caught.exception.failed, failed, caught.exception.result)
        return caught.exception.result

    def test_every_registered_action_route(self):
        count = 0
        for resource, actions in router.ACTION_ROUTES.items():
            for action, (detail, read_only, required) in actions.items():
                with self.subTest(resource=resource, action=action):
                    self.client.post.reset_mock()
                    self.client.post.return_value = dict(status='ok')
                    data = dict((key, [1] if key == 'refs' else 1) for key in required)
                    params = dict(resource=resource, action=action, data=data)
                    if detail:
                        params['id'] = 12
                    result = self.run_module(flatman_workflow_action, params)
                    path = '/api/%s/%s%s/' % (resource, '12/' if detail else '', action)
                    self.client.post.assert_called_once_with(path, data=data)
                    self.assertEqual(result['changed'], not read_only)
                    count += 1
        self.assertEqual(count, 58)

    def test_all_action_pairs_check_mode_no_requests(self):
        for resource, actions in router.ACTION_ROUTES.items():
            for action, (detail, read_only, required) in actions.items():
                with self.subTest(resource=resource, action=action):
                    params = dict(resource=resource, action=action, data=dict.fromkeys(required, 1))
                    if detail:
                        params['id'] = 1
                    result = self.run_module(flatman_workflow_action, params, check=True)
                    self.assertEqual(result['changed'], not read_only)
        self.client.post.assert_not_called()

    def test_action_validation(self):
        cases = [
            dict(resource='clients', action='cleanup'),
            dict(resource='clients', action='lockdown'),
            dict(resource='clients', action='lockdown', id=-1),
            dict(resource='site-config', action='cleanup', id=1),
            dict(resource='rpm-packages', action='toggle-repository', id=1),
            dict(resource='rpm-packages', action='signing-key', id=1),
            dict(resource='external-refs', action='bulk-import', data=dict(repository_id=1, remote_id=1)),
            dict(resource='gpg-keys', action='renew', id=1),
            dict(resource='ldap-sources', action='test-connection', id=1, data=dict(hostname='ldap.example.com')),
            dict(resource='ldap-sources', action='test-search', data=dict(hostname='ldap.example.com')),
            dict(resource='rpm-packages', action='scan-spec-files', id=1, data=dict(url='https://example.com/repo.git')),
            dict(resource='rpm-packages', action='scan-branches'),
        ]
        for params in cases:
            with self.subTest(params=params):
                self.run_module(flatman_workflow_action, params, failed=True)
        self.client.post.assert_not_called()

    def test_action_http_and_success_shaped_errors(self):
        for body in [
            dict(errors=['invalid']), dict(error='denied'), dict(status='error'),
            dict(ok=False, message='Bind failed'), '<html>Login</html>',
        ]:
            with self.subTest(body=body):
                self.client.post.return_value = body
                result = self.run_module(
                    flatman_workflow_action, dict(resource='site-config', action='cleanup'), failed=True)
                self.assertEqual(result['body'], body)
        self.client.post.side_effect = flatman.FlatManagerError('Forbidden', status=403)
        result = self.run_module(
            flatman_workflow_action, dict(resource='site-config', action='cleanup'), failed=True)
        self.assertEqual(result['status'], 403)

    def test_helper_payloads_and_return_shapes(self):
        cases = [
            ('gpg-keys', 'renew', 7, dict(key_lifetime='0'), dict(status='ok', id=7), True),
            ('ldap-sources', 'test-connection', None,
             dict(hostname='ldap.example.com', port=636, protocol='ldaps', source_pk=4),
             dict(ok=True, message='Connection and bind successful.'), False),
            ('ldap-sources', 'test-search', None,
             dict(hostname='ldap.example.com', base_dn='dc=example,dc=com', search_username='alice'),
             dict(ok=True, dn='uid=alice,dc=example,dc=com', attributes=dict(uid='alice')), False),
            ('rpm-packages', 'scan-spec-files', None,
             dict(url='https://example.com/repo.git', branch='main'), dict(spec_files=['SPECS/app.spec']), False),
            ('rpm-packages', 'scan-branches', None,
             dict(url='https://example.com/repo.git'), dict(branches=['main', 'stable']), False),
        ]
        for resource, action, pk, data, response, changed in cases:
            with self.subTest(action=action):
                self.client.post.reset_mock()
                self.client.post.return_value = response
                params = dict(resource=resource, action=action, data=data)
                if pk is not None:
                    params['id'] = pk
                result = self.run_module(flatman_workflow_action, params)
                self.assertEqual(result['result'], response)
                self.assertEqual(result['changed'], changed)
                self.client.post.assert_called_once_with(
                    '/api/%s/%s%s/' % (resource, '7/' if pk is not None else '', action), data=data)

    def test_ldap_failure_is_explicit_and_credentials_are_forwarded(self):
        self.client.post.return_value = dict(ok=False, message='Service bind failed')
        result = self.run_module(flatman_workflow_action, dict(
            resource='ldap-sources', action='test-connection',
            data=dict(hostname='ldap.example.com', bind_dn='cn=service'),
            secret_data=dict(bind_password='directory-secret')), failed=True)
        self.assertEqual(result['body']['message'], 'Service bind failed')
        self.client.post.assert_called_once_with('/api/ldap-sources/test-connection/', data=dict(
            hostname='ldap.example.com', bind_dn='cn=service', bind_password='directory-secret'))

    def test_every_info_resource_and_exact_match(self):
        record = dict(id=12, name='example', is_active=True)
        self.client.get_all.return_value = [record, dict(record, id=13, is_active=False)]
        self.client.get.return_value = record
        for resource in router.INFO_RESOURCES:
            with self.subTest(resource=resource):
                result = self.run_module(
                    flatman_resource_info, dict(resource=resource, match=dict(is_active=True)), check=True)
                self.assertFalse(result['changed'])
                self.assertEqual(result['resources'], [record])

    def test_info_detail_missing_and_catalogue_validation(self):
        self.client.get_or_none.return_value = None
        result = self.run_module(flatman_resource_info, dict(resource='clients', id=12))
        self.assertEqual(result['resources'], [])
        self.client.get_or_none.assert_called_once_with('/api/clients/12/')
        self.run_module(flatman_resource_info, dict(resource='workflows', id=1), failed=True)

    def test_output_names_keep_numeric_ids_and_enrich_promotion_records(self):
        client = object.__new__(flatman.FlatManagerClient)
        client._display_cache = {}
        records = {
            '/api/builds/19/': {
                'id': 19, 'build_number': 7, 'status': 'published',
                'package_name': 'Example App', 'package_package_id': 'org.example.App',
                'repository_name': 'testing',
            },
            '/api/packages/3/': {
                'id': 3, 'package_id': 'org.example.App', 'package_name': 'Example App',
            },
            '/api/repositories/10/': {'id': 10, 'name': 'stable'},
        }

        def get_record(path):
            return records.get(path)

        client.get_or_none = get_record
        promotion = {
            'id': 4, 'build': 19, 'package': 3, 'target_repo': 10, 'status': 'promoted',
        }

        result = client.add_display_names({'changed': False, 'promotions': [promotion]})
        enriched = result['promotions'][0]
        self.assertEqual((enriched['build'], enriched['package'], enriched['target_repo']), (19, 3, 10))
        self.assertEqual(enriched['build_name'], 'Build 7 - Example App')
        self.assertEqual(enriched['package_name'], 'Example App')
        self.assertEqual(enriched['package_identifier'], 'org.example.App')
        self.assertEqual(enriched['target_repo_name'], 'stable')

    def test_external_version_gets_parent_external_name(self):
        client = object.__new__(flatman.FlatManagerClient)
        client._display_cache = {}

        def get_externals(path, params=None):
            return [{
                'id': 2, 'display_name': 'Example Runtime',
                'versions': [{'id': 8, 'ref': 'runtime/org.example.Platform/x86_64/stable',
                              'commit_hash': 'abcdef0123456789'}],
            }]

        def get_external(path, params=None):
            return {'id': 2, 'display_name': 'Example Runtime'} if path == '/api/external-refs/2/' else None

        client.get_all = get_externals
        client.get_or_none = get_external
        result = client.add_display_names({
            'id': 5, 'external_ref': 2, 'external_ref_version': 8, 'target_repo': 10,
        })
        self.assertEqual(result['external_ref_name'], 'Example Runtime')
        self.assertEqual(result['external_ref_version_name'], 'runtime/org.example.Platform/x86_64/stable')
        self.assertEqual(result['external_ref_version_commit_hash'], 'abcdef0123456789')

    def test_related_name_option_is_shared_and_enabled_by_default(self):
        self.assertIn('include_names', flatman.flatman_argument_spec())
        self.assertTrue(flatman.flatman_argument_spec()['include_names']['default'])

    def test_display_names_add_friendly_labels_without_replacing_ids(self):
        client = object.__new__(flatman.FlatManagerClient)
        client._display_cache = {}
        records = {
            '/api/builds/19/': {
                'id': 19, 'build_number': 7, 'status': 'published',
                'package_name': 'Example App', 'package_package_id': 'org.example.App',
                'repository_name': 'testing',
            },
            '/api/packages/3/': {
                'id': 3, 'package_id': 'org.example.App', 'package_name': 'Example App',
            },
            '/api/repositories/10/': {'id': 10, 'name': 'stable'},
        }

        def get_record(path):
            return records.get(path)

        client.get_or_none = get_record

        result = client.add_display_names({
            'promotions': [{'build': 19, 'package': 3, 'target_repo': 10, 'status': 'promoted'}],
        })['promotions'][0]

        self.assertEqual((result['build'], result['package'], result['target_repo']), (19, 3, 10))
        self.assertEqual(result['build_name'], 'Build 7 - Example App')
        self.assertEqual(result['package_name'], 'Example App')
        self.assertEqual(result['package_identifier'], 'org.example.App')
        self.assertEqual(result['target_repo_name'], 'stable')

    def test_external_version_output_names_external_and_commit(self):
        client = object.__new__(flatman.FlatManagerClient)
        client._display_cache = {}
        client.get_all = lambda path, params=None: [{
            'id': 2, 'display_name': 'Example Runtime',
            'versions': [{'id': 8, 'ref': 'runtime/org.example.Platform/x86_64/stable',
                          'commit_hash': 'abcdef0123456789'}],
        }]

        result = client.add_display_names({
            'external_ref': 2, 'external_ref_version': 8, 'target_repo': {'id': 10, 'name': 'stable'},
        })

        self.assertEqual(result['external_ref_name'], 'Example Runtime')
        self.assertEqual(result['external_ref_version_name'], 'runtime/org.example.Platform/x86_64/stable')
        self.assertEqual(result['external_ref_version_commit_hash'], 'abcdef0123456789')
        self.assertEqual(result['target_repo'], {'id': 10, 'name': 'stable', 'display_name': 'stable'})

    def test_every_supported_resource_create_and_check(self):
        for resource, operations in router.RESOURCE_OPERATIONS.items():
            if 'create' not in operations:
                continue
            with self.subTest(resource=resource):
                self.client.post.reset_mock()
                self.client.post.return_value = dict(status='ok', id=12)
                self.client.get.return_value = dict(id=12, name='example')
                params = dict(resource=resource, match=dict(name='example'))
                result = self.run_module(flatman_resource, params)
                self.assertTrue(result['changed'])
                self.assertEqual(result['resource']['id'], 12)
                self.client.post.assert_called_once_with(
                    '/api/%s/' % resource, data=dict(name='example'), expect=(200, 201, 202))
                self.client.post.reset_mock()
                result = self.run_module(flatman_resource, params, check=True)
                self.assertEqual(result['resource'], dict(name='example'))
                self.client.post.assert_not_called()

    def test_repeated_convergence_and_order_insensitive_relations(self):
        self.client.get_all.return_value = [dict(id=12, name='example', organisations=[2, 1])]
        result = self.run_module(flatman_resource, dict(
            resource='bst-sources', match=dict(name='example'), data=dict(organisations=[1, 2])))
        self.assertFalse(result['changed'])
        self.client.patch.assert_not_called()

    def test_every_supported_resource_update(self):
        for resource, operations in router.RESOURCE_OPERATIONS.items():
            if 'update' not in operations:
                continue
            with self.subTest(resource=resource):
                self.client.patch.reset_mock()
                self.client.get_or_none.return_value = dict(id=12, name='before')
                self.client.patch.return_value = dict(status='ok')
                self.client.get.return_value = dict(id=12, name='after')
                result = self.run_module(
                    flatman_resource, dict(resource=resource, id=12, data=dict(name='after')))
                self.assertTrue(result['changed'])
                self.client.patch.assert_called_once_with('/api/%s/12/' % resource, data=dict(name='after'))

    def test_every_supported_resource_delete(self):
        for resource, operations in router.RESOURCE_OPERATIONS.items():
            if 'delete' not in operations:
                continue
            with self.subTest(resource=resource):
                self.client.delete.reset_mock()
                self.client.delete.return_value = dict(status='ok')
                self.client.get_or_none.return_value = dict(id=12)
                result = self.run_module(flatman_resource, dict(resource=resource, id=12, state='absent'))
                self.assertTrue(result['changed'])
                self.assertEqual(result['resource'], {})
                self.client.delete.assert_called_once_with('/api/%s/12/' % resource)
                self.client.get_or_none.return_value = None
                result = self.run_module(flatman_resource, dict(resource=resource, id=12, state='absent'))
                self.assertFalse(result['changed'])

    def test_update_and_delete_check_mode(self):
        self.client.get_or_none.return_value = dict(id=12, name='before')
        for state in ['present', 'absent']:
            with self.subTest(state=state):
                result = self.run_module(flatman_resource, dict(
                    resource='organisations', id=12, state=state, data=dict(name='after')), check=True)
                self.assertTrue(result['changed'])
        self.client.patch.assert_not_called()
        self.client.delete.assert_not_called()

    def test_ambiguous_missing_and_conflicting_identity(self):
        params = dict(resource='organisations', match=dict(name='example'))
        self.client.get_all.return_value = [dict(id=1, name='example'), dict(id=2, name='example')]
        self.run_module(flatman_resource, params, failed=True)
        self.client.get_all.return_value = []
        self.run_module(flatman_resource, dict(params, data=dict(name='different')), failed=True)
        self.run_module(flatman_resource, dict(resource='organisations', match={}), failed=True)
        self.client.get_or_none.return_value = None
        self.run_module(flatman_resource, dict(resource='organisations', id=999), failed=True)
        self.client.post.assert_not_called()

    def test_null_scope_identity_does_not_match_scoped_grant(self):
        self.client.get_all.return_value = [
            dict(id=1, user=2, role='view', organisation=3),
            dict(id=2, user=2, role='view', organisation=None),
        ]
        result = self.run_module(flatman_resource, dict(
            resource='user-roles', match=dict(user=2, role='view', organisation=None)))
        self.assertFalse(result['changed'])
        self.assertEqual(result['resource']['id'], 2)
        self.client.post.assert_not_called()

    def test_explicit_null_clears_nullable_field(self):
        self.client.get_or_none.return_value = dict(id=12, organisation=3)
        self.client.patch.return_value = dict(id=12)
        self.client.get.return_value = dict(id=12, organisation=None)
        result = self.run_module(flatman_resource, dict(
            resource='user-roles', id=12, data=dict(organisation=None)))
        self.assertTrue(result['changed'])
        self.client.patch.assert_called_once_with('/api/user-roles/12/', data=dict(organisation=None))

    def test_unsupported_mutations(self):
        self.client.get_or_none.return_value = dict(id=12, hostname='before')
        self.run_module(flatman_resource, dict(
            resource='clients', id=12, data=dict(hostname='after')), failed=True)
        self.run_module(flatman_resource, dict(
            resource='site-config', id=12, state='absent'), failed=True)
        self.run_module(flatman_resource, dict(
            resource='clients', match=dict(hostname='example')), failed=True)
        self.client.post.assert_not_called()
        self.client.patch.assert_not_called()
        self.client.delete.assert_not_called()

    def test_mutation_acknowledgement_is_reread_and_verified(self):
        self.client.get_or_none.return_value = dict(id=12, name='before')
        self.client.patch.return_value = dict(status='ok')
        self.client.get.return_value = dict(id=12, name='before')
        result = self.run_module(flatman_resource, dict(
            resource='organisations', id=12, data=dict(name='after')), failed=True)
        self.assertIn('not applied', result['msg'])

    def test_create_without_response_id_uses_exact_identity(self):
        self.client.get_all.side_effect = [[], [dict(id=12, name='example')]]
        self.client.post.return_value = dict(status='ok')
        result = self.run_module(flatman_resource, dict(resource='organisations', match=dict(name='example')))
        self.assertEqual(result['resource']['id'], 12)

    def test_write_only_field_is_not_silently_skipped(self):
        self.client.get_or_none.return_value = dict(id=12, name='directory')
        self.client.patch.return_value = dict(status='ok')
        self.client.get.return_value = dict(id=12, name='directory')
        result = self.run_module(flatman_resource, dict(
            resource='ldap-sources', id=12, data=dict(bind_password='secret')), check=True)
        self.assertTrue(result['changed'])

    def test_secret_payloads_are_merged_without_redacting_public_ids(self):
        module = MagicMock()
        module.params = dict(
            data=dict(repository=2, nested=dict(password='nested-secret')),
            secret_data=dict(bind_password='directory-secret'))
        module.no_log_values = {'directory-secret'}
        payload = router.workflow_payload(module)
        self.assertEqual(payload['repository'], 2)
        self.assertEqual(payload['bind_password'], 'directory-secret')
        self.assertIn('nested-secret', module.no_log_values)
        self.assertNotIn('2', module.no_log_values)

    def test_conflicting_secret_payload_is_rejected(self):
        self.run_module(flatman_resource, dict(
            resource='ldap-sources', id=12,
            data=dict(bind_password='one'), secret_data=dict(bind_password='two')), failed=True)
        self.client.patch.assert_not_called()

    def test_bulk_quality_rejection(self):
        params = dict(app_id='org.example.App', action='reject-pending-reviews')
        result = self.run_module(flatman_quality_moderation, params, check=True)
        self.assertTrue(result['changed'])
        self.client.delete.assert_not_called()
        result = self.run_module(flatman_quality_moderation, params)
        self.assertTrue(result['changed'])
        self.client.delete.assert_called_once_with('/api/v2/quality-moderation/org.example.App/request-review')
