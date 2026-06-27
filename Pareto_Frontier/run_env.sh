#!/bin/bash
# Pareto Frontier Environment Wrapper (The "One-Command" UX)
# This script abstracts the complexity of Docker orchestration, 
# providing a seamless interface for running prompts and benchmarks.

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCKER_COMPOSE="${PROJECT_ROOT}/docker-compose.yml"
CONTAINER_NAME="pareto-cli"

# Colors for feedback
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

log_info() { echo -e "${BLUE}[INFO]${NC} $*"; }
log_success() { echo -e "${GREEN}[OK]${NC} $*"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; exit 1; }

usage() {
    echo "$0"
    echo ""
    echo "Usage: $0 <command> [args...]"
    echo ""
    echo "Commands:"
    echo "  up          Start the full stack (Ollama + Pareto) in detached mode."
    echo "  down        Stop and remove all containers and volumes (Clean Slate)."
    echo "  run         Execute a prompt: $0 run <prompt> (e.g., $0 run 'Hello')"
    echo "          (Supports piped input from stdin)"
    echo "  benchmark   Run automated benchmarks within the container."
    echo "              $0 benchmark --experiment [standard|cache]"
    echo ""
    echo "Note: If you are running locally without Docker, use ./bin/pareto-run directly."
    exit 1
}

if [[ $# -eq 0 ]]; then
    usage
fi

COMMAND="$1"
shift # Remove command from arguments list

case "$COMMAND" in
    up)
        log_info "Starting Pareto stack via Docker Compose..."
        docker-compose -f "${DOCKER_COMPOSE}" up -d
        log_success "Stack is running. You can now use '$0 run <prompt>'"
        ;;
    down)
        echo -n "[!] This will remove all containers and volumes (including Ollama data). Continue? (y/N): "
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]] ; then
            log_warn "Tearing down the environment..."
            docker-compose -f "${DOCKER_COMPOSE}" down -v
            log_success "Environment destroyed."
        else
            echo "Aborted."
        fi
        ;;
    run|benchmark)
        # We use 'exec' because we want to run the command inside an existing container.
        # If the container isn't running, docker-compose exec will fail, which is appropriate.
        if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
            log_error "Container '${CONTAINER_NAME}' is not running. Did you run '$0 up'?"
        fi

        # If user provided no command (e.g. just './run_env.sh'), default to 'run' for legacy compatibility
        if [[ -z "$COMMAND" ]]; then CMD="run"; else CMD="$COMMAND"; fi
        
        log_info "Executing: $CMD $*"
        # Use docker exec with interactive terminal and pass through all arguments
        docker exec -it "${CONTAINER_NAME}" python3 bin/pareto_cli.py "$@"
        ;;
    *)
        usage
        ;;
esac
