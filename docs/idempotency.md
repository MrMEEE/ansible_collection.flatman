# Idempotency and check mode

## How change modules decide

Change modules follow the same three steps:

1. Look up the existing object by its natural key (for example the repository
   `name`, or the package `package_id`).
2. Compare *only the options you supplied* against the current object. Options
   left unset are ignored, so a module never reverts a field it was not told
   about, and server-populated fields such as `created_at`, `repo_path` or
   `build_count` never cause a false change.
3. Send a `PATCH` with just the differing fields, a `POST` if the object does
   not exist, or a `DELETE` for `state: absent`.

Lists are compared order-insensitively, so reordering `parent_repos` is not a
change.

## Check mode and diff

Every module supports `--check` and `--diff`. In check mode no write request is
ever sent; the module reports what would change and returns the object as it
would look afterwards. With `--diff` you get a before and after view of the
affected fields.

```bash
ansible-playbook playbooks/provision-repository.yml --check --diff
```

## Write-only fields

Some API fields can be written but are not returned in the same shape. The
clearest example is `gpg_key_id` on a repository: you write
`gpg_key_id: 4` but the server returns a nested `gpg_key` object. The modules
normalise this before comparing, so re-running a task does not repeatedly
re-send the same value. The same applies to `repository_id` on packages,
subsets and tokens.

`flatman_app_metadata` goes a step further: the API accepts `developer_name`,
`is_verified` and `is_mobile` but returns them as `developer`, `verified` and
`mobile`, so the module translates between the two before diffing.

## Imperative operations

Some endpoints are actions rather than state, and cannot be made idempotent
because the server has no "already done" concept:

| Module | Behaviour |
|---|---|
| `flatman_package_action` with `start`, `cancel`, `commit`, `publish`, `build_ref` | Always reports `changed` when it runs. Guard with `when:` or run from a dedicated playbook. |
| `flatman_quality_moderation` with `request-review` | Creates a new moderation request each time. |
| `flatman_external_ref_action` with `pull` | Always queues a fresh pull and publication. Use for deliberate upstream refreshes, not recurring convergence. |
| `flatman_workflow_action` | Imperative dispatch; read/report actions return unchanged. Never automatically retries or polls. |
| `flatman_quality_moderation` with `reject-pending-reviews` | Bulk rejection reports changed when dispatched. |

For `flatman_workflow_action`, GPG `renew` recalculates expiry from today and
reports changed whenever dispatched; guard it with an explicit opt-in.
LDAP `test-connection`/`test-search` and RPM `scan-spec-files`/`scan-branches`
report unchanged on success. LDAP `ok: false` responses fail the task.
Check mode sends no action requests, including these diagnostic/discovery calls.

These are idempotent or partially idempotent:

| Module | Behaviour |
|---|---|
| `flatman_gpg_key` with `state: generated` or `imported` | Checks for an existing key of that name first, so re-running does nothing. |
| `flatman_quality_moderation` with `fullscreen` | Reads the current status and skips the write when it is already set. |
| `flatman_moderation_request` | Skips when a pending request already exists for the app. Use `force: true` to submit anyway. |
| `flatman_moderation_review` | Skips when the request already carries the requested status. |
| `flatman_app_pick` | Matches an existing selection by app, kind and date. |
| `flatman_package_action` with `missing_objects` | Read-only, always `changed: false`. |
| `flatman_external_ref_action` with `publish` | Skips an already-published ref; otherwise requires `pulled`. |
| `flatman_promotion` | Reuses pending, promoting or promoted records for the same source, version and target. Queues again after failure. |

`flatman_promotion` pins an External promotion to the supplied version ID or
selects the latest published version by pull time and ID. Old-version records
do not prevent promotion of a newer version. Flatpak promotions take a build
history ID, not a package ID or build attempt number. Failed Flatpak promotions
reuse the server's existing record; failed External promotions create a new one.

With `wait: true`, promotion also waits for an existing in-progress record
without reporting a change. It fails on a failed state or timeout and reports
the server's error details. External pull/publish waits for `published`, not
merely `pulled`. Both modules require positive `wait_timeout` and `wait_interval`.
In check mode they read and validate existing resources without dispatching
or polling. New promotion target eligibility is checked by the server only
when actually dispatching.

The expanded `flatman_resource` module compares only supplied readable fields
and fails on ambiguous identities. Write-only fields (for example LDAP bind
passwords) cause a write each time they are supplied. It rereads after writes
to verify requested readable fields. Unlike older modules, explicit null
values are reconciled for APIs supporting nullable fields. No diff is returned
because payloads may contain credentials. See [expanded-api.md](expanded-api.md).

## Waiting for builds

`flatman_package_action` can poll until a build reaches a terminal state:

```yaml
- mrmeee.flatman.flatman_package_action:
    package_id: org.example.App
    action: start
    wait: true
    wait_timeout: 1800
    wait_interval: 10
```

The module fails if the package enters a failure state, reporting the server's
`error_message`. Without `wait`, the task returns as soon as the Celery job has
been queued.

## Info modules

Info modules never write and always return `changed: false`, so they are safe
in check mode and in `--diff` runs, and safe to use inside `register` loops.
