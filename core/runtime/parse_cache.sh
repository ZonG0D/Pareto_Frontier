#!/bin/bash

# ==============================================================================
# parse_cache.sh - Intelligent LRU (Least Recently Used) Caching Shim
# Optimized for: High-value retention via Filesystem Metadata.
# 
# Logic: Instead of pruning the "oldest" files, we prune the "least recently used"
# files by updating timestamps on every cache hit. This ensures that valuable,
# frequently-used results are preserved regardless of when they were first created.
# ==============================================================================

# --- Configuration ---
CACHE_DIR="$HOME/.cache/parse_input_shim"
MAX_SIZE_BYTES=1073741824  # Hard Ceiling: 1 GB
SAFE_FLOOR_BYTES=536870912 # Safety Buffer (512 MB)
ORIGINAL_TOOL="/home/anonz/parse-input.sh"

# Ensure cache directory exists
mkdir -p "$CACHE_DIR"

# --- Background Rotation Logic ---
rotate_cache() {
    local current_size=$(du -sb "$CACHE_DIR" | awk '{print $1}')
    if [ "$current_size" -gt "$MAX_SIZE_BYTES" ]; then
        # Sort by modification time (newest first) to identify the "least recently used" files.
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

# Trigger rotation in the background to ensure zero user-perceived latency.
rotate_cache &!

# --- Input Capture and Hashing ---
INPUT_ARGS="$*"
if [ ! -t 0 ]; then
    STDIN_CONTENT=$(cat)
else
    STDIN_CONTENT=""
fi

HASH_TMP=$(mktemp /tmp/parse_cache_hash.XXXXXX)
echo -n "${INPUT_ARGS}${STDIN_CONTENT}" > "$HASH_TMP"
CACHE_ID=$(sha256sum "$HASH_TMP" | awk '{print substr($1, 1, 40)}')
rm -f "$HASH_TMP"

CACHE_FILE="$CACHE_DIR/$CACHE_ID.cache"

# --- Execution / Cache Check (The LRU Logic) ---

if [ -f "$CACHE_FILE" ]; then
    # [CACHE HIT]
    # THE CRITICAL "LRU" STEP: 
    # We 'touch' the file to update its modification time (mtime).
    # This moves it from the "old/unused" category to the "fresh/active" category.
    touch "$CACHE_FILE"
    cat "$CACHE_FILE"
else
    # [CACHE MISS]
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        RESULT=$(bash "$ORIGINAL_TOOL" $INPUT_ARGS)
    else
        RESULT=$(bash "$ORIGINAL_TOOL" $INPUT_ARGS)
    fi
    
    if [ -n "$RESULT" ]; then
        echo "$RESULT" > "$CACHE_FILE"
    fi
    
    echo "$RESULT"
fi

exit 0
