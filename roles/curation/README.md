# mrmeee.flatman.curation

Manage the storefront side of a flat-manager instance: appstream metadata
overrides, curated app picks and quality moderation flags.

All three task groups require an admin API token.

## Variables

| Variable | Default | Description |
|---|---|---|
| `flatman_url` | `$FLATMAN_URL` | Base URL of the flat-manager server |
| `flatman_api_token` | `$FLATMAN_API_TOKEN` | Admin API token |
| `flatman_validate_certs` | `true` | Validate the server TLS certificate |
| `flatman_timeout` | `30` | Per-request timeout in seconds |
| `flatman_app_metadata` | `[]` | Items accept the options of `flatman_app_metadata` |
| `flatman_app_picks` | `[]` | Items accept the options of `flatman_app_pick` |
| `flatman_quality_overrides` | `[]` | Items accept the options of `flatman_quality_moderation` |

`flatman_app_metadata` and `flatman_app_picks` are fully idempotent. Of the
quality actions only `fullscreen` is idempotent; `request-review` always creates
a new moderation request, so drive it from a one-off playbook rather than a
recurring converge.

## Example

```yaml
- hosts: localhost
  gather_facts: false
  roles:
    - role: mrmeee.flatman.curation
      vars:
        flatman_url: https://flatman.example.com
        flatman_api_token: "{{ vault_flatman_token }}"

        flatman_app_metadata:
          - app_id: org.example.App
            summary: Edit and share example documents
            developer_name: Example Inc
            categories: [Office, Utility]
            is_verified: true

        flatman_app_picks:
          - app_id: org.example.App
            kind: day
            date: "2026-10-01"
            title: App of the day
            rank: 1

        flatman_quality_overrides:
          - app_id: org.example.App
            action: fullscreen
```
