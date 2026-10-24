# mrmeee.flatman

Ansible collection for [flat-manager-django](https://github.com/MrMEEE/flat-manager-django).

It covers the core and expanded token API resources under `/api/` and the
Flathub-compatible catalogue under `/api/v2/` with 45 modules and 3 roles.
The modules talk HTTP from the controller, so there is nothing to install on the
flat-manager server and no Python dependency beyond ansible-core itself.

- [Getting started](docs/getting-started.md)
- [Authentication](docs/authentication.md)
- [Endpoint to module map](docs/endpoint-map.md)
- [Idempotency and check mode](docs/idempotency.md)
- [Expanded API resources and workflows](docs/expanded-api.md)
- [Example playbooks](playbooks/README.md)

## Requirements

- ansible-core 2.15 or newer
- Network access to a flat-manager server
- An API token for anything other than the public `/api/v2/` read endpoints

## Installation

```bash
ansible-galaxy collection build
ansible-galaxy collection install mrmeee-flatman-*.tar.gz
```

Or install straight from git:

```bash
ansible-galaxy collection install git+https://github.com/MrMEEE/ansible_collection.flatman.git
```

## Quick start

```yaml
- name: Provision a signed stable repository
  hosts: localhost
  gather_facts: false
  module_defaults:
    group/mrmeee.flatman.flatman:
      url: https://flatman.example.com
      api_token: "{{ vault_flatman_token }}"
  tasks:
    - name: Generate a signing key
      mrmeee.flatman.flatman_gpg_key:
        name: release-signing-key
        email: release@example.com
        state: generated

    - name: Create the repository
      mrmeee.flatman.flatman_repository:
        name: stable
        collection_id: org.example.Stable
        gpg_key: release-signing-key
```

All modules belong to the `mrmeee.flatman.flatman` action group, so the
connection options can be set once with `module_defaults` as shown above.

## Complete Module Reference

Every module below is a public collection function. The linked module source
contains its authoritative `DOCUMENTATION`, `EXAMPLES`, `RETURN`, argument types,
choices, defaults, check-mode behavior, and notes; these pages are rendered by
`ansible-doc mrmeee.flatman.<module>`.

### Repositories and signing

| Module | Function and main inputs |
|---|---|
| [flatman_repository](plugins/modules/flatman_repository.py) | Create, reconcile, or delete `/api/repositories/` by `name`; set `collection_id`, `description`, `gpg_key`/`gpg_key_id`, `parent_repos`, and `is_active`. |
| [flatman_repository_info](plugins/modules/flatman_repository_info.py) | List/get repositories by `id`, `name`, `collection_id`, `is_active`, or `search`; `include` can load `builds` or `subsets`. |
| [flatman_repository_subset](plugins/modules/flatman_repository_subset.py) | Create, reconcile, or delete `/api/repository-subsets/` by repository plus `name`; configure `collection_id` and `base_url`. |
| [flatman_repository_subset_info](plugins/modules/flatman_repository_subset_info.py) | List/get subsets by `id`, `name`, `repository`/`repository_id`, or `search`. |
| [flatman_gpg_key](plugins/modules/flatman_gpg_key.py) | Manage keys by `name`; `state` is `present`, `absent`, `generated`, or `imported`. Private-key inputs are protected with `no_log`. |
| [flatman_gpg_key_info](plugins/modules/flatman_gpg_key_info.py) | List/get keys by `id`, `name`, or `search`; `include: [public_key]` retrieves the public key. |
| [flatman_token](plugins/modules/flatman_token.py) | Manage repository token records by repository plus `name`; select `token_type`, expiry, and active state. **Stored tokens are not enforced by the server.** |
| [flatman_token_info](plugins/modules/flatman_token_info.py) | Read repository token records by ID, repository, type, or active state. Returned token values are secret; use `no_log`. |

### Packages, builds, and artifacts

| Module | Function and main inputs |
|---|---|
| [flatman_package](plugins/modules/flatman_package.py) | Create, reconcile, or delete a Flatpak definition by `package_id`; configure source Git, branch, architecture, repository, and dependencies. |
| [flatman_package_info](plugins/modules/flatman_package_info.py) | List/get packages by ID, status, repository, architecture, branch, or search; `full` controls embedded build history. |
| [flatman_package_action](plugins/modules/flatman_package_action.py) | Dispatch `start`, `cancel`, `commit`, `publish`, `build_ref`, or `missing_objects`; build-ref needs `ref` and `commit`, missing-object POST takes `wanted`; optional `wait` polls status. |
| [flatman_build_info](plugins/modules/flatman_build_info.py) | Read build history by ID, package, status, build number, or search; `full` controls embedded logs. |
| [flatman_build_log_info](plugins/modules/flatman_build_log_info.py) | Read logs by `build_id`, `package_id`, or `package_pk`; filter by `level` and limit to the last N entries. |
| [flatman_artifact](plugins/modules/flatman_artifact.py) | Create, reconcile, or delete a build artifact by `build_id` plus `filename`; record path, size, and checksum. |
| [flatman_artifact_info](plugins/modules/flatman_artifact_info.py) | Read artifacts by ID, build, filename, or search. |

### Externals and promotions

| Module | Function and main inputs |
|---|---|
| [flatman_external_ref_info](plugins/modules/flatman_external_ref_info.py) | Read External definitions, immutable versions, logs, and publication status. |
| [flatman_external_ref_action](plugins/modules/flatman_external_ref_action.py) | Pull (then publish) or publish an existing External definition; `state`/`action` and optional wait settings are documented in the module. |
| [flatman_promotion](plugins/modules/flatman_promotion.py) | Promote a specific Flatpak build or External version to `target_repo_id`; the exact version is selected explicitly. |
| [flatman_promotion_info](plugins/modules/flatman_promotion_info.py) | Poll build or External promotions by ID, source, version, target repository, and status. |
| [flatman_promotion_ready_info](plugins/modules/flatman_promotion_ready_info.py) | List server-calculated ready build/External-to-repository candidates, optionally filtered by source, kind, or target. |
| [flatman_promotion_batch](plugins/modules/flatman_promotion_batch.py) | Promote all ready candidates to one target or advance all sources through every currently eligible release-chain target. |

These modules need the token workflow API and appropriate workflow and
organisation permissions. External actions operate on existing definitions and
configured remotes. Use [flatman_resource](plugins/modules/flatman_resource.py)
to create/update/delete External definitions; see [expanded-api.md](docs/expanded-api.md).

`flatman_promotion_ready_info` returns one candidate per ready source/target
pair. `flatman_promotion_batch` supports `mode: target` with a repository name
or ID, and `mode: all_ready` to promote every currently eligible pair. With
`wait: true` (the default), it waits for each promotion and refreshes readiness
so parent completion can unlock the next repository in the chain. With
`wait: false`, it submits only the current snapshot; run it again after those
jobs finish. In check mode it reports that snapshot without dispatching tasks.

### Expanded resources and workflows

| Module | Function and main inputs |
|---|---|
| [flatman_resource](plugins/modules/flatman_resource.py) | Reconcile a supported router resource using `resource`, `match` or `id`, and `data`; `state: absent` deletes. Supported operations are listed below. |
| [flatman_resource_info](plugins/modules/flatman_resource_info.py) | Read a named router resource by `resource`, optional `id`, or exact `match`; `workflows` returns the server action catalogue. |
| [flatman_workflow_action](plugins/modules/flatman_workflow_action.py) | Dispatch one explicitly allowed action using `resource`, `action`, optional detail `id`, and JSON `data`; use `secret_data` for credentials. |

`flatman_resource` supports these state-changing operations:

| Resource | Operations |
|---|---|
| `flatpak-remotes`, `organisations`, `bst-sources`, `permission-groups`, `ldap-sources`, `ldap-group-mappings`, `rpm-packages`, `rpm-distributions`, `user-roles`, `permission-grants`, `group-permissions`, `external-refs` | Create, update, delete |
| `clients`, `rpm-builds`, `rpm-destinations` | Delete only |
| `satellite-servers`, `satellite-repositories` | Create and delete |
| `site-config` | Update only |
| `bst-promotions`, `rpm-repositories`, `rpm-signing-keys` | Read only through `flatman_resource_info` |

`flatman_resource_info` can read every router resource below, including the
read-only resources in the final group:

| Resource family | `resource` values |
|---|---|
| Core | `gpg-keys`, `packages`, `repositories`, `builds`, `promotions`, `external-refs`, `external-ref-promotions` |
| Flatpak administration | `flatpak-remotes`, `organisations`, `bst-sources`, `bst-promotions`, `clients` |
| Users and access | `permission-groups`, `ldap-sources`, `ldap-group-mappings`, `user-roles`, `permission-grants`, `group-permissions` |
| RPM | `rpm-packages`, `rpm-builds`, `rpm-distributions`, `rpm-repositories`, `satellite-servers`, `satellite-repositories`, `rpm-destinations`, `rpm-signing-keys` |
| Singleton and discovery | `site-config`, `workflows` |

Use `id` for one record or `match` for exact local field matching. The workflow
catalogue is a singleton read and has no detail ID.

`flatman_workflow_action` accepts only these resource/action pairs:

| Resource | Actions |
|---|---|
| `gpg-keys` | `renew` (`key_lifetime`) |
| `ldap-sources` | `test-connection`, `test-search` |
| `flatpak-remotes` | `toggle` |
| `external-refs` | `bulk-import`, `unpublish` |
| `packages` | `retry`, `republish`, `check-upstream`, `check-available` |
| `repositories` | `update-metadata` |
| `builds` | `unpublish`, `recommit`, `delete`, `cancel`, `bst-promote` |
| `promotions`, `external-ref-promotions`, `bst-promotions` | `retry`, `delete` |
| `bst-sources` | `build`, `retry`, `force-rebuild`, `integrity-check` |
| `clients` | `assign-organisations`, `lockdown` |
| `permission-groups` | `memberships` |
| `site-config` | `cleanup`, `sync-repositories`, `check-external-updates`, `scan-available-versions`, `scan-upstream-versions`, `repair-permissions`, `scan-orphaned-refs`, `prune-orphaned-ref`, `prune-orphaned-refs` |
| `rpm-packages` | `scan-spec-files`, `scan-branches`, `build`, `build-with-number`, `check-upstream`, `check-available`, `toggle-repository`, `signing-key`, `assign-destination` |
| `rpm-builds` | `retry`, `repush`, `cancel`, `logs` |
| `rpm-distributions` | `sync`, `toggle`, `sync-repos` |
| `rpm-repositories` | `toggle` |
| `satellite-servers` | `fetch-organisations`, `fetch-products`, `fetch-repositories` |

### Users and access

| Module | Function and main inputs |
|---|---|
| [flatman_user](plugins/modules/flatman_user.py) | Create, reconcile, or delete accounts by username; manages user fields, not passwords. |
| [flatman_user_info](plugins/modules/flatman_user_info.py) | List/get users or query the authenticated user with `me: true`. |
| [flatman_user_profile](plugins/modules/flatman_user_profile.py) | Create, reconcile, or delete a profile by `user` or `user_id`; fields are bio, phone, and organization. |
| [flatman_user_profile_info](plugins/modules/flatman_user_profile_info.py) | Read profiles by user or profile ID. |

### Catalogue (`/api/v2/`)

| Module | Function and main inputs |
|---|---|
| [flatman_app_metadata](plugins/modules/flatman_app_metadata.py) | Reconcile appstream metadata by `app_id`: summary, description, homepage, screenshots, developer, categories, keywords, verification, and mobile flags. |
| [flatman_app_info](plugins/modules/flatman_app_info.py) | Read appstream list/detail by `app_id`; optional sort and related summary/addon/fullscreen reads. |
| [flatman_app_stats_info](plugins/modules/flatman_app_stats_info.py) | Read global stats or stats for one `app_id`. |
| [flatman_collection_info](plugins/modules/flatman_collection_info.py) | Browse supported collections, feeds, categories, developers, keywords, or category subcategories. |
| [flatman_search_info](plugins/modules/flatman_search_info.py) | Search the public catalogue with required `query`. |
| [flatman_platform_info](plugins/modules/flatman_platform_info.py) | Read supported platforms and runtimes. |
| [flatman_usage_info](plugins/modules/flatman_usage_info.py) | Read popular apps over `days` (1–365). |
| [flatman_year_in_review_info](plugins/modules/flatman_year_in_review_info.py) | Read the summary for required `year`. |

### Moderation and curation

| Module | Function and main inputs |
|---|---|
| [flatman_quality_moderation](plugins/modules/flatman_quality_moderation.py) | Set fullscreen or request review for `app_id`; request-review is imperative. |
| [flatman_quality_moderation_info](plugins/modules/flatman_quality_moderation_info.py) | Read quality status, reports, or one app's moderation result. |
| [flatman_moderation_request](plugins/modules/flatman_moderation_request.py) | Submit a review request by `app_id`; skips a pending request unless forced. |
| [flatman_moderation_review](plugins/modules/flatman_moderation_review.py) | Record `approved` or `rejected` and optional comment for `request_id`. |
| [flatman_moderation_info](plugins/modules/flatman_moderation_info.py) | List moderation requests, optionally for an app or status. |
| [flatman_app_pick](plugins/modules/flatman_app_pick.py) | Create, reconcile, or delete a curated selection by app, kind, and date; accepts an explicit selection ID. |
| [flatman_app_pick_info](plugins/modules/flatman_app_pick_info.py) | Read day/week/curated selections, admin selections, themes, and admin week picks. |

### Utility

| Module | Function and main inputs |
|---|---|
| [flatman_git_branch_info](plugins/modules/flatman_git_branch_info.py) | List branches for required `repo_url`. |
| [flatman_status_info](plugins/modules/flatman_status_info.py) | Read application version and public service health. |

### Common behavior

- Every module accepts `url`, `api_token`, `validate_certs`, `timeout`, `client_cert`, and `client_key`; token and TLS options are documented in [the shared connection fragment](plugins/doc_fragments/flatman.py).
- `include_names` defaults to `true` and adds readable companion fields such as `package_name`, `target_repo_name`, `build_name`, and `repository_name` wherever related records can be read. Original numeric IDs are retained. Set `include_names: false` to skip the extra lookups.
- `*_info` modules are read-only and return `changed: false`.
- Resource modules use `state: present|absent`, reconcile only supplied fields, and support check mode where documented.
- Actions are imperative: they dispatch a server action and may change state. Check each module's `ansible-doc` page for check-mode support and required arguments.
- Credentials belong in Ansible Vault or environment variables; use task-level `no_log: true` for secret-bearing data.
- The repository-token model is not enforced by the server; `flatman_token` does not create an API credential. Use a DRF user token as `api_token`.

### Roles

| Role | Variables and behavior |
|---|---|
| [`repository`](roles/repository/README.md) | `flatman_gpg_keys`, `flatman_repositories`, `flatman_repository_subsets`, `flatman_tokens`; declarative repository/signing setup. Repository tokens are stored but not enforced. |
| [`package`](roles/package/README.md) | `flatman_packages`; optional `flatman_package_build`, `flatman_package_pipeline`, `flatman_package_wait`, `flatman_package_wait_timeout`, and `flatman_package_wait_interval`. |
| [`curation`](roles/curation/README.md) | `flatman_app_metadata`, `flatman_app_picks`, and `flatman_quality_overrides`. |

## Documentation

See the [publishing and promotion examples](playbooks/README.md#publishing-and-promotion-what-is-supported)
for Flatpak and External publication, release repository setup, and
cross-repository promotion through the token API.

Every module carries full `ansible-doc` documentation:

```bash
ansible-doc mrmeee.flatman.flatman_repository
```

## Testing

`ansible-test` only runs from inside an `ansible_collections/<namespace>/<name>`
directory tree, so a bare clone of this repository cannot be tested in place.
Build and install the current working tree into a temporary collection layout:

```bash
collection_test_dir="$(mktemp -d)"
ansible-galaxy collection build --output-path "$collection_test_dir"
ansible-galaxy collection install "$collection_test_dir"/mrmeee-flatman-*.tar.gz \
  -p "$collection_test_dir/collections"
cd "$collection_test_dir/collections/ansible_collections/mrmeee/flatman"
ansible-test sanity --python 3.12 --venv
```

Workflow regression tests can also be run from that collection directory:

```bash
ansible-test units --python 3.12 --venv tests/unit/plugins/modules/
```

Choose an installed Python version supported by your ansible-core release.
Rebuild and reinstall after editing the source. A symlink to a bare clone does
not work because `ansible-test` resolves the real working directory.

The [flat-manager-django](https://github.com/MrMEEE/flat-manager-django)
repository already vendors this collection as a submodule at
`ansible/collections/ansible_collections/mrmeee/flatman`, so running
`ansible-test` from there works with no extra setup.

## License

MIT
