#!/bin/bash

# --- Configuration ---
CACHE_DIR="$HOME/.cache/parse_input_shim"
MAX_SIZE_BYTES=1073741824  # Hard Ceiling: 1 GB
SAFE_FLOOR_BYTES=536870912 # Safety Buffer (512 MB)

# Use a relative path to find the partner script in the same directory
ORIGINAL_TOOL="$(dirname "$(readlink -f "$0")")/parse-input.sh"

# Ensure cache directory exists
mkdir -p "$CACHE_DIR"

# --- Background Rotation Logic ---
rotate_cache() {
    local current_size=$(du -sb "$CACHE_DIR" | awk '{print $1}')
    if [ "$current_size" -gt "$MAX_SIZE_BYTES" ]; then
        find "$CACHE_DIR" -type f -printf "%T@ %s\t%p\n" | \
        sort -rn | \
        awk -v limit="$SAFE_FLOOR_BYTES" 'BEGIN {FS="\t"; total=0} 
           {
             if (total < limit) {
               total += $2;
             } else {
               print $3;
             }
           }' | xargs -d '\n' rm -f -- 2>/dev/null
    fi
}

rotate_cache &!

# --- Input Capture and Hashing ---
# We receive the entire user input as a single string in $1.
INPUT_TEXT="$1"

if [ ! -t 0 ] && [ -z "$INPUT_TEXT" ]; then
    INPUT_TEXT=$(cat)
fi

if [ -z "$INPUT_TEXT" ]; then
    exit 0
fi

HASH_TMP=$(mktemp /tmp/parse_cache_hash.XXXXXX)
echo -n "$INPUT_TEXT" > "$HASH_TMP"
CACHE_ID=$(sha256sum "$HASH_TMP" | awk '{print substr($1, 1, 40)}')
rm -f "$HASH_TMP"

CACHE_FILE="$CACHE_DIR/$CACHE_ID.cache"

# --- Execution / Cache Check (The LRU Logic) ---

if [ -f "$CACHE_FILE" ]; then
    touch "$CACHE_FILE"
    cat "$CACHE_FILE"
else
    RESULT=$(bash "$ORIGINAL_TOOL" "$INPUT_TEXT")
    
    if [ -n "$RESULT" ]; then
        echo "$RESULT" > "$CACHE_FILE"
    fi
    
    echo "$RESULT"
fi

exit 0