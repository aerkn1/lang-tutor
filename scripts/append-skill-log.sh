#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 3 ]]; then
  printf 'Usage: %s <skill_name> <language> <summary>\n' "${0##*/}" >&2
  exit 1
fi

skill_name="$1"
language_name="$2"
shift 2
summary="$*"

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/.." && pwd)"
changelog_file="$repo_root/CHANGELOG.md"
today="$(date +%F)"
time_stamp="$(date +%H:%M:%S)"
date_header="## $today"
log_line="- $time_stamp | \`$skill_name\` | \`$language_name\` | $summary"

if [[ ! -f "$changelog_file" ]]; then
  cat > "$changelog_file" <<EOF
# Change Log

Centralized daily log for skill activity in this repository.

EOF
fi

if ! grep -Fqx "$date_header" "$changelog_file"; then
  printf '\n%s\n\n' "$date_header" >> "$changelog_file"
fi

printf '%s\n' "$log_line" >> "$changelog_file"
