# mrmeee.flatman.repository

Declaratively manage the repository layer of a flat-manager server: GPG signing
keys, repositories, repository subsets and repository access tokens.

Everything is driven from four list variables, so the whole repository layout can
live in one inventory group_vars file. The role is idempotent and check-mode safe.

## Variables

| Variable | Default | Description |
|---|---|---|
| `flatman_url` | `$FLATMAN_URL` | Base URL of the flat-manager server |
| `flatman_api_token` | `$FLATMAN_API_TOKEN` | API token with admin rights |
| `flatman_validate_certs` | `true` | Validate the server TLS certificate |
| `flatman_timeout` | `30` | Per-request timeout in seconds |
| `flatman_gpg_keys` | `[]` | Items accept the options of `flatman_gpg_key` |
| `flatman_repositories` | `[]` | Items accept the options of `flatman_repository` |
| `flatman_repository_subsets` | `[]` | Items accept the options of `flatman_repository_subset` |
| `flatman_tokens` | `[]` | Items accept the options of `flatman_token`. Not enforced by the server yet — see below |

Tasks touching keys and tokens run with `no_log: true`.

## Repository tokens are not enforced yet

`flatman_tokens` manages the `/api/tokens/` endpoint, which stores repository
scoped upload/download/admin credentials. The server does not currently validate
any request against them and `token_type` carries no meaning, so creating a token
grants no access and deleting one revokes none. The variable is left in place so
the repository layout can already be declared, but do not build a workflow that
depends on these tokens working.

The credential that *does* work is the user scoped Django REST Framework token
passed as `flatman_api_token`.

## Example

```yaml
- hosts: localhost
  gather_facts: false
  roles:
    - role: mrmeee.flatman.repository
      vars:
        flatman_url: https://flatman.example.com
        flatman_api_token: "{{ vault_flatman_token }}"

        flatman_gpg_keys:
          - name: release-signing-key
            state: generated
            email: release@example.com

        flatman_repositories:
          - name: stable
            collection_id: org.example.Stable
            gpg_key: release-signing-key
          - name: beta
            collection_id: org.example.Beta
            gpg_key: release-signing-key
            parent_repos: [stable]

        flatman_repository_subsets:
          - repository: stable
            name: aarch64
            collection_id: org.example.Stable.aarch64
            base_url: https://dl.example.com/stable/aarch64
```
