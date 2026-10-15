# Example playbooks

Run these from a clone of this repository with the collection installed; see
[Getting started](../docs/getting-started.md). Modules make HTTP requests from
the controller. Set connection details before running an example:

```bash
export FLATMAN_URL=https://flatman.example.com
export FLATMAN_API_TOKEN=...
```

Keep real tokens in the environment or Ansible Vault, not in a playbook.

## Publishing and promotion: what is supported?

Publishing makes a build available in its configured repository. Promotion
copies a published build or External ref version to another repository in
the release chain; it is not a package configuration change.

| Workflow | Module-only support |
|---|---|
| Declare a Flatpak package and build, commit and publish it | [build-package.yml](build-package.yml) |
| Commit/publish an existing Flatpak build without rebuilding | [publish-flatpak.yml](publish-flatpak.yml) |
| Configure repositories and their promotion chain | [configure-release-repositories.yml](configure-release-repositories.yml) |
| Pull/publish an app managed under **Externals** | [publish-external.yml](publish-external.yml) |
| Promote a published Flatpak build to another repository | [promote-flatpak.yml](promote-flatpak.yml) |
| Promote a published External ref version to another repository | [promote-external.yml](promote-external.yml) |

### Publish a Flatpak

For an existing package that has already finished building:

```bash
ansible-playbook playbooks/publish-flatpak.yml -e app_id=org.example.App
```

The playbook commits a `built` package, publishes a `committed` package, and
skips both actions when it is already `published`. It waits for each action
and verifies the final status. Missing packages and other states fail explicitly.
In `--check` mode it reads the current state and predicts actions without
writing or asserting that publication has actually happened.

To declare a git-based package and run the whole pipeline instead, edit the
application/source/repository settings in [build-package.yml](build-package.yml)
and opt in to the build:

```bash
ansible-playbook playbooks/build-package.yml -e '{"do_build": true}'
```

That example defaults to configuration-only mode. Its `start` action requires
a pending package; it is not a recurring rebuild or promotion playbook.
Choose the initial publication repository with the package's `repository`
option before building. Neither example promotes an existing release.

### Prepare different release repositories

[configure-release-repositories.yml](configure-release-repositories.yml)
creates a signing key and this release chain:

```text
testing -> stable
```

```bash
ansible-playbook playbooks/configure-release-repositories.yml
```

`stable.parent_repos: [testing]` makes stable a child of testing, the direction
used by upstream promotion eligibility checks. The target must be active;
any other required parent promotions must have completed first. This configures
the topology only: it does not copy or promote any content.

Use this as an alternative to [provision-repository.yml](provision-repository.yml),
which demonstrates a different topology (`beta` inheriting from `stable`).
The examples set `parent_repos` declaratively and replace the target's existing
parent list, so review the names and topology before applying to existing repos.

### Externals and cross-repository promotion

