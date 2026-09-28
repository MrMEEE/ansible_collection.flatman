# Endpoint to module map

Every documented endpoint of the flat-manager API and the module that wraps it.

## Core API (`/api/`)

Authenticated with an API token. Paths keep their trailing slash.

### Users

| Method | Endpoint | Module |
|---|---|---|
| GET | `/api/users/` | `flatman_user_info` |
| GET | `/api/users/{id}/` | `flatman_user_info` (`id`) |
| GET | `/api/users/me/` | `flatman_user_info` (`me: true`) |
| POST, PUT, DELETE | `/api/users/` | `flatman_user` |
| GET | `/api/profiles/` | `flatman_user_profile_info` |
| PUT, DELETE | `/api/profiles/{id}/` | `flatman_user_profile` |

### GPG keys

| Method | Endpoint | Module |
|---|---|---|
| GET | `/api/gpg-keys/` | `flatman_gpg_key_info` |
| GET | `/api/gpg-keys/{id}/public_key/` | `flatman_gpg_key_info` (`include: [public_key]`) |
| POST, PUT, DELETE | `/api/gpg-keys/` | `flatman_gpg_key` |
| POST | `/api/gpg-keys/generate/` | `flatman_gpg_key` (`state: generated`) |
| POST | `/api/gpg-keys/import_key/` | `flatman_gpg_key` (`state: imported`) |

### Repositories

| Method | Endpoint | Module |
|---|---|---|
| GET | `/api/repositories/` | `flatman_repository_info` |
| GET | `/api/repositories/{id}/builds/` | `flatman_repository_info` (`include: [builds]`) |
| GET | `/api/repositories/{id}/subsets/` | `flatman_repository_info` (`include: [subsets]`) |
| POST, PUT, DELETE | `/api/repositories/` | `flatman_repository` |
| GET | `/api/repository-subsets/` | `flatman_repository_subset_info` |
| POST, PUT, DELETE | `/api/repository-subsets/` | `flatman_repository_subset` |

### Packages

| Method | Endpoint | Module |
|---|---|---|
| GET | `/api/packages/` | `flatman_package_info` |
| POST, PUT, DELETE | `/api/packages/` | `flatman_package` |
| POST | `/api/packages/{id}/start/` | `flatman_package_action` (`action: start`) |
| POST | `/api/packages/{id}/cancel/` | `flatman_package_action` (`action: cancel`) |
| POST | `/api/packages/{id}/commit/` | `flatman_package_action` (`action: commit`) |
| POST | `/api/packages/{id}/publish/` | `flatman_package_action` (`action: publish`) |
| POST | `/api/packages/{id}/build_ref/` | `flatman_package_action` (`action: build_ref`) |
| GET, POST | `/api/packages/{id}/missing_objects/` | `flatman_package_action` (`action: missing_objects`) |
| POST | `/api/packages/{id}/upload/` | not wrapped — needs multipart |
| GET | `/api/packages/{id}/logs/` | `flatman_build_log_info` (`package_id`) |

### Builds and artifacts

| Method | Endpoint | Module |
|---|---|---|
| GET | `/api/builds/` | `flatman_build_info` |
| GET | `/api/builds/{id}/logs/` | `flatman_build_log_info` (`build_id`) |
| GET | `/api/artifacts/` | `flatman_artifact_info` |
| POST, PUT, DELETE | `/api/artifacts/` | `flatman_artifact` |

### Repository tokens and utility

| Method | Endpoint | Module |
|---|---|---|
| GET | `/api/tokens/` | `flatman_token_info` |
| POST, PUT, DELETE | `/api/tokens/` | `flatman_token` |
| GET | `/api/git-branches/` | `flatman_git_branch_info` |
| GET | `/api/version/` | `flatman_status_info` |

