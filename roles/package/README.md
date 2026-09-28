# mrmeee.flatman.package

Declare flat-manager packages and, optionally, drive them through the
build → commit → publish pipeline.

Declaring packages is idempotent. Running the pipeline is *imperative*: every
stage is an explicit operation on the server, so those tasks always report
`changed` when they execute. Guard them with `flatman_package_build` (default
`false`) so that a normal converge only reconciles configuration.

## Variables

| Variable | Default | Description |
|---|---|---|
| `flatman_url` | `$FLATMAN_URL` | Base URL of the flat-manager server |
| `flatman_api_token` | `$FLATMAN_API_TOKEN` | API token with build rights |
| `flatman_validate_certs` | `true` | Validate the server TLS certificate |
| `flatman_timeout` | `30` | Per-request timeout in seconds |
| `flatman_packages` | `[]` | Items accept the options of `flatman_package` |
| `flatman_package_build` | `false` | Run the pipeline after declaring packages |
| `flatman_package_pipeline` | `[start, commit, publish]` | Stages to run, in order |
| `flatman_package_wait` | `true` | Poll until each stage reaches a terminal state |
| `flatman_package_wait_timeout` | `1800` | Seconds to wait per stage |
| `flatman_package_wait_interval` | `10` | Seconds between status polls |

## Example

```yaml
- hosts: localhost
  gather_facts: false
  roles:
    - role: mrmeee.flatman.package
      vars:
        flatman_url: https://flatman.example.com
        flatman_api_token: "{{ vault_flatman_token }}"
        flatman_packages:
          - package_id: org.example.App
            package_name: Example App
            repository: stable
            git_repo_url: https://github.com/example/app.git
            git_branch: main
            branch: stable
            arch: x86_64
```

Add `flatman_package_build: true` to also build and publish each package. Use
`flatman_build_log_info` afterwards to collect the build output.
