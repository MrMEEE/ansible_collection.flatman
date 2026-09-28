# mrmeee.flatman

Ansible collection for [flat-manager-django](https://github.com/MrMEEE/flat-manager-django).

It covers the complete HTTP API — the DRF resources under `/api/` and the
Flathub-compatible catalogue under `/api/v2/` — with 36 modules and 3 roles.
The modules talk HTTP from the controller, so there is nothing to install on the
flat-manager server and no Python dependency beyond ansible-core itself.

- [Getting started](docs/getting-started.md)
- [Authentication](docs/authentication.md)
- [Endpoint to module map](docs/endpoint-map.md)
- [Idempotency and check mode](docs/idempotency.md)
- [Example playbooks](playbooks/)

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

Every module carries full `ansible-doc` documentation:

```bash
ansible-doc mrmeee.flatman.flatman_repository
```

## Testing

`ansible-test` only runs from inside an `ansible_collections/<namespace>/<name>`
directory tree, so a bare clone of this repository cannot be tested in place.
Check it out into the expected path first:

```bash
mkdir -p build/ansible_collections/mrmeee
ln -s "$PWD" build/ansible_collections/mrmeee/flatman
cd build/ansible_collections/mrmeee/flatman
ansible-test sanity --python 3.12 --local
```

The [flat-manager-django](https://github.com/MrMEEE/flat-manager-django)
repository already vendors this collection as a submodule at
`ansible/collections/ansible_collections/mrmeee/flatman`, so running
`ansible-test` from there works with no extra setup.

## License

MIT
