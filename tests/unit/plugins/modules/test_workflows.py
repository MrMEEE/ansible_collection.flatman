# Copyright (c) 2026 MrMEEE
# MIT License

import json
import unittest
from unittest.mock import MagicMock, patch

from ansible.module_utils import basic
from ansible_collections.mrmeee.flatman.plugins.module_utils import flatman
from ansible_collections.mrmeee.flatman.plugins.modules import (
    flatman_external_ref_action,
    flatman_external_ref_info,
    flatman_promotion,
    flatman_promotion_info,
)


class ModuleResult(Exception):
    def __init__(self, failed, result):
        self.failed = failed
        self.result = result


def exit_json(self, **kwargs):
    raise ModuleResult(False, kwargs)


def fail_json(self, **kwargs):
    raise ModuleResult(True, kwargs)


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.client = MagicMock()
        self.external = dict(
            id=12, status='published', remote=1,
            versions=[
                dict(id=7, status='published', pulled_at='2026-10-01T00:00:00Z'),
                dict(id=8, status='published', pulled_at='2026-10-02T00:00:00Z'),
                dict(id=9, status='failed', pulled_at='2026-10-03T00:00:00Z'),
            ],
        )
        self.client.get.return_value = self.external
        self.client.get_all.return_value = []

    def run_module(self, module, params, failed=False, check=False):
        args = dict(url='https://flatman.example.com', api_token='test-token', **params)
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

    def test_external_pull_waits_through_publication(self):
        self.client.post.return_value = dict(id=12, status='pending')
        self.client.wait_for.return_value = self.external
        result = self.run_module(flatman_external_ref_action, dict(id=12, action='pull', wait=True))
        self.assertTrue(result['changed'])
        self.assertEqual(result['external_ref']['status'], 'published')
        self.client.post.assert_called_once_with('/api/external-refs/12/pull/', expect=(202,))
        self.client.wait_for.assert_called_once_with(
            '/api/external-refs/12/', 'status', ['published'], fail_values=['failed', 'cancelled'],
            timeout=600, interval=5,
        )

    def test_external_publish_requires_pulled_and_uses_publish_route(self):
        self.external['status'] = 'pulled'
        result = self.run_module(flatman_external_ref_action, dict(id=12, action='publish'))
        self.assertTrue(result['changed'])
        self.client.post.assert_called_once_with('/api/external-refs/12/publish/', expect=(202,))
        self.client.wait_for.assert_not_called()

    def test_external_publish_skips_published(self):
        result = self.run_module(flatman_external_ref_action, dict(id=12, action='publish', wait=True))
        self.assertFalse(result['changed'])
        self.assertEqual(result['result'], {})
        self.client.post.assert_not_called()
        self.client.wait_for.assert_not_called()

    def test_external_invalid_states_and_missing_remote(self):
        for action, state, remote in [
            ('pull', 'pulling', 1), ('pull', 'publishing', 1),
            ('pull', 'published', None), ('publish', 'pending', 1),
            ('publish', 'failed', 1), ('publish', 'publishing', 1),
        ]:
            with self.subTest(action=action, state=state, remote=remote):
                self.external.update(status=state, remote=remote)
                self.run_module(flatman_external_ref_action, dict(id=12, action=action), failed=True)
        self.client.post.assert_not_called()

    def test_external_check_mode_never_dispatches_or_polls(self):
        for action, state in [('pull', 'published'), ('publish', 'pulled')]:
            with self.subTest(action=action):
                self.external['status'] = state
                result = self.run_module(
                    flatman_external_ref_action, dict(id=12, action=action, wait=True), check=True)
                self.assertTrue(result['changed'])
                self.assertEqual(result['result'], {})
        self.client.post.assert_not_called()
        self.client.wait_for.assert_not_called()

    def test_positive_wait_settings(self):
        for module, params in [
            (flatman_external_ref_action, dict(id=12, action='pull')),
            (flatman_promotion, dict(build_id=48, target_repo_id=3)),
        ]:
            for key in ['wait_timeout', 'wait_interval']:
                for value in [0, -1]:
                    with self.subTest(module=module.__name__, key=key, value=value):
                        result = self.run_module(module, dict(params, **{key: value}), failed=True)
                        self.assertIn('must be positive', result['msg'])

    def test_external_info_filters_and_return_shape(self):
        self.client.resolve.return_value = dict(id=3)
        self.client.get_all.return_value = [self.external]
        result = self.run_module(flatman_external_ref_info, dict(
            repository='testing', remote_id=1, ref='app/org.example.App/x86_64/stable',
            status='published', search='App',
        ))
        self.assertFalse(result['changed'])
        self.assertEqual(result['external_refs'], [self.external])
        self.client.get_all.assert_called_once_with('/api/external-refs/', params=dict(
            repository=3, remote=1, ref='app/org.example.App/x86_64/stable',
            status='published', search='App',
        ))

    def test_info_detail_missing_and_check_mode(self):
        for module, params, path, key in [
            (flatman_external_ref_info, dict(id=12), '/api/external-refs/12/', 'external_refs'),
            (flatman_promotion_info, dict(id=10), '/api/promotions/10/', 'promotions'),
            (flatman_promotion_info, dict(kind='external', id=10),
             '/api/external-ref-promotions/10/', 'promotions'),
        ]:
            for found in [None, dict(id=10)]:
                with self.subTest(module=module.__name__, params=params, found=found):
                    self.client.get_or_none.return_value = found
                    result = self.run_module(module, params, check=True)
                    self.assertEqual(result[key], [found] if found else [])
                    self.assertFalse(result['changed'])
                    self.client.get_or_none.assert_called_with(path)

    def test_build_promotion_dispatch_and_wait(self):
        promotion = dict(id=10, build=48, target_repo=3, status='pending')
        self.client.get.side_effect = [dict(id=48, status='published'), promotion]
        self.client.resolve.return_value = dict(id=3)
        self.client.post.return_value = dict(promotion_id=10, status='pending')
        self.client.wait_for.return_value = dict(promotion, status='promoted')
        result = self.run_module(flatman_promotion, dict(build_id=48, repository='stable', wait=True))
        self.assertTrue(result['changed'])
        self.assertEqual(result['promotion']['status'], 'promoted')
        self.client.get_all.assert_called_once_with('/api/promotions/', params=dict(target_repo=3, build=48))
        self.client.post.assert_called_once_with(
            '/api/builds/48/promote/', data=dict(target_repo_id=3), expect=(202,))
        self.client.wait_for.assert_called_once_with(
            '/api/promotions/10/', 'status', ['promoted'], fail_values=['failed'], timeout=600, interval=5)

    def test_build_promotion_reuses_active_and_completed(self):
        self.client.get.return_value = dict(id=48, status='published')
        for state in ['pending', 'promoting', 'promoted']:
            with self.subTest(state=state):
                promotion = dict(id=10, build=48, target_repo=3, status=state)
                self.client.get_all.return_value = [promotion]
                self.client.wait_for.reset_mock()
                self.client.wait_for.return_value = dict(promotion, status='promoted')
                result = self.run_module(flatman_promotion, dict(build_id=48, target_repo_id=3, wait=True))
                self.assertFalse(result['changed'])
                self.assertEqual(result['promotion']['status'], 'promoted')
                self.assertEqual(self.client.wait_for.call_count, 0 if state == 'promoted' else 1)
        self.client.post.assert_not_called()

    def test_failed_build_promotion_is_retried(self):
        promotion = dict(id=10, build=48, target_repo=3, status='failed')
        self.client.get_all.return_value = [promotion]
        self.client.get.side_effect = [
            dict(id=48, status='published'), dict(promotion, status='pending'),
        ]
        self.client.post.return_value = dict(promotion_id=10)
        result = self.run_module(flatman_promotion, dict(build_id=48, target_repo_id=3))
        self.assertTrue(result['changed'])
        self.client.post.assert_called_once()

    def test_external_promotion_latest_and_explicit_version(self):
        for version_id in [None, 7]:
            with self.subTest(version_id=version_id):
                expected = version_id or 8
                promotion = dict(
                    id=10, external_ref=12, external_ref_version=expected, target_repo=3, status='pending')
                self.client.get.side_effect = [self.external, promotion]
                self.client.post.reset_mock()
                self.client.post.return_value = dict(promotion_id=10)
                params = dict(external_ref_id=12, target_repo_id=3)
                if version_id is not None:
                    params['external_ref_version_id'] = version_id
                result = self.run_module(flatman_promotion, params)
                self.assertTrue(result['changed'])
                self.client.post.assert_called_once_with(
                    '/api/external-refs/12/promote/',
                    data=dict(target_repo_id=3, external_ref_version_id=expected), expect=(202,))
                self.client.get_all.assert_called_with('/api/external-ref-promotions/', params=dict(
                    target_repo=3, external_ref=12, external_ref_version=expected))

    def test_external_promotion_is_version_scoped(self):
        older = dict(id=10, external_ref=12, external_ref_version=7, target_repo=3, status='promoted')
        self.client.get_all.return_value = [older]
        self.client.post.return_value = dict(promotion_id=11)
        self.client.get.side_effect = [self.external, dict(older, id=11, external_ref_version=8, status='pending')]
        result = self.run_module(flatman_promotion, dict(external_ref_id=12, target_repo_id=3))
        self.assertTrue(result['changed'])
        self.client.post.assert_called_once()

    def test_external_latest_version_orders_timestamps_not_strings(self):
        self.external['versions'] = [
            dict(id=7, status='published', pulled_at='2026-10-01T01:00:00+01:00'),
            dict(id=8, status='published', pulled_at='2026-10-01T00:00:00.100000Z'),
            dict(id=9, status='published', pulled_at='2026-10-01T00:00:00.100000Z'),
        ]
        result = self.run_module(
            flatman_promotion, dict(external_ref_id=12, target_repo_id=3), check=True)
        self.assertEqual(result['promotion']['external_ref_version'], 9)

    def test_failed_external_promotion_does_not_hide_completed_retry(self):
        common = dict(external_ref=12, external_ref_version=8, target_repo=3)
        self.client.get_all.return_value = [
            dict(common, id=10, status='failed'), dict(common, id=11, status='promoted')]
        result = self.run_module(flatman_promotion, dict(external_ref_id=12, target_repo_id=3))
        self.assertFalse(result['changed'])
        self.assertEqual(result['promotion']['id'], 11)
        self.client.post.assert_not_called()

    def test_external_promotion_rejects_unpublished_or_unrelated_version(self):
        for version_id in [9, 999]:
            with self.subTest(version_id=version_id):
                self.run_module(flatman_promotion, dict(
                    external_ref_id=12, external_ref_version_id=version_id, target_repo_id=3), failed=True)
        self.external['versions'] = []
        self.run_module(flatman_promotion, dict(external_ref_id=12, target_repo_id=3), failed=True)
        self.client.post.assert_not_called()

    def test_build_promotion_requires_published(self):
        self.client.get.return_value = dict(status='built')
        self.run_module(flatman_promotion, dict(build_id=48, target_repo_id=3), failed=True)
        self.client.post.assert_not_called()

    def test_promotion_check_mode_new_and_existing(self):
        for source in [dict(build_id=48), dict(external_ref_id=12)]:
            with self.subTest(source=source):
                self.client.get.return_value = (
                    dict(status='published') if 'build_id' in source else self.external)
                self.client.get_all.return_value = []
                result = self.run_module(
                    flatman_promotion, dict(source, target_repo_id=3, wait=True), check=True)
                self.assertTrue(result['changed'])
                self.assertEqual(result['promotion']['status'], 'pending')
                self.assertNotIn('id', result['promotion'])
                promotion = dict(result['promotion'], id=10, status='promoting')
                self.client.get_all.return_value = [promotion]
                result = self.run_module(
                    flatman_promotion, dict(source, target_repo_id=3, wait=True), check=True)
                self.assertFalse(result['changed'])
        self.client.post.assert_not_called()
        self.client.wait_for.assert_not_called()

    def test_promotion_argument_constraints(self):
        for params in [
            dict(target_repo_id=3),
            dict(build_id=48),
            dict(build_id=48, external_ref_id=12, target_repo_id=3),
            dict(build_id=48, repository='stable', target_repo_id=3),
            dict(build_id=48, external_ref_version_id=7, target_repo_id=3),
        ]:
            with self.subTest(params=params):
                self.run_module(flatman_promotion, params, failed=True)
        self.client.post.assert_not_called()

    def test_promotion_info_filters(self):
        self.client.resolve.return_value = dict(id=3)
        for kind, supplied, expected in [
            ('build', dict(build_id=48), dict(build=48)),
            ('external', dict(external_ref_id=12, external_ref_version_id=8),
             dict(external_ref=12, external_ref_version=8)),
        ]:
            with self.subTest(kind=kind):
                result = self.run_module(flatman_promotion_info, dict(
                    supplied, kind=kind, repository='stable', status='failed'))
                self.assertFalse(result['changed'])
                path = '/api/promotions/' if kind == 'build' else '/api/external-ref-promotions/'
                self.client.get_all.assert_called_with(path, params=dict(expected, target_repo=3, status='failed'))

    def test_promotion_info_rejects_wrong_kind_filters(self):
        for params in [
            dict(kind='build', external_ref_id=12),
            dict(kind='build', external_ref_version_id=7),
            dict(kind='external', build_id=48),
        ]:
            with self.subTest(params=params):
                self.run_module(flatman_promotion_info, params, failed=True)

    def test_http_and_polling_errors_are_reported(self):
        for status in [401, 403, 404, 400]:
            with self.subTest(status=status):
                self.client.get.side_effect = flatman.FlatManagerError('request failed', status=status)
                result = self.run_module(
                    flatman_external_ref_action, dict(id=12, action='pull'), failed=True)
                self.assertEqual(result['status'], status)
        self.client.get.side_effect = None
        self.client.wait_for.side_effect = flatman.FlatManagerError(
            'publication failed', body=dict(status='failed', error_message='OSTree error'))
        result = self.run_module(
            flatman_external_ref_action, dict(id=12, action='pull', wait=True), failed=True)
        self.assertEqual(result['body']['error_message'], 'OSTree error')


