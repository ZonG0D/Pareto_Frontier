#!/usr/bin/env bash
# parse-input.sh – Clean & enrich user text via Ollama.

set -euo pipefail

# ---------- Colours ----------
readonly RED='\033[1;31m'
readonly GREEN='\033[1;32m'
readonly BLUE='\033[1;34m'
readonly NC='\033[0m'

DEBUG="${DEBUG:-false}"
log()  { [[ "$DEBUG" == "true" ]] && echo -e "${BLUE}[DEBUG]${NC} $*" >&2 || true ; }
info() { echo -e "${GREEN}[INFO]${NC} $*" >&2 ; }
die()  { echo -e "${RED}[ERROR]${NC} $*" >&2; exit 1; }

# ---------- Dependency checks ----------
for cmd in curl jq sed awk; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
        die "Required command '$cmd' is not installed or not in PATH."
    fi
done

# ---------- Utility: trim whitespace (using sed) ----------
trim() {
    echo -n "$1" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//'
}

# ---------- Input collection ----------
collect_input() {
    local temp_file
    temp_file=$(mktemp)

    if [[ "$1" == "-s" || "${STDIN_ONLY:-0}" == "1" ]]; then
        log "Reading forced from stdin."
        cat > "$temp_file"
    else
        if [ $# -gt 0 ]; then
            log "Processing CLI argument(s) ($#)."
            printf '%s\n' "$@" > "$temp_file"
        else
            log "No CLI args found. Reading from stdin."
            cat >> "$temp_file" || true
        fi
    fi

    local raw_text
    raw_text=$(sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' < "$temp_file")
    rm -f -- "$temp_file"
    [[ -z "$raw_text" ]] && die "No input text supplied – nothing to parse."
    echo "$raw_text"
}

# ---------- Extraction logic ----------------------------------
extract_fields() {
    local resp="$1"
    CLEANED_TEXT=""
    SEMANTIC_HELPER=""

    if ! echo "$resp" | jq . >/dev/null 2>&1; then
        CLEANED_TEXT=$(trim "$resp")
        SEMANTIC_HELPER="Model returned non-JSON response; raw output used."
    else
        local resp_type
        resp_type=$(echo "$resp" | jq -r 'type')

        case "$resp_type" in
            object)
                CLEANED_TEXT=$(echo "$resp" | jq -r '.cleaned_text // empty' 2>/dev/null || echo "")
                SEMANTIC_HELPER=$(echo "$resp" | jq -r '.semantic_helper // empty' 2>/dev/null || echo "")

                if [[ -z "$CLEANED_TEXT" ]]; then
                    local msg_content
                    msg_content=$(echo "$resp" | jq -r '.message.content // .thinking // empty' 2>/dev/null || echo "")
                    if [[ -n "$msg_content" ]]; then
                        CLEANED_TEXT="$msg_content"
                        [[ -z "$SEMANTIC_HELPER" ]] && SEMANTIC_HELPER="Extracted from message content."
                    fi
                fi

                if [[ -z "$CLEANED_TEXT" || "$CLEANED_TEXT" == "null" ]]; then
                    local nested
                    nested=$(echo "$resp" | jq -r '.. | select(type=="object") | if (.[$env.CLEANED_KEY] != null and .semantic_helper != null) then {ct: .[$env.CLEANED_KEY], sh: .semantic_helper} else empty end' 2>/dev/null || echo "")
                    if [[ -n "$nested" ]]; then
                        CLEANED_TEXT=$(echo "$nested" | jq -r '.ct')
                        SEMANTIC_HELPER=$(echo "$nested" | jq -r '.sh')
                    fi
                fi

                [[ -z "$CLEANED_TEXT" || "$CLEANED_TEXT" == "null" ]] && CLEANED_TEXT="$(trim "$resp")"
                [[ -z "$SEMANTIC_HELPER" || "$SEMANTIC_HELPER" == "null" ]] && SEMANTIC_HELPER="Parsed content (auto-inferred)."
            *)
                CLEANED_TEXT=$(trim "$resp")
                SEMANTIC_HELPER="Model returned $resp_type; raw output used."
                ;;
        esac
    fi
}

# ---------- Main entry point ----------
main() {
    STDIN_ONLY=0
    CLEANED_KEY="cleaned_text"
    OUTPUT_AS_JSON=0
    INPUT_PARTS=()

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -h|--help) usage; exit 0 ;;
            -s|--stdin) STDIN_ONLY=1; shift ;;
            -o|--output) OUTPUT_AS_JSON=1; shift ;;
            -k|--key) CLEANED_KEY="$2"; shift 2 ;;
            --) shift; break ;;
            *) INPUT_PARTS+=("$1"); shift ;;
        esac
    done

    # Input Collection
    local raw_input
    if [[ "$STDIN_ONLY" == "1" ]]; then
        raw_input=$(collect_input "-s")
    elif [ ${#INPUT_PARTS[@]} -gt 0 ]; then
        raw_input="${INPUT_PARTS[*]}"
    else
        if read -r first_arg; then
            INPUT_PARTS+=("$first_arg")
            raw_input="$first_arg"
        else
            die "No input supplied."
        fi
    fi

    # Resolve Ollama connection info
    local endpoint_url="${OLLAMA_ENDPOINT:-http://localhost:11434/api/chat}"
    if [[ ! "$endpoint_url" =~ ^http ]]; then
        endpoint_url="http://${endpoint_url}/api/chat"
    fi

    log "Sending request to Ollama at $endpoint_url..."

    # Construct payload using jq - highly robust against special characters in prompt.
    local payload_json
    payload_json=$(jq -n \
        --arg model "${MODEL_NAME:-gemma3n:e2b-it-q4_K_M}" \
        --arg user "$raw_input" \
        --arg sys "You are Silas, a deterministic input parsing engine. Your job is to sanitize and classify text into JSON format: {\"cleaned_text\": \"string\", \"semantic_helper\": \"string\"}. Rules: 1. Correct typos/grammar while preserving original intent. 2. Output ONLY valid JSON. 3. No meta-talk." \
        '{model: $model, messages: [{role: "system", content: $sys}, {role: "user", content: $user}], stream: false, format: "json"}')

    local ollama_resp curl_status
    curl -sSf -X POST "$endpoint_url" \
         -H "Content-Type: application/json" \n
         -d "$payload_json" > /tmp/ollama_resp.json || curl_status=$?

    if [ $curl_status -ne 0 ]; then
        die "Ollama API call failed with exit code $curl_status at $endpoint_url."
    fi

    local resp_content
    resp_content=$(cat /tmp/ollama_resp.json)

    # Extraction
    extract_fields "$resp_content"

    if [[ "$OUTPUT_AS_JSON" -eq 1 ]]; then
        jq -n --arg ck "$CLEANED_KEY" --arg ct "$CLEANED_TEXT" --arg sh "$SEMANTIC_HELPER" '{($ck): $ct, "semantic_helper": $sh}'
        exit 0
    fi

    # Output the JSON object containing enriched data.
    jq -n \
        --arg ck "$CLEANED_KEY" \
        --arg ct "$CLEANED_TEXT" \
        --arg sh "$SEMANTIC_HELPER" \
        '{($ck): $ct, "semantic_helper": $sh}'

    log "=== Finished successfully ==="
}

usage() {
    cat <<EOF
Usage: $(basename "$0") [options] <text...>
Options:
  -h, --help          Show this help
  -s, --stdin         Force reading from stdin
  -o, --output json   Output raw JSON response
  -k, --key FIELD      Field name for cleaned text (default: cleaned_text)
EOF
}

main "$@"
