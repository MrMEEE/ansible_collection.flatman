# Getting started

## 1. Make the collection available

Install it straight from git:

```bash
ansible-galaxy collection install git+https://github.com/MrMEEE/ansible_collection.flatman.git
ansible-doc mrmeee.flatman.flatman_repository
```

Or build and install a tarball from a clone:

```bash
ansible-galaxy collection build
ansible-galaxy collection install mrmeee-flatman-*.tar.gz
```

If you are working in the [flat-manager-django](https://github.com/MrMEEE/flat-manager-django)
repository, this collection is already vendored as a submodule and its
`ansible/ansible.cfg` sets `collections_path`, so nothing needs installing:

```bash
git submodule update --init
cd ansible
ansible-doc mrmeee.flatman.flatman_repository
```

## 2. Point the modules at your server

Every module needs `url`, and everything except the public `/api/v2/` reads also
needs `api_token`. Both fall back to the `FLATMAN_URL` and `FLATMAN_API_TOKEN`
environment variables, so for interactive use:

```bash
export FLATMAN_URL=https://flatman.example.com
export FLATMAN_API_TOKEN=...
```

In playbooks, prefer setting them once for the whole play. All modules are
members of the `mrmeee.flatman.flatman` action group:

```yaml
module_defaults:
  group/mrmeee.flatman.flatman:
    url: "{{ flatman_url }}"
    api_token: "{{ vault_flatman_token }}"
    validate_certs: true
```

See [authentication.md](authentication.md) for how to create a token.

## 3. Verify connectivity

```yaml
- hosts: localhost
  gather_facts: false
  tasks:
    - name: Check the server version
      mrmeee.flatman.flatman_status_info:
        url: "{{ flatman_url }}"
      register: server

    - ansible.builtin.debug:
        msg: "flat-manager {{ server.version }} ({{ server.status }})"
```

`flatman_status_info` needs no token, which makes it a good first test.

## 4. Where the modules run

These modules are HTTP clients. They run on the controller and never touch a
managed node, so target `localhost` with `connection: local`. The
`ansible/inventory/localhost.yml` file in the flat-manager-django repository
does exactly that.

## 5. Naming conventions

- `flatman_<resource>` manages a resource and supports `state`.
- `flatman_<resource>_info` only reads and always returns `changed: false`.
- Info modules return a plural list key (`repositories`, `packages`); change
  modules return the singular object (`repository`, `package`).
- Where a resource can be addressed by name or numeric ID, both options exist
  and are mutually exclusive, for example `repository` and `repository_id`.

## 6. Next steps

- [Endpoint to module map](endpoint-map.md) — find the module for an API call
- [Idempotency and check mode](idempotency.md) — what is safe to run repeatedly
- [../playbooks/](../playbooks/) — runnable examples
- [../roles/repository/README.md](../roles/repository/README.md) — declarative
  repository provisioning without writing task lists
