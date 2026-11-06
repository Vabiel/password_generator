#!/usr/bin/env bash
# Собирает описание релиза: раздел версии из CHANGELOG.md + общее дополнение
# (.github/release-notes-footer.md). Падает, если в CHANGELOG.md нет раздела этой версии.
#
#   .github/scripts/release-notes.sh 1.1.0 > notes.md
set -euo pipefail

version="${1:?usage: release-notes.sh VERSION}"
root="$(cd "$(dirname "$0")/../.." && pwd)"

# Текст между «## [VERSION]» и следующим заголовком «## [» (или ссылками внизу файла)
section="$(awk -v header="## [$version]" '
  index($0, header) == 1 { found = 1; next }
  found && (/^## \[/ || /^\[[^]]+\]: /) { exit }
  found { print }
' "$root/CHANGELOG.md" | sed -e '/./,$!d')"

if [[ -z "${section//[[:space:]]/}" ]]; then
  echo "CHANGELOG.md has no section for version $version (expected a heading '## [$version] - YYYY-MM-DD')" >&2
  exit 1
fi

printf '%s\n' "$section"
cat "$root/.github/release-notes-footer.md"
