# -*- coding: utf-8 -*-
# Copyright (c) 2026 MrMEEE
# MIT License

from __future__ import absolute_import, division, print_function

__metaclass__ = type


def wait_argument_spec():
    return dict(
        wait=dict(type='bool', default=False),
        wait_timeout=dict(type='int', default=600),
        wait_interval=dict(type='int', default=5),
    )


def validate_wait(module):
    for key in ('wait_timeout', 'wait_interval'):
        if module.params[key] <= 0:
            module.fail_json(msg='%s must be positive' % key)