class ClientWorkflowTests(unittest.TestCase):
    def setUp(self):
        module = MagicMock()
        module.params = dict(url='https://flatman.example.com', api_token='test-token')
        self.client = flatman.FlatManagerClient(module)

    def test_paginated_workflow_records(self):
        self.client.get = MagicMock(side_effect=[
            dict(results=[dict(id=1)], next='https://flatman.example.com/api/promotions/?page=2'),
            dict(results=[dict(id=2)], next=None),
        ])
        self.assertEqual(self.client.get_all('/api/promotions/'), [dict(id=1), dict(id=2)])
        self.client.get.assert_any_call('https://flatman.example.com/api/promotions/?page=2')

    def test_wait_completion_failure_and_timeout(self):
        with patch.object(flatman.time, 'sleep'):
            self.client.get = MagicMock(side_effect=[dict(status='promoting'), dict(status='promoted')])
            self.assertEqual(self.client.wait_for('/api/promotions/10/', 'status', ['promoted'])['status'], 'promoted')
            self.client.get = MagicMock(return_value=dict(status='failed', error_message='copy failed'))
            with self.assertRaisesRegex(flatman.FlatManagerError, 'copy failed'):
                self.client.wait_for('/api/promotions/10/', 'status', ['promoted'], fail_values=['failed'])
            self.client.get = MagicMock(return_value=dict(status='pending'))
            with patch.object(flatman.time, 'time', side_effect=[0, 0, 2]):
                with self.assertRaisesRegex(flatman.FlatManagerError, 'Timed out'):
                    self.client.wait_for('/api/promotions/10/', 'status', ['promoted'], timeout=1)
