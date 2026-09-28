# -*- coding: utf-8 -*-
# Copyright (c) 2026 MrMEEE
# MIT License

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json
import time

from ansible.module_utils.basic import env_fallback
from ansible.module_utils.six.moves.urllib.error import HTTPError, URLError
from ansible.module_utils.six.moves.urllib.parse import urlencode, urlparse
from ansible.module_utils.urls import open_url


def flatman_argument_spec():
    """Connection arguments shared by every flatman_* module."""
    return dict(
        url=dict(
            type='str',
            required=True,
            fallback=(env_fallback, ['FLATMAN_URL']),
        ),
        api_token=dict(
            type='str',
            no_log=True,
            fallback=(env_fallback, ['FLATMAN_API_TOKEN']),
        ),
        validate_certs=dict(
            type='bool',
            default=True,
            fallback=(env_fallback, ['FLATMAN_VALIDATE_CERTS']),
        ),
        timeout=dict(type='int', default=30),
        client_cert=dict(type='path'),
        client_key=dict(type='path', no_log=False),
    )


class FlatManagerError(Exception):
    def __init__(self, msg, status=None, body=None, url=None):
        super(FlatManagerError, self).__init__(msg)
        self.msg = msg
        self.status = status
        self.body = body
        self.url = url


class FlatManagerClient(object):
    """Thin REST client for the flat-manager-django API.

    Only relies on ansible.module_utils.urls so the collection has no
    Python dependencies beyond ansible-core itself.
    """

    def __init__(self, module):
        self.module = module
        params = module.params
        self.base_url = params['url'].rstrip('/')
        self.api_token = params.get('api_token')
        self.validate_certs = params.get('validate_certs', True)
        self.timeout = params.get('timeout', 30)
        self.client_cert = params.get('client_cert')
        self.client_key = params.get('client_key')

        parsed = urlparse(self.base_url)
        if parsed.scheme not in ('http', 'https'):
            module.fail_json(msg="url must start with http:// or https://, got %r" % params['url'])

        self.changed = False
        self.diff = {}

    # ------------------------------------------------------------------
    # low level
    # ------------------------------------------------------------------
    def _full_url(self, path, params=None):
        if path.startswith('http://') or path.startswith('https://'):
            url = path
        else:
            url = '%s/%s' % (self.base_url, path.lstrip('/'))
        if params:
            clean = {}
            for key, value in params.items():
                if value is None:
                    continue
                if isinstance(value, bool):
                    value = 'true' if value else 'false'
                clean[key] = value
            if clean:
                url = '%s%s%s' % (url, '&' if '?' in url else '?', urlencode(clean))
        return url

    def _headers(self):
        headers = {'Accept': 'application/json'}
        if self.api_token:
            headers['Authorization'] = 'Token %s' % self.api_token
        return headers

    def request(self, method, path, data=None, params=None, expect=None):
        """Perform a request and return (status, parsed_body)."""
        url = self._full_url(path, params)
        headers = self._headers()
        body = None
        if data is not None:
            body = json.dumps(data)
            headers['Content-Type'] = 'application/json'

        try:
            response = open_url(
                url,
                method=method.upper(),
                data=body,
                headers=headers,
                validate_certs=self.validate_certs,
                timeout=self.timeout,
                client_cert=self.client_cert,
                client_key=self.client_key,
                follow_redirects='all',
            )
            status = response.getcode()
            raw = response.read()
        except HTTPError as exc:
            status = exc.code
            try:
                raw = exc.read()
            except Exception:
                raw = b''
            parsed = _parse_body(raw)
            if expect is not None and status in expect:
                return status, parsed
            raise FlatManagerError(
                self._error_message(method, url, status, parsed),
                status=status,
                body=parsed,
                url=url,
            )
        except URLError as exc:
            raise FlatManagerError(
                'Could not reach %s: %s' % (url, exc.reason),
                url=url,
            )

        parsed = _parse_body(raw)
        if expect is not None and status not in expect:
            raise FlatManagerError(
                self._error_message(method, url, status, parsed),
                status=status,
                body=parsed,
                url=url,
            )
        return status, parsed

    @staticmethod
    def _error_message(method, url, status, parsed):
        detail = ''
        if isinstance(parsed, dict):
            if 'detail' in parsed:
                detail = str(parsed['detail'])
            else:
                # DRF field validation errors: {"name": ["This field is required."]}
                parts = []
                for key, value in parsed.items():
                    if isinstance(value, list):
                        parts.append('%s: %s' % (key, '; '.join(str(v) for v in value)))
                    else:
                        parts.append('%s: %s' % (key, value))
                detail = ', '.join(parts)
        elif parsed:
            # Non-JSON bodies are usually a Django HTML error page; keep it short.
            detail = ' '.join(str(parsed).split())[:200]

        msg = '%s %s failed with HTTP %s' % (method.upper(), url, status)
        if status == 401:
            msg += ' (authentication failed - check api_token)'
        elif status == 403:
            msg += ' (permission denied)'
        elif status == 404:
            msg += ' (not found)'
        if detail:
            msg += ': %s' % detail
        return msg

    # ------------------------------------------------------------------
    # convenience verbs
    # ------------------------------------------------------------------
    def get(self, path, params=None, expect=(200,)):
        return self.request('GET', path, params=params, expect=expect)[1]

    def post(self, path, data=None, params=None, expect=(200, 201, 202, 204)):
        return self.request('POST', path, data=data, params=params, expect=expect)[1]

    def put(self, path, data=None, params=None, expect=(200, 201, 202)):
        return self.request('PUT', path, data=data, params=params, expect=expect)[1]

    def patch(self, path, data=None, params=None, expect=(200, 202)):
        return self.request('PATCH', path, data=data, params=params, expect=expect)[1]

    def delete(self, path, expect=(200, 202, 204)):
        return self.request('DELETE', path, expect=expect)[1]

    def get_or_none(self, path, params=None):
        status, parsed = self.request('GET', path, params=params, expect=(200, 404))
        if status == 404:
            return None
        return parsed

    # ------------------------------------------------------------------
    # pagination / lookup
    # ------------------------------------------------------------------
    def get_all(self, path, params=None):
        """Return every result from a (possibly paginated) list endpoint."""
        results = []
        page = self.get(path, params=params)
        while True:
            if isinstance(page, list):
                results.extend(page)
                return results
            if not isinstance(page, dict):
                return results
            results.extend(page.get('results') or [])
            next_url = page.get('next')
            if not next_url:
                return results
            page = self.get(next_url)

    def find_one(self, path, key, value, params=None):
        """Find a single object in a list endpoint by an exact field match.

        Server-side filters are used when available; the exact match is always
        re-checked locally because DRF ``search`` filters are fuzzy.
        """
        if value is None:
            return None
        for candidate in self.get_all(path, params=params):
            if str(candidate.get(key)) == str(value):
                return candidate
        return None

    def resolve(self, path, key, value, what, params=None):
        """Like find_one but fails the module when nothing matches."""
        found = self.find_one(path, key, value, params=params)
        if found is None:
            self.module.fail_json(msg='%s %r not found' % (what, value))
        return found

    # ------------------------------------------------------------------
    # idempotency helpers
    # ------------------------------------------------------------------
    @staticmethod
    def diff_fields(current, desired):
        """Return the subset of desired that differs from current.

        Only keys present in ``desired`` are considered, so read-only and
        server-populated fields never cause spurious changes.
        """
        changes = {}
        for key, want in desired.items():
            if want is None:
                continue
            have = current.get(key)
            if isinstance(want, list) and isinstance(have, list):
                if sorted(_stringify(v) for v in want) != sorted(_stringify(v) for v in have):
                    changes[key] = want
            elif _stringify(have) != _stringify(want):
                changes[key] = want
        return changes

    def make_diff(self, before, after):
        if not self.module._diff:
            return {}
        return {'before': before or {}, 'after': after or {}}

    def ensure(self, collection_path, current, desired, state='present'):
        """Create, update or delete an object and return (changed, object, diff).

        ``collection_path`` must end with a slash, matching DRF's router URLs.
        """
        if state == 'absent':
            if current is None:
                return False, None, {}
            if self.module.check_mode:
                return True, current, self.make_diff(current, {})
            self.delete('%s%s/' % (collection_path, current['id']))
            return True, current, self.make_diff(current, {})

        payload = dict((k, v) for k, v in desired.items() if v is not None)

        if current is None:
            if self.module.check_mode:
                return True, payload, self.make_diff({}, payload)
            created = self.post(collection_path, data=payload, expect=(200, 201))
            return True, created, self.make_diff({}, created)

        changes = self.diff_fields(current, payload)
        if not changes:
            return False, current, {}
        if self.module.check_mode:
            preview = dict(current)
            preview.update(changes)
            return True, preview, self.make_diff(current, preview)

        # DRF ModelViewSets accept PATCH for partial updates.
        updated = self.patch('%s%s/' % (collection_path, current['id']), data=changes)
        return True, updated, self.make_diff(current, updated)

    # ------------------------------------------------------------------
    # polling
    # ------------------------------------------------------------------
    def wait_for(self, path, key, done_values, fail_values=None, timeout=600, interval=5):
        """Poll an object until ``key`` reaches one of ``done_values``."""
        fail_values = fail_values or []
        deadline = time.time() + timeout
        obj = {}
        while time.time() < deadline:
            obj = self.get(path)
            value = obj.get(key)
            if value in done_values:
                return obj
            if value in fail_values:
                raise FlatManagerError(
                    "%s reached failure state %r: %s" % (path, value, obj.get('error_message') or ''),
                    body=obj,
                )
            time.sleep(interval)
        raise FlatManagerError(
            'Timed out after %ss waiting for %s to reach one of %s (last value: %r)'
            % (timeout, path, done_values, obj.get(key)),
            body=obj,
        )


def _stringify(value):
    if value is None:
        return ''
    if isinstance(value, bool):
        return 'true' if value else 'false'
    if isinstance(value, dict):
        return json.dumps(value, sort_keys=True)
    return str(value)


def _parse_body(raw):
    if not raw:
        return {}
    if isinstance(raw, bytes):
        raw = raw.decode('utf-8', errors='replace')
    raw = raw.strip()
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except ValueError:
        return raw


def run_module(module, handler):
    """Execute ``handler(client)`` translating FlatManagerError into fail_json."""
    client = FlatManagerClient(module)
    try:
        handler(client)
    except FlatManagerError as exc:
        module.fail_json(msg=exc.msg, status=exc.status, body=exc.body, url=exc.url)