**Externals** are apps pulled from an upstream Flatpak remote by
flat-manager-django, not packages built from git by this collection.
Upstream added token-authenticated pull/publish and promotion endpoints in
[commit d7c24f5](https://github.com/MrMEEE/flat-manager-django/commit/d7c24f5ea5b4ce6827925aeb096c6c4d0abe8fba).
Use a server version containing that commit or later.

| Operation | Token API endpoint |
|---|---|
| List/inspect External refs and their versions | `GET /api/external-refs/`, `GET /api/external-refs/{id}/` |
| Pull an External and queue publication | `POST /api/external-refs/{id}/pull/` |
| Publish an already-pulled External | `POST /api/external-refs/{id}/publish/` |
| Promote a published Flatpak build | `POST /api/builds/{id}/promote/` |
| Promote a published External version | `POST /api/external-refs/{id}/promote/` |
| Poll Flatpak promotion status | `GET /api/promotions/{id}/` |
| Poll External promotion status | `GET /api/external-ref-promotions/{id}/` |

Promotion requests take `target_repo_id`. External promotion also accepts
`external_ref_version_id`; when omitted, the latest published version is used.
Actions queue asynchronous tasks and return HTTP 202. Poll the External ref
or promotion record for completion, and check its status and `error_message`.
Tokens must belong to users with the appropriate workflow and organisation
permissions.

The collection wraps these endpoints with `flatman_external_ref_info`,
`flatman_external_ref_action`, `flatman_promotion` and `flatman_promotion_info`.
The workflow is:

1. Configure the External app's upstream remote/ref and initial repository.
2. Pull the External app. Upstream's pull workflow queues publication afterwards;
   its separate publish action requires the `pulled` state.
3. Once the External ref or Flatpak build is published, promote it to an
   eligible child repository, then wait for that promotion to complete before
   proceeding down the chain.

Configure the External definition and remote with
[manage-externals.yml](manage-externals.yml) on servers with the expanded
workflow router, or through the web interface. Find its numeric ID with
`flatman_external_ref_info`. To pull and publish it:

```bash
ansible-playbook playbooks/publish-external.yml \
  -e external_ref_id=12 -e external_action=pull
```

Pull deliberately queues a fresh upstream fetch on every run. To publish an
already-pulled ref instead, omit `external_action=pull`; the default `publish`
action skips a ref that is already published.

Promote a published Flatpak build or External version to stable:

```bash
ansible-playbook playbooks/promote-flatpak.yml \
  -e build_id=48 -e target_repository=stable
ansible-playbook playbooks/promote-external.yml \
  -e external_ref_id=12 -e external_ref_version_id=7 -e target_repository=stable
```

`build_id` is the build history record ID returned by `flatman_build_info`,
not the package ID or build attempt number. For Externals, omit
`external_ref_version_id` to select the latest published version. Pin it for
repeatable releases. Use `target_repository` to choose each eligible child
repository in turn.

Both promotion examples wait for completion, reuse an existing pending or
completed promotion, and queue again after failure. Existing in-progress
promotions are awaited without reporting a change. Use `flatman_promotion_info`
with `kind: build` (the default) or `kind: external` to query promotion status.
All three examples support `--check` without queueing tasks. In check mode,
new promotion target eligibility is not validated by the server.

Setting a package's `status: published` only edits a state
field; changing its `repository` or `branch` only edits configuration.
Neither performs the actual content-copying, signing or promotion workflow.
Likewise, `flatman_app_pick` features an app editorially; it does not promote
it between repositories.

## Other examples

The following examples require the expanded workflow router. Adjust placeholder
URLs and IDs before running. Build and maintenance actions are opt-in.

| Playbook | Purpose |
|---|---|
| [manage-externals.yml](manage-externals.yml) | Configure a remote and External definition; source repository must exist |
| [manage-access.yml](manage-access.yml) | Configure an organisation and role; supply `user_id` |
| [manage-buildstream.yml](manage-buildstream.yml) | Configure a source; supply `repository_id`; optionally set `do_build=true` |
| [manage-clients.yml](manage-clients.yml) | Read inventory; optionally replace organisation assignments |
| [server-maintenance.yml](server-maintenance.yml) | Read settings/catalogue; optionally set `run_cleanup=true` |
| [manage-rpm.yml](manage-rpm.yml) | Configure a package; supply `distribution_ids`; optionally set `do_build=true` |
| [renew-gpg-key.yml](renew-gpg-key.yml) | Renew an existing key; supply `gpg_key_id`; opt in with `do_renew=true` |
| [test-ldap.yml](test-ldap.yml) | Test connection and user search; supply directory settings and optional Vault credentials |
| [discover-rpm-source.yml](discover-rpm-source.yml) | Discover branches and spec files; supply `rpm_git_url` and optional `rpm_branch` |

For example:

```bash
ansible-playbook playbooks/manage-externals.yml -e repository_name=testing
ansible-playbook playbooks/manage-access.yml -e user_id=12
ansible-playbook playbooks/manage-buildstream.yml -e repository_id=2
ansible-playbook playbooks/manage-rpm.yml -e '{"distribution_ids": [2]}'
ansible-playbook playbooks/renew-gpg-key.yml -e gpg_key_id=3 -e '{"do_renew": true}'
ansible-playbook playbooks/test-ldap.yml -e ldap_hostname=ldap.example.com -e ldap_base_dn=dc=example,dc=com -e ldap_search_username=alice
ansible-playbook playbooks/discover-rpm-source.yml -e rpm_git_url=https://github.com/example/app-rpm.git
```

The renewal, LDAP and RPM discovery examples require server release 1.0.34
or later. Renewal is imperative and recalculates expiry from today; do not
enable it on every routine configuration run. LDAP tests and RPM discovery
report unchanged on success and skip requests in check mode. LDAP failures,
including HTTP 200 responses with `ok: false`, fail the task. LDAP tests accept
`ldap_source_id` to reuse a stored bind password, or `vault_ldap_bind_password`
from Ansible Vault. All other directory settings must still be provided.

See the [expanded API guide](../docs/expanded-api.md) for LDAP, granular
permissions, Satellite, release lifecycle and the complete action matrix.
Check mode skips dependent tasks when creation only predicts a resource and
therefore cannot provide a server-assigned ID.

- [provision-repository.yml](provision-repository.yml): signing key and
  stable/beta repositories.
- [smoke.yml](smoke.yml): connectivity and API checks.
- [report.yml](report.yml): read-only reporting.
