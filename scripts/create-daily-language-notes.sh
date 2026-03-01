#!/usr/bin/env bash
set -euo pipefail

date_suffix="${1:-$(date +%F)}"
language_dir="${PWD##*/}"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
created_files=()
existing_files=()

for section in grammar vocab; do
  if [[ ! -d "$section" ]]; then
    printf 'Missing required folder: %s/%s\n' "$PWD" "$section" >&2
    exit 1
  fi
  mkdir -p "$section/daily"
done

create_note() {
  local section="$1"
  local target="$section/daily/daily-notes-$date_suffix.md"

  if [[ -e "$target" ]]; then
    existing_files+=("$target")
    printf 'Exists: %s\n' "$target"
    return
  fi

  if [[ "$section" == "grammar" ]]; then
    cat > "$target" <<EOF
# ${language_dir} grammar daily notes - $date_suffix

## Focus
-

## Rules and Patterns
-

## Example Sentences
-

## Questions
-
EOF
  else
    cat > "$target" <<EOF
# ${language_dir} vocab daily notes - $date_suffix

## New Words
-

## Review
-

## Example Sentences
-

## Notes
-
EOF
  fi

  created_files+=("$target")
  printf 'Created: %s\n' "$target"
}

join_list() {
  local joined=""
  local item

  for item in "$@"; do
    if [[ -n "$joined" ]]; then
      joined="$joined, "
    fi
    joined="$joined$item"
  done

  printf '%s' "$joined"
}

create_note grammar
create_note vocab

created_summary="none"
if [[ ${#created_files[@]} -gt 0 ]]; then
  created_summary="$(join_list "${created_files[@]}")"
fi

existing_summary="none"
if [[ ${#existing_files[@]} -gt 0 ]]; then
  existing_summary="$(join_list "${existing_files[@]}")"
fi

"$script_dir/append-skill-log.sh" \
  "create_daily_language_notes" \
  "$language_dir" \
  "date=$date_suffix; created=$created_summary; existing=$existing_summary"
