#!/usr/bin/env bash
set -euo pipefail

collection_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
collections_root="$(cd "$collection_root/../../.." && pwd)"
output="$collection_root/docs/module-reference.md"
temporary_output="$(mktemp "$collection_root/docs/.module-reference.XXXXXX")"
trap 'rm -f "$temporary_output"' EXIT

export ANSIBLE_COLLECTIONS_PATH="$collections_root"

{
  cat <<'EOF'
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

EOF

  while IFS= read -r plugin; do
    short_name="${plugin##*.}"
    printf -- '- [%s](#%s)\n' "$short_name" "$short_name"
  done < <(ansible-doc -t module -l mrmeee.flatman | awk '{print $1}')

  while IFS= read -r plugin; do
    short_name="${plugin##*.}"
    printf '\n### %s\n\n**FQCN:** `%s`\n\n```text\n' "$short_name" "$plugin"
    ansible-doc -t module "$plugin" | sed '1{/^> MODULE /d;}'
    printf '\n```\n\n'
  done < <(ansible-doc -t module -l mrmeee.flatman | awk '{print $1}')

  cat <<'EOF'
## Roles

Roles are documented in their individual guides:

- [curation](../roles/curation/README.md)
- [package](../roles/package/README.md)
- [repository](../roles/repository/README.md)
EOF
} > "$temporary_output"

mv "$temporary_output" "$output"
