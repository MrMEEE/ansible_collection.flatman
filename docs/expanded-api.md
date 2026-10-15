# Expanded token API

Collection 1.2.0 adds shared modules for the resources and actions registered by
upstream [workflows.py](https://github.com/MrMEEE/flat-manager-django/blob/4c7f659520f1284cd8e1a04eec751a7954385d56/apps/api/workflows.py).
Install a server version containing `register_workflows`; the earlier
External/promotion API alone is not sufficient.
Coverage was checked against upstream commit
[4c7f659](https://github.com/MrMEEE/flat-manager-django/commit/4c7f659520f1284cd8e1a04eec751a7954385d56)
(server release 1.0.34): all 21 newly registered resource prefixes and all
58 added action routes, including GPG renewal, LDAP tests and RPM discovery.

- `flatman_resource_info`: list/read resources, following pagination; returns `resources`.
- `flatman_resource`: reconcile supported resource operations; returns `resource`.
- `flatman_workflow_action`: dispatch an explicit resource/action pair; returns `result`.

All modules use the existing connection options and
`group/mrmeee.flatman.flatman` module defaults. The server enforces workflow,
administrator and organisation permissions.

## Resource operations

Use the router prefix as `resource`. Reads use `GET /api/{resource}/` or
`GET /api/{resource}/{id}/`; create, update and delete use POST, PATCH and DELETE.

| Resource | Supported mutations through `flatman_resource` |
|---|---|
| `flatpak-remotes` | Create, update, delete |
| `organisations` | Create, update, delete |
| `bst-sources` | Create, update, delete |
| `clients` | Delete |
| `permission-groups` | Create, update, delete |
| `ldap-sources` | Create, update, delete |
| `ldap-group-mappings` | Create, update, delete |
| `rpm-packages` | Create, update, delete |
| `rpm-builds` | Delete |
| `rpm-distributions` | Create, update, delete |
| `satellite-servers` | Create, delete |
| `satellite-repositories` | Create, delete |
| `rpm-destinations` | Delete |
| `user-roles` | Create, update, delete |
| `permission-grants` | Create, update, delete |
| `group-permissions` | Create, update, delete |
| `site-config` | Update |
| `external-refs` | Create, update, delete |

Additional resources readable through `flatman_resource_info`:
`bst-promotions`, `rpm-repositories`, `rpm-signing-keys`, `packages`,
`repositories`, `builds`, `promotions`, `external-ref-promotions`, `gpg-keys`, and `workflows`.
Existing dedicated modules continue to cover core resources and the catalogue.

`site-config` list returns one configuration dictionary; `workflows` list
returns the action catalogue. The module normalises both into a one-element
`resources` list. The workflow catalogue has no detail endpoint.

### Identity, payloads and convergence

Supply either `id` for an existing record or a nonempty `match` dictionary
containing exact **readable** identity fields. Matching is performed locally,
not with fuzzy server search. Ambiguous identities fail rather than updating
an arbitrary record. Include related IDs in the identity when names alone are
not unique. Explicit `null` values match null scope, not all scopes.

With `state: present`, a missing identity is created using `match` plus `data`.
An existing record is updated only when supplied fields differ. `data` cannot
contradict `match`; use `id` to rename a resource. A missing numeric ID cannot
create a record. Lists compare order-insensitively. Explicit null values are
sent to the server to clear nullable fields where that API supports it.

Payload fields use the upstream serializer or web form's names, with numeric
IDs for relationships. The server validates required fields, choices and
permissions; the generic modules do not provide per-resource form schemas.
Do not supply read-only fields. Unknown/write-only fields cannot be verified
from the response; consult the server forms before using them.

Some upstream workflows return an acknowledgement rather than a resource.
After writes, the module rereads the record and checks supplied readable
fields. It fails if those fields were not applied. Operations not supported
by a resource fail explicitly rather than falling back to another operation.

Write-only credentials cause a write every time they are supplied: omit them
on subsequent runs unless rotating them. Put credentials in `secret_data`,
which is merged into `data` and marked `no_log`; do not duplicate a field in
both dictionaries. Known credential field names in `data` are also redacted.
Ordinary IDs and configuration values are not treated as secrets, so returned
IDs remain usable by dependent tasks. No diff is returned.
Use task-level `no_log: true` for credential operations and
site configuration, whose response may itself contain sensitive settings.
Never put real credentials in source control.

### Access and LDAP examples

See [manage-access.yml](../playbooks/manage-access.yml) for organisation and
role configuration. More examples, using IDs discovered with the info modules:

```yaml
- name: Grant read access within one organisation
  mrmeee.flatman.flatman_resource:
    resource: permission-grants
    match:
      user: 12
      resource: builds
      action: read
      organisation: 3
    data:
      granted: true

- name: Configure a permission group
  mrmeee.flatman.flatman_resource:
    resource: permission-groups
    match:
      name: Release readers
    data:
      description: Read-only release access
      organisation: 3

- name: Configure an LDAP source
  mrmeee.flatman.flatman_resource:
    resource: ldap-sources
    match:
      name: Corporate directory
    data:
      hostname: ldap.example.com
      port: 636
      protocol: ldaps
      verify_certs: true
      server_type: posix
      base_dn: dc=example,dc=com
      bind_dn: cn=flatman,dc=example,dc=com
      is_active: true
    secret_data:
      bind_password: "{{ vault_ldap_bind_password }}"
  no_log: true

- name: Map a directory group to an organisation role
  mrmeee.flatman.flatman_resource:
    resource: ldap-group-mappings
    match:
      source: 2
      ldap_group_dn: cn=readers,ou=groups,dc=example,dc=com
      organisation: 3
      role: view
```

`group-permissions` uses `group` instead of `user`. For a global role/grant,
use `organisation: null` rather than omitting it from the identity.

## Workflow actions

Actions use `POST /api/{resource}/{id}/{action}/` for detail operations and
`POST /api/{resource}/{action}/` for collection operations. Supply `id` only
for detail operations; it is required there and forbidden on collection
operations. Hyphenated action names match the router.

| Resource | Detail actions | Collection actions |
|---|---|---|
| `gpg-keys` | `renew` | |
| `ldap-sources` | | `test-connection`, `test-search` |
| `flatpak-remotes` | `toggle` | |
| `external-refs` | `unpublish` | `bulk-import` |
| `packages` | `retry`, `republish`, `check-upstream`, `check-available` | |
| `repositories` | `update-metadata` | |
| `builds` | `unpublish`, `recommit`, `delete`, `cancel`, `bst-promote` | |
| `promotions` | `retry`, `delete` | |
| `external-ref-promotions` | `retry`, `delete` | |
| `bst-promotions` | `retry`, `delete` | |
| `bst-sources` | `build`, `retry`, `force-rebuild` | `integrity-check` |
| `clients` | `assign-organisations`, `lockdown` | |
| `permission-groups` | `memberships` | |
| `site-config` | | `cleanup`, `sync-repositories`, `check-external-updates`, `scan-available-versions`, `scan-upstream-versions`, `repair-permissions`, `scan-orphaned-refs`, `prune-orphaned-ref`, `prune-orphaned-refs` |
| `rpm-packages` | `build`, `build-with-number`, `check-upstream`, `check-available`, `toggle-repository`, `signing-key`, `assign-destination` | `scan-spec-files`, `scan-branches` |
| `rpm-builds` | `retry`, `repush`, `cancel`, `logs` | |
| `rpm-distributions` | `toggle`, `sync-repos` | `sync` |
| `rpm-repositories` | `toggle` | |
| `satellite-servers` | | `fetch-organisations`, `fetch-products`, `fetch-repositories` |

`data` contains upstream JSON/form fields. In particular:

- External `bulk-import`: `repository_id`, `remote_id`, `refs` (list of full refs).
- Build `bst-promote`: `target_repo_id`.
- RPM `toggle-repository`: `repo_pk`.
- RPM `signing-key`: `dist_pk`, plus `signing_key_id` to assign a key.
- RPM `assign-destination`: `distribution_id`, `repository_id`.
- RPM `build-with-number`: `build_number`.
- Client `assign-organisations`: `organisations` (replacement list of IDs).
- GPG `renew`: `key_lifetime` as `"0"` (never expires), `1y`, `2y`, `5y`, or `10y`.
- LDAP `test-connection`: `hostname`, with optional `port`, `protocol`,
  `verify_certs`, `bind_dn` and `bind_password` (use `secret_data`).
- LDAP `test-search`: the same connection fields plus `base_dn` and
  `search_username`; optional `ldap_filter`, `attr_username`, `attr_first_name`,
  `attr_last_name` and `attr_email`. Set attribute names for your directory.
- LDAP tests accept `source_pk` to reuse a saved source's bind password when
  no password is supplied. Other connection/search settings must still be sent.
- RPM `scan-branches`: Git repository `url`; returns `result.branches`.
- RPM `scan-spec-files`: Git repository `url`, optional `branch` (default
  `main`); returns relative paths in `result.spec_files`.

For other fields and nested IDs, inspect `resource: workflows` and the
upstream workflow handler. Some workflows, particularly Satellite lookups,
require credentials or additional form fields.

These actions are **imperative**: successful dispatch reports `changed: true`
and does not imply an asynchronous build/job has completed. No automatic
polling or retries occur. Read/report actions (`check-upstream`,
`check-available`, `integrity-check`, RPM build `logs`, Satellite fetches,
LDAP tests and RPM discovery)
report `changed: false`, although version checks can update server caches.
Maintenance scans are conservatively reported as changed.
Check mode validates local arguments but sends no action requests, including
read/report actions. It does not validate server-side prerequisites.

Prefer existing dedicated External and promotion modules when you need
idempotent publication/promotion or built-in waiting.

### Signing-key renewal and diagnostic/discovery examples

- [renew-gpg-key.yml](../playbooks/renew-gpg-key.yml) requires `gpg_key_id` and
  explicit `do_renew=true`. Renewal recalculates expiry from today and updates
  repository public-key files; it is imperative, not an expiry-threshold policy.
- [test-ldap.yml](../playbooks/test-ldap.yml) tests bind and user lookup without
  saving configuration. It requires administrator access and server-side
  `ldap3`. Tasks use `no_log: true` to protect credentials and directory data.
  Successful results include `ok` and `message`; search also returns `dn` and
  `attributes`. HTTP 200 responses with `ok: false` fail explicitly.
- [discover-rpm-source.yml](../playbooks/discover-rpm-source.yml) discovers
  branches and spec files without creating a package. Git runs on the server,
  which needs access to the repository. Spec discovery can take 120 seconds,
  so the example increases the request timeout to 180 seconds.

All five routes use JSON POST through the token API, including the RPM scanners
whose underlying web handlers use GET. No action requests run in check mode.

### Release lifecycle examples

```yaml
- name: Refresh repository metadata
  mrmeee.flatman.flatman_workflow_action:
    resource: repositories
    id: 3
    action: update-metadata

- name: Unpublish a specific build
  mrmeee.flatman.flatman_workflow_action:
    resource: builds
    id: 48
    action: unpublish
  when: unpublish_release | default(false) | bool

- name: Promote a BuildStream build
  mrmeee.flatman.flatman_workflow_action:
    resource: builds
    id: 49
    action: bst-promote
    data:
      target_repo_id: 3
  when: promote_bst | default(false) | bool
```

Unpublishing, deletion, pruning, lockdown and toggles must be deliberate.
Use declarative resource updates instead of toggles where possible.
Deleting a promotion can remove published content, not just history.

### RPM and Satellite examples

See [manage-rpm.yml](../playbooks/manage-rpm.yml) for package configuration and
optional build dispatch. To assign an existing destination or signing key:

```yaml
- name: Assign an RPM destination
  mrmeee.flatman.flatman_workflow_action:
    resource: rpm-packages
    id: 12
    action: assign-destination
    data:
      distribution_id: 2
      repository_id: 7

- name: Assign an RPM signing key for a distribution
  mrmeee.flatman.flatman_workflow_action:
    resource: rpm-packages
    id: 12
    action: signing-key
    data:
      dist_pk: 2
      signing_key_id: 4

- name: Add a repository on an existing Satellite server
  mrmeee.flatman.flatman_resource:
    resource: satellite-repositories
    match:
      server: 1
      repository_id: 123
    data:
      server_pk: 1
      name: Example RPMs
      organization: Example
      product: Applications
```

Satellite server creation uses `name`, `url`, `admin_user`, `admin_pass`,
`svc_login`, and checkbox `ssl_verify: "on"`; it can provision a remote
service account. Read fields differ from creation credentials. Protect the
entire task with `no_log: true`. Satellite resources do not support updates
through this router; an existing matching definition is reused, or an
unsupported change fails.

## Verified limits

The shared modules cover the added router resources/actions, including the
previously web-only GPG renewal, LDAP tests and RPM spec/branch discovery.
The existing package `upload`, `build_ref` and `missing_objects` handlers
still contain upstream TODO implementations; adding wrappers does not make
those server operations functional.

The collection additionally exposes bulk pending-review rejection through
`flatman_quality_moderation` with `action: reject-pending-reviews`.
