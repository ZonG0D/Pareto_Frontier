#!/bin/bash
set -euo pipefail

CACHE_DIR="$HOME/.cache/parse_input_shim"
MAX_SIZE_BYTES=1073741824
SAFE_FLOOR_BYTES=536870912
ORIGINAL_TOOL="$(dirname "$(readlink -f "$0")")/parse-input.sh"

mkdir -p "$CACHE_DIR"

rotate_cache() {
    local current_size=$(du -sb "$CACHE_DIR" | awk '{print $1}')
    if [ "$current_size" -gt "$MAX_SIZE_BYTES" ]; then
        find "$CACHE_DIR" -type f -printf "%T@ %s\t%p\n" | sort -rn | awk -v limit="$SAFE_FLOOR_BYTES" 'BEGIN {FS="\t"; total=0} {if (total < limit) {total += $2;} else {print $3;}}' | xargs -d '\n' rm -f -- 2>/dev/null || true
    fi
}

rotate_cache &!

INPUT_TEXT="$1"
[[ ! -t 0 && -z "$INPUT_TEXT" ]] && INPUT_TEXT=$(cat)
[[ -z "$INPUT_TEXT" ]] && exit 0

HASH_TMP=$(mktemp /tmp/parse_cache_hash.XXXXXX)
echo -n "$INPUT_TEXT" > "$HASH_TMP"
CACHE_ID=$(sha256sum "$HASH_TMP" | awk '{print substr($1, 1, 40)}')
rm -f "$HASH_TMP"

CACHE_FILE="$CACHE_DIR/$CACHE_ID.cache"

if [ -f "$CACHE_FILE" ]; then
    touch "$CACHE_FILE"
    RAW_CONTENT=$(cat "$CACHE_FILE")
    if echo "$RAW_CONTENT" | jq . >/dev/null 2>&1; then
        # Inject cache hit info into the JSON
        echo "$RAW_CONTENT" | jq --argjson hit '{"cache_hit": true}' '. + $hit'
    else
        echo "$RAW_CONTENT"
    fi
else
    RESULT=$(printf "%s
" "$INPUT_TEXT" | bash "$ORIGINAL_TOOL" -s)
    if [ -n "$RESULT" ]; then
        echo "$RESULT" > "$CACHE_FILE"
        echo "$RESULT"
    fi
fi

exit 0
