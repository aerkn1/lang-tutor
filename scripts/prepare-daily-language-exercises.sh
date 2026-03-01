#!/usr/bin/env bash
set -euo pipefail

force=0
date_suffix=""

for arg in "$@"; do
  case "$arg" in
    --force)
      force=1
      ;;
    *)
      if [[ -n "$date_suffix" ]]; then
        printf 'Usage: %s [--force] [YYYY-MM-DD]\n' "${0##*/}" >&2
        exit 1
      fi
      date_suffix="$arg"
      ;;
  esac
done

if [[ -z "$date_suffix" ]]; then
  date_suffix="$(date +%F)"
fi

language_dir="${PWD##*/}"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
language_title="$(printf '%s' "$language_dir" | awk '{ print toupper(substr($0, 1, 1)) substr($0, 2) }')"

for required_dir in grammar vocab exercise; do
  if [[ ! -d "$required_dir" ]]; then
    printf 'Missing required folder: %s/%s\n' "$PWD" "$required_dir" >&2
    exit 1
  fi
done

mkdir -p grammar/daily vocab/daily exercise/daily

grammar_file="grammar/daily/daily-notes-$date_suffix.md"
vocab_file="vocab/daily/daily-notes-$date_suffix.md"
target_file="exercise/daily/daily-exercises-$date_suffix.md"

note_status() {
  local source="$1"

  if [[ ! -f "$source" ]]; then
    printf 'missing'
    return
  fi

  if awk '
    /^[[:space:]]*#/ { next }
    /^[[:space:]]*$/ { next }
    /^[[:space:]]*-[[:space:]]*$/ { next }
    { found=1; exit }
    END {
      if (found) {
        print "filled"
      } else {
        print "empty"
      }
    }
  ' "$source"; then
    return
  fi

  printf 'empty'
}

grammar_status="$(note_status "$grammar_file")"
vocab_status="$(note_status "$vocab_file")"

action="create"
if [[ -e "$target_file" ]]; then
  if [[ $force -eq 1 ]]; then
    action="regenerate"
  else
    action="skip"
  fi
fi

if [[ "$action" != "skip" ]]; then
  cat > "$target_file" <<EOF
# $language_title Daily Exercises - $date_suffix

## Source Summary
- \`$grammar_file\`: $grammar_status
- \`$vocab_file\`: $vocab_status

## Exercise Basis
Pending AI generation.

## Coverage Checklist
- Pending AI generation.

## Fill in the Blank
1. Pending AI generation.

## Grammar Practice
1. Pending AI generation.
EOF
fi

"$script_dir/append-skill-log.sh" \
  "create_daily_language_exercises" \
  "$language_dir" \
  "date=$date_suffix; action=$action; target=$target_file; grammar=$grammar_status; vocab=$vocab_status"

printf 'ACTION=%s\n' "$action"
printf 'LANGUAGE=%s\n' "$language_dir"
printf 'DATE=%s\n' "$date_suffix"
printf 'TARGET_FILE=%s\n' "$target_file"
printf 'GRAMMAR_FILE=%s\n' "$grammar_file"
printf 'GRAMMAR_STATUS=%s\n' "$grammar_status"
printf 'VOCAB_FILE=%s\n' "$vocab_file"
printf 'VOCAB_STATUS=%s\n' "$vocab_status"
