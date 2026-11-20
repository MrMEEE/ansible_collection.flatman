# Collection module reference

Complete module documentation rendered by `ansible-doc`, including options,
defaults, requirements, attributes, examples, notes, related modules, and return
values. Each module's `DOCUMENTATION`, `EXAMPLES`, and `RETURN` blocks in
`plugins/modules/` are the source of truth for this generated reference.

Regenerate from the collection root with:

```bash
bash docs/generate-module-reference.sh
```

## Modules

- [flatman_app_info](#flatman_app_info)
- [flatman_app_metadata](#flatman_app_metadata)
- [flatman_app_pick](#flatman_app_pick)
- [flatman_app_pick_info](#flatman_app_pick_info)
- [flatman_app_stats_info](#flatman_app_stats_info)
- [flatman_artifact](#flatman_artifact)
- [flatman_artifact_info](#flatman_artifact_info)
- [flatman_build_info](#flatman_build_info)
- [flatman_build_log_info](#flatman_build_log_info)
- [flatman_collection_info](#flatman_collection_info)
- [flatman_external_ref_action](#flatman_external_ref_action)
- [flatman_external_ref_info](#flatman_external_ref_info)
- [flatman_git_branch_info](#flatman_git_branch_info)
- [flatman_gpg_key](#flatman_gpg_key)
- [flatman_gpg_key_info](#flatman_gpg_key_info)
- [flatman_moderation_info](#flatman_moderation_info)
- [flatman_moderation_request](#flatman_moderation_request)
- [flatman_moderation_review](#flatman_moderation_review)
- [flatman_package](#flatman_package)
- [flatman_package_action](#flatman_package_action)
- [flatman_package_info](#flatman_package_info)
- [flatman_platform_info](#flatman_platform_info)
- [flatman_promotion](#flatman_promotion)
- [flatman_promotion_batch](#flatman_promotion_batch)
- [flatman_promotion_info](#flatman_promotion_info)
- [flatman_promotion_ready_info](#flatman_promotion_ready_info)
- [flatman_quality_moderation](#flatman_quality_moderation)
- [flatman_quality_moderation_info](#flatman_quality_moderation_info)
- [flatman_repository](#flatman_repository)
- [flatman_repository_info](#flatman_repository_info)
- [flatman_repository_subset](#flatman_repository_subset)
- [flatman_repository_subset_info](#flatman_repository_subset_info)
- [flatman_resource](#flatman_resource)
- [flatman_resource_info](#flatman_resource_info)
- [flatman_search_info](#flatman_search_info)
- [flatman_status_info](#flatman_status_info)
- [flatman_token](#flatman_token)
- [flatman_token_info](#flatman_token_info)
- [flatman_usage_info](#flatman_usage_info)
- [flatman_user](#flatman_user)
- [flatman_user_info](#flatman_user_info)
- [flatman_user_profile](#flatman_user_profile)
- [flatman_user_profile_info](#flatman_user_profile_info)
- [flatman_workflow_action](#flatman_workflow_action)
- [flatman_year_in_review_info](#flatman_year_in_review_info)

### flatman_app_info

**FQCN:** `mrmeee.flatman.flatman_app_info`

```text

  Retrieve the public application catalogue from the Flathub
  compatible `/api/v2' API.
  Wraps the `/api/v2/appstream' endpoints, optionally enriched with
  summary, addon and fullscreen data.
  These endpoints are public, so `api_token' is optional.

[1mOPTIONS[0m (red indicates it is required):

   api_token  API token used for authentication, sent in an
              `Authorization' header of the form `Token <api_token>'.
              Create one in the web UI under your user profile, or
              with the `createapitoken' management command.
              May also be set with the `FLATMAN_API_TOKEN' environment
              variable.
              Not required for the public read-only `/api/v2'
              endpoints.
        default: null
        type: str

   app_id  Return only the application with this ID, for example
           `org.example.App'.
           When omitted, every published application is returned.
        default: null
        type: str

   client_cert  Path to a PEM formatted client certificate used for
                mutual TLS.
        default: null
        type: path

   client_key  Path to the PEM formatted private key matching
               `client_cert'.
        default: null
        type: path

   include  Extra sub-resources to fetch for the requested
            application.
            Only honoured when `app_id' is set.
            `summary' adds a `summary' key, `addon' adds an `addons'
            key and `fullscreen' adds an `is_fullscreen' key.
        choices: [summary, addon, fullscreen]
        default: null
        elements: str
        type: list

   include_names  Add best-effort human-readable companion fields for
                  related resource IDs in returned records.
                  Original numeric IDs are retained. Set to `false' to
                  skip the extra lookup requests.
        default: true
        type: bool

   sort    Sort order requested from the server.
           Only honoured when `app_id' is not set, because the single
           application form takes no query parameters.
        choices: [alphabetical, recent, recently-updated]
        default: null
        type: str

   timeout  Socket timeout in seconds for each individual HTTP
            request.
        default: 30
        type: int

   [1murl[0m     Base URL of the flat-manager-django instance, for example
           `https://flatman.example.com'.
           May also be set with the `FLATMAN_URL' environment
           variable.
        type: str

   validate_certs  Whether to validate the TLS certificate of the
                   flat-manager server.
                   May also be set with the `FLATMAN_VALIDATE_CERTS'
                   environment variable.
        default: true
        type: bool

[1mATTRIBUTES:[0m

        [4mcheck_mode:[0m
        description: This module makes no changes, so it fully supports `check_mode'.
        support: full

        [4mdiff_mode:[0m
        description: This module makes no changes, so it never reports a diff.
        support: N/A

[1mSEE ALSO:[0m
      * Module mrmeee.flatman.flatman_app_metadata
      * Module mrmeee.flatman.flatman_app_stats_info
      * Module mrmeee.flatman.flatman_search_info

[1mREQUIREMENTS:[0m  ansible-core >= 2.15


[1mAUTHOR[0m: MrMEEE (@MrMEEE)

[1mEXAMPLES:[0m
- name: List every published application
  mrmeee.flatman.flatman_app_info:
    url: https://flatman.example.com
  register: catalogue

- name: List applications ordered by last update
  mrmeee.flatman.flatman_app_info:
    url: https://flatman.example.com
    sort: recently-updated
  register: recent_apps

- name: Fetch one application with all extra data
  mrmeee.flatman.flatman_app_info:
    url: https://flatman.example.com
    app_id: org.example.App
    include:
      - summary
      - addon
      - fullscreen
  register: app

[1mRETURN VALUES:[0m

   apps    The matching applications.
           Contains at most one element when `app_id' is set, and is
           empty when that application does not exist.
        elements: dict
        returned: always
        sample: [{arch: x86_64, branch: stable, categories: [Utility], developer: Example Inc, id: org.example.App,
            mobile: false, name: Example App, repository: stable, summary: A small example
              application, verified: true, version: 1.2.3}]
        type: list


```


### flatman_app_metadata

**FQCN:** `mrmeee.flatman.flatman_app_metadata`

```text

  Update the cached public metadata that the Flathub compatible
  `/api/v2' API exposes for an application.
  Wraps the `/api/v2/appstream/<app_id>/metadata' endpoint.
  This endpoint requires an administrator API token, unlike the
  read-only `/api/v2' endpoints.

[1mOPTIONS[0m (red indicates it is required):

   api_token  API token used for authentication, sent in an
              `Authorization' header of the form `Token <api_token>'.
              Create one in the web UI under your user profile, or
              with the `createapitoken' management command.
              May also be set with the `FLATMAN_API_TOKEN' environment
              variable.
              Not required for the public read-only `/api/v2'
              endpoints.
        default: null
        type: str

   [1mapp_id[0m  Application ID of the package, for example
           `org.example.App'.
        type: str

   categories  Categories the application belongs to.
               Replaces the existing list when specified.
        default: null
        elements: str
        type: list

   client_cert  Path to a PEM formatted client certificate used for
                mutual TLS.
        default: null
        type: path

   client_key  Path to the PEM formatted private key matching
               `client_cert'.
        default: null
        type: path

   description  Long form description of the application.
        default: null
        type: str

   developer_name  Name of the developer or vendor of the application.
        default: null
        type: str

   homepage  Homepage URL of the application.
        default: null
        type: str

   icon_url  URL of the application icon.
        default: null
        type: str

   include_names  Add best-effort human-readable companion fields for
                  related resource IDs in returned records.
                  Original numeric IDs are retained. Set to `false' to
                  skip the extra lookup requests.
        default: true
        type: bool

   is_mobile  Whether the application is marked as suitable for mobile
              form factors.
        default: null
        type: bool

   is_verified  Whether the application is marked as verified.
        default: null
        type: bool

   keywords  Search keywords for the application.
             Replaces the existing list when specified.
        default: null
        elements: str
        type: list

   screenshots  Screenshot entries stored verbatim in the metadata.
                Each element may be a plain URL string or a
                dictionary, depending on your conventions.
        default: null
        elements: raw
        type: list

   summary  Short one line summary of the application.
        default: null
        type: str

   timeout  Socket timeout in seconds for each individual HTTP
            request.
        default: 30
        type: int

   [1murl[0m     Base URL of the flat-manager-django instance, for example
           `https://flatman.example.com'.
           May also be set with the `FLATMAN_URL' environment
           variable.
        type: str

   validate_certs  Whether to validate the TLS certificate of the
                   flat-manager server.
                   May also be set with the `FLATMAN_VALIDATE_CERTS'
                   environment variable.
        default: true
        type: bool

[1mATTRIBUTES:[0m

        [4mcheck_mode:[0m
        description: Can run in `check_mode' and return the changes that would be made.
        support: full

        [4mdiff_mode:[0m
        description: Returns details on what has changed (or would have changed) when `--diff'
          is used.
        support: full

[1mSEE ALSO:[0m
      * Module mrmeee.flatman.flatman_app_info
      * Module mrmeee.flatman.flatman_search_info

[1mREQUIREMENTS:[0m  ansible-core >= 2.15


[1mAUTHOR[0m: MrMEEE (@MrMEEE)

[1mEXAMPLES:[0m
- name: Publish metadata for an application
  mrmeee.flatman.flatman_app_metadata:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    app_id: org.example.App
    summary: A small example application
    developer_name: Example Inc
    homepage: https://example.com/app
    categories:
      - Utility
      - Development

- name: Mark an application as verified and mobile friendly
  mrmeee.flatman.flatman_app_metadata:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    app_id: org.example.App
    is_verified: true
    is_mobile: true

- name: Replace the screenshot list
  mrmeee.flatman.flatman_app_metadata:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    app_id: org.example.App
    screenshots:
      - https://example.com/app/shot1.png
      - https://example.com/app/shot2.png

[1mRETURN VALUES:[0m

   app     The public application entry after the change, in the same
           shape as `/api/v2/appstream/<app_id>'.
           In check mode this is the locally computed preview of the
           entry.
        returned: always
        sample:
          arch: x86_64
          branch: stable
          categories:
          - Utility
          description: A slightly longer description.
          developer: Example Inc
          homepage: https://example.com/app
          icon_url: https://example.com/app/icon.png
          id: org.example.App
          keywords:
          - example
          mobile: false
          name: Example App
          repository: stable
          screenshots: []
          summary: A small example application
          verified: true
          version: 1.2.3
        type: dict


```


### flatman_app_pick

**FQCN:** `mrmeee.flatman.flatman_app_pick`

```text

  Creates, updates and deletes the dated editorial app selections
  exposed by the Flathub compatible API.
  Creates use `POST /api/v2/app-picks/admin/curated-app-selections',
  updates use `PUT
  /api/v2/app-picks/admin/curated-app-selections/<id>' and deletions
  use the matching `DELETE'.
  The admin endpoint is used for every kind of selection because it is
  the only create endpoint that takes an explicit `kind', so a single
  code path covers app of the day, app of the week and curated
  selections.
  All of these endpoints require an API token belonging to an
  administrator.

[1mOPTIONS[0m (red indicates it is required):

   api_token  API token used for authentication, sent in an
              `Authorization' header of the form `Token <api_token>'.
              Create one in the web UI under your user profile, or
              with the `createapitoken' management command.
              May also be set with the `FLATMAN_API_TOKEN' environment
              variable.
              Not required for the public read-only `/api/v2'
              endpoints.
        default: null
        type: str

   app_id  Application ID (the Flatpak package ID) that is being
           picked.
           Required to create a selection, and required together with
           `kind' and `date' to look one up.
           The application must already be published.
        default: null
        type: str

   client_cert  Path to a PEM formatted client certificate used for
                mutual TLS.
        default: null
        type: path

   client_key  Path to the PEM formatted private key matching
               `client_cert'.
        default: null
        type: path

   date    ISO date the selection is shown on, for example
           `2026-02-14'.
        default: null
        type: str

   description  Editorial description shown with the selection.
                Defaults to an empty string on the server.
        default: null
        type: str

   id      Numeric ID of an existing selection.
           When omitted, an existing selection is looked up by
           `app_id', `kind' and `date', which together are unique on
           the server.
        default: null
        type: int

   include_names  Add best-effort human-readable companion fields for
                  related resource IDs in returned records.
                  Original numeric IDs are retained. Set to `false' to
                  skip the extra lookup requests.
        default: true
        type: bool

   kind    Kind of editorial selection, taken from the server side
           choices.
        choices: [day, week, curated]
        default: null
        type: str

   rank    Ordering rank within a single date. Defaults to `0' on the
           server.
        default: null
        type: int

   state   Whether the selection should exist or not.
        choices: [present, absent]
        default: present
        type: str

   timeout  Socket timeout in seconds for each individual HTTP
            request.
        default: 30
        type: int

   title   Editorial title shown with the selection. Defaults to an
           empty string on the server.
        default: null
        type: str

   [1murl[0m     Base URL of the flat-manager-django instance, for example
           `https://flatman.example.com'.
           May also be set with the `FLATMAN_URL' environment
           variable.
        type: str

   validate_certs  Whether to validate the TLS certificate of the
                   flat-manager server.
                   May also be set with the `FLATMAN_VALIDATE_CERTS'
                   environment variable.
        default: true
        type: bool

[1mATTRIBUTES:[0m

        [4mcheck_mode:[0m
        description: Can run in `check_mode' and return the changes that would be made.
        support: full

        [4mdiff_mode:[0m
        description: Returns details on what has changed (or would have changed) when `--diff'
          is used.
        support: full

[1mSEE ALSO:[0m
      * Module mrmeee.flatman.flatman_app_pick_info

[1mREQUIREMENTS:[0m  ansible-core >= 2.15


[1mAUTHOR[0m: MrMEEE (@MrMEEE)

[1mEXAMPLES:[0m
- name: Pick an application as app of the day
  mrmeee.flatman.flatman_app_pick:
    url: https://flatman.example.com
    api_token: "{{ flatman_admin_token }}"
    app_id: org.example.Editor
    kind: day
    date: '2026-02-14'
    title: Editor
    description: A fast plain text editor

- name: Reorder a known curated selection
  mrmeee.flatman.flatman_app_pick:
    url: https://flatman.example.com
    api_token: "{{ flatman_admin_token }}"
    id: 42
    rank: 1

- name: Remove an app of the week selection
  mrmeee.flatman.flatman_app_pick:
    url: https://flatman.example.com
    api_token: "{{ flatman_admin_token }}"
    app_id: org.example.Game
    kind: week
    date: '2026-02-09'
    state: absent

[1mRETURN VALUES:[0m

   app_pick  The app pick selection as returned by the API after the
             change.
        returned: when `state=present'
        sample:
          app_id: org.example.Editor
          date: '2026-02-14'
          description: A fast plain text editor
          id: 42
          kind: day
          name: Editor
          rank: 0
          title: Editor
        type: dict


```


### flatman_app_pick_info

**FQCN:** `mrmeee.flatman.flatman_app_pick_info`

```text

  Reads the dated editorial app selections exposed by the Flathub
  compatible API.
  Wraps the `/api/v2/app-picks' endpoints.

[1mOPTIONS[0m (red indicates it is required):

   api_token  API token used for authentication, sent in an
              `Authorization' header of the form `Token <api_token>'.
              Create one in the web UI under your user profile, or
              with the `createapitoken' management command.
              May also be set with the `FLATMAN_API_TOKEN' environment
              variable.
              Not required for the public read-only `/api/v2'
              endpoints.
        default: null
        type: str

   client_cert  Path to a PEM formatted client certificate used for
                mutual TLS.
        default: null
        type: path

   client_key  Path to the PEM formatted private key matching
               `client_cert'.
        default: null
        type: path

   date    ISO date to read the selections for, for example
           `2026-02-14'.
           Required for `scope=apps-of-the-week', `scope=curated' and
           `scope=admin-apps-of-the-week', because their URL contains
           the date.
           Optional for `scope=app-of-the-day', where it switches to
           the dated endpoint.
        default: null
        type: str

   id      Return only the selection with this numeric ID.
           Only meaningful with `scope=admin-selections', because the
           detail endpoint itself is write only, so the filtering is
           done by the module.
        default: null
        type: int

   include_names  Add best-effort human-readable companion fields for
                  related resource IDs in returned records.
                  Original numeric IDs are retained. Set to `false' to
                  skip the extra lookup requests.
        default: true
        type: bool

   [1mscope[0m   Which set of app picks to read.
           `app-of-the-day' reads `/api/v2/app-picks/app-of-the-day',
           or the dated variant when `date' is set.
           `app-of-the-week' reads
           `/api/v2/app-picks/app-of-the-week', which always uses the
           current date.
           `apps-of-the-week' reads
           `/api/v2/app-picks/apps-of-the-week/<date>'.
           `curated' reads
           `/api/v2/app-picks/curated-app-selections/<date>'.
           `admin-selections' reads
           `/api/v2/app-picks/admin/curated-app-selections' and needs
           an administrator token. Set `id' to pick a single selection
           out of that list.
           `admin-apps-of-the-week' reads
           `/api/v2/app-picks/admin/apps-of-the-week/<date>' and needs
           an administrator token.
           `themes' reads
           `/api/v2/app-picks/admin/curated-app-selection-themes' and
           needs an administrator token.
        choices: [app-of-the-day, app-of-the-week, apps-of-the-week, curated, admin-selections, admin-apps-of-the-week,
          themes]
        type: str

   timeout  Socket timeout in seconds for each individual HTTP
            request.
        default: 30
        type: int

   [1murl[0m     Base URL of the flat-manager-django instance, for example
           `https://flatman.example.com'.
           May also be set with the `FLATMAN_URL' environment
           variable.
        type: str

   validate_certs  Whether to validate the TLS certificate of the
                   flat-manager server.
                   May also be set with the `FLATMAN_VALIDATE_CERTS'
                   environment variable.
        default: true
        type: bool

[1mATTRIBUTES:[0m

        [4mcheck_mode:[0m
        description: This module makes no changes, so it fully supports `check_mode'.
        support: full

        [4mdiff_mode:[0m
        description: This module makes no changes, so it never reports a diff.
        support: N/A

[1mSEE ALSO:[0m
      * Module mrmeee.flatman.flatman_app_pick

[1mREQUIREMENTS:[0m  ansible-core >= 2.15


[1mAUTHOR[0m: MrMEEE (@MrMEEE)

[1mEXAMPLES:[0m
- name: Read today's app of the day
  mrmeee.flatman.flatman_app_pick_info:
    url: https://flatman.example.com
    scope: app-of-the-day
  register: today

- name: Read the apps of the week for a given week
  mrmeee.flatman.flatman_app_pick_info:
    url: https://flatman.example.com
    scope: apps-of-the-week
    date: '2026-02-09'
  register: this_week

- name: Read every curated selection as an administrator
  mrmeee.flatman.flatman_app_pick_info:
    url: https://flatman.example.com
    api_token: "{{ flatman_admin_token }}"
    scope: admin-selections
  register: selections

[1mRETURN VALUES:[0m

   app_picks  The matching app pick selections.
              For `scope=themes' the entries are theme objects with
              `id', `name' and `description' keys.
              When `id' is used the list holds at most the single
              matching selection.
        elements: dict
        returned: always
        sample: [{app_id: org.example.Editor, date: '2026-02-14', description: A fast plain text editor,
            id: 42, kind: day, name: Editor, rank: 0, title: Editor}]
        type: list


```


### flatman_app_stats_info

**FQCN:** `mrmeee.flatman.flatman_app_stats_info`

```text

  Retrieve global catalogue statistics, or the statistics of a single
  published application.
  Wraps the `/api/v2/stats/' endpoints.
  These endpoints are public, so `api_token' is optional.

[1mOPTIONS[0m (red indicates it is required):

   api_token  API token used for authentication, sent in an
              `Authorization' header of the form `Token <api_token>'.
              Create one in the web UI under your user profile, or
              with the `createapitoken' management command.
              May also be set with the `FLATMAN_API_TOKEN' environment
              variable.
              Not required for the public read-only `/api/v2'
              endpoints.
        default: null
        type: str

   app_id  Return the statistics of this application only, for example
           `org.example.App'.
           When omitted, server wide catalogue counters are returned
           instead.
        default: null
        type: str

   client_cert  Path to a PEM formatted client certificate used for
                mutual TLS.
        default: null
        type: path

   client_key  Path to the PEM formatted private key matching
               `client_cert'.
        default: null
        type: path

   include_names  Add best-effort human-readable companion fields for
                  related resource IDs in returned records.
                  Original numeric IDs are retained. Set to `false' to
                  skip the extra lookup requests.
        default: true
        type: bool

   timeout  Socket timeout in seconds for each individual HTTP
            request.
        default: 30
        type: int

   [1murl[0m     Base URL of the flat-manager-django instance, for example
           `https://flatman.example.com'.
           May also be set with the `FLATMAN_URL' environment
           variable.
        type: str

   validate_certs  Whether to validate the TLS certificate of the
                   flat-manager server.
                   May also be set with the `FLATMAN_VALIDATE_CERTS'
                   environment variable.
        default: true
        type: bool

[1mATTRIBUTES:[0m

        [4mcheck_mode:[0m
        description: This module makes no changes, so it fully supports `check_mode'.
        support: full

        [4mdiff_mode:[0m
        description: This module makes no changes, so it never reports a diff.
        support: N/A

[1mSEE ALSO:[0m
      * Module mrmeee.flatman.flatman_app_info
      * Module mrmeee.flatman.flatman_usage_info

[1mREQUIREMENTS:[0m  ansible-core >= 2.15


[1mAUTHOR[0m: MrMEEE (@MrMEEE)

[1mEXAMPLES:[0m
- name: Get global catalogue statistics
  mrmeee.flatman.flatman_app_stats_info:
    url: https://flatman.example.com
  register: totals

- name: Show how many applications are published
  ansible.builtin.debug:
    msg: "{{ totals.stats.apps }} applications in {{ totals.stats.repositories }} repositories"

- name: Get statistics for a single application
  mrmeee.flatman.flatman_app_stats_info:
    url: https://flatman.example.com
    app_id: org.example.App
  register: app_stats

[1mRETURN VALUES:[0m

   stats   Global counters when `app_id' is not set, otherwise the
           statistics of that application.
           Empty when the requested application does not exist.
        returned: always
        sample:
          app_id: org.example.App
          build_number: 12
          builds: 12
          updated_at: '2026-01-05T09:15:00+00:00'
          usage:
            observations: 431
            unique_clients: 87
          version: 1.2.3
        type: dict


```


### flatman_artifact

**FQCN:** `mrmeee.flatman.flatman_artifact`

```text

  Register, update and delete build artifact records on a
  flat-manager-django server.
  Wraps the `/api/artifacts/' endpoint.

[1mOPTIONS[0m (red indicates it is required):

   api_token  API token used for authentication, sent in an
              `Authorization' header of the form `Token <api_token>'.
              Create one in the web UI under your user profile, or
              with the `createapitoken' management command.
              May also be set with the `FLATMAN_API_TOKEN' environment
              variable.
              Not required for the public read-only `/api/v2'
              endpoints.
        default: null
        type: str

   build_id  Numeric ID of the build the artifact belongs to.
             Required when the artifact has to be created, and used to
             narrow the search server side.
        default: null
        type: int

   checksum  Checksum of the artifact file, normally a SHA256 hex
             digest.
        default: null
        type: str

   client_cert  Path to a PEM formatted client certificate used for
                mutual TLS.
        default: null
        type: path

   client_key  Path to the PEM formatted private key matching
               `client_cert'.
        default: null
        type: path

   file_path  Path of the artifact file on the flat-manager server.
        default: null
        type: str

   file_size  Size of the artifact file in bytes.
        default: null
        type: int

   [1mfilename[0m  Name of the artifact file, for example
             `org.example.MyApp.flatpak'.
             Together with `build_id' this forms the unique key used
             for idempotency.
        type: str

   include_names  Add best-effort human-readable companion fields for
                  related resource IDs in returned records.
                  Original numeric IDs are retained. Set to `false' to
                  skip the extra lookup requests.
        default: true
        type: bool

   state   Whether the artifact record should exist or not.
        choices: [present, absent]
        default: present
        type: str

   timeout  Socket timeout in seconds for each individual HTTP
            request.
        default: 30
        type: int

   [1murl[0m     Base URL of the flat-manager-django instance, for example
           `https://flatman.example.com'.
           May also be set with the `FLATMAN_URL' environment
           variable.
        type: str

   validate_certs  Whether to validate the TLS certificate of the
                   flat-manager server.
                   May also be set with the `FLATMAN_VALIDATE_CERTS'
                   environment variable.
        default: true
        type: bool

[1mATTRIBUTES:[0m

        [4mcheck_mode:[0m
        description: Can run in `check_mode' and return the changes that would be made.
        support: full

        [4mdiff_mode:[0m
        description: Returns details on what has changed (or would have changed) when `--diff'
          is used.
        support: full

[1mNOTES:[0m
      * This module only manages the artifact metadata record.
        The file itself has to be placed on the server by other
        means, because the API offers no multipart upload that
        this collection can use.
      * The owning build is written as `build_id' but is not
        returned by the API, so `build_id' is never compared for
        idempotency.

[1mSEE ALSO:[0m
      * Module mrmeee.flatman.flatman_artifact_info
      * Module mrmeee.flatman.flatman_build_info

[1mREQUIREMENTS:[0m  ansible-core >= 2.15


[1mAUTHOR[0m: MrMEEE (@MrMEEE)

[1mEXAMPLES:[0m
- name: Register a bundle produced by build 48
  mrmeee.flatman.flatman_artifact:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    build_id: 48
    filename: org.example.MyApp.flatpak
    file_path: /var/lib/flat-manager/artifacts/48/org.example.MyApp.flatpak
    file_size: 48271360
    checksum: 4a3b1c8d9e0f1a2b3c4d5e6f708192a3b4c5d6e7f8091a2b3c4d5e6f70819200

- name: Correct the recorded size of an artifact
  mrmeee.flatman.flatman_artifact:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    build_id: 48
    filename: org.example.MyApp.flatpak
    file_size: 48271872

- name: Remove an artifact record
  mrmeee.flatman.flatman_artifact:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    build_id: 48
    filename: org.example.MyApp.flatpak
    state: absent

[1mRETURN VALUES:[0m

   artifact  The artifact as returned by the API after the change.
        returned: when `state=present'
        sample:
          checksum: 4a3b1c8d9e0f1a2b3c4d5e6f708192a3b4c5d6e7f8091a2b3c4d5e6f70819200
          file_path: /var/lib/flat-manager/artifacts/48/org.example.MyApp.flatpak
          file_size: 48271360
          filename: org.example.MyApp.flatpak
          id: 91
          uploaded_at: '2026-04-11T09:31:02Z'
        type: dict


```


### flatman_artifact_info

**FQCN:** `mrmeee.flatman.flatman_artifact_info`

```text

  Retrieve one or more build artifact records from a
  flat-manager-django server.
  Wraps the `/api/artifacts/' endpoint.

[1mOPTIONS[0m (red indicates it is required):

   api_token  API token used for authentication, sent in an
              `Authorization' header of the form `Token <api_token>'.
              Create one in the web UI under your user profile, or
              with the `createapitoken' management command.
              May also be set with the `FLATMAN_API_TOKEN' environment
              variable.
              Not required for the public read-only `/api/v2'
              endpoints.
        default: null
        type: str

   build_id  Return only artifacts belonging to the build with this
             numeric ID.
        default: null
        type: int

   client_cert  Path to a PEM formatted client certificate used for
                mutual TLS.
        default: null
        type: path

   client_key  Path to the PEM formatted private key matching
               `client_cert'.
        default: null
        type: path

   filename  Return only the artifact with this exact filename.
        default: null
        type: str

   id      Return only the artifact with this numeric ID.
        default: null
        type: int

   include_names  Add best-effort human-readable companion fields for
                  related resource IDs in returned records.
                  Original numeric IDs are retained. Set to `false' to
                  skip the extra lookup requests.
        default: true
        type: bool

   search  Free text search across the artifact filename.
        default: null
        type: str

   timeout  Socket timeout in seconds for each individual HTTP
            request.
        default: 30
        type: int

   [1murl[0m     Base URL of the flat-manager-django instance, for example
           `https://flatman.example.com'.
           May also be set with the `FLATMAN_URL' environment
           variable.
        type: str

   validate_certs  Whether to validate the TLS certificate of the
                   flat-manager server.
                   May also be set with the `FLATMAN_VALIDATE_CERTS'
                   environment variable.
        default: true
        type: bool

[1mATTRIBUTES:[0m

        [4mcheck_mode:[0m
        description: This module makes no changes, so it fully supports `check_mode'.
        support: full

        [4mdiff_mode:[0m
        description: This module makes no changes, so it never reports a diff.
        support: N/A

[1mSEE ALSO:[0m
      * Module mrmeee.flatman.flatman_artifact
      * Module mrmeee.flatman.flatman_build_info

[1mREQUIREMENTS:[0m  ansible-core >= 2.15


[1mAUTHOR[0m: MrMEEE (@MrMEEE)

[1mEXAMPLES:[0m
- name: List every artifact
  mrmeee.flatman.flatman_artifact_info:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
  register: artifacts

- name: List the artifacts of one build
  mrmeee.flatman.flatman_artifact_info:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    build_id: 48
  register: build_artifacts

- name: Show the total size of the artifacts of a build
  ansible.builtin.debug:
    msg: "{{ build_artifacts.artifacts | map(attribute='file_size') | sum }} bytes"

[1mRETURN VALUES:[0m

   artifacts  The matching artifacts.
        elements: dict
        returned: always
        sample: [{checksum: 4a3b1c8d9e0f1a2b3c4d5e6f708192a3b4c5d6e7f8091a2b3c4d5e6f70819200, file_path: /var/lib/flat-manager/artifacts/48/org.example.MyApp.flatpak,
            file_size: 48271360, filename: org.example.MyApp.flatpak, id: 91, uploaded_at: '2026-04-11T09:31:02Z'}]
        type: list


```


### flatman_build_info

**FQCN:** `mrmeee.flatman.flatman_build_info`

```text

  Retrieve build history records from a flat-manager-django server.
  Wraps the read only `/api/builds/' endpoint.

[1mOPTIONS[0m (red indicates it is required):

   api_token  API token used for authentication, sent in an
              `Authorization' header of the form `Token <api_token>'.
              Create one in the web UI under your user profile, or
              with the `createapitoken' management command.
              May also be set with the `FLATMAN_API_TOKEN' environment
              variable.
              Not required for the public read-only `/api/v2'
              endpoints.
        default: null
        type: str

   build_number  Return only the build with this build attempt number.
        default: null
        type: int

   client_cert  Path to a PEM formatted client certificate used for
                mutual TLS.
        default: null
        type: path

   client_key  Path to the PEM formatted private key matching
               `client_cert'.
        default: null
        type: path

   full    Whether to return the complete log output embedded in every
           build.
           The API embeds every log line of a build, which makes the
           response very large; when this is `false' the `logs' key is
           removed from each result.
        default: false
        type: bool

   id      Return only the build with this numeric ID.
        default: null
        type: int

   include_names  Add best-effort human-readable companion fields for
                  related resource IDs in returned records.
                  Original numeric IDs are retained. Set to `false' to
                  skip the extra lookup requests.
        default: true
        type: bool

   package  Flatpak application ID of the package whose builds should
            be returned, for example `org.example.MyApp'.
            Mutually exclusive with `package_pk'.
        default: null
        type: str

   package_pk  Numeric ID of the package whose builds should be
               returned.
               Mutually exclusive with `package'.
        default: null
        type: int

   search  Free text search across the application ID and the package
           name of the owning package.
        default: null
        type: str

   status  Filter builds by state.
        choices: [building, built, committing, committed, publishing, published, failed, cancelled]
        default: null
        type: str

   timeout  Socket timeout in seconds for each individual HTTP
            request.
        default: 30
        type: int

   [1murl[0m     Base URL of the flat-manager-django instance, for example
           `https://flatman.example.com'.
           May also be set with the `FLATMAN_URL' environment
           variable.
        type: str

   validate_certs  Whether to validate the TLS certificate of the
                   flat-manager server.
                   May also be set with the `FLATMAN_VALIDATE_CERTS'
                   environment variable.
        default: true
        type: bool

[1mATTRIBUTES:[0m

        [4mcheck_mode:[0m
        description: This module makes no changes, so it fully supports `check_mode'.
        support: full

        [4mdiff_mode:[0m
        description: This module makes no changes, so it never reports a diff.
        support: N/A

[1mSEE ALSO:[0m
      * Module mrmeee.flatman.flatman_build_log_info
      * Module mrmeee.flatman.flatman_package_info

[1mREQUIREMENTS:[0m  ansible-core >= 2.15


[1mAUTHOR[0m: MrMEEE (@MrMEEE)

[1mEXAMPLES:[0m
- name: List every build
  mrmeee.flatman.flatman_build_info:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
  register: builds

- name: List the failed builds of one package
  mrmeee.flatman.flatman_build_info:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    package: org.example.MyApp
    status: failed
  register: failures

- name: Fetch build attempt number 7 including its logs
  mrmeee.flatman.flatman_build_info:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    package: org.example.MyApp
    build_number: 7
    full: true
  register: attempt

[1mRETURN VALUES:[0m

   builds  The matching build history records.
        elements: dict
        returned: always
        sample: [{build_number: 7, commit_hash: 4a3b1c8d9e0f1a2b3c4d5e6f708192a3b4c5d6e7, completed_at: '2026-04-11T09:31:02Z',
            id: 48, package_id: 12, package_name: My Application, package_package_id: org.example.MyApp,
            repository_name: stable, started_at: '2026-04-11T09:12:44Z', status: published,
            version: 1.4.2}]
        type: list


```


### flatman_build_log_info

**FQCN:** `mrmeee.flatman.flatman_build_log_info`

```text

  Retrieve the log lines produced by a build.
  Wraps the `/api/builds/<id>/logs/' and `/api/packages/<id>/logs/'
  endpoints.

[1mOPTIONS[0m (red indicates it is required):

   api_token  API token used for authentication, sent in an
              `Authorization' header of the form `Token <api_token>'.
              Create one in the web UI under your user profile, or
              with the `createapitoken' management command.
              May also be set with the `FLATMAN_API_TOKEN' environment
              variable.
              Not required for the public read-only `/api/v2'
              endpoints.
        default: null
        type: str

   build_id  Numeric ID of the build whose log should be fetched.
             Exactly one of `build_id', `package_id' and `package_pk'
             is required.
        default: null
        type: int

   client_cert  Path to a PEM formatted client certificate used for
                mutual TLS.
        default: null
        type: path

   client_key  Path to the PEM formatted private key matching
               `client_cert'.
        default: null
        type: path

   include_names  Add best-effort human-readable companion fields for
                  related resource IDs in returned records.
                  Original numeric IDs are retained. Set to `false' to
                  skip the extra lookup requests.
        default: true
        type: bool

   level   Return only log entries with this level, for example `info'
           or `error'.
           The filtering happens on the controller, because the
           endpoint has no level filter.
        default: null
        type: str

   limit   Return only the last given number of log entries, after
           `level' filtering.
        default: null
        type: int

   package_id  Flatpak application ID of the package whose log should
               be fetched, for example `org.example.MyApp'.
               Exactly one of `build_id', `package_id' and
               `package_pk' is required.
        default: null
        type: str

   package_pk  Numeric ID of the package whose log should be fetched.
               Exactly one of `build_id', `package_id' and
               `package_pk' is required.
        default: null
        type: int

   timeout  Socket timeout in seconds for each individual HTTP
            request.
        default: 30
        type: int

   [1murl[0m     Base URL of the flat-manager-django instance, for example
           `https://flatman.example.com'.
           May also be set with the `FLATMAN_URL' environment
           variable.
        type: str

   validate_certs  Whether to validate the TLS certificate of the
                   flat-manager server.
                   May also be set with the `FLATMAN_VALIDATE_CERTS'
                   environment variable.
        default: true
        type: bool

[1mATTRIBUTES:[0m

        [4mcheck_mode:[0m
        description: This module makes no changes, so it fully supports `check_mode'.
        support: full

        [4mdiff_mode:[0m
        description: This module makes no changes, so it never reports a diff.
        support: N/A

[1mNOTES:[0m
      * Both log endpoints allow unauthenticated access, so
        `api_token' is optional for this module.
      * Resolving `package_id' to a numeric ID does require an
        authenticated request against `/api/packages/', so use
        `package_pk' or `build_id' when no token is available.

[1mSEE ALSO:[0m
      * Module mrmeee.flatman.flatman_build_info
      * Module mrmeee.flatman.flatman_package_action

[1mREQUIREMENTS:[0m  ansible-core >= 2.15


[1mAUTHOR[0m: MrMEEE (@MrMEEE)

[1mEXAMPLES:[0m
- name: Fetch the full log of one build
  mrmeee.flatman.flatman_build_log_info:
    url: https://flatman.example.com
    build_id: 48
  register: buildlog

- name: Show the last 20 log lines of a package
  mrmeee.flatman.flatman_build_log_info:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    package_id: org.example.MyApp
    limit: 20
  register: tail

- name: Collect only the error lines of a build
  mrmeee.flatman.flatman_build_log_info:
    url: https://flatman.example.com
    build_id: 48
    level: error
  register: errors

[1mRETURN VALUES:[0m

   build   The metadata the log endpoint returns alongside the log
           entries, without the log entries themselves.
           Empty when the endpoint returns a bare list of log entries.
        returned: always
        sample:
          build_number: 7
          package_id: org.example.MyApp
          status: published
          total_logs: 213
        type: dict

   logs    The matching log entries, oldest first.
        elements: dict
        returned: always
        sample: [{id: 981, level: info, message: 'Cloning https://github.com/example/org.example.MyApp',
            timestamp: '09:12:44'}]
        type: list


```


### flatman_collection_info

**FQCN:** `mrmeee.flatman.flatman_collection_info`

```text

  Retrieve the curated application collections and feeds of the
  Flathub compatible `/api/v2' API.
  Wraps the `/api/v2/collection' and `/api/v2/feed' endpoints.
  These endpoints are public, so `api_token' is optional.

[1mOPTIONS[0m (red indicates it is required):

   api_token  API token used for authentication, sent in an
              `Authorization' header of the form `Token <api_token>'.
              Create one in the web UI under your user profile, or
              with the `createapitoken' management command.
              May also be set with the `FLATMAN_API_TOKEN' environment
              variable.
              Not required for the public read-only `/api/v2'
              endpoints.
        default: null
        type: str

   client_cert  Path to a PEM formatted client certificate used for
                mutual TLS.
        default: null
        type: path

   client_key  Path to the PEM formatted private key matching
               `client_cert'.
        default: null
        type: path

   [1mcollection[0m  Which collection to retrieve.
               `popular' and `trending' rank applications by unique
               clients seen in the last 30 days.
               `recently-added' and `new' are equivalent and order by
               creation date.
               `category', `developer', `keyword' and `keywords' list
               names when `value' is not set.
               `keyword' and `keywords' always return the full keyword
               list and ignore `value'.
               `feed' retrieves `/api/v2/feed/<value>' and therefore
               requires `value'.
        choices: [popular, trending, recently-added, new, recently-updated, verified, mobile, alphabetical,
          category, developer, keyword, keywords, feed]
        type: str

   include_names  Add best-effort human-readable companion fields for
                  related resource IDs in returned records.
                  Original numeric IDs are retained. Set to `false' to
                  skip the extra lookup requests.
        default: true
        type: bool

   subcategories  Retrieve the subcategories of `value' instead of its
                  applications.
                  Only meaningful together with `collection=category'
                  and a `value'.
        default: false
        type: bool

   timeout  Socket timeout in seconds for each individual HTTP
            request.
        default: 30
        type: int

   [1murl[0m     Base URL of the flat-manager-django instance, for example
           `https://flatman.example.com'.
           May also be set with the `FLATMAN_URL' environment
           variable.
        type: str

   validate_certs  Whether to validate the TLS certificate of the
                   flat-manager server.
                   May also be set with the `FLATMAN_VALIDATE_CERTS'
                   environment variable.
        default: true
        type: bool

   value   The category name, developer name or feed name to look up.
           Required when `collection=feed' or when
           `subcategories=true'.
           Valid feed names are `new' and `recently-updated'.
        default: null
        type: str

[1mATTRIBUTES:[0m

        [4mcheck_mode:[0m
        description: This module makes no changes, so it fully supports `check_mode'.
        support: full

        [4mdiff_mode:[0m
        description: This module makes no changes, so it never reports a diff.
        support: N/A

[1mSEE ALSO:[0m
      * Module mrmeee.flatman.flatman_app_info
      * Module mrmeee.flatman.flatman_search_info

[1mREQUIREMENTS:[0m  ansible-core >= 2.15


[1mAUTHOR[0m: MrMEEE (@MrMEEE)

[1mEXAMPLES:[0m
- name: Get the most popular applications
  mrmeee.flatman.flatman_collection_info:
    url: https://flatman.example.com
    collection: popular
  register: popular

- name: List every known category
  mrmeee.flatman.flatman_collection_info:
    url: https://flatman.example.com
    collection: category
  register: categories

- name: Get the applications of one developer
  mrmeee.flatman.flatman_collection_info:
    url: https://flatman.example.com
    collection: developer
    value: Example Inc
  register: by_developer

- name: Read the new applications feed
  mrmeee.flatman.flatman_collection_info:
    url: https://flatman.example.com
    collection: feed
    value: new
  register: feed

[1mRETURN VALUES:[0m

   items   The contents of the requested collection.
           A list of application dictionaries for the application
           collections and feeds.
           A list of plain strings for the name listings, that is
           `collection=category', `collection=developer',
           `collection=keyword' and `collection=keywords' without a
           `value', and for subcategory lookups.
        elements: raw
        returned: always
        sample: [{developer: Example Inc, id: org.example.App, name: Example App, repository: stable,
            summary: A small example application, verified: true, version: 1.2.3}]
        type: list


```


### flatman_external_ref_action

**FQCN:** `mrmeee.flatman.flatman_external_ref_action`

```text

  Queue token-authenticated actions under `/api/external-refs/'.
  Pull fetches from the configured remote and queues publication to
  the source repository.
  Publish queues publication of an already-pulled ref.

[1mOPTIONS[0m (red indicates it is required):

   [1maction[0m  Action to queue.
        choices: [pull, publish]
        type: str

   api_token  API token used for authentication, sent in an
              `Authorization' header of the form `Token <api_token>'.
              Create one in the web UI under your user profile, or
              with the `createapitoken' management command.
              May also be set with the `FLATMAN_API_TOKEN' environment
              variable.
              Not required for the public read-only `/api/v2'
              endpoints.
        default: null
        type: str

   client_cert  Path to a PEM formatted client certificate used for
                mutual TLS.
        default: null
        type: path

   client_key  Path to the PEM formatted private key matching
               `client_cert'.
        default: null
        type: path

   [1mid[0m      Numeric ID of an existing External ref.
        type: int

   include_names  Add best-effort human-readable companion fields for
                  related resource IDs in returned records.
                  Original numeric IDs are retained. Set to `false' to
                  skip the extra lookup requests.
        default: true
        type: bool

   timeout  Socket timeout in seconds for each individual HTTP
            request.
        default: 30
        type: int

   [1murl[0m     Base URL of the flat-manager-django instance, for example
           `https://flatman.example.com'.
           May also be set with the `FLATMAN_URL' environment
           variable.
        type: str

   validate_certs  Whether to validate the TLS certificate of the
                   flat-manager server.
                   May also be set with the `FLATMAN_VALIDATE_CERTS'
                   environment variable.
        default: true
        type: bool

   wait    Poll until the External ref is published, failing on a
           failed or cancelled state.
        default: false
        type: bool

   wait_interval  Seconds between polls. Must be positive.
        default: 5
        type: int

   wait_timeout  Maximum polling duration in seconds. Must be
                 positive.
        default: 600
        type: int

[1mATTRIBUTES:[0m

        [4mcheck_mode:[0m
        description: Validates the current ref without dispatching or polling.
        support: full

        [4mdiff_mode:[0m
        description: Imperative actions do not return a diff.
        support: N/A

[1mNOTES:[0m
      * Pull is imperative and always reports changed when
        queued, even for a published ref.
      * Publish skips an already-published ref and otherwise
        requires the pulled state.
      * Pull rejects refs that are pulling or publishing, or
        have no configured remote.
      * Check mode validates the current ref but never queues or
        polls an action.
      * Requires a server with the token-authenticated External
        workflow API and appropriate user permissions.

[1mSEE ALSO:[0m
      * Module mrmeee.flatman.flatman_external_ref_info
      * Module mrmeee.flatman.flatman_promotion

[1mREQUIREMENTS:[0m  ansible-core >= 2.15


[1mAUTHOR[0m: MrMEEE (@MrMEEE)

[1mEXAMPLES:[0m
- name: Pull and publish an External from its configured remote
  mrmeee.flatman.flatman_external_ref_action:
    id: 12
    action: pull
    wait: true
    wait_timeout: 1800

- name: Publish an already-pulled External
  mrmeee.flatman.flatman_external_ref_action:
    id: 12
    action: publish
    wait: true

[1mRETURN VALUES:[0m

   external_ref  Ref at completion when waiting, otherwise the ref
                 read before dispatch.
        returned: always
        sample:
          id: 12
          status: published
        type: dict

   result  Action response, or an empty dictionary when skipped or in
           check mode.
        returned: always
        type: dict


```


### flatman_external_ref_info

**FQCN:** `mrmeee.flatman.flatman_external_ref_info`

```text

  Read External refs, including versions, logs and publication status,
  from `/api/external-refs/'.
  Requires a server with the token-authenticated External workflow
  API.

[1mOPTIONS[0m (red indicates it is required):

   api_token  API token used for authentication, sent in an
              `Authorization' header of the form `Token <api_token>'.
              Create one in the web UI under your user profile, or
              with the `createapitoken' management command.
              May also be set with the `FLATMAN_API_TOKEN' environment
              variable.
              Not required for the public read-only `/api/v2'
              endpoints.
        default: null
        type: str

   client_cert  Path to a PEM formatted client certificate used for
                mutual TLS.
        default: null
        type: path

   client_key  Path to the PEM formatted private key matching
               `client_cert'.
        default: null
        type: path

   id      Return only the External ref with this numeric ID.
        default: null
        type: int

   include_names  Add best-effort human-readable companion fields for
                  related resource IDs in returned records.
                  Original numeric IDs are retained. Set to `false' to
                  skip the extra lookup requests.
        default: true
        type: bool

   ref     Filter by full OSTree ref, for example
           `app/org.example.App/x86_64/stable'.
        default: null
        type: str

   remote_id  Filter by numeric upstream remote ID.
        default: null
        type: int

   repository  Filter by repository name.
               Mutually exclusive with `repository_id'.
        default: null
        type: str

   repository_id  Filter by numeric repository ID.
                  Mutually exclusive with `repository'.
        default: null
        type: int

   search  Search the ref and display name.
        default: null
        type: str

   status  Filter by External ref state.
        default: null
        type: str

   timeout  Socket timeout in seconds for each individual HTTP
            request.
        default: 30
        type: int

   [1murl[0m     Base URL of the flat-manager-django instance, for example
           `https://flatman.example.com'.
           May also be set with the `FLATMAN_URL' environment
           variable.
        type: str

   validate_certs  Whether to validate the TLS certificate of the
                   flat-manager server.
                   May also be set with the `FLATMAN_VALIDATE_CERTS'
                   environment variable.
        default: true
        type: bool

[1mATTRIBUTES:[0m

        [4mcheck_mode:[0m
        description: This module makes no changes, so it fully supports `check_mode'.
        support: full

        [4mdiff_mode:[0m
        description: This module makes no changes, so it never reports a diff.
        support: N/A

[1mNOTES:[0m
      * When `id' is supplied, list filters are ignored.

[1mSEE ALSO:[0m
      * Module mrmeee.flatman.flatman_external_ref_action

[1mREQUIREMENTS:[0m  ansible-core >= 2.15


[1mAUTHOR[0m: MrMEEE (@MrMEEE)

[1mEXAMPLES:[0m
- name: Find External apps in testing
  mrmeee.flatman.flatman_external_ref_info:
    repository: testing
  register: externals

- name: Inspect an External and its published versions
  mrmeee.flatman.flatman_external_ref_info:
    id: 12
  register: external

[1mRETURN VALUES:[0m

   external_refs  Matching External refs including their versions and
                  logs.
        elements: dict
        returned: always
        sample: [{id: 12, ref: app/org.example.App/x86_64/stable, status: published, versions: []}]
        type: list


```


### flatman_git_branch_info

**FQCN:** `mrmeee.flatman.flatman_git_branch_info`

```text

  Ask a flat-manager-django server to list the heads of a remote Git
  repository.
  Wraps the `/api/git-branches/' endpoint, which runs `git ls-remote'
  on the server.

[1mOPTIONS[0m (red indicates it is required):

   api_token  API token used for authentication, sent in an
              `Authorization' header of the form `Token <api_token>'.
              Create one in the web UI under your user profile, or
              with the `createapitoken' management command.
              May also be set with the `FLATMAN_API_TOKEN' environment
              variable.
              Not required for the public read-only `/api/v2'
              endpoints.
        default: null
        type: str

   client_cert  Path to a PEM formatted client certificate used for
                mutual TLS.
        default: null
        type: path

   client_key  Path to the PEM formatted private key matching
               `client_cert'.
        default: null
        type: path

   include_names  Add best-effort human-readable companion fields for
                  related resource IDs in returned records.
                  Original numeric IDs are retained. Set to `false' to
                  skip the extra lookup requests.
        default: true
        type: bool

   [1mrepo_url[0m  URL of the remote Git repository to inspect, as the
             server would clone it.
        type: str

   timeout  Socket timeout in seconds for each individual HTTP
            request.
        default: 30
        type: int

   [1murl[0m     Base URL of the flat-manager-django instance, for example
           `https://flatman.example.com'.
           May also be set with the `FLATMAN_URL' environment
           variable.
        type: str

   validate_certs  Whether to validate the TLS certificate of the
                   flat-manager server.
                   May also be set with the `FLATMAN_VALIDATE_CERTS'
                   environment variable.
        default: true
        type: bool

[1mATTRIBUTES:[0m

        [4mcheck_mode:[0m
        description: This module makes no changes, so it fully supports `check_mode'.
        support: full

        [4mdiff_mode:[0m
        description: This module makes no changes, so it never reports a diff.
        support: N/A

[1mNOTES:[0m
      * This endpoint allows anonymous access, so `api_token' is
        optional.
      * The server applies a short timeout to the remote lookup.
        If the remote cannot be reached in time it returns the
        fallback list `['main', 'master']' instead of an error.

[1mSEE ALSO:[0m
      * Module mrmeee.flatman.flatman_package

[1mREQUIREMENTS:[0m  ansible-core >= 2.15


[1mAUTHOR[0m: MrMEEE (@MrMEEE)

[1mEXAMPLES:[0m
- name: List the branches of a manifest repository
  mrmeee.flatman.flatman_git_branch_info:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    repo_url: https://github.com/example/org.example.App.git
  register: branches

- name: Fail early when the expected release branch is missing
  ansible.builtin.assert:
    that: "'stable' in branches.branches"
    fail_msg: The manifest repository has no stable branch

- name: Query anonymously without a token
  mrmeee.flatman.flatman_git_branch_info:
    url: https://flatman.example.com
    repo_url: https://gitlab.example.com/apps/org.example.Tool.git
  register: tool_branches

[1mRETURN VALUES:[0m

   branches  Sorted branch names reported by the server.
        elements: str
        returned: always
        sample: [beta, main, stable]
        type: list


```


### flatman_gpg_key

**FQCN:** `mrmeee.flatman.flatman_gpg_key`

```text

  Create, update and delete GPG key records on a flat-manager-django
  server.
  Can also ask the server to generate a brand new key pair, or import
  an existing one.
  Wraps the `/api/gpg-keys/' endpoint and its `generate' and
  `import_key' actions.

[1mOPTIONS[0m (red indicates it is required):

   api_token  API token used for authentication, sent in an
              `Authorization' header of the form `Token <api_token>'.
              Create one in the web UI under your user profile, or
              with the `createapitoken' management command.
              May also be set with the `FLATMAN_API_TOKEN' environment
              variable.
              Not required for the public read-only `/api/v2'
              endpoints.
        default: null
        type: str

   client_cert  Path to a PEM formatted client certificate used for
                mutual TLS.
        default: null
        type: path

   client_key  Path to the PEM formatted private key matching
               `client_cert'.
        default: null
        type: path

   comment  Comment embedded in the generated key user ID.
            Only used when `state=generated'.
        default: null
        type: str

   email   Email address associated with the key.
           Required by the server when `state=generated' or
           `state=imported'.
        default: null
        type: str

   fingerprint  Full GPG fingerprint. Normally filled in by the
                server.
        default: null
        type: str

   include_names  Add best-effort human-readable companion fields for
                  related resource IDs in returned records.
                  Original numeric IDs are retained. Set to `false' to
                  skip the extra lookup requests.
        default: true
        type: bool

   is_active  Whether the key is active.
        default: null
        type: bool

   key_id  Short GPG key ID. Normally filled in by the server.
        default: null
        type: str

   key_length  Size in bits of the generated RSA key.
               Only used when `state=generated'.
        default: 4096
        type: int

   [1mname[0m    Name of the key. Used as the unique key for idempotency.
        type: str

   passphrase  Passphrase protecting `private_key', used only when
               `state=imported'.
        default: null
        type: str

   passphrase_hint  Free form reminder of where the passphrase is
                    kept.
        default: null
        type: str

   private_key  ASCII armored private key, used only when
                `state=imported'.
                Never returned by the API once stored.
        default: null
        type: str

   public_key  ASCII armored public key.
               Required when `state=imported'.
        default: null
        type: str

   state   `present' manages a key record through plain CRUD.
           `absent' deletes the key.
           `generated' asks the server to create a new key pair, but
           only when no key with this name exists yet. Generating is
           not repeatable, so the existence check is what makes this
           option safe to run more than once.
           `imported' uploads an existing key pair, but only when no
           key with this name exists yet.
        choices: [present, absent, generated, imported]
        default: present
        type: str

   timeout  Socket timeout in seconds for each individual HTTP
            request.
        default: 30
        type: int

   [1murl[0m     Base URL of the flat-manager-django instance, for example
           `https://flatman.example.com'.
           May also be set with the `FLATMAN_URL' environment
           variable.
        type: str

   validate_certs  Whether to validate the TLS certificate of the
                   flat-manager server.
                   May also be set with the `FLATMAN_VALIDATE_CERTS'
                   environment variable.
        default: true
        type: bool

[1mATTRIBUTES:[0m

        [4mcheck_mode:[0m
        description: Can run in `check_mode' and return the changes that would be made.
        support: full

        [4mdiff_mode:[0m
        description: Returns details on what has changed (or would have changed) when `--diff'
          is used.
        support: full

[1mSEE ALSO:[0m
      * Module mrmeee.flatman.flatman_gpg_key_info
      * Module mrmeee.flatman.flatman_repository

[1mREQUIREMENTS:[0m  ansible-core >= 2.15


[1mAUTHOR[0m: MrMEEE (@MrMEEE)

[1mEXAMPLES:[0m
- name: Generate a signing key if the server does not have one yet
  mrmeee.flatman.flatman_gpg_key:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    name: release-signing-key
    email: release@example.com
    comment: Example release signing key
    key_length: 4096
    state: generated
  register: signing_key
  no_log: true

- name: Import an existing key pair
  mrmeee.flatman.flatman_gpg_key:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    name: legacy-signing-key
    email: legacy@example.com
    public_key: "{{ lookup('file', 'legacy.pub.asc') }}"
    private_key: "{{ lookup('file', 'legacy.sec.asc') }}"
    passphrase: "{{ vaulted_legacy_passphrase }}"
    state: imported

- name: Retire a key without deleting it
  mrmeee.flatman.flatman_gpg_key:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    name: legacy-signing-key
    is_active: false

[1mRETURN VALUES:[0m

   gpg_key  The GPG key as returned by the API after the change.
            When a key has just been generated the server may include
            a `private_key' member. That member is only available in
            the response of the generate action and can never be read
            back afterwards, so store it somewhere safe and use
            `no_log' on the task.
        returned: when `state' is `present', `generated' or `imported'
        sample:
          email: release@example.com
          fingerprint: 1234567890ABCDEF1234567890ABCDEF12345678
          id: 2
          is_active: true
          key_id: A1B2C3D4E5F60718
          name: release-signing-key
          public_key: '-----BEGIN PGP PUBLIC KEY BLOCK-----'
        type: dict


```


### flatman_gpg_key_info

**FQCN:** `mrmeee.flatman.flatman_gpg_key_info`

```text

  Retrieve one or more GPG key records from a flat-manager-django
  server.
  Optionally fetch the ASCII armored public key of every returned key.
  Private key material is never exposed by the API and is therefore
  never returned.

[1mOPTIONS[0m (red indicates it is required):

   api_token  API token used for authentication, sent in an
              `Authorization' header of the form `Token <api_token>'.
              Create one in the web UI under your user profile, or
              with the `createapitoken' management command.
              May also be set with the `FLATMAN_API_TOKEN' environment
              variable.
              Not required for the public read-only `/api/v2'
              endpoints.
        default: null
        type: str

   client_cert  Path to a PEM formatted client certificate used for
                mutual TLS.
        default: null
        type: path

   client_key  Path to the PEM formatted private key matching
               `client_cert'.
        default: null
        type: path

   email   Return only keys with this exact email address.
        default: null
        type: str

   id      Return only the key with this numeric ID.
        default: null
        type: int

   include  Extra sub-resources to fetch for every returned key.
            `public_key' merges the result of the `public_key' action
            into each key.
        choices: [public_key]
        default: null
        elements: str
        type: list

   include_names  Add best-effort human-readable companion fields for
                  related resource IDs in returned records.
                  Original numeric IDs are retained. Set to `false' to
                  skip the extra lookup requests.
        default: true
        type: bool

   name    Return only the key with this exact name.
        default: null
        type: str

   search  Free text search across name, email, key ID and
           fingerprint.
        default: null
        type: str

   timeout  Socket timeout in seconds for each individual HTTP
            request.
        default: 30
        type: int

   [1murl[0m     Base URL of the flat-manager-django instance, for example
           `https://flatman.example.com'.
           May also be set with the `FLATMAN_URL' environment
           variable.
        type: str

   validate_certs  Whether to validate the TLS certificate of the
                   flat-manager server.
                   May also be set with the `FLATMAN_VALIDATE_CERTS'
                   environment variable.
        default: true
        type: bool

[1mATTRIBUTES:[0m

        [4mcheck_mode:[0m
        description: This module makes no changes, so it fully supports `check_mode'.
        support: full

        [4mdiff_mode:[0m
        description: This module makes no changes, so it never reports a diff.
        support: N/A

[1mSEE ALSO:[0m
      * Module mrmeee.flatman.flatman_gpg_key

[1mREQUIREMENTS:[0m  ansible-core >= 2.15


[1mAUTHOR[0m: MrMEEE (@MrMEEE)

[1mEXAMPLES:[0m
- name: List all GPG keys
  mrmeee.flatman.flatman_gpg_key_info:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
  register: keys

- name: Fetch one key including its armored public key
  mrmeee.flatman.flatman_gpg_key_info:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    name: release-signing-key
    include:
      - public_key
  register: signing_key

- name: Write the public key to disk
  ansible.builtin.copy:
    content: "{{ signing_key.gpg_keys[0].public_key }}"
    dest: /etc/pki/example-release.asc
    mode: "0644"

[1mRETURN VALUES:[0m

   gpg_keys  The matching GPG keys.
        elements: dict
        returned: always
        sample: [{email: release@example.com, fingerprint: 1234567890ABCDEF1234567890ABCDEF12345678,
            id: 2, is_active: true, key_id: A1B2C3D4E5F60718, name: release-signing-key}]
        type: list


```


### flatman_moderation_info

**FQCN:** `mrmeee.flatman.flatman_moderation_info`

```text

  Lists the moderation requests known to a flat-manager-django server,
  optionally narrowed to one application.
  Wraps the `/api/v2/moderation/apps' and
  `/api/v2/moderation/apps/<app_id>' endpoints.
  Requires an API token belonging to an administrator.

[1mOPTIONS[0m (red indicates it is required):

   api_token  API token used for authentication, sent in an
              `Authorization' header of the form `Token <api_token>'.
              Create one in the web UI under your user profile, or
              with the `createapitoken' management command.
              May also be set with the `FLATMAN_API_TOKEN' environment
              variable.
              Not required for the public read-only `/api/v2'
              endpoints.
        default: null
        type: str

   app_id  Return only the moderation requests belonging to this
           application ID.
        default: null
        type: str

   client_cert  Path to a PEM formatted client certificate used for
                mutual TLS.
        default: null
        type: path

   client_key  Path to the PEM formatted private key matching
               `client_cert'.
        default: null
        type: path

   include_names  Add best-effort human-readable companion fields for
                  related resource IDs in returned records.
                  Original numeric IDs are retained. Set to `false' to
                  skip the extra lookup requests.
        default: true
        type: bool

   status  Return only the moderation requests in this state.
           The filtering is done by the module, because the endpoint
           has no status query parameter.
        choices: [pending, approved, rejected]
        default: null
        type: str

   timeout  Socket timeout in seconds for each individual HTTP
            request.
        default: 30
        type: int

   [1murl[0m     Base URL of the flat-manager-django instance, for example
           `https://flatman.example.com'.
           May also be set with the `FLATMAN_URL' environment
           variable.
        type: str

   validate_certs  Whether to validate the TLS certificate of the
                   flat-manager server.
                   May also be set with the `FLATMAN_VALIDATE_CERTS'
                   environment variable.
        default: true
        type: bool

[1mATTRIBUTES:[0m

        [4mcheck_mode:[0m
        description: This module makes no changes, so it fully supports `check_mode'.
        support: full

        [4mdiff_mode:[0m
        description: This module makes no changes, so it never reports a diff.
        support: N/A

[1mSEE ALSO:[0m
      * Module mrmeee.flatman.flatman_moderation_request
      * Module mrmeee.flatman.flatman_moderation_review

[1mREQUIREMENTS:[0m  ansible-core >= 2.15


[1mAUTHOR[0m: MrMEEE (@MrMEEE)

[1mEXAMPLES:[0m
- name: List every moderation request
  mrmeee.flatman.flatman_moderation_info:
    url: https://flatman.example.com
    api_token: "{{ flatman_admin_token }}"
  register: moderation

- name: List the pending requests of a single application
  mrmeee.flatman.flatman_moderation_info:
    url: https://flatman.example.com
    api_token: "{{ flatman_admin_token }}"
    app_id: org.example.Editor
    status: pending
  register: pending

- name: Show how many requests are still waiting for a decision
  ansible.builtin.debug:
    msg: "{{ pending.moderation_requests | length }} requests pending"

[1mRETURN VALUES:[0m

   moderation_requests  The matching moderation requests.
        elements: dict
        returned: always
        sample: [{app_id: org.example.Editor, created_at: '2026-01-14T09:12:44.512000+00:00', id: 17,
            reason: New maintainer took over the project, review_comment: '', reviewed_at: null,
            status: pending}]
        type: list


```


### flatman_moderation_request

**FQCN:** `mrmeee.flatman.flatman_moderation_request`

```text

  Submits a moderation review request for an application.
  Wraps the `/api/v2/moderation/submit_review_request' endpoint.
  Requires an API token belonging to an administrator.

[1mOPTIONS[0m (red indicates it is required):

   api_token  API token used for authentication, sent in an
              `Authorization' header of the form `Token <api_token>'.
              Create one in the web UI under your user profile, or
              with the `createapitoken' management command.
              May also be set with the `FLATMAN_API_TOKEN' environment
              variable.
              Not required for the public read-only `/api/v2'
              endpoints.
        default: null
        type: str

   [1mapp_id[0m  Application ID (the Flatpak package ID) to open a
           moderation request for.
        type: str

   client_cert  Path to a PEM formatted client certificate used for
                mutual TLS.
        default: null
        type: path

   client_key  Path to the PEM formatted private key matching
               `client_cert'.
        default: null
        type: path

   force   Submit a new request even when the application already has
           a request in the `pending' state.
           By default the existing requests are listed first and the
           submission is skipped when one is pending.
        default: false
        type: bool

   include_names  Add best-effort human-readable companion fields for
                  related resource IDs in returned records.
                  Original numeric IDs are retained. Set to `false' to
                  skip the extra lookup requests.
        default: true
        type: bool

   reason  Free form reason stored on the moderation request.
        default: null
        type: str

   timeout  Socket timeout in seconds for each individual HTTP
            request.
        default: 30
        type: int

   [1murl[0m     Base URL of the flat-manager-django instance, for example
           `https://flatman.example.com'.
           May also be set with the `FLATMAN_URL' environment
           variable.
        type: str

   validate_certs  Whether to validate the TLS certificate of the
                   flat-manager server.
                   May also be set with the `FLATMAN_VALIDATE_CERTS'
                   environment variable.
        default: true
        type: bool

[1mATTRIBUTES:[0m

        [4mcheck_mode:[0m
        description: Can run in `check_mode' and return the changes that would be made.
        support: full

        [4mdiff_mode:[0m
        description: Returns details on what has changed (or would have changed) when `--diff'
          is used.
        support: full

[1mSEE ALSO:[0m
      * Module mrmeee.flatman.flatman_moderation_info
      * Module mrmeee.flatman.flatman_moderation_review

[1mREQUIREMENTS:[0m  ansible-core >= 2.15


[1mAUTHOR[0m: MrMEEE (@MrMEEE)

[1mEXAMPLES:[0m
- name: Request moderation for an application
  mrmeee.flatman.flatman_moderation_request:
    url: https://flatman.example.com
    api_token: "{{ flatman_admin_token }}"
    app_id: org.example.Editor
    reason: New maintainer took over the project

- name: Always submit a fresh request, even when one is still pending
  mrmeee.flatman.flatman_moderation_request:
    url: https://flatman.example.com
    api_token: "{{ flatman_admin_token }}"
    app_id: org.example.Editor
    reason: Re-submitted after the metadata fix
    force: true

[1mRETURN VALUES:[0m

   moderation_request  The moderation request created by this task.
                       When an existing pending request was reused,
                       that request is returned instead.
        returned: success
        sample:
          id: 17
          status: pending
        type: dict


```


### flatman_moderation_review

**FQCN:** `mrmeee.flatman.flatman_moderation_review`

```text

  Records a review decision on an existing moderation request.
  Wraps the `/api/v2/moderation/requests/<request_id>/review'
  endpoint.
  Requires an API token belonging to an administrator.

[1mOPTIONS[0m (red indicates it is required):

   api_token  API token used for authentication, sent in an
              `Authorization' header of the form `Token <api_token>'.
              Create one in the web UI under your user profile, or
              with the `createapitoken' management command.
              May also be set with the `FLATMAN_API_TOKEN' environment
              variable.
              Not required for the public read-only `/api/v2'
              endpoints.
        default: null
        type: str

   client_cert  Path to a PEM formatted client certificate used for
                mutual TLS.
        default: null
        type: path

   client_key  Path to the PEM formatted private key matching
               `client_cert'.
        default: null
        type: path

   comment  Review comment stored on the moderation request, sent as
            the `comment' body key.
            The server stores an empty comment when this is omitted.
        default: null
        type: str

   include_names  Add best-effort human-readable companion fields for
                  related resource IDs in returned records.
                  Original numeric IDs are retained. Set to `false' to
                  skip the extra lookup requests.
        default: true
        type: bool

   [1mrequest_id[0m  Numeric ID of the moderation request to review.
        type: int

   [1mstatus[0m  Decision to record on the moderation request.
           The server rejects any other value, even though the model
           also knows the initial `pending' state.
        choices: [approved, rejected]
        type: str

   timeout  Socket timeout in seconds for each individual HTTP
            request.
        default: 30
        type: int

   [1murl[0m     Base URL of the flat-manager-django instance, for example
           `https://flatman.example.com'.
           May also be set with the `FLATMAN_URL' environment
           variable.
        type: str

   validate_certs  Whether to validate the TLS certificate of the
                   flat-manager server.
                   May also be set with the `FLATMAN_VALIDATE_CERTS'
                   environment variable.
        default: true
        type: bool

[1mATTRIBUTES:[0m

        [4mcheck_mode:[0m
        description: Can run in `check_mode' and return the changes that would be made.
        support: full

        [4mdiff_mode:[0m
        description: Returns details on what has changed (or would have changed) when `--diff'
          is used.
        support: full

[1mSEE ALSO:[0m
      * Module mrmeee.flatman.flatman_moderation_info
      * Module mrmeee.flatman.flatman_moderation_request

[1mREQUIREMENTS:[0m  ansible-core >= 2.15


[1mAUTHOR[0m: MrMEEE (@MrMEEE)

[1mEXAMPLES:[0m
- name: Approve a moderation request
  mrmeee.flatman.flatman_moderation_review:
    url: https://flatman.example.com
    api_token: "{{ flatman_admin_token }}"
    request_id: 17
    status: approved
    comment: Metadata and screenshots look good

- name: Reject every pending request for an application
  mrmeee.flatman.flatman_moderation_review:
    url: https://flatman.example.com
    api_token: "{{ flatman_admin_token }}"
    request_id: "{{ item.id }}"
    status: rejected
    comment: Superseded by a newer submission
  loop: "{{ pending.moderation_requests }}"

[1mRETURN VALUES:[0m

   moderation_request  The moderation request after the review
                       decision was applied.
        returned: success
        sample:
          id: 17
          status: approved
        type: dict


```


### flatman_package

**FQCN:** `mrmeee.flatman.flatman_package`

```text

  Create, update and delete package definitions on a
  flat-manager-django server.
  Wraps the `/api/packages/' endpoint.
  A package holds the build configuration (git source, branch,
  architecture) and the current build state.

[1mOPTIONS[0m (red indicates it is required):

   api_token  API token used for authentication, sent in an
              `Authorization' header of the form `Token <api_token>'.
              Create one in the web UI under your user profile, or
              with the `createapitoken' management command.
              May also be set with the `FLATMAN_API_TOKEN' environment
              variable.
              Not required for the public read-only `/api/v2'
              endpoints.
        default: null
        type: str

   arch    Architecture the package is built for, for example
           `x86_64'.
        default: null
        type: str

   branch  Flatpak branch the package is published to, for example
           `stable' or `beta'.
        default: null
        type: str

   client_cert  Path to a PEM formatted client certificate used for
                mutual TLS.
        default: null
        type: path

   client_key  Path to the PEM formatted private key matching
               `client_cert'.
        default: null
        type: path

   dependencies  Flatpak SDK and runtime dependencies detected for
                 this package.
        default: null
        type: dict

   error_message  Error message stored on the package.
                  Set it to an empty string to clear a previous
                  failure message.
        default: null
        type: str

   git_branch  Git branch to build from.
        default: null
        type: str

   git_repo_url  URL of the git repository holding the Flatpak
                 manifest.
        default: null
        type: str

   include_names  Add best-effort human-readable companion fields for
                  related resource IDs in returned records.
                  Original numeric IDs are retained. Set to `false' to
                  skip the extra lookup requests.
        default: true
        type: bool

   [1mpackage_id[0m  Flatpak application ID in reverse DNS notation, for
               example `org.example.MyApp'.
               Used as the unique key for idempotency.
        type: str

   package_name  Human readable name of the package, for example `My
                 Application'.
        default: null
        type: str

   repository  Name of the repository the package belongs to.
               Mutually exclusive with `repository_id'.
        default: null
        type: str

   repository_id  Numeric ID of the repository the package belongs to.
                  Mutually exclusive with `repository'.
        default: null
        type: int

   state   Whether the package should exist or not.
        choices: [present, absent]
        default: present
        type: str

   status  Build state of the package.
           Normally managed by the server; set it only to force a
           package back to a given state.
        choices: [pending, building, built, committing, committed, publishing, published, failed, cancelled]
        default: null
        type: str

   timeout  Socket timeout in seconds for each individual HTTP
            request.
        default: 30
        type: int

   [1murl[0m     Base URL of the flat-manager-django instance, for example
           `https://flatman.example.com'.
           May also be set with the `FLATMAN_URL' environment
           variable.
        type: str

   validate_certs  Whether to validate the TLS certificate of the
                   flat-manager server.
                   May also be set with the `FLATMAN_VALIDATE_CERTS'
                   environment variable.
        default: true
        type: bool

   version  Version number of the package.
            Normally extracted from the manifest for git based
            packages.
        default: null
        type: str

[1mATTRIBUTES:[0m

        [4mcheck_mode:[0m
        description: Can run in `check_mode' and return the changes that would be made.
        support: full

        [4mdiff_mode:[0m
        description: Returns details on what has changed (or would have changed) when `--diff'
          is used.
        support: full

[1mNOTES:[0m
      * The API returns the repository as a nested object while
        it is written as `repository_id', so the nested value is
        unpacked before comparison to keep the module
        idempotent.

[1mSEE ALSO:[0m
      * Module mrmeee.flatman.flatman_package_info
      * Module mrmeee.flatman.flatman_package_action
      * Module mrmeee.flatman.flatman_repository

[1mREQUIREMENTS:[0m  ansible-core >= 2.15


[1mAUTHOR[0m: MrMEEE (@MrMEEE)

[1mEXAMPLES:[0m
- name: Create a git based package in the stable repository
  mrmeee.flatman.flatman_package:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    package_id: org.example.MyApp
    package_name: My Application
    repository: stable
    git_repo_url: https://github.com/example/org.example.MyApp
    git_branch: main
    branch: stable
    arch: x86_64

- name: Move a package to the beta branch
  mrmeee.flatman.flatman_package:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    package_id: org.example.MyApp
    repository_id: 3
    branch: beta

- name: Delete a retired package
  mrmeee.flatman.flatman_package:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    package_id: org.example.OldApp
    state: absent

[1mRETURN VALUES:[0m

   package  The package as returned by the API after the change.
        returned: when `state=present'
        sample:
          arch: x86_64
          branch: stable
          build_number: 7
          git_branch: main
          git_repo_url: https://github.com/example/org.example.MyApp
          id: 12
          package_id: org.example.MyApp
          package_name: My Application
          status: published
          version: 1.4.2
        type: dict


```


### flatman_package_action

**FQCN:** `mrmeee.flatman.flatman_package_action`

```text

  Trigger the imperative actions exposed by the `/api/packages/'
  endpoint, such as starting, cancelling, committing or publishing a
  build.
  Optionally wait until the package reaches a terminal build state.

[1mOPTIONS[0m (red indicates it is required):

   [1maction[0m  The action to perform on the package.
           `start' queues a git based build, and only works while the
           package is pending.
           `cancel' marks a running build as cancelled.
           `commit' commits a built package into the OSTree
           repository.
           `publish' publishes a committed package.
           `build_ref' registers an OSTree ref and commit pair for the
           package.
           `missing_objects' asks the server which OSTree objects are
           still missing.
        choices: [start, cancel, commit, publish, build_ref, missing_objects]
        type: str

   api_token  API token used for authentication, sent in an
              `Authorization' header of the form `Token <api_token>'.
              Create one in the web UI under your user profile, or
              with the `createapitoken' management command.
              May also be set with the `FLATMAN_API_TOKEN' environment
              variable.
              Not required for the public read-only `/api/v2'
              endpoints.
        default: null
        type: str

   client_cert  Path to a PEM formatted client certificate used for
                mutual TLS.
        default: null
        type: path

   client_key  Path to the PEM formatted private key matching
               `client_cert'.
        default: null
        type: path

   commit  OSTree commit hash to associate with `ref'.
           Required when `action=build_ref'.
        default: null
        type: str

   id      Numeric ID of the package to act on.
           Mutually exclusive with `package_id'; exactly one of the
           two is required.
        default: null
        type: int

   include_names  Add best-effort human-readable companion fields for
                  related resource IDs in returned records.
                  Original numeric IDs are retained. Set to `false' to
                  skip the extra lookup requests.
        default: true
        type: bool

   package_id  Flatpak application ID of the package to act on, for
               example `org.example.MyApp'.
               Mutually exclusive with `id'; exactly one of the two is
               required.
        default: null
        type: str

   ref     Full OSTree ref, for example
           `app/org.example.MyApp/x86_64/stable'.
           Required when `action=build_ref'.
        default: null
        type: str

   timeout  Socket timeout in seconds for each individual HTTP
            request.
        default: 30
        type: int

   [1murl[0m     Base URL of the flat-manager-django instance, for example
           `https://flatman.example.com'.
           May also be set with the `FLATMAN_URL' environment
           variable.
        type: str

   validate_certs  Whether to validate the TLS certificate of the
                   flat-manager server.
                   May also be set with the `FLATMAN_VALIDATE_CERTS'
                   environment variable.
        default: true
        type: bool

   wait    Whether to poll the package until it reaches a terminal
           build state.
           Only applies to `action=start', `action=commit' and
           `action=publish'.
        default: false
        type: bool

   wait_interval  Number of seconds between polls when `wait=true'.
        default: 5
        type: int

   wait_timeout  Maximum number of seconds to wait when `wait=true'.
        default: 600
        type: int

   wanted  OSTree object names to check for.
           Only used when `action=missing_objects'; the request is
           sent as a POST when this is given and as a GET otherwise.
        default: null
        elements: str
        type: list

[1mATTRIBUTES:[0m

        [4mcheck_mode:[0m
        description: Can run in `check_mode' and return the changes that would be made.
        support: full

        [4mdiff_mode:[0m
        description: Returns details on what has changed (or would have changed) when `--diff'
          is used.
        support: full

[1mNOTES:[0m
      * The actions `start', `cancel', `commit', `publish' and
        `build_ref' are imperative operations, so this module
        always reports a change for them. `missing_objects' is
        read only and never reports a change.
      * The `upload' action of the API is not implemented,
        because uploading artifacts requires a multipart request
        body which the collection HTTP client does not support.

[1mSEE ALSO:[0m
      * Module mrmeee.flatman.flatman_package
      * Module mrmeee.flatman.flatman_package_info
      * Module mrmeee.flatman.flatman_build_log_info

[1mREQUIREMENTS:[0m  ansible-core >= 2.15


[1mAUTHOR[0m: MrMEEE (@MrMEEE)

[1mEXAMPLES:[0m
- name: Start a build and wait for it to finish
  mrmeee.flatman.flatman_package_action:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    package_id: org.example.MyApp
    action: start
    wait: true
    wait_timeout: 3600
  register: build

- name: Publish a committed package
  mrmeee.flatman.flatman_package_action:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    id: 12
    action: publish
    wait: true

- name: Ask which OSTree objects are still missing
  mrmeee.flatman.flatman_package_action:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    package_id: org.example.MyApp
    action: missing_objects
    wanted:
      - 4a3b1c8d9e0f1a2b3c4d5e6f708192a3b4c5d6e7f8091a2b3c4d5e6f70819200
  register: missing

[1mRETURN VALUES:[0m

   package  The package as returned by the API once it reached a
            terminal state.
        returned: when `wait=true' and `action' is `start', `commit' or `publish'
        sample:
          build_number: 7
          id: 12
          package_id: org.example.MyApp
          status: published
        type: dict

   result  The raw body returned by the API for the requested action.
        returned: always
        sample:
          package_id: org.example.MyApp
          status: Build started manually
        type: dict


```


### flatman_package_info

**FQCN:** `mrmeee.flatman.flatman_package_info`

```text

  Retrieve one or more packages from a flat-manager-django server.
  Wraps the `/api/packages/' endpoint.

[1mOPTIONS[0m (red indicates it is required):

   api_token  API token used for authentication, sent in an
              `Authorization' header of the form `Token <api_token>'.
              Create one in the web UI under your user profile, or
              with the `createapitoken' management command.
              May also be set with the `FLATMAN_API_TOKEN' environment
              variable.
              Not required for the public read-only `/api/v2'
              endpoints.
        default: null
        type: str

   arch    Filter packages by architecture, for example `x86_64'.
        default: null
        type: str

   branch  Filter packages by Flatpak branch, for example `stable'.
        default: null
        type: str

   client_cert  Path to a PEM formatted client certificate used for
                mutual TLS.
        default: null
        type: path

   client_key  Path to the PEM formatted private key matching
               `client_cert'.
        default: null
        type: path

   full    Whether to return the complete build history embedded in
           every package.
           The API embeds every build together with all of its log
           lines, which makes the response very large; when this is
           `false' the `builds' key is removed from each result.
           The `latest_build' key is always kept.
        default: false
        type: bool

   id      Return only the package with this numeric ID.
        default: null
        type: int

   include_names  Add best-effort human-readable companion fields for
                  related resource IDs in returned records.
                  Original numeric IDs are retained. Set to `false' to
                  skip the extra lookup requests.
        default: true
        type: bool

   package_id  Return only the package with this exact Flatpak
               application ID.
        default: null
        type: str

   repository  Name of the repository to filter on.
               Mutually exclusive with `repository_id'.
        default: null
        type: str

   repository_id  Numeric ID of the repository to filter on.
                  Mutually exclusive with `repository'.
        default: null
        type: int

   search  Free text search across the application ID and the package
           name.
        default: null
        type: str

   status  Filter packages by build state.
        choices: [pending, building, built, committing, committed, publishing, published, failed, cancelled]
        default: null
        type: str

   timeout  Socket timeout in seconds for each individual HTTP
            request.
        default: 30
        type: int

   [1murl[0m     Base URL of the flat-manager-django instance, for example
           `https://flatman.example.com'.
           May also be set with the `FLATMAN_URL' environment
           variable.
        type: str

   validate_certs  Whether to validate the TLS certificate of the
                   flat-manager server.
                   May also be set with the `FLATMAN_VALIDATE_CERTS'
                   environment variable.
        default: true
        type: bool

[1mATTRIBUTES:[0m

        [4mcheck_mode:[0m
        description: This module makes no changes, so it fully supports `check_mode'.
        support: full

        [4mdiff_mode:[0m
        description: This module makes no changes, so it never reports a diff.
        support: N/A

[1mSEE ALSO:[0m
      * Module mrmeee.flatman.flatman_package
      * Module mrmeee.flatman.flatman_build_info

[1mREQUIREMENTS:[0m  ansible-core >= 2.15


[1mAUTHOR[0m: MrMEEE (@MrMEEE)

[1mEXAMPLES:[0m
- name: List every package
  mrmeee.flatman.flatman_package_info:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
  register: packages

- name: Find failed packages in the stable repository
  mrmeee.flatman.flatman_package_info:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    repository: stable
    status: failed
  register: broken

- name: Fetch one package including its full build history
  mrmeee.flatman.flatman_package_info:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    package_id: org.example.MyApp
    full: true
  register: myapp

[1mRETURN VALUES:[0m

   packages  The matching packages.
        elements: dict
        returned: always
        sample: [{arch: x86_64, branch: stable, build_number: 7, id: 12, package_id: org.example.MyApp,
            package_name: My Application, status: published, version: 1.4.2}]
        type: list


```


### flatman_platform_info

**FQCN:** `mrmeee.flatman.flatman_platform_info`

```text

  Retrieve the architectures and runtimes used by the published
  applications.
  Wraps the `/api/v2/platforms' and `/api/v2/runtimes' endpoints.
  These endpoints are public, so `api_token' is optional.

[1mOPTIONS[0m (red indicates it is required):

   api_token  API token used for authentication, sent in an
              `Authorization' header of the form `Token <api_token>'.
              Create one in the web UI under your user profile, or
              with the `createapitoken' management command.
              May also be set with the `FLATMAN_API_TOKEN' environment
              variable.
              Not required for the public read-only `/api/v2'
              endpoints.
        default: null
        type: str

   client_cert  Path to a PEM formatted client certificate used for
                mutual TLS.
        default: null
        type: path

   client_key  Path to the PEM formatted private key matching
               `client_cert'.
        default: null
        type: path

   include_names  Add best-effort human-readable companion fields for
                  related resource IDs in returned records.
                  Original numeric IDs are retained. Set to `false' to
                  skip the extra lookup requests.
        default: true
        type: bool

   timeout  Socket timeout in seconds for each individual HTTP
            request.
        default: 30
        type: int

   [1murl[0m     Base URL of the flat-manager-django instance, for example
           `https://flatman.example.com'.
           May also be set with the `FLATMAN_URL' environment
           variable.
        type: str

   validate_certs  Whether to validate the TLS certificate of the
                   flat-manager server.
                   May also be set with the `FLATMAN_VALIDATE_CERTS'
                   environment variable.
        default: true
        type: bool

[1mATTRIBUTES:[0m

        [4mcheck_mode:[0m
        description: This module makes no changes, so it fully supports `check_mode'.
        support: full

        [4mdiff_mode:[0m
        description: This module makes no changes, so it never reports a diff.
        support: N/A

[1mSEE ALSO:[0m
      * Module mrmeee.flatman.flatman_app_info
      * Module mrmeee.flatman.flatman_app_stats_info

[1mREQUIREMENTS:[0m  ansible-core >= 2.15


[1mAUTHOR[0m: MrMEEE (@MrMEEE)

[1mEXAMPLES:[0m
- name: Gather the supported platforms and runtimes
  mrmeee.flatman.flatman_platform_info:
    url: https://flatman.example.com
  register: platforms

- name: Fail when x86_64 is not published
  ansible.builtin.assert:
    that: "'x86_64' in platforms.platforms"

- name: Show the runtimes in use
  ansible.builtin.debug:
    var: platforms.runtimes

[1mRETURN VALUES:[0m

   platforms  The sorted architectures of every published package.
        elements: str
        returned: always
        sample: [aarch64, x86_64]
        type: list

   runtimes  The sorted runtimes declared by the dependencies of every
             published package.
        elements: str
        returned: always
        sample: [org.freedesktop.Platform/x86_64/23.08, org.gnome.Platform/x86_64/45]
        type: list


```


### flatman_promotion

**FQCN:** `mrmeee.flatman.flatman_promotion`

```text

  Queue a promotion through the token API and optionally wait until it
  completes.
  Reuses pending, promoting or promoted records for the same source
  and target.
  Failed Flatpak promotions are retried by the server; failed External
  promotions are queued anew.

[1mOPTIONS[0m (red indicates it is required):

   api_token  API token used for authentication, sent in an
              `Authorization' header of the form `Token <api_token>'.
              Create one in the web UI under your user profile, or
              with the `createapitoken' management command.
              May also be set with the `FLATMAN_API_TOKEN' environment
              variable.
              Not required for the public read-only `/api/v2'
              endpoints.
        default: null
        type: str

   build_id  Numeric build history ID, not a package ID or build
             attempt number.
             Exactly one of `build_id' and `external_ref_id' is
             required.
        default: null
        type: int

   client_cert  Path to a PEM formatted client certificate used for
                mutual TLS.
        default: null
        type: path

   client_key  Path to the PEM formatted private key matching
               `client_cert'.
        default: null
        type: path

   external_ref_id  Numeric External ref ID.
                    Exactly one of `build_id' and `external_ref_id' is
                    required.
        default: null
        type: int

   external_ref_version_id  Published version belonging to
                            `external_ref_id'.
                            When omitted, the latest published version
                            by pull time and ID is selected.
                            Only valid with `external_ref_id'.
        default: null
        type: int

   include_names  Add best-effort human-readable companion fields for
                  related resource IDs in returned records.
                  Original numeric IDs are retained. Set to `false' to
                  skip the extra lookup requests.
        default: true
        type: bool

   repository  Target repository name.
               Exactly one of `repository' and `target_repo_id' is
               required.
        default: null
        type: str

   target_repo_id  Numeric target repository ID.
                   Exactly one of `repository' and `target_repo_id' is
                   required.
        default: null
        type: int

   timeout  Socket timeout in seconds for each individual HTTP
            request.
        default: 30
        type: int

   [1murl[0m     Base URL of the flat-manager-django instance, for example
           `https://flatman.example.com'.
           May also be set with the `FLATMAN_URL' environment
           variable.
        type: str

   validate_certs  Whether to validate the TLS certificate of the
                   flat-manager server.
                   May also be set with the `FLATMAN_VALIDATE_CERTS'
                   environment variable.
        default: true
        type: bool

   wait    Poll the new or existing promotion until promoted, failing
           on a failed state.
        default: false
        type: bool

   wait_interval  Seconds between polls. Must be positive.
        default: 5
        type: int

   wait_timeout  Maximum polling duration in seconds. Must be
                 positive.
        default: 600
        type: int

[1mATTRIBUTES:[0m

        [4mcheck_mode:[0m
        description: Predicts changes from source and promotion records without dispatching
          or polling.
        support: full

        [4mdiff_mode:[0m
        description: Promotion actions do not return a diff.
        support: N/A

[1mNOTES:[0m
      * Requires a server with the token-authenticated promotion
        API and appropriate user permissions.
      * The server enforces active child targets and completion
        of prerequisite parent promotions.
      * Check mode reads source and promotion records but never
        dispatches or polls.
      * Target eligibility for a new promotion is validated by
        the server on dispatch, not in check mode.
      * Configure External refs through the server web
        interface; this module does not create them.

[1mSEE ALSO:[0m
      * Module mrmeee.flatman.flatman_promotion_info
      * Module mrmeee.flatman.flatman_external_ref_info
      * Module mrmeee.flatman.flatman_build_info

[1mREQUIREMENTS:[0m  ansible-core >= 2.15


[1mAUTHOR[0m: MrMEEE (@MrMEEE)

[1mEXAMPLES:[0m
- name: Promote an exact published Flatpak build to stable
  mrmeee.flatman.flatman_promotion:
    build_id: 48
    repository: stable
    wait: true

- name: Promote an exact External version to stable
  mrmeee.flatman.flatman_promotion:
    external_ref_id: 12
    external_ref_version_id: 7
    repository: stable
    wait: true

[1mRETURN VALUES:[0m

   promotion  New or reused promotion record, or the predicted fields
              in check mode.
        returned: always
        sample:
          build: 48
          id: 10
          status: promoted
          target_repo: 3
        type: dict

   result  Raw dispatch response, or an empty dictionary when reused
           or in check mode.
        returned: always
        type: dict


```


### flatman_promotion_batch

**FQCN:** `mrmeee.flatman.flatman_promotion_batch`

```text

  Discover server-eligible Flatpak build and External version
  promotions and submit them sequentially.
  `target' sends every currently eligible candidate to one selected
  repository.
  `all_ready' promotes to all repositories currently eligible in the
  release chain.
  With `wait=true', refresh eligibility after each completed round to
  discover newly unlocked child repositories.

[1mOPTIONS[0m (red indicates it is required):

   api_token  API token used for authentication, sent in an
              `Authorization' header of the form `Token <api_token>'.
              Create one in the web UI under your user profile, or
              with the `createapitoken' management command.
              May also be set with the `FLATMAN_API_TOKEN' environment
              variable.
              Not required for the public read-only `/api/v2'
              endpoints.
        default: null
        type: str

   client_cert  Path to a PEM formatted client certificate used for
                mutual TLS.
        default: null
        type: path

   client_key  Path to the PEM formatted private key matching
               `client_cert'.
        default: null
        type: path

   include_names  Add best-effort human-readable companion fields for
                  related resource IDs in returned records.
                  Original numeric IDs are retained. Set to `false' to
                  skip the extra lookup requests.
        default: true
        type: bool

   kind    Limit the batch to Flatpak builds, External versions, or
           both.
        choices: [both, build, external]
        default: both
        type: str

   max_promotions  Safety limit on promotions submitted in one
                   invocation.
        default: 500
        type: int

   mode    Promote to one selected target or advance through every
           eligible repository in the chain.
        choices: [target, all_ready]
        default: target
        type: str

   repository  Target repository name; required with `mode=target'.
               Mutually exclusive with `target_repo_id'.
        default: null
        type: str

   source_repo_id  Restrict candidates to this source repository ID.
                   Mutually exclusive with `source_repository'.
        default: null
        type: int

   source_repository  Restrict candidates to this source repository
                      name.
                      Mutually exclusive with `source_repo_id'.
        default: null
        type: str

   target_repo_id  Target repository ID; required with `mode=target'.
                   Mutually exclusive with `repository'.
        default: null
        type: int

   timeout  Socket timeout in seconds for each individual HTTP
            request.
        default: 30
        type: int

   [1murl[0m     Base URL of the flat-manager-django instance, for example
           `https://flatman.example.com'.
           May also be set with the `FLATMAN_URL' environment
           variable.
        type: str

   validate_certs  Whether to validate the TLS certificate of the
                   flat-manager server.
                   May also be set with the `FLATMAN_VALIDATE_CERTS'
                   environment variable.
        default: true
        type: bool

   wait    Wait for each promotion and refresh eligibility to traverse
           release chains.
        default: true
        type: bool

   wait_interval  Seconds between promotion status checks.
        default: 10
        type: int

   wait_timeout  Maximum seconds to wait for each promotion.
        default: 1800
        type: int

[1mATTRIBUTES:[0m

        [4mcheck_mode:[0m
        description: Reports the current plan without submitting any promotions.
        support: full

        [4mdiff_mode:[0m
        description: Returns the planned source and target pairs when `--diff' is used.
        support: partial

[1mNOTES:[0m
      * Eligibility and parent-chain prerequisites are
        calculated and enforced by the server.
      * `all_ready' with `wait=false' submits only the current
        readiness snapshot. Run again after jobs finish to
        continue the chain.
      * Check mode predicts only the current readiness snapshot;
        it cannot predict targets unlocked by future promotions.
      * Eligibility can change between listing and dispatch if
        another actor promotes the same source.
      * Requires promotion permission and organisation access to
        each source.

[1mSEE ALSO:[0m
      * Module mrmeee.flatman.flatman_promotion_ready_info
      * Module mrmeee.flatman.flatman_promotion

[1mREQUIREMENTS:[0m  ansible-core >= 2.15


[1mAUTHOR[0m: MrMEEE (@MrMEEE)

[1mEXAMPLES:[0m
- name: Promote all currently-ready items to stable
  mrmeee.flatman.flatman_promotion_batch:
    url: https://flatman.example.com
    api_token: "{{ flatman_api_token }}"
    mode: target
    repository: stable
    source_repository: testing
    kind: both
    wait: true

- name: Promote all Flatpak builds and Externals through the release chain
  mrmeee.flatman.flatman_promotion_batch:
    url: https://flatman.example.com
    api_token: "{{ flatman_api_token }}"
    mode: all_ready
    kind: both
    wait: true

- name: Preview currently-ready promotions
  mrmeee.flatman.flatman_promotion_batch:
    url: https://flatman.example.com
    api_token: "{{ flatman_api_token }}"
    mode: all_ready
  check_mode: true

[1mRETURN VALUES:[0m

   count   Number of promotions dispatched.
        returned: always
        type: int

   planned_promotions  Currently eligible source/target pairs returned
                       in check mode.
        elements: dict
        returned: in check mode
        type: list

   promotions  Dispatched promotion records with readable source and
               target names.
        elements: dict
        returned: always
        sample: [{build_id: 19, kind: build, package_name: Example App, promotion_id: 31, status: promoted,
            target_repo_id: 10, target_repo_name: stable}]
        type: list

   remaining_ready  Candidates left when the safety limit or
                    non-waiting mode stops the batch.
        elements: dict
        returned: always
        type: list


```


### flatman_promotion_info

**FQCN:** `mrmeee.flatman.flatman_promotion_info`

```text

  Read promotion records through the token API, including completion
  status and errors.

[1mOPTIONS[0m (red indicates it is required):

   api_token  API token used for authentication, sent in an
              `Authorization' header of the form `Token <api_token>'.
              Create one in the web UI under your user profile, or
              with the `createapitoken' management command.
              May also be set with the `FLATMAN_API_TOKEN' environment
              variable.
              Not required for the public read-only `/api/v2'
              endpoints.
        default: null
        type: str

   build_id  Filter by numeric build history ID. Only valid with
             `kind=build'.
        default: null
        type: int

   client_cert  Path to a PEM formatted client certificate used for
                mutual TLS.
        default: null
        type: path

   client_key  Path to the PEM formatted private key matching
               `client_cert'.
        default: null
        type: path

   external_ref_id  Filter by External ref ID. Only valid with
                    `kind=external'.
        default: null
        type: int

   external_ref_version_id  Filter by External version ID. Only valid
                            with `kind=external'.
        default: null
        type: int

   id      Return only this numeric promotion ID. List filters are
           ignored.
        default: null
        type: int

   include_names  Add best-effort human-readable companion fields for
                  related resource IDs in returned records.
                  Original numeric IDs are retained. Set to `false' to
                  skip the extra lookup requests.
        default: true
        type: bool

   kind    Select Flatpak build or External version promotion records.
        choices: [build, external]
        default: build
        type: str

   repository  Filter by target repository name.
               Mutually exclusive with `target_repo_id'.
        default: null
        type: str

   status  Filter by promotion state.
        choices: [pending, promoting, promoted, failed]
        default: null
        type: str

   target_repo_id  Filter by numeric target repository ID.
                   Mutually exclusive with `repository'.
        default: null
        type: int

   timeout  Socket timeout in seconds for each individual HTTP
            request.
        default: 30
        type: int

   [1murl[0m     Base URL of the flat-manager-django instance, for example
           `https://flatman.example.com'.
           May also be set with the `FLATMAN_URL' environment
           variable.
        type: str

   validate_certs  Whether to validate the TLS certificate of the
                   flat-manager server.
                   May also be set with the `FLATMAN_VALIDATE_CERTS'
                   environment variable.
        default: true
        type: bool

[1mATTRIBUTES:[0m

        [4mcheck_mode:[0m
        description: This module makes no changes, so it fully supports `check_mode'.
        support: full

        [4mdiff_mode:[0m
        description: This module makes no changes, so it never reports a diff.
        support: N/A

[1mNOTES:[0m
      * Requires a server with the token-authenticated promotion
        API and appropriate user permissions.

[1mSEE ALSO:[0m
      * Module mrmeee.flatman.flatman_promotion

[1mREQUIREMENTS:[0m  ansible-core >= 2.15


[1mAUTHOR[0m: MrMEEE (@MrMEEE)

[1mEXAMPLES:[0m
- name: Find completed build promotions to stable
  mrmeee.flatman.flatman_promotion_info:
    repository: stable
    status: promoted

- name: Inspect an External promotion
  mrmeee.flatman.flatman_promotion_info:
    kind: external
    id: 10
  register: promotion

[1mRETURN VALUES:[0m

   promotions  Matching promotion records.
        elements: dict
        returned: always
        sample: [{error_message: '', id: 10, status: promoted, target_repo: 3}]
        type: list


```


### flatman_promotion_ready_info

**FQCN:** `mrmeee.flatman.flatman_promotion_ready_info`

```text

  Query the server-calculated promotion eligibility for published
  Flatpak builds and External versions.
  Each result is one eligible source and target repository pair.
  Repository-chain prerequisites and existing promotion records are
  evaluated by the server.

[1mOPTIONS[0m (red indicates it is required):

   api_token  API token used for authentication, sent in an
              `Authorization' header of the form `Token <api_token>'.
              Create one in the web UI under your user profile, or
              with the `createapitoken' management command.
              May also be set with the `FLATMAN_API_TOKEN' environment
              variable.
              Not required for the public read-only `/api/v2'
              endpoints.
        default: null
        type: str

   build_id  Restrict candidates to this published build-history ID.
        default: null
        type: int

   client_cert  Path to a PEM formatted client certificate used for
                mutual TLS.
        default: null
        type: path

   client_key  Path to the PEM formatted private key matching
               `client_cert'.
        default: null
        type: path

   external_ref_id  Restrict candidates to this External definition
                    ID.
        default: null
        type: int

   external_ref_version_id  Restrict candidates to this immutable
                            External version ID.
        default: null
        type: int

   include_names  Add best-effort human-readable companion fields for
                  related resource IDs in returned records.
                  Original numeric IDs are retained. Set to `false' to
                  skip the extra lookup requests.
        default: true
        type: bool

   kind    Limit results to Flatpak builds, External versions, or
           both.
        choices: [both, build, external]
        default: both
        type: str

   repository  Restrict candidates to this target repository name.
               Mutually exclusive with `target_repo_id'.
        default: null
        type: str

   source_repo_id  Restrict candidates to this source repository ID.
                   Mutually exclusive with `source_repository'.
        default: null
        type: int

   source_repository  Restrict candidates to this source repository
                      name.
                      Mutually exclusive with `source_repo_id'.
        default: null
        type: str

   target_repo_id  Restrict candidates to this target repository ID.
                   Mutually exclusive with `repository'.
        default: null
        type: int

   timeout  Socket timeout in seconds for each individual HTTP
            request.
        default: 30
        type: int

   [1murl[0m     Base URL of the flat-manager-django instance, for example
           `https://flatman.example.com'.
           May also be set with the `FLATMAN_URL' environment
           variable.
        type: str

   validate_certs  Whether to validate the TLS certificate of the
                   flat-manager server.
                   May also be set with the `FLATMAN_VALIDATE_CERTS'
                   environment variable.
        default: true
        type: bool

[1mATTRIBUTES:[0m

        [4mcheck_mode:[0m
        description: This module makes no changes, so it fully supports `check_mode'.
        support: full

        [4mdiff_mode:[0m
        description: This module makes no changes, so it never reports a diff.
        support: N/A

[1mNOTES:[0m
      * Requires the token promotion API and promotion
        permission for the source organisation.
      * Results are an eligibility snapshot; another request can
        change eligibility before a promotion is submitted.

[1mSEE ALSO:[0m
      * Module mrmeee.flatman.flatman_promotion
      * Module mrmeee.flatman.flatman_promotion_batch

[1mREQUIREMENTS:[0m  ansible-core >= 2.15


[1mAUTHOR[0m: MrMEEE (@MrMEEE)

[1mEXAMPLES:[0m
- name: List every Flatpak and External promotion currently ready
  mrmeee.flatman.flatman_promotion_ready_info:
    url: https://flatman.example.com
    api_token: "{{ flatman_api_token }}"
  register: ready

- name: List targets ready for build 48
  mrmeee.flatman.flatman_promotion_ready_info:
    url: https://flatman.example.com
    api_token: "{{ flatman_api_token }}"
    kind: build
    build_id: 48

[1mRETURN VALUES:[0m

   count   Number of eligible source/target pairs.
        returned: always
        type: int

   ready_promotions  Eligible source/target pairs. IDs remain
                     available alongside readable names.
        elements: dict
        returned: always
        sample: [{build_id: 19, build_number: 7, kind: build, package_id: 3, package_identifier: org.example.App,
            package_name: Example App, source_repo_id: 2, source_repo_name: testing, target_repo_id: 10,
            target_repo_name: stable}]
        type: list


```


### flatman_quality_moderation

**FQCN:** `mrmeee.flatman.flatman_quality_moderation`

```text

  Marks an application as a fullscreen application or opens a quality
  review request for it.
  Wraps the `/api/v2/quality-moderation/<app_id>/fullscreen' and
  `/api/v2/quality-moderation/<app_id>/request-review' endpoints.
  Both actions require an API token belonging to an administrator.

[1mOPTIONS[0m (red indicates it is required):

   [1maction[0m  `fullscreen' flags the application as a fullscreen
           application. This action is idempotent - the current
           quality status is read first and the write is skipped when
           the flag is already set.
           `request-review' creates a new moderation request for the
           application. This action is imperative, so it always
           reports a change outside of check mode.
           `reject-pending-reviews' rejects all pending review
           requests for the application.
        choices: [fullscreen, request-review, reject-pending-reviews]
        type: str

   api_token  API token used for authentication, sent in an
              `Authorization' header of the form `Token <api_token>'.
              Create one in the web UI under your user profile, or
              with the `createapitoken' management command.
              May also be set with the `FLATMAN_API_TOKEN' environment
              variable.
              Not required for the public read-only `/api/v2'
              endpoints.
        default: null
        type: str

   [1mapp_id[0m  Application ID (the Flatpak package ID) the action applies
           to.
        type: str

   client_cert  Path to a PEM formatted client certificate used for
                mutual TLS.
        default: null
        type: path

   client_key  Path to the PEM formatted private key matching
               `client_cert'.
        default: null
        type: path

   include_names  Add best-effort human-readable companion fields for
                  related resource IDs in returned records.
                  Original numeric IDs are retained. Set to `false' to
                  skip the extra lookup requests.
        default: true
        type: bool

   reason  Reason recorded on the moderation request, sent as the
           `reason' body key.
           Only used with `action=request-review'. The server defaults
           it to `Quality review requested'.
        default: null
        type: str

   timeout  Socket timeout in seconds for each individual HTTP
            request.
        default: 30
        type: int

   [1murl[0m     Base URL of the flat-manager-django instance, for example
           `https://flatman.example.com'.
           May also be set with the `FLATMAN_URL' environment
           variable.
        type: str

   validate_certs  Whether to validate the TLS certificate of the
                   flat-manager server.
                   May also be set with the `FLATMAN_VALIDATE_CERTS'
                   environment variable.
        default: true
        type: bool

[1mATTRIBUTES:[0m

        [4mcheck_mode:[0m
        description: Can run in `check_mode' and return the changes that would be made.
        support: full

        [4mdiff_mode:[0m
        description: Returns details on what has changed (or would have changed) when `--diff'
          is used.
        support: full

[1mNOTES:[0m
      * `reject-pending-reviews' rejects all pending requests
        through DELETE on the request-review endpoint.
      * This bulk action was added in collection version 1.2.0
        and reports changed when dispatched.

[1mSEE ALSO:[0m
      * Module mrmeee.flatman.flatman_quality_moderation_info
      * Module mrmeee.flatman.flatman_moderation_request

[1mREQUIREMENTS:[0m  ansible-core >= 2.15


[1mAUTHOR[0m: MrMEEE (@MrMEEE)

[1mEXAMPLES:[0m
- name: Flag an application as a fullscreen application
  mrmeee.flatman.flatman_quality_moderation:
    url: https://flatman.example.com
    api_token: "{{ flatman_admin_token }}"
    app_id: org.example.Game
    action: fullscreen

- name: Ask for a quality review of an application
  mrmeee.flatman.flatman_quality_moderation:
    url: https://flatman.example.com
    api_token: "{{ flatman_admin_token }}"
    app_id: org.example.Editor
    action: request-review
    reason: Screenshots were refreshed for the 2.0 release

- name: Flag several games as fullscreen applications
  mrmeee.flatman.flatman_quality_moderation:
    url: https://flatman.example.com
    api_token: "{{ flatman_admin_token }}"
    app_id: "{{ item }}"
    action: fullscreen
  loop:
    - org.example.Game
    - org.example.Racer

[1mRETURN VALUES:[0m

   result  The raw API response.
           For `action=fullscreen' this is the fullscreen state of the
           application. When the flag was already set no request is
           sent and the current quality status is returned instead.
           For `action=request-review' this is the newly created
           moderation request.
        returned: success
        sample:
          app_id: org.example.Game
          fullscreen: true
        type: dict


```


### flatman_quality_moderation_info

**FQCN:** `mrmeee.flatman.flatman_quality_moderation_info`

```text

  Reads the quality moderation status of a single application, or one
  of the aggregated quality reports.
  Wraps the read-only `/api/v2/quality-moderation' endpoints, which do
  not require authentication.

[1mOPTIONS[0m (red indicates it is required):

   api_token  API token used for authentication, sent in an
              `Authorization' header of the form `Token <api_token>'.
              Create one in the web UI under your user profile, or
              with the `createapitoken' management command.
              May also be set with the `FLATMAN_API_TOKEN' environment
              variable.
              Not required for the public read-only `/api/v2'
              endpoints.
        default: null
        type: str

   app_id  Application ID to read the quality status for, using
           `/api/v2/quality-moderation/<app_id>/status'.
           Mutually exclusive with `report'.
        default: null
        type: str

   client_cert  Path to a PEM formatted client certificate used for
                mutual TLS.
        default: null
        type: path

   client_key  Path to the PEM formatted private key matching
               `client_cert'.
        default: null
        type: path

   include_names  Add best-effort human-readable companion fields for
                  related resource IDs in returned records.
                  Original numeric IDs are retained. Set to `false' to
                  skip the extra lookup requests.
        default: true
        type: bool

   report  Aggregated quality report to fetch.
           `status' returns the instance wide counters from
           `/api/v2/quality-moderation/status'.
           `stats-by-category' returns a mapping of branch to
           application count.
           `passing-apps' returns the applications whose quality
           status is `passing'.
           `failed-by-guideline' returns the failing applications
           together with the guidelines they failed.
           `app-pick-recommendations' returns applications recommended
           for an editorial pick.
           Mutually exclusive with `app_id'.
        choices: [status, stats-by-category, passing-apps, failed-by-guideline, app-pick-recommendations]
        default: null
        type: str

   timeout  Socket timeout in seconds for each individual HTTP
            request.
        default: 30
        type: int

   [1murl[0m     Base URL of the flat-manager-django instance, for example
           `https://flatman.example.com'.
           May also be set with the `FLATMAN_URL' environment
           variable.
        type: str

   validate_certs  Whether to validate the TLS certificate of the
                   flat-manager server.
                   May also be set with the `FLATMAN_VALIDATE_CERTS'
                   environment variable.
        default: true
        type: bool

[1mATTRIBUTES:[0m

        [4mcheck_mode:[0m
        description: This module makes no changes, so it fully supports `check_mode'.
        support: full

        [4mdiff_mode:[0m
        description: This module makes no changes, so it never reports a diff.
        support: N/A

[1mSEE ALSO:[0m
      * Module mrmeee.flatman.flatman_quality_moderation
      * Module mrmeee.flatman.flatman_moderation_info

[1mREQUIREMENTS:[0m  ansible-core >= 2.15


[1mAUTHOR[0m: MrMEEE (@MrMEEE)

[1mEXAMPLES:[0m
- name: Read the quality status of a single application
  mrmeee.flatman.flatman_quality_moderation_info:
    url: https://flatman.example.com
    app_id: org.example.Editor
  register: app_quality

- name: Fail when the application is not a fullscreen application
  ansible.builtin.assert:
    that: app_quality.quality.fullscreen

- name: List every application that passes quality moderation
  mrmeee.flatman.flatman_quality_moderation_info:
    url: https://flatman.example.com
    report: passing-apps
  register: passing

[1mRETURN VALUES:[0m

   quality  The quality data returned by the selected endpoint.
            A dict for `app_id', `report=status' and
            `report=stats-by-category'.
            A list of dicts for `report=passing-apps',
            `report=failed-by-guideline' and
            `report=app-pick-recommendations'.
        returned: always
        sample:
          fullscreen: false
          guidelines: []
          id: org.example.Editor
          review_comment: ''
          status: passing
        type: raw


```


### flatman_repository

**FQCN:** `mrmeee.flatman.flatman_repository`

```text

  Create, update and delete repositories on a flat-manager-django
  server.
  Wraps the `/api/repositories/' endpoint.

[1mOPTIONS[0m (red indicates it is required):

   api_token  API token used for authentication, sent in an
              `Authorization' header of the form `Token <api_token>'.
              Create one in the web UI under your user profile, or
              with the `createapitoken' management command.
              May also be set with the `FLATMAN_API_TOKEN' environment
              variable.
              Not required for the public read-only `/api/v2'
              endpoints.
        default: null
        type: str

   client_cert  Path to a PEM formatted client certificate used for
                mutual TLS.
        default: null
        type: path

   client_key  Path to the PEM formatted private key matching
               `client_cert'.
        default: null
        type: path

   collection_id  OSTree collection ID advertised by this repository,
                  for example `org.example.Repo'.
        default: null
        type: str

   description  Free form description of the repository.
        default: null
        type: str

   gpg_key  Name of the GPG key used to sign commits in this
            repository.
            Mutually exclusive with `gpg_key_id'.
        default: null
        type: str

   gpg_key_id  Numeric ID of the GPG key used to sign commits in this
               repository.
               Mutually exclusive with `gpg_key'.
        default: null
        type: int

   include_names  Add best-effort human-readable companion fields for
                  related resource IDs in returned records.
                  Original numeric IDs are retained. Set to `false' to
                  skip the extra lookup requests.
        default: true
        type: bool

   is_active  Whether the repository is active.
        default: null
        type: bool

   [1mname[0m    Name of the repository. Used as the unique key for
           idempotency.
        type: str

   parent_repos  Names or numeric IDs of the parent repositories this
                 repository inherits from.
                 Replaces the existing list when specified.
        default: null
        elements: raw
        type: list

   state   Whether the repository should exist or not.
        choices: [present, absent]
        default: present
        type: str

   timeout  Socket timeout in seconds for each individual HTTP
            request.
        default: 30
        type: int

   [1murl[0m     Base URL of the flat-manager-django instance, for example
           `https://flatman.example.com'.
           May also be set with the `FLATMAN_URL' environment
           variable.
        type: str

   validate_certs  Whether to validate the TLS certificate of the
                   flat-manager server.
                   May also be set with the `FLATMAN_VALIDATE_CERTS'
                   environment variable.
        default: true
        type: bool

[1mATTRIBUTES:[0m

        [4mcheck_mode:[0m
        description: Can run in `check_mode' and return the changes that would be made.
        support: full

        [4mdiff_mode:[0m
        description: Returns details on what has changed (or would have changed) when `--diff'
          is used.
        support: full

[1mSEE ALSO:[0m
      * Module mrmeee.flatman.flatman_repository_info
      * Module mrmeee.flatman.flatman_repository_subset
      * Module mrmeee.flatman.flatman_gpg_key

[1mREQUIREMENTS:[0m  ansible-core >= 2.15


[1mAUTHOR[0m: MrMEEE (@MrMEEE)

[1mEXAMPLES:[0m
- name: Create a stable repository signed with an existing key
  mrmeee.flatman.flatman_repository:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    name: stable
    collection_id: org.example.Stable
    description: Production Flatpak repository
    gpg_key: release-signing-key
    is_active: true

- name: Chain beta on top of stable
  mrmeee.flatman.flatman_repository:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    name: beta
    collection_id: org.example.Beta
    parent_repos:
      - stable

- name: Remove a retired repository
  mrmeee.flatman.flatman_repository:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    name: old-testing
    state: absent

[1mRETURN VALUES:[0m

   repository  The repository as returned by the API after the change.
        returned: when `state=present'
        sample:
          build_count: 42
          collection_id: org.example.Stable
          description: Production Flatpak repository
          id: 3
          is_active: true
          name: stable
          repo_path: /var/lib/flat-manager/repos/stable
        type: dict


```


### flatman_repository_info

**FQCN:** `mrmeee.flatman.flatman_repository_info`

```text

  Retrieve one or more repositories from a flat-manager-django server.
  Optionally include the builds and subsets belonging to each
  repository.

[1mOPTIONS[0m (red indicates it is required):

   api_token  API token used for authentication, sent in an
              `Authorization' header of the form `Token <api_token>'.
              Create one in the web UI under your user profile, or
              with the `createapitoken' management command.
              May also be set with the `FLATMAN_API_TOKEN' environment
              variable.
              Not required for the public read-only `/api/v2'
              endpoints.
        default: null
        type: str

   client_cert  Path to a PEM formatted client certificate used for
                mutual TLS.
        default: null
        type: path

   client_key  Path to the PEM formatted private key matching
               `client_cert'.
        default: null
        type: path

   collection_id  Filter repositories by OSTree collection ID.
        default: null
        type: str

   id      Return only the repository with this numeric ID.
        default: null
        type: int

   include  Extra sub-resources to fetch for every returned
            repository.
            `builds' adds a `builds' key, `subsets' refreshes the
            `subsets' key.
        choices: [builds, subsets]
        default: null
        elements: str
        type: list

   include_names  Add best-effort human-readable companion fields for
                  related resource IDs in returned records.
                  Original numeric IDs are retained. Set to `false' to
                  skip the extra lookup requests.
        default: true
        type: bool

   is_active  Filter repositories by their active flag.
        default: null
        type: bool

   name    Return only the repository with this exact name.
        default: null
        type: str

   search  Free text search across name, description and collection
           ID.
        default: null
        type: str

   timeout  Socket timeout in seconds for each individual HTTP
            request.
        default: 30
        type: int

   [1murl[0m     Base URL of the flat-manager-django instance, for example
           `https://flatman.example.com'.
           May also be set with the `FLATMAN_URL' environment
           variable.
        type: str

   validate_certs  Whether to validate the TLS certificate of the
                   flat-manager server.
                   May also be set with the `FLATMAN_VALIDATE_CERTS'
                   environment variable.
        default: true
        type: bool

[1mATTRIBUTES:[0m

        [4mcheck_mode:[0m
        description: This module makes no changes, so it fully supports `check_mode'.
        support: full

        [4mdiff_mode:[0m
        description: This module makes no changes, so it never reports a diff.
        support: N/A

[1mSEE ALSO:[0m
      * Module mrmeee.flatman.flatman_repository

[1mREQUIREMENTS:[0m  ansible-core >= 2.15


[1mAUTHOR[0m: MrMEEE (@MrMEEE)

[1mEXAMPLES:[0m
- name: List all repositories
  mrmeee.flatman.flatman_repository_info:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
  register: repos

- name: Fetch one repository including its builds
  mrmeee.flatman.flatman_repository_info:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    name: stable
    include:
      - builds
  register: stable

- name: Show how many builds the stable repository has
  ansible.builtin.debug:
    msg: "{{ stable.repositories[0].builds | length }} builds"

[1mRETURN VALUES:[0m

   repositories  The matching repositories.
        elements: dict
        returned: always
        sample: [{build_count: 42, collection_id: org.example.Stable, id: 3, is_active: true, name: stable}]
        type: list


```


### flatman_repository_subset

**FQCN:** `mrmeee.flatman.flatman_repository_subset`

```text

  Create, update and delete repository subsets on a
  flat-manager-django server.
  A subset is a partial mirror of a repository with its own collection
  ID and base URL.
  Wraps the `/api/repository-subsets/' endpoint.

[1mOPTIONS[0m (red indicates it is required):

   api_token  API token used for authentication, sent in an
              `Authorization' header of the form `Token <api_token>'.
              Create one in the web UI under your user profile, or
              with the `createapitoken' management command.
              May also be set with the `FLATMAN_API_TOKEN' environment
              variable.
              Not required for the public read-only `/api/v2'
              endpoints.
        default: null
        type: str

   base_url  Base URL clients use to reach this subset.
        default: null
        type: str

   client_cert  Path to a PEM formatted client certificate used for
                mutual TLS.
        default: null
        type: path

   client_key  Path to the PEM formatted private key matching
               `client_cert'.
        default: null
        type: path

   collection_id  OSTree collection ID advertised by this subset, for
                  example `org.example.Repo.Stable'.
        default: null
        type: str

   include_names  Add best-effort human-readable companion fields for
                  related resource IDs in returned records.
                  Original numeric IDs are retained. Set to `false' to
                  skip the extra lookup requests.
        default: true
        type: bool

   [1mname[0m    Name of the subset.
           Together with the owning repository this forms the unique
           key used for idempotency.
        type: str

   repository  Name of the repository owning the subset.
               Mutually exclusive with `repository_id'.
        default: null
        type: str

   repository_id  Numeric ID of the repository owning the subset.
                  Mutually exclusive with `repository'.
        default: null
        type: int

   state   Whether the subset should exist or not.
        choices: [present, absent]
        default: present
        type: str

   timeout  Socket timeout in seconds for each individual HTTP
            request.
        default: 30
        type: int

   [1murl[0m     Base URL of the flat-manager-django instance, for example
           `https://flatman.example.com'.
           May also be set with the `FLATMAN_URL' environment
           variable.
        type: str

   validate_certs  Whether to validate the TLS certificate of the
                   flat-manager server.
                   May also be set with the `FLATMAN_VALIDATE_CERTS'
                   environment variable.
        default: true
        type: bool

[1mATTRIBUTES:[0m

        [4mcheck_mode:[0m
        description: Can run in `check_mode' and return the changes that would be made.
        support: full

        [4mdiff_mode:[0m
        description: Returns details on what has changed (or would have changed) when `--diff'
          is used.
        support: full

[1mNOTES:[0m
      * The owning repository is written as `repository_id' but
        is not returned by the API, so the module filters the
        list endpoint server side by repository ID and then
        matches `name' locally.

[1mSEE ALSO:[0m
      * Module mrmeee.flatman.flatman_repository_subset_info
      * Module mrmeee.flatman.flatman_repository

[1mREQUIREMENTS:[0m  ansible-core >= 2.15


[1mAUTHOR[0m: MrMEEE (@MrMEEE)

[1mEXAMPLES:[0m
- name: Create a stable subset of the main repository
  mrmeee.flatman.flatman_repository_subset:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    repository: stable
    name: apps
    collection_id: org.example.Stable.Apps
    base_url: https://cdn.example.com/stable/apps

- name: Point an existing subset at a new CDN
  mrmeee.flatman.flatman_repository_subset:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    repository_id: 3
    name: apps
    base_url: https://cdn2.example.com/stable/apps

- name: Remove a subset
  mrmeee.flatman.flatman_repository_subset:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    repository: stable
    name: legacy
    state: absent

[1mRETURN VALUES:[0m

   repository_subset  The repository subset as returned by the API
                      after the change.
        returned: when `state=present'
        sample:
          base_url: https://cdn.example.com/stable/apps
          collection_id: org.example.Stable.Apps
          id: 7
          name: apps
        type: dict


```


### flatman_repository_subset_info

**FQCN:** `mrmeee.flatman.flatman_repository_subset_info`

```text

  Retrieve one or more repository subsets from a flat-manager-django
  server.
  Wraps the `/api/repository-subsets/' endpoint.

[1mOPTIONS[0m (red indicates it is required):

   api_token  API token used for authentication, sent in an
              `Authorization' header of the form `Token <api_token>'.
              Create one in the web UI under your user profile, or
              with the `createapitoken' management command.
              May also be set with the `FLATMAN_API_TOKEN' environment
              variable.
              Not required for the public read-only `/api/v2'
              endpoints.
        default: null
        type: str

   client_cert  Path to a PEM formatted client certificate used for
                mutual TLS.
        default: null
        type: path

   client_key  Path to the PEM formatted private key matching
               `client_cert'.
        default: null
        type: path

   id      Return only the subset with this numeric ID.
        default: null
        type: int

   include_names  Add best-effort human-readable companion fields for
                  related resource IDs in returned records.
                  Original numeric IDs are retained. Set to `false' to
                  skip the extra lookup requests.
        default: true
        type: bool

   name    Return only the subset with this exact name.
        default: null
        type: str

   repository  Restrict the result to subsets of the repository with
               this name.
               Mutually exclusive with `repository_id'.
        default: null
        type: str

   repository_id  Restrict the result to subsets of the repository
                  with this numeric ID.
                  Mutually exclusive with `repository'.
        default: null
        type: int

   search  Free text search across subset name and collection ID.
        default: null
        type: str

   timeout  Socket timeout in seconds for each individual HTTP
            request.
        default: 30
        type: int

   [1murl[0m     Base URL of the flat-manager-django instance, for example
           `https://flatman.example.com'.
           May also be set with the `FLATMAN_URL' environment
           variable.
        type: str

   validate_certs  Whether to validate the TLS certificate of the
                   flat-manager server.
                   May also be set with the `FLATMAN_VALIDATE_CERTS'
                   environment variable.
        default: true
        type: bool

[1mATTRIBUTES:[0m

        [4mcheck_mode:[0m
        description: This module makes no changes, so it fully supports `check_mode'.
        support: full

        [4mdiff_mode:[0m
        description: This module makes no changes, so it never reports a diff.
        support: N/A

[1mSEE ALSO:[0m
      * Module mrmeee.flatman.flatman_repository_subset
      * Module mrmeee.flatman.flatman_repository_info

[1mREQUIREMENTS:[0m  ansible-core >= 2.15


[1mAUTHOR[0m: MrMEEE (@MrMEEE)

[1mEXAMPLES:[0m
- name: List every subset on the server
  mrmeee.flatman.flatman_repository_subset_info:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
  register: all_subsets

- name: List the subsets of the stable repository
  mrmeee.flatman.flatman_repository_subset_info:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    repository: stable
  register: stable_subsets

- name: Show the collection IDs of the stable subsets
  ansible.builtin.debug:
    msg: "{{ stable_subsets.repository_subsets | map(attribute='collection_id') | list }}"

[1mRETURN VALUES:[0m

   repository_subsets  The matching repository subsets.
        elements: dict
        returned: always
        sample: [{base_url: 'https://cdn.example.com/stable/apps', collection_id: org.example.Stable.Apps,
            id: 7, name: apps}]
        type: list


```


### flatman_resource

**FQCN:** `mrmeee.flatman.flatman_resource`

```text

  Manage supported resources through their router endpoints using JSON
  or web-form field names.
  Identify an existing record by numeric ID or an exact, unique field
  match.
  Only fields supplied in `data' are reconciled; lists are compared
  order-insensitively.

[1mOPTIONS[0m (red indicates it is required):

   api_token  API token used for authentication, sent in an
              `Authorization' header of the form `Token <api_token>'.
              Create one in the web UI under your user profile, or
              with the `createapitoken' management command.
              May also be set with the `FLATMAN_API_TOKEN' environment
              variable.
              Not required for the public read-only `/api/v2'
              endpoints.
        default: null
        type: str

   client_cert  Path to a PEM formatted client certificate used for
                mutual TLS.
        default: null
        type: path

   client_key  Path to the PEM formatted private key matching
               `client_cert'.
        default: null
        type: path

   data    Desired JSON or web-form fields. Use numeric IDs for
           related resources.
           Write-only fields cannot be compared and cause a write on
           every run when supplied.
           Put credentials in `secret_data', not ordinary fields or
           identity.
        default: {}
        type: dict

   id      Numeric ID of an existing record. Mutually exclusive with
           `match'.
           A missing ID cannot be used to create a new resource.
        default: null
        type: int

   include_names  Add best-effort human-readable companion fields for
                  related resource IDs in returned records.
                  Original numeric IDs are retained. Set to `false' to
                  skip the extra lookup requests.
        default: true
        type: bool

   match   Nonempty exact identity fields used to find a unique
           record.
           On creation these fields are included in the payload.
           Use readable fields, not credentials, for identity.
        default: null
        type: dict

   [1mresource[0m  Router resource to manage. Supported operations vary by
             resource.
        choices: [flatpak-remotes, organisations, bst-sources, clients, permission-groups, ldap-sources,
          ldap-group-mappings, rpm-packages, rpm-builds, rpm-distributions, satellite-servers,
          satellite-repositories, rpm-destinations, user-roles, permission-grants, group-permissions,
          site-config, external-refs]
        type: str

   secret_data  Write-only credential fields merged into `data' and
                protected with `no_log'.
                Must not duplicate fields in `data'.
                Only include secrets here; ordinary IDs belong in
                `data' to keep returned IDs usable.
        default: {}
        type: dict

   state   Whether the resource should exist.
        choices: [present, absent]
        default: present
        type: str

   timeout  Socket timeout in seconds for each individual HTTP
            request.
        default: 30
        type: int

   [1murl[0m     Base URL of the flat-manager-django instance, for example
           `https://flatman.example.com'.
           May also be set with the `FLATMAN_URL' environment
           variable.
        type: str

   validate_certs  Whether to validate the TLS certificate of the
                   flat-manager server.
                   May also be set with the `FLATMAN_VALIDATE_CERTS'
                   environment variable.
        default: true
        type: bool

[1mATTRIBUTES:[0m

        [4mcheck_mode:[0m
        description: Reads existing records and predicts changes without sending mutations.
        support: full

        [4mdiff_mode:[0m
        description: Payloads may contain credentials, so no diff is returned.
        support: N/A

[1mNOTES:[0m
      * Requires the expanded token router and suitable
        workflow/organisation permissions.
      * External refs may auto-queue a pull on creation
        according to upstream settings.
      * Unsupported create, update or delete operations fail
        explicitly.
      * Client, RPM build and destination resources only support
        deletion here.
      * Satellite servers and repositories support creation and
        deletion but not update.
      * Site configuration supports updates only; use `id' from
        `flatman_resource_info'.
      * Responses from web-form adapters are acknowledgements,
        not resource records. The module rereads after writes.
      * Use task-level `no_log=true' when managing site settings
        or credentials.

[1mREQUIREMENTS:[0m  ansible-core >= 2.15


[1mAUTHOR[0m: MrMEEE (@MrMEEE)

[1mEXAMPLES:[0m
- name: Configure an upstream Flatpak remote
  mrmeee.flatman.flatman_resource:
    resource: flatpak-remotes
    match:
      name: flathub
    data:
      url: https://dl.flathub.org/repo/
      is_active: true
      priority: 1

- name: Create an External definition
  mrmeee.flatman.flatman_resource:
    resource: external-refs
    match:
      repository: 2
      ref: app/org.example.App/x86_64/stable
    data:
      remote: 1
      display_name: Example App

[1mRETURN VALUES:[0m

   resource  Current resource, predicted fields in check mode, or an
             empty dictionary after deletion.
        returned: always
        type: dict


```


### flatman_resource_info

**FQCN:** `mrmeee.flatman.flatman_resource_info`

```text

  Read resources from the expanded router, including BuildStream,
  access control, RPM and server configuration.
  Returns a consistent list even for the singleton site configuration
  and workflow catalogue.
  Follows pagination and optionally selects exact field values
  locally.

[1mOPTIONS[0m (red indicates it is required):

   api_token  API token used for authentication, sent in an
              `Authorization' header of the form `Token <api_token>'.
              Create one in the web UI under your user profile, or
              with the `createapitoken' management command.
              May also be set with the `FLATMAN_API_TOKEN' environment
              variable.
              Not required for the public read-only `/api/v2'
              endpoints.
        default: null
        type: str

   client_cert  Path to a PEM formatted client certificate used for
                mutual TLS.
        default: null
        type: path

   client_key  Path to the PEM formatted private key matching
               `client_cert'.
        default: null
        type: path

   id      Numeric detail ID. Mutually exclusive with `match'.
        default: null
        type: int

   include_names  Add best-effort human-readable companion fields for
                  related resource IDs in returned records.
                  Original numeric IDs are retained. Set to `false' to
                  skip the extra lookup requests.
        default: true
        type: bool

   match   Exact returned field values to select locally, not fuzzy
           search parameters.
        default: {}
        type: dict

   [1mresource[0m  Router resource to read.
        choices: [gpg-keys, flatpak-remotes, organisations, bst-sources, bst-promotions, clients, permission-groups,
          ldap-sources, ldap-group-mappings, rpm-packages, rpm-builds, rpm-distributions,
          rpm-repositories, satellite-servers, satellite-repositories, rpm-destinations, rpm-signing-keys,
          user-roles, permission-grants, group-permissions, site-config, external-refs, packages,
          repositories, builds, promotions, external-ref-promotions, workflows]
        type: str

   timeout  Socket timeout in seconds for each individual HTTP
            request.
        default: 30
        type: int

   [1murl[0m     Base URL of the flat-manager-django instance, for example
           `https://flatman.example.com'.
           May also be set with the `FLATMAN_URL' environment
           variable.
        type: str

   validate_certs  Whether to validate the TLS certificate of the
                   flat-manager server.
                   May also be set with the `FLATMAN_VALIDATE_CERTS'
                   environment variable.
        default: true
        type: bool

[1mATTRIBUTES:[0m

        [4mcheck_mode:[0m
        description: This module makes no changes, so it fully supports `check_mode'.
        support: full

        [4mdiff_mode:[0m
        description: This module makes no changes, so it never reports a diff.
        support: N/A

[1mNOTES:[0m
      * Requires a server with the expanded token workflow
        router.
      * Site configuration can contain sensitive settings. Use
        task-level `no_log=true' when inspecting it.
      * `workflows' supports list reads only and returns the
        server action catalogue.

[1mREQUIREMENTS:[0m  ansible-core >= 2.15


[1mAUTHOR[0m: MrMEEE (@MrMEEE)

[1mEXAMPLES:[0m
- name: Find active Flatpak remotes
  mrmeee.flatman.flatman_resource_info:
    resource: flatpak-remotes
    match:
      is_active: true
  register: remotes

- name: Discover server workflow endpoints
  mrmeee.flatman.flatman_resource_info:
    resource: workflows
  register: catalogue

[1mRETURN VALUES:[0m

   resources  Matching resource records, or a single
              configuration/catalogue dictionary.
        elements: dict
        returned: always
        type: list


```


### flatman_search_info

**FQCN:** `mrmeee.flatman.flatman_search_info`

```text

  Search the published application catalogue by ID, name, summary or
  developer name.
  Wraps the `/api/v2/search' endpoint, which is queried with a POST
  request carrying a JSON body.
  This endpoint is public, so `api_token' is optional.

[1mOPTIONS[0m (red indicates it is required):

   api_token  API token used for authentication, sent in an
              `Authorization' header of the form `Token <api_token>'.
              Create one in the web UI under your user profile, or
              with the `createapitoken' management command.
              May also be set with the `FLATMAN_API_TOKEN' environment
              variable.
              Not required for the public read-only `/api/v2'
              endpoints.
        default: null
        type: str

   client_cert  Path to a PEM formatted client certificate used for
                mutual TLS.
        default: null
        type: path

   client_key  Path to the PEM formatted private key matching
               `client_cert'.
        default: null
        type: path

   include_names  Add best-effort human-readable companion fields for
                  related resource IDs in returned records.
                  Original numeric IDs are retained. Set to `false' to
                  skip the extra lookup requests.
        default: true
        type: bool

   [1mquery[0m   The search string, sent to the server as the `query' key of
           the request body.
           Matched case insensitively against application ID, package
           name, summary and developer name.
        type: str

   timeout  Socket timeout in seconds for each individual HTTP
            request.
        default: 30
        type: int

   [1murl[0m     Base URL of the flat-manager-django instance, for example
           `https://flatman.example.com'.
           May also be set with the `FLATMAN_URL' environment
           variable.
        type: str

   validate_certs  Whether to validate the TLS certificate of the
                   flat-manager server.
                   May also be set with the `FLATMAN_VALIDATE_CERTS'
                   environment variable.
        default: true
        type: bool

[1mATTRIBUTES:[0m

        [4mcheck_mode:[0m
        description: This module makes no changes, so it fully supports `check_mode'.
        support: full

        [4mdiff_mode:[0m
        description: This module makes no changes, so it never reports a diff.
        support: N/A

[1mSEE ALSO:[0m
      * Module mrmeee.flatman.flatman_app_info
      * Module mrmeee.flatman.flatman_collection_info

[1mREQUIREMENTS:[0m  ansible-core >= 2.15


[1mAUTHOR[0m: MrMEEE (@MrMEEE)

[1mEXAMPLES:[0m
- name: Search for editors
  mrmeee.flatman.flatman_search_info:
    url: https://flatman.example.com
    query: editor
  register: results

- name: Show the matching application IDs
  ansible.builtin.debug:
    msg: "{{ results.apps | map(attribute='id') | list }}"

- name: Find everything published by one developer
  mrmeee.flatman.flatman_search_info:
    url: https://flatman.example.com
    query: Example Inc
  register: by_developer

[1mRETURN VALUES:[0m

   apps    The applications matching the search query.
        elements: dict
        returned: always
        sample: [{arch: x86_64, branch: stable, developer: Example Inc, id: org.example.Editor, name: Example
              Editor, repository: stable, summary: A small text editor, verified: true, version: 1.2.3}]
        type: list


```


### flatman_status_info

**FQCN:** `mrmeee.flatman.flatman_status_info`

```text

  Query the running version of a flat-manager-django server through
  `/api/version/'.
  Query the service health flag through the Flathub compatible
  `/api/v2/status' endpoint.

[1mOPTIONS[0m (red indicates it is required):

   api_token  API token used for authentication, sent in an
              `Authorization' header of the form `Token <api_token>'.
              Create one in the web UI under your user profile, or
              with the `createapitoken' management command.
              May also be set with the `FLATMAN_API_TOKEN' environment
              variable.
              Not required for the public read-only `/api/v2'
              endpoints.
        default: null
        type: str

   client_cert  Path to a PEM formatted client certificate used for
                mutual TLS.
        default: null
        type: path

   client_key  Path to the PEM formatted private key matching
               `client_cert'.
        default: null
        type: path

   include_names  Add best-effort human-readable companion fields for
                  related resource IDs in returned records.
                  Original numeric IDs are retained. Set to `false' to
                  skip the extra lookup requests.
        default: true
        type: bool

   timeout  Socket timeout in seconds for each individual HTTP
            request.
        default: 30
        type: int

   [1murl[0m     Base URL of the flat-manager-django instance, for example
           `https://flatman.example.com'.
           May also be set with the `FLATMAN_URL' environment
           variable.
        type: str

   validate_certs  Whether to validate the TLS certificate of the
                   flat-manager server.
                   May also be set with the `FLATMAN_VALIDATE_CERTS'
                   environment variable.
        default: true
        type: bool

[1mATTRIBUTES:[0m

        [4mcheck_mode:[0m
        description: This module makes no changes, so it fully supports `check_mode'.
        support: full

        [4mdiff_mode:[0m
        description: This module makes no changes, so it never reports a diff.
        support: N/A

[1mNOTES:[0m
      * Both endpoints allow anonymous access, so `api_token' is
        optional. This makes the module useful as a readiness
        check before any credentials have been provisioned.

[1mSEE ALSO:[0m
      * Module mrmeee.flatman.flatman_repository_info

[1mREQUIREMENTS:[0m  ansible-core >= 2.15


[1mAUTHOR[0m: MrMEEE (@MrMEEE)

[1mEXAMPLES:[0m
- name: Check that the server is up and report its version
  mrmeee.flatman.flatman_status_info:
    url: https://flatman.example.com
  register: flatman_status

- name: Show the running version
  ansible.builtin.debug:
    msg: "flat-manager {{ flatman_status.version }} built {{ flatman_status.build_date }}"

- name: Wait until the service reports itself healthy
  mrmeee.flatman.flatman_status_info:
    url: https://flatman.example.com
  register: health
  until: health.status == 'ok'
  retries: 30
  delay: 5

[1mRETURN VALUES:[0m

   build_date  Build date reported by the server.
        returned: always
        sample: '2026-09-22'
        type: str

   server  The raw responses of both endpoints, keyed by endpoint
           name.
        returned: always
        type: dict
        contains:

           status  Raw body of the `/api/v2/status' response.
          returned: always
          sample:
            status: ok
          type: dict

           version  Raw body of the `/api/version/' response.
          returned: always
          sample:
            build_date: '2026-09-22'
            version: 1.0.29
          type: dict

   status  Health flag reported by the `/api/v2/status' endpoint.
        returned: always
        sample: ok
        type: str

   version  Version string reported by the server.
        returned: always
        sample: 1.0.29
        type: str


```


### flatman_token

**FQCN:** `mrmeee.flatman.flatman_token`

```text

  Create, update and delete repository scoped access tokens on a
  flat-manager-django server.
  Wraps the `/api/tokens/' endpoint.

[1mOPTIONS[0m (red indicates it is required):

   api_token  API token used for authentication, sent in an
              `Authorization' header of the form `Token <api_token>'.
              Create one in the web UI under your user profile, or
              with the `createapitoken' management command.
              May also be set with the `FLATMAN_API_TOKEN' environment
              variable.
              Not required for the public read-only `/api/v2'
              endpoints.
        default: null
        type: str

   client_cert  Path to a PEM formatted client certificate used for
                mutual TLS.
        default: null
        type: path

   client_key  Path to the PEM formatted private key matching
               `client_cert'.
        default: null
        type: path

   expires_at  Expiry timestamp in ISO 8601 form, for example
               `2027-01-31T23:59:59Z'.
               Leave unset for a token that never expires.
        default: null
        type: str

   include_names  Add best-effort human-readable companion fields for
                  related resource IDs in returned records.
                  Original numeric IDs are retained. Set to `false' to
                  skip the extra lookup requests.
        default: true
        type: bool

   is_active  Whether the token is active.
        default: null
        type: bool

   [1mname[0m    Name of the token.
           Together with the owning repository this forms the unique
           key used for idempotency.
        type: str

   repository  Name of the repository the token grants access to.
               Mutually exclusive with `repository_id'.
        default: null
        type: str

   repository_id  Numeric ID of the repository the token grants access
                  to.
                  Mutually exclusive with `repository'.
        default: null
        type: int

   state   Whether the token should exist or not.
        choices: [present, absent]
        default: present
        type: str

   timeout  Socket timeout in seconds for each individual HTTP
            request.
        default: 30
        type: int

   token_type  Kind of access the token grants.
        choices: [upload, download, admin]
        default: null
        type: str

   [1murl[0m     Base URL of the flat-manager-django instance, for example
           `https://flatman.example.com'.
           May also be set with the `FLATMAN_URL' environment
           variable.
        type: str

   validate_certs  Whether to validate the TLS certificate of the
                   flat-manager server.
                   May also be set with the `FLATMAN_VALIDATE_CERTS'
                   environment variable.
        default: true
        type: bool

[1mATTRIBUTES:[0m

        [4mcheck_mode:[0m
        description: Can run in `check_mode' and return the changes that would be made.
        support: full

        [4mdiff_mode:[0m
        description: Returns details on what has changed (or would have changed) when `--diff'
          is used.
        support: full

[1mNOTES:[0m
      * [1mThese tokens are not enforced by the server yet.[0m
        The flat-manager-django server stores repository tokens
        but no code path validates an incoming request against
        them, and `token_type' currently carries no meaning.
        Creating a token therefore grants no access and deleting
        one revokes none. This module exists so the
        `/api/tokens/' endpoint can be managed declaratively
        once enforcement lands.
      * Repository tokens are not the same thing as the
        `api_token' used to talk to the API. That one is a user
        scoped Django REST Framework token, created from the web
        UI under Profile or with the `drf_create_token'
        management command. A repository token cannot be used as
        `api_token'.
      * The secret value of a token is generated by the server
        and is only ever readable through the API. Use `no_log'
        on tasks that register the result.

[1mSEE ALSO:[0m
      * Module mrmeee.flatman.flatman_token_info
      * Module mrmeee.flatman.flatman_repository

[1mREQUIREMENTS:[0m  ansible-core >= 2.15


[1mAUTHOR[0m: MrMEEE (@MrMEEE)

[1mEXAMPLES:[0m
- name: Create an upload token for the CI pipeline
  mrmeee.flatman.flatman_token:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    repository: stable
    name: ci-upload
    token_type: upload
    expires_at: "2027-01-31T23:59:59Z"
  register: ci_token
  no_log: true

- name: Disable a token without deleting it
  mrmeee.flatman.flatman_token:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    repository_id: 3
    name: ci-upload
    is_active: false

- name: Remove a token that is no longer needed
  mrmeee.flatman.flatman_token:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    repository: stable
    name: old-download
    state: absent

[1mRETURN VALUES:[0m

   token   The token object as returned by the API after the change.
           The `token' member holds the secret value and is only
           readable through the API, so treat the whole return value
           as sensitive.
        returned: when `state=present'
        sample:
          expires_at: '2027-01-31T23:59:59Z'
          id: 11
          is_active: true
          name: ci-upload
          token: VALUE_SPECIFIED_IN_NO_LOG_PARAMETER
          token_type: upload
        type: dict


```


### flatman_token_info

**FQCN:** `mrmeee.flatman.flatman_token_info`

```text

  Retrieve one or more repository scoped access tokens from a
  flat-manager-django server.
  Wraps the `/api/tokens/' endpoint.

[1mOPTIONS[0m (red indicates it is required):

   api_token  API token used for authentication, sent in an
              `Authorization' header of the form `Token <api_token>'.
              Create one in the web UI under your user profile, or
              with the `createapitoken' management command.
              May also be set with the `FLATMAN_API_TOKEN' environment
              variable.
              Not required for the public read-only `/api/v2'
              endpoints.
        default: null
        type: str

   client_cert  Path to a PEM formatted client certificate used for
                mutual TLS.
        default: null
        type: path

   client_key  Path to the PEM formatted private key matching
               `client_cert'.
        default: null
        type: path

   id      Return only the token with this numeric ID.
        default: null
        type: int

   include_names  Add best-effort human-readable companion fields for
                  related resource IDs in returned records.
                  Original numeric IDs are retained. Set to `false' to
                  skip the extra lookup requests.
        default: true
        type: bool

   is_active  Restrict the result to tokens with this active flag.
        default: null
        type: bool

   name    Return only the token with this exact name.
        default: null
        type: str

   repository  Restrict the result to tokens of the repository with
               this name.
               Mutually exclusive with `repository_id'.
        default: null
        type: str

   repository_id  Restrict the result to tokens of the repository with
                  this numeric ID.
                  Mutually exclusive with `repository'.
        default: null
        type: int

   timeout  Socket timeout in seconds for each individual HTTP
            request.
        default: 30
        type: int

   token_type  Restrict the result to tokens granting this kind of
               access.
        choices: [upload, download, admin]
        default: null
        type: str

   [1murl[0m     Base URL of the flat-manager-django instance, for example
           `https://flatman.example.com'.
           May also be set with the `FLATMAN_URL' environment
           variable.
        type: str

   validate_certs  Whether to validate the TLS certificate of the
                   flat-manager server.
                   May also be set with the `FLATMAN_VALIDATE_CERTS'
                   environment variable.
        default: true
        type: bool

[1mATTRIBUTES:[0m

        [4mcheck_mode:[0m
        description: This module makes no changes, so it fully supports `check_mode'.
        support: full

        [4mdiff_mode:[0m
        description: This module makes no changes, so it never reports a diff.
        support: N/A

[1mNOTES:[0m
      * [1mThese tokens are not enforced by the server yet.[0m
        The flat-manager-django server stores repository tokens
        but no code path validates an incoming request against
        them, so the values returned here currently grant no
        access.
      * Repository tokens are not the same thing as the
        `api_token' used to talk to the API. That one is a user
        scoped Django REST Framework token and cannot be read
        from this endpoint.
      * Every returned token carries its secret value, so use
        `no_log' on tasks that register the result.

[1mSEE ALSO:[0m
      * Module mrmeee.flatman.flatman_token

[1mREQUIREMENTS:[0m  ansible-core >= 2.15


[1mAUTHOR[0m: MrMEEE (@MrMEEE)

[1mEXAMPLES:[0m
- name: List the active upload tokens of the stable repository
  mrmeee.flatman.flatman_token_info:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    repository: stable
    token_type: upload
    is_active: true
  register: upload_tokens
  no_log: true

- name: Fail when the CI token is missing
  ansible.builtin.assert:
    that: upload_tokens.tokens | selectattr('name', 'equalto', 'ci-upload') | list | length == 1
    fail_msg: The ci-upload token is not present

- name: Look up a single token by ID
  mrmeee.flatman.flatman_token_info:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    id: 11
  register: one_token
  no_log: true

[1mRETURN VALUES:[0m

   tokens  The matching tokens.
           Each entry contains the secret `token' value, so treat the
           result as sensitive.
        elements: dict
        returned: always
        sample: [{expires_at: '2027-01-31T23:59:59Z', id: 11, is_active: true, name: ci-upload, token: VALUE_SPECIFIED_IN_NO_LOG_PARAMETER,
            token_type: upload}]
        type: list


```


### flatman_usage_info

**FQCN:** `mrmeee.flatman.flatman_usage_info`

```text

  Retrieve the published applications ranked by the number of unique
  clients that reported using them.
  Wraps the `/api/v2/usage/popular' endpoint.
  This endpoint is public, so `api_token' is optional.

[1mOPTIONS[0m (red indicates it is required):

   api_token  API token used for authentication, sent in an
              `Authorization' header of the form `Token <api_token>'.
              Create one in the web UI under your user profile, or
              with the `createapitoken' management command.
              May also be set with the `FLATMAN_API_TOKEN' environment
              variable.
              Not required for the public read-only `/api/v2'
              endpoints.
        default: null
        type: str

   client_cert  Path to a PEM formatted client certificate used for
                mutual TLS.
        default: null
        type: path

   client_key  Path to the PEM formatted private key matching
               `client_cert'.
        default: null
        type: path

   days    Size of the reporting window in days.
           The server clamps this value to the range 1 to 365, so
           smaller or larger values are silently adjusted.
           The value actually used is reported in `days'.
        default: 30
        type: int

   include_names  Add best-effort human-readable companion fields for
                  related resource IDs in returned records.
                  Original numeric IDs are retained. Set to `false' to
                  skip the extra lookup requests.
        default: true
        type: bool

   timeout  Socket timeout in seconds for each individual HTTP
            request.
        default: 30
        type: int

   [1murl[0m     Base URL of the flat-manager-django instance, for example
           `https://flatman.example.com'.
           May also be set with the `FLATMAN_URL' environment
           variable.
        type: str

   validate_certs  Whether to validate the TLS certificate of the
                   flat-manager server.
                   May also be set with the `FLATMAN_VALIDATE_CERTS'
                   environment variable.
        default: true
        type: bool

[1mATTRIBUTES:[0m

        [4mcheck_mode:[0m
        description: This module makes no changes, so it fully supports `check_mode'.
        support: full

        [4mdiff_mode:[0m
        description: This module makes no changes, so it never reports a diff.
        support: N/A

[1mSEE ALSO:[0m
      * Module mrmeee.flatman.flatman_app_stats_info
      * Module mrmeee.flatman.flatman_collection_info

[1mREQUIREMENTS:[0m  ansible-core >= 2.15


[1mAUTHOR[0m: MrMEEE (@MrMEEE)

[1mEXAMPLES:[0m
- name: Gather usage over the default 30 day window
  mrmeee.flatman.flatman_usage_info:
    url: https://flatman.example.com
  register: usage

- name: Gather usage over the last year
  mrmeee.flatman.flatman_usage_info:
    url: https://flatman.example.com
    days: 365
  register: yearly_usage

- name: Show the ten most used applications
  ansible.builtin.debug:
    msg: "{{ usage.apps[:10] | map(attribute='app_id') | list }}"

[1mRETURN VALUES:[0m

   apps    The applications with usage in the window, ordered by
           unique clients and then by observations.
        elements: dict
        returned: always
        sample: [{app_id: org.example.App, observations: 431, unique_clients: 87}, {app_id: org.example.Editor,
            observations: 54, unique_clients: 12}]
        type: list

   days    The reporting window actually used by the server, after
           clamping to the range 1 to 365.
        returned: always
        sample: 30
        type: int


```


### flatman_user

**FQCN:** `mrmeee.flatman.flatman_user`

```text

  Create, update and delete user records on a flat-manager-django
  server.
  Wraps the `/api/users/' endpoint.

[1mOPTIONS[0m (red indicates it is required):

   api_token  API token used for authentication, sent in an
              `Authorization' header of the form `Token <api_token>'.
              Create one in the web UI under your user profile, or
              with the `createapitoken' management command.
              May also be set with the `FLATMAN_API_TOKEN' environment
              variable.
              Not required for the public read-only `/api/v2'
              endpoints.
        default: null
        type: str

   client_cert  Path to a PEM formatted client certificate used for
                mutual TLS.
        default: null
        type: path

   client_key  Path to the PEM formatted private key matching
               `client_cert'.
        default: null
        type: path

   email   Email address of the user.
        default: null
        type: str

   first_name  Given name of the user.
        default: null
        type: str

   include_names  Add best-effort human-readable companion fields for
                  related resource IDs in returned records.
                  Original numeric IDs are retained. Set to `false' to
                  skip the extra lookup requests.
        default: true
        type: bool

   is_local  Whether this is a locally managed account rather than one
             provided by an external identity source.
        default: null
        type: bool

   last_name  Family name of the user.
        default: null
        type: str

   state   Whether the user should exist or not.
        choices: [present, absent]
        default: present
        type: str

   timeout  Socket timeout in seconds for each individual HTTP
            request.
        default: 30
        type: int

   [1murl[0m     Base URL of the flat-manager-django instance, for example
           `https://flatman.example.com'.
           May also be set with the `FLATMAN_URL' environment
           variable.
        type: str

   [1musername[0m  Login name of the user. Used as the unique key for
             idempotency.
        type: str

   validate_certs  Whether to validate the TLS certificate of the
                   flat-manager server.
                   May also be set with the `FLATMAN_VALIDATE_CERTS'
                   environment variable.
        default: true
        type: bool

[1mATTRIBUTES:[0m

        [4mcheck_mode:[0m
        description: Can run in `check_mode' and return the changes that would be made.
        support: full

        [4mdiff_mode:[0m
        description: Returns details on what has changed (or would have changed) when `--diff'
          is used.
        support: full

[1mNOTES:[0m
      * This module manages user records only. The API
        serializer exposes no password field, so a password
        cannot be set or changed here. Set local passwords
        through the web UI or a Django management command on the
        server.
      * Creating, updating and deleting users requires an
        administrator API token. Read access only requires an
        authenticated token.
      * Creating a user also creates an empty user profile on
        the server through a post-save signal.

[1mSEE ALSO:[0m
      * Module mrmeee.flatman.flatman_user_info
      * Module mrmeee.flatman.flatman_user_profile
      * Module mrmeee.flatman.flatman_token

[1mREQUIREMENTS:[0m  ansible-core >= 2.15


[1mAUTHOR[0m: MrMEEE (@MrMEEE)

[1mEXAMPLES:[0m
- name: Create a local maintainer account
  mrmeee.flatman.flatman_user:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    username: jdoe
    email: jdoe@example.com
    first_name: Jane
    last_name: Doe
    is_local: true

- name: Update the email address of an existing user
  mrmeee.flatman.flatman_user:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    username: jdoe
    email: jane.doe@example.com

- name: Remove a user that left the project
  mrmeee.flatman.flatman_user:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    username: olduser
    state: absent

[1mRETURN VALUES:[0m

   user    The user as returned by the API after the change.
        returned: when `state=present'
        sample:
          created_at: '2026-01-14T09:21:00Z'
          email: jdoe@example.com
          first_name: Jane
          id: 7
          is_local: true
          last_name: Doe
          username: jdoe
        type: dict


```


### flatman_user_info

**FQCN:** `mrmeee.flatman.flatman_user_info`

```text

  Retrieve one or more user records from a flat-manager-django server.
  Can also return the user the supplied API token belongs to.

[1mOPTIONS[0m (red indicates it is required):

   api_token  API token used for authentication, sent in an
              `Authorization' header of the form `Token <api_token>'.
              Create one in the web UI under your user profile, or
              with the `createapitoken' management command.
              May also be set with the `FLATMAN_API_TOKEN' environment
              variable.
              Not required for the public read-only `/api/v2'
              endpoints.
        default: null
        type: str

   client_cert  Path to a PEM formatted client certificate used for
                mutual TLS.
        default: null
        type: path

   client_key  Path to the PEM formatted private key matching
               `client_cert'.
        default: null
        type: path

   id      Return only the user with this numeric ID.
        default: null
        type: int

   include_names  Add best-effort human-readable companion fields for
                  related resource IDs in returned records.
                  Original numeric IDs are retained. Set to `false' to
                  skip the extra lookup requests.
        default: true
        type: bool

   me      Return only the user the API token authenticates as, using
           the `/api/users/me/' endpoint.
           Mutually exclusive with `username' and `id'.
        default: false
        type: bool

   search  Free text search across username, email, first name and
           last name.
        default: null
        type: str

   timeout  Socket timeout in seconds for each individual HTTP
            request.
        default: 30
        type: int

   [1murl[0m     Base URL of the flat-manager-django instance, for example
           `https://flatman.example.com'.
           May also be set with the `FLATMAN_URL' environment
           variable.
        type: str

   username  Return only the user with this exact login name.
        default: null
        type: str

   validate_certs  Whether to validate the TLS certificate of the
                   flat-manager server.
                   May also be set with the `FLATMAN_VALIDATE_CERTS'
                   environment variable.
        default: true
        type: bool

[1mATTRIBUTES:[0m

        [4mcheck_mode:[0m
        description: This module makes no changes, so it fully supports `check_mode'.
        support: full

        [4mdiff_mode:[0m
        description: This module makes no changes, so it never reports a diff.
        support: N/A

[1mSEE ALSO:[0m
      * Module mrmeee.flatman.flatman_user
      * Module mrmeee.flatman.flatman_user_profile_info

[1mREQUIREMENTS:[0m  ansible-core >= 2.15


[1mAUTHOR[0m: MrMEEE (@MrMEEE)

[1mEXAMPLES:[0m
- name: List every user
  mrmeee.flatman.flatman_user_info:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
  register: all_users

- name: Look up a single user by name
  mrmeee.flatman.flatman_user_info:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    username: jdoe
  register: jdoe

- name: Show who the token belongs to
  mrmeee.flatman.flatman_user_info:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    me: true
  register: whoami

- name: Print the authenticated username
  ansible.builtin.debug:
    msg: "Authenticated as {{ whoami.users[0].username }}"

[1mRETURN VALUES:[0m

   users   The matching users. Contains at most one element when
           `me=true', `id' or `username' is set.
        elements: dict
        returned: always
        sample: [{created_at: '2026-01-14T09:21:00Z', email: jdoe@example.com, first_name: Jane, id: 7,
            is_local: true, last_name: Doe, username: jdoe}]
        type: list


```


### flatman_user_profile

**FQCN:** `mrmeee.flatman.flatman_user_profile`

```text

  Create, update and delete the profile attached to a flat-manager
  user.
  Wraps the `/api/profiles/' endpoint.

[1mOPTIONS[0m (red indicates it is required):

   api_token  API token used for authentication, sent in an
              `Authorization' header of the form `Token <api_token>'.
              Create one in the web UI under your user profile, or
              with the `createapitoken' management command.
              May also be set with the `FLATMAN_API_TOKEN' environment
              variable.
              Not required for the public read-only `/api/v2'
              endpoints.
        default: null
        type: str

   bio     Free form biography text shown on the profile page.
        default: null
        type: str

   client_cert  Path to a PEM formatted client certificate used for
                mutual TLS.
        default: null
        type: path

   client_key  Path to the PEM formatted private key matching
               `client_cert'.
        default: null
        type: path

   include_names  Add best-effort human-readable companion fields for
                  related resource IDs in returned records.
                  Original numeric IDs are retained. Set to `false' to
                  skip the extra lookup requests.
        default: true
        type: bool

   organization  Organisation or company the user belongs to.
        default: null
        type: str

   phone   Contact phone number.
        default: null
        type: str

   state   Whether the profile should exist or not.
        choices: [present, absent]
        default: present
        type: str

   timeout  Socket timeout in seconds for each individual HTTP
            request.
        default: 30
        type: int

   [1murl[0m     Base URL of the flat-manager-django instance, for example
           `https://flatman.example.com'.
           May also be set with the `FLATMAN_URL' environment
           variable.
        type: str

   user    Login name of the user whose profile is managed.
           Mutually exclusive with `user_id'. One of the two is
           required.
        default: null
        type: str

   user_id  Numeric ID of the user whose profile is managed.
            Mutually exclusive with `user'. One of the two is
            required.
        default: null
        type: int

   validate_certs  Whether to validate the TLS certificate of the
                   flat-manager server.
                   May also be set with the `FLATMAN_VALIDATE_CERTS'
                   environment variable.
        default: true
        type: bool

[1mATTRIBUTES:[0m

        [4mcheck_mode:[0m
        description: Can run in `check_mode' and return the changes that would be made.
        support: full

        [4mdiff_mode:[0m
        description: Returns details on what has changed (or would have changed) when `--diff'
          is used.
        support: full

[1mNOTES:[0m
      * The server already creates one empty profile
        automatically whenever a user is created, so in practice
        this module updates that profile rather than creating a
        new one.
      * A user can only have one profile, so the owning user is
        the natural key. Addressing a user that already has a
        profile updates it instead of failing.
      * Changing or deleting a profile requires an administrator
        API token.

[1mSEE ALSO:[0m
      * Module mrmeee.flatman.flatman_user
      * Module mrmeee.flatman.flatman_user_profile_info

[1mREQUIREMENTS:[0m  ansible-core >= 2.15


[1mAUTHOR[0m: MrMEEE (@MrMEEE)

[1mEXAMPLES:[0m
- name: Fill in the profile of an existing user
  mrmeee.flatman.flatman_user_profile:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    user: jdoe
    bio: Flatpak packager and release manager
    organization: Example Inc
    phone: "+45 12 34 56 78"

- name: Update only the organisation, addressing the user by ID
  mrmeee.flatman.flatman_user_profile:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    user_id: 7
    organization: Example Foundation

- name: Delete the profile of a decommissioned account
  mrmeee.flatman.flatman_user_profile:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    user: olduser
    state: absent

[1mRETURN VALUES:[0m

   user_profile  The profile as returned by the API after the change.
        returned: when `state=present'
        sample:
          bio: Flatpak packager and release manager
          id: 12
          organization: Example Inc
          phone: +45 12 34 56 78
          user:
            email: jdoe@example.com
            id: 7
            username: jdoe
        type: dict


```


### flatman_user_profile_info

**FQCN:** `mrmeee.flatman.flatman_user_profile_info`

```text

  Retrieve one or more user profiles from a flat-manager-django
  server.
  Wraps the `/api/profiles/' endpoint.

[1mOPTIONS[0m (red indicates it is required):

   api_token  API token used for authentication, sent in an
              `Authorization' header of the form `Token <api_token>'.
              Create one in the web UI under your user profile, or
              with the `createapitoken' management command.
              May also be set with the `FLATMAN_API_TOKEN' environment
              variable.
              Not required for the public read-only `/api/v2'
              endpoints.
        default: null
        type: str

   client_cert  Path to a PEM formatted client certificate used for
                mutual TLS.
        default: null
        type: path

   client_key  Path to the PEM formatted private key matching
               `client_cert'.
        default: null
        type: path

   id      Return only the profile with this numeric profile ID,
           fetched from the detail endpoint.
        default: null
        type: int

   include_names  Add best-effort human-readable companion fields for
                  related resource IDs in returned records.
                  Original numeric IDs are retained. Set to `false' to
                  skip the extra lookup requests.
        default: true
        type: bool

   timeout  Socket timeout in seconds for each individual HTTP
            request.
        default: 30
        type: int

   [1murl[0m     Base URL of the flat-manager-django instance, for example
           `https://flatman.example.com'.
           May also be set with the `FLATMAN_URL' environment
           variable.
        type: str

   user    Return only the profile belonging to the user with this
           login name.
        default: null
        type: str

   user_id  Return only the profile belonging to the user with this
            numeric ID.
        default: null
        type: int

   validate_certs  Whether to validate the TLS certificate of the
                   flat-manager server.
                   May also be set with the `FLATMAN_VALIDATE_CERTS'
                   environment variable.
        default: true
        type: bool

[1mATTRIBUTES:[0m

        [4mcheck_mode:[0m
        description: This module makes no changes, so it fully supports `check_mode'.
        support: full

        [4mdiff_mode:[0m
        description: This module makes no changes, so it never reports a diff.
        support: N/A

[1mNOTES:[0m
      * The profile serializer exposes `user' as a nested
        read-only object, so filtering by `user' or `user_id' is
        done on the nested user object after the list has been
        retrieved.

[1mSEE ALSO:[0m
      * Module mrmeee.flatman.flatman_user_profile
      * Module mrmeee.flatman.flatman_user_info

[1mREQUIREMENTS:[0m  ansible-core >= 2.15


[1mAUTHOR[0m: MrMEEE (@MrMEEE)

[1mEXAMPLES:[0m
- name: List every user profile
  mrmeee.flatman.flatman_user_profile_info:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
  register: profiles

- name: Fetch the profile of a single user
  mrmeee.flatman.flatman_user_profile_info:
    url: https://flatman.example.com
    api_token: "{{ flatman_token }}"
    user: jdoe
  register: jdoe_profile

- name: Show the organisation of that user
  ansible.builtin.debug:
    msg: "{{ jdoe_profile.user_profiles[0].organization }}"

[1mRETURN VALUES:[0m

   user_profiles  The matching user profiles.
        elements: dict
        returned: always
        sample: [{bio: Flatpak packager and release manager, organization: Example Inc, phone: +45
              12 34 56 78, user: {email: jdoe@example.com, id: 7, username: jdoe}}]
        type: list


```


### flatman_workflow_action

**FQCN:** `mrmeee.flatman.flatman_workflow_action`

```text

  Dispatch an explicitly supported resource/action pair as a JSON
  POST.
  Supports BuildStream, release lifecycle, RPM, access membership and
  maintenance workflows.
  Uses the server web workflow field names for `data', including
  nested route IDs.

[1mOPTIONS[0m (red indicates it is required):

   [1maction[0m  Action name. Only pairs listed in the collection workflow
           guide are accepted.
           `delete', `unpublish', pruning and toggles can be
           destructive.
        choices: [renew, test-connection, test-search, scan-spec-files, scan-branches, toggle, bulk-import,
          unpublish, retry, republish, check-upstream, check-available, update-metadata, recommit,
          delete, cancel, bst-promote, build, force-rebuild, integrity-check, assign-organisations,
          lockdown, memberships, cleanup, sync-repositories, check-external-updates, scan-available-versions,
          scan-upstream-versions, repair-permissions, scan-orphaned-refs, prune-orphaned-ref,
          prune-orphaned-refs, build-with-number, toggle-repository, signing-key, assign-destination,
          repush, logs, sync, sync-repos, fetch-organisations, fetch-products, fetch-repositories]
        type: str

   api_token  API token used for authentication, sent in an
              `Authorization' header of the form `Token <api_token>'.
              Create one in the web UI under your user profile, or
              with the `createapitoken' management command.
              May also be set with the `FLATMAN_API_TOKEN' environment
              variable.
              Not required for the public read-only `/api/v2'
              endpoints.
        default: null
        type: str

   client_cert  Path to a PEM formatted client certificate used for
                mutual TLS.
        default: null
        type: path

   client_key  Path to the PEM formatted private key matching
               `client_cert'.
        default: null
        type: path

   data    JSON workflow body using upstream form/JSON names.
           Nested identifiers such as `repo_pk' or `dist_pk' belong
           here.
           Put credentials in `secret_data', not ordinary fields.
        default: {}
        type: dict

   id      Numeric source ID. Required for detail actions and
           forbidden for collection actions.
        default: null
        type: int

   include_names  Add best-effort human-readable companion fields for
                  related resource IDs in returned records.
                  Original numeric IDs are retained. Set to `false' to
                  skip the extra lookup requests.
        default: true
        type: bool

   [1mresource[0m  Router resource owning the action.
        choices: [gpg-keys, ldap-sources, flatpak-remotes, external-refs, packages, repositories, builds,
          promotions, external-ref-promotions, bst-promotions, bst-sources, clients, permission-groups,
          site-config, rpm-packages, rpm-builds, rpm-distributions, rpm-repositories, satellite-servers]
        type: str

   secret_data  Credential fields merged into `data' and protected
                with `no_log'.
                Must not duplicate fields in `data'.
                Only include secrets here; ordinary IDs belong in
                `data'.
        default: {}
        type: dict

   timeout  Socket timeout in seconds for each individual HTTP
            request.
        default: 30
        type: int

   [1murl[0m     Base URL of the flat-manager-django instance, for example
           `https://flatman.example.com'.
           May also be set with the `FLATMAN_URL' environment
           variable.
        type: str

   validate_certs  Whether to validate the TLS certificate of the
                   flat-manager server.
                   May also be set with the `FLATMAN_VALIDATE_CERTS'
                   environment variable.
        default: true
        type: bool

[1mATTRIBUTES:[0m

        [4mcheck_mode:[0m
        description: Validates arguments without dispatching any action, including read actions.
        support: full

        [4mdiff_mode:[0m
        description: Imperative actions do not return a diff.
        support: N/A

[1mNOTES:[0m
      * Requires a server with the expanded token workflow
        router.
      * Actions are imperative, not convergent, and never
        automatically retried or polled.
      * Read/report actions return `changed=false', even though
        the router uses POST for them.
      * Other actions return `changed=true' when successfully
        dispatched.
      * Version checks may update cached server fields even
        though reported as read actions.
      * Use `flatman_resource_info' to poll the affected record
        or inspect `error_message'.
      * Prefer dedicated promotion and External action modules
        when their idempotency/wait support is needed.
      * Use task-level `no_log=true' for workflows containing
        credentials.
      * GPG renewal takes `key_lifetime' as `"0"', `1y', `2y',
        `5y', or `10y', recalculated from today.
      * LDAP tests require `hostname'; search also requires
        `base_dn' and `search_username'.
      * LDAP tests accept connection settings and optional
        `source_pk' to reuse a saved bind password.
      * RPM discovery requires `url'; spec discovery accepts
        `branch', defaulting to `main'.
      * LDAP tests and RPM discovery return `changed=false';
        LDAP `ok=false' responses fail the task.

[1mREQUIREMENTS:[0m  ansible-core >= 2.15


[1mAUTHOR[0m: MrMEEE (@MrMEEE)

[1mEXAMPLES:[0m
- name: Build a BuildStream source
  mrmeee.flatman.flatman_workflow_action:
    resource: bst-sources
    action: build
    id: 12

- name: Inspect orphaned refs without pruning them
  mrmeee.flatman.flatman_workflow_action:
    resource: site-config
    action: scan-orphaned-refs

- name: Discover RPM spec files without changing a package
  mrmeee.flatman.flatman_workflow_action:
    resource: rpm-packages
    action: scan-spec-files
    timeout: 180
    data:
      url: https://github.com/example/app-rpm.git
      branch: main
  register: discovered_specs

[1mRETURN VALUES:[0m

   result  Raw workflow response, or an empty dictionary in check
           mode.
        returned: always
        type: dict


```


### flatman_year_in_review_info

**FQCN:** `mrmeee.flatman.flatman_year_in_review_info`

```text

  Retrieve the aggregated activity summary of a single calendar year.
  Wraps the `/api/v2/year-in-review/<year>' endpoint.
  This endpoint is public, so `api_token' is optional.

[1mOPTIONS[0m (red indicates it is required):

   api_token  API token used for authentication, sent in an
              `Authorization' header of the form `Token <api_token>'.
              Create one in the web UI under your user profile, or
              with the `createapitoken' management command.
              May also be set with the `FLATMAN_API_TOKEN' environment
              variable.
              Not required for the public read-only `/api/v2'
              endpoints.
        default: null
        type: str

   client_cert  Path to a PEM formatted client certificate used for
                mutual TLS.
        default: null
        type: path

   client_key  Path to the PEM formatted private key matching
               `client_cert'.
        default: null
        type: path

   include_names  Add best-effort human-readable companion fields for
                  related resource IDs in returned records.
                  Original numeric IDs are retained. Set to `false' to
                  skip the extra lookup requests.
        default: true
        type: bool

   timeout  Socket timeout in seconds for each individual HTTP
            request.
        default: 30
        type: int

   [1murl[0m     Base URL of the flat-manager-django instance, for example
           `https://flatman.example.com'.
           May also be set with the `FLATMAN_URL' environment
           variable.
        type: str

   validate_certs  Whether to validate the TLS certificate of the
                   flat-manager server.
                   May also be set with the `FLATMAN_VALIDATE_CERTS'
                   environment variable.
        default: true
        type: bool

   [1myear[0m    The calendar year to summarise, for example `2026'.
        type: int

[1mATTRIBUTES:[0m

        [4mcheck_mode:[0m
        description: This module makes no changes, so it fully supports `check_mode'.
        support: full

        [4mdiff_mode:[0m
        description: This module makes no changes, so it never reports a diff.
        support: N/A

[1mSEE ALSO:[0m
      * Module mrmeee.flatman.flatman_app_stats_info
      * Module mrmeee.flatman.flatman_usage_info

[1mREQUIREMENTS:[0m  ansible-core >= 2.15


[1mAUTHOR[0m: MrMEEE (@MrMEEE)

[1mEXAMPLES:[0m
- name: Gather the summary of last year
  mrmeee.flatman.flatman_year_in_review_info:
    url: https://flatman.example.com
    year: 2025
  register: review

- name: Show how many applications were added
  ansible.builtin.debug:
    msg: "{{ review.year_in_review.apps_added }} applications added in 2025"

- name: Gather the summary of the current year
  mrmeee.flatman.flatman_year_in_review_info:
    url: https://flatman.example.com
    year: "{{ '%Y' | ansible.builtin.strftime | int }}"
  register: current_review

[1mRETURN VALUES:[0m

   year_in_review  The aggregated activity summary of the requested
                   year.
        returned: always
        sample:
          apps_added: 42
          apps_updated: 128
          generated_at: '2026-01-02T08:00:00+00:00'
          unique_clients: 517
          usage_observations: 10432
          year: 2025
        type: dict


```

## Roles

Roles are documented in their individual guides:

- [curation](../roles/curation/README.md)
- [package](../roles/package/README.md)
- [repository](../roles/repository/README.md)