The repository tokens behind `/api/tokens/` are stored but never validated by the
server — see [authentication.md](authentication.md#repository-access-tokens-are-something-else--and-are-not-enforced-yet).

## Catalogue API (`/api/v2/`)

Mostly public. Note that these paths have **no** trailing slash, except
`/api/v2/stats/`.

### Applications

| Method | Endpoint | Module |
|---|---|---|
| GET | `/api/v2/status` | `flatman_status_info` |
| GET | `/api/v2/appstream` | `flatman_app_info` |
| GET | `/api/v2/appstream/{app_id}` | `flatman_app_info` (`app_id`) |
| PUT | `/api/v2/appstream/{app_id}/metadata` | `flatman_app_metadata` |
| GET | `/api/v2/summary/{app_id}` | `flatman_app_info` (`include: [summary]`) |
| GET | `/api/v2/addon/{app_id}` | `flatman_app_info` (`include: [addon]`) |
| GET | `/api/v2/is-fullscreen-app/{app_id}` | `flatman_app_info` (`include: [fullscreen]`) |
| GET | `/api/v2/platforms` | `flatman_platform_info` |
| GET | `/api/v2/runtimes` | `flatman_platform_info` |
| POST | `/api/v2/search` | `flatman_search_info` |

### Statistics

| Method | Endpoint | Module |
|---|---|---|
| GET | `/api/v2/stats/` | `flatman_app_stats_info` |
| GET | `/api/v2/stats/{app_id}` | `flatman_app_stats_info` (`app_id`) |
| GET | `/api/v2/usage/popular` | `flatman_usage_info` |
| GET | `/api/v2/year-in-review/{year}` | `flatman_year_in_review_info` |

### Collections and feeds

All handled by `flatman_collection_info`.

| Endpoint | Options |
|---|---|
| `/api/v2/collection/{collection}` | `collection: popular\|trending\|recently-added\|new\|recently-updated\|verified\|mobile\|alphabetical` |
| `/api/v2/collection/category` | `collection: category` |
| `/api/v2/collection/category/{value}` | `collection: category`, `value` |
| `/api/v2/collection/category/{value}/subcategories` | `collection: category`, `value`, `subcategories: true` |
| `/api/v2/collection/developer` | `collection: developer` |
| `/api/v2/collection/developer/{value}` | `collection: developer`, `value` |
| `/api/v2/collection/keyword` | `collection: keyword` |
| `/api/v2/collection/keywords` | `collection: keywords` |
| `/api/v2/feed/{feed}` | `collection: feed`, `value: new\|recently-updated` |

### Quality moderation

| Method | Endpoint | Module |
|---|---|---|
| GET | `/api/v2/quality-moderation/status` | `flatman_quality_moderation_info` (`report: status`) |
| GET | `/api/v2/quality-moderation/stats-by-category` | `flatman_quality_moderation_info` (`report: stats-by-category`) |
| GET | `/api/v2/quality-moderation/passing-apps` | `flatman_quality_moderation_info` (`report: passing-apps`) |
| GET | `/api/v2/quality-moderation/failed-by-guideline` | `flatman_quality_moderation_info` (`report: failed-by-guideline`) |
| GET | `/api/v2/quality-moderation/app-pick-recommendations` | `flatman_quality_moderation_info` (`report: app-pick-recommendations`) |
| GET | `/api/v2/quality-moderation/{app_id}/status` | `flatman_quality_moderation_info` (`app_id`) |
| POST | `/api/v2/quality-moderation/{app_id}/fullscreen` | `flatman_quality_moderation` (`action: fullscreen`) |
| POST | `/api/v2/quality-moderation/{app_id}/request-review` | `flatman_quality_moderation` (`action: request-review`) |

### Moderation requests

| Method | Endpoint | Module |
|---|---|---|
| POST | `/api/v2/moderation/submit_review_request` | `flatman_moderation_request` |
| GET | `/api/v2/moderation/apps` | `flatman_moderation_info` |
| GET | `/api/v2/moderation/apps/{app_id}` | `flatman_moderation_info` (`app_id`) |
| POST | `/api/v2/moderation/requests/{id}/review` | `flatman_moderation_review` |

### App picks

| Method | Endpoint | Module |
|---|---|---|
| GET | `/api/v2/app-picks/app-of-the-day` | `flatman_app_pick_info` (`scope: app-of-the-day`) |
| GET | `/api/v2/app-picks/app-of-the-day/{date}` | `flatman_app_pick_info` (`scope: app-of-the-day`, `date`) |
| GET | `/api/v2/app-picks/app-of-the-week` | `flatman_app_pick_info` (`scope: app-of-the-week`) |
| GET | `/api/v2/app-picks/apps-of-the-week/{date}` | `flatman_app_pick_info` (`scope: apps-of-the-week`, `date`) |
| GET | `/api/v2/app-picks/curated-app-selections/{date}` | `flatman_app_pick_info` (`scope: curated`, `date`) |
| GET | `/api/v2/app-picks/admin/curated-app-selections` | `flatman_app_pick_info` (`scope: admin-selections`) |
| GET | `/api/v2/app-picks/admin/curated-app-selection-themes` | `flatman_app_pick_info` (`scope: themes`) |
| GET | `/api/v2/app-picks/admin/apps-of-the-week/{date}` | `flatman_app_pick_info` (`scope: admin-apps-of-the-week`, `date`) |
| POST | `/api/v2/app-picks/admin/curated-app-selections` | `flatman_app_pick` (`state: present`) |
| PUT | `/api/v2/app-picks/admin/curated-app-selections/{id}` | `flatman_app_pick` (`state: present`, `id`) |
| DELETE | `/api/v2/app-picks/admin/curated-app-selections/{id}` | `flatman_app_pick` (`state: absent`) |

## Not wrapped

| Endpoint | Reason |
|---|---|
| `POST /api/packages/{id}/upload/` | Requires `multipart/form-data`, which the shared HTTP client does not build |
| `/api/auth/` | The DRF browsable API login form, not a data endpoint |
| Everything under `apps/flatpak/urls.py` and `apps/rpm/urls.py` | Session-authenticated HTML views for the web UI, not a public API |
| WebSocket consumers | Not reachable over HTTP |
