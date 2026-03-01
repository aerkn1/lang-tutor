#!/usr/bin/env bash
set -euo pipefail

date_suffix="${1:-$(date +%F)}"
language_dir="${PWD##*/}"

for section in grammar vocab; do
  if [[ ! -d "$section" ]]; then
    printf 'Missing required folder: %s/%s\n' "$PWD" "$section" >&2
    exit 1
  fi
done

create_note() {
  local section="$1"
  local target="$section/daily-notes-$date_suffix.md"

  if [[ -e "$target" ]]; then
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

  printf 'Created: %s\n' "$target"
}

create_note grammar
create_note vocab
