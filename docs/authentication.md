# Authentication

## How the modules authenticate

Every request carries an `Authorization` header holding the word `Token`
followed by the value of the `api_token` option. This is Django REST
Framework's `TokenAuthentication`, the first entry in
`REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES']` in `config/settings.py`,
backed by the `rest_framework.authtoken` table.

The modules never use session cookies, so no CSRF handling is involved.

## Creating a token

The easiest way is the web UI: log in, open **Profile**, and use the **API
Token** card to create, copy, regenerate or revoke your token. That page also
shows ready-to-run `curl` examples.

From the server shell, `rest_framework.authtoken` ships a management command:

```bash
python manage.py drf_create_token automation
```

It prints the token for the `automation` user, creating one if that user does
not have one yet. Equivalently, from the Django shell:

```bash
python manage.py shell -c "
from rest_framework.authtoken.models import Token
from apps.users.models import User
token, _ = Token.objects.get_or_create(user=User.objects.get(username='automation'))
print(token.key)
"
```

Tokens can also be managed from the Django admin under **Auth Token**. A user
has at most one token, so delete it to rotate.

An invalid or missing token produces a clear failure message from the modules,
reporting HTTP 401.

## Supplying the token to Ansible

Preferred, for a whole play:

```yaml
module_defaults:
  group/mrmeee.flatman.flatman:
    url: "{{ flatman_url }}"
    api_token: "{{ vault_flatman_token }}"
```

Keep the value in Ansible Vault or an external secret store. Never commit a
plain token.

Alternatively, export the environment variables on the controller:

| Variable | Option |
|---|---|
| `FLATMAN_URL` | `url` |
| `FLATMAN_API_TOKEN` | `api_token` |
| `FLATMAN_VALIDATE_CERTS` | `validate_certs` |

The `api_token` option is marked `no_log`, so it is never printed, even with
`-vvv`.

## Permissions

The server enforces role based access control. Which role you need depends on
the endpoint:

| Operation | Required role |
|---|---|
| Any read under `/api/` | Authenticated user |
| Repositories, subsets, GPG keys, tokens (write) | Repository admin |
| Packages, artifacts, build actions (write) | Build permission |
| Users and profiles (write) | Admin |
| Appstream metadata, moderation, app picks (write) | Admin |
| Public `/api/v2/` reads | None — no token required |

A token that lacks the required role produces HTTP 403 and the module fails with
`permission denied`.

## Repository access tokens are something else — and are not enforced yet

`flatman_token` and `flatman_token_info` manage the *repository* tokens from
`apps.flatpak.models.Token`. These were intended as upload, download and admin
credentials handed to CI systems and client machines to talk to a specific
repository, mirroring the upstream Rust `flat-manager`.

**That enforcement does not exist in flat-manager-django today.** The server
stores the tokens and exposes them over `/api/tokens/`, but no authentication
class, permission class, middleware or nginx rule ever validates an incoming
request against them, and the `token_type` field has no conditional logic
anywhere. Creating a repository token grants no access, and deleting one revokes
none.

The two modules are provided so the endpoint can be managed declaratively, and
so the collection covers the whole API. Do not build a workflow that relies on
these tokens gating anything until the server implements it. A repository token
also cannot be used as the `api_token` for these modules.

## TLS

`validate_certs` defaults to `true` and should stay that way. For mutual TLS,
supply `client_cert` and `client_key`. If your server uses a private CA, install
that CA in the controller trust store rather than disabling verification.
