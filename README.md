# mrmeee.flatman

Ansible collection for [flat-manager-django](https://github.com/MrMEEE/flat-manager-django).

It covers the core and expanded token API resources under `/api/` and the
Flathub-compatible catalogue under `/api/v2/` with 43 modules and 3 roles.
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

## Modules

### Repositories and signing

| Module | Description |
|---|---|
| `flatman_repository` | Manage Flatpak/OSTree repositories |
| `flatman_repository_info` | Gather information about repositories |
| `flatman_repository_subset` | Manage repository subsets |
| `flatman_repository_subset_info` | Gather information about repository subsets |
| `flatman_gpg_key` | Manage, generate or import GPG signing keys |
| `flatman_gpg_key_info` | Gather information about GPG keys |
| `flatman_token` | Manage repository access tokens (not enforced by the server yet) |
| `flatman_token_info` | Gather information about repository access tokens |

### Packages and builds

| Module | Description |
|---|---|
| `flatman_package` | Manage Flatpak packages |
| `flatman_package_info` | Gather information about packages |
| `flatman_package_action` | Run build actions (start, cancel, commit, publish, build_ref, missing_objects) |
| `flatman_build_info` | Gather information about build history records |
| `flatman_build_log_info` | Fetch the build log of a build or package |
| `flatman_artifact` | Manage build artifacts |
| `flatman_artifact_info` | Gather information about build artifacts |

### Externals and promotion

| Module | Description |
|---|---|
| `flatman_external_ref_info` | Read External refs, their versions, logs and publication status |
| `flatman_external_ref_action` | Pull and publish an existing External ref |
| `flatman_promotion` | Promote an exact Flatpak build or External version to a target repository |
| `flatman_promotion_info` | Read Flatpak or External promotion records and status |

These modules require a server containing the
[token workflow API](https://github.com/MrMEEE/flat-manager-django/commit/d7c24f5ea5b4ce6827925aeb096c6c4d0abe8fba)
and an API token with the appropriate workflow and organisation permissions.
Dedicated External action modules require existing definitions and remotes.
With the expanded workflow router, use `flatman_resource` to configure them
directly.

### Expanded resources and workflows

| Module | Description |
|---|---|
| `flatman_resource` | Reconcile supported External, BuildStream, access-control, RPM and configuration resources |
| `flatman_resource_info` | Read expanded resources and discover the workflow catalogue |
| `flatman_workflow_action` | Dispatch release lifecycle, maintenance, client, BuildStream, RPM discovery, LDAP tests and GPG renewal actions |

See the [expanded API guide](docs/expanded-api.md) for exact operation support,
payload conventions, credential handling, examples and remaining server limits.

### Users and access

| Module | Description |
|---|---|
| `flatman_user` | Manage user accounts |
| `flatman_user_info` | Gather information about users |
| `flatman_user_profile` | Manage user profiles |
| `flatman_user_profile_info` | Gather information about user profiles |

### Catalogue (`/api/v2/`)

| Module | Description |
|---|---|
| `flatman_app_metadata` | Manage the public Flathub metadata of an application |
| `flatman_app_info` | Gather information about published applications |
| `flatman_app_stats_info` | Gather application statistics |
| `flatman_collection_info` | Browse application collections and feeds |
| `flatman_search_info` | Search published applications |
| `flatman_platform_info` | Gather the known platforms and runtimes |
| `flatman_usage_info` | Gather popular application usage |
| `flatman_year_in_review_info` | Gather the year in review summary |

### Moderation and curation

| Module | Description |
|---|---|
| `flatman_quality_moderation` | Perform quality moderation actions |
| `flatman_quality_moderation_info` | Gather quality moderation information |
| `flatman_moderation_request` | Submit a moderation review request |
| `flatman_moderation_review` | Approve or reject a moderation request |
| `flatman_moderation_info` | List moderation requests |
| `flatman_app_pick` | Manage curated app selections |
| `flatman_app_pick_info` | Read curated app selections |

### Utility

| Module | Description |
|---|---|
| `flatman_git_branch_info` | List the branches of a remote Git repository |
| `flatman_status_info` | Gather the version and health status of the server |

## Roles

| Role | Description |
|---|---|
| [`repository`](roles/repository/README.md) | Declarative GPG keys, repositories, subsets and tokens |
| [`package`](roles/package/README.md) | Declare packages and optionally drive the build pipeline |
| [`curation`](roles/curation/README.md) | Appstream metadata, app picks and quality moderation |

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
