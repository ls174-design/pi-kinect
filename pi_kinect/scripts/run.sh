#!/bin/bash
set -euo pipefail

# Pi-Kinect Run Script
# Provides easy commands to run Pi-Kinect components

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Default configuration
CONFIG_FILE="${CONFIG_FILE:-$PROJECT_DIR/config/default.yaml}"
DEBUG="${DEBUG:-false}"

# Function to show usage
show_usage() {
    echo "Pi-Kinect Run Script"
    echo "===================="
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  probe                    Probe for available devices"
    echo "  stream [options]         Start streaming server"
    echo "  viewer [options]         Start GUI viewer"
    echo "  help                     Show this help message"
    echo ""
    echo "Options:"
    echo "  --config FILE           Configuration file (default: config/default.yaml)"
    echo "  --debug                 Enable debug mode"
    echo "  --host HOST             Host to bind to (streaming only)"
    echo "  --port PORT             Port to bind to (streaming only)"
    echo "  --camera INDEX          Camera index (streaming only)"
    echo "  --pi-ip IP              Pi IP address (viewer only)"
    echo "  --pi-port PORT          Pi port (viewer only)"
    echo ""
    echo "Examples:"
    echo "  $0 probe"
    echo "  $0 stream --port 8081"
    echo "  $0 viewer --pi-ip 192.168.1.50"
    echo "  $0 stream --config custom.yaml --debug"
}

# Parse command line arguments
COMMAND=""
ARGS=()

while [[ $# -gt 0 ]]; do
    case $1 in
        probe|stream|viewer|help)
            COMMAND="$1"
            shift
            ;;
        --config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        --debug)
            DEBUG="true"
            shift
            ;;
        --host|--port|--camera|--pi-ip|--pi-port)
            ARGS+=("$1" "$2")
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Check if command was provided
if [[ -z "$COMMAND" ]]; then
    echo "Error: No command provided"
    show_usage
    exit 1
fi

# Build command arguments
CMD_ARGS=()
if [[ "$DEBUG" == "true" ]]; then
    CMD_ARGS+=("--debug")
fi
if [[ -f "$CONFIG_FILE" ]]; then
    CMD_ARGS+=("--config" "$CONFIG_FILE")
fi
CMD_ARGS+=("${ARGS[@]}")

# Execute command
case "$COMMAND" in
    probe)
        echo "🔍 Probing for available devices..."
        pi-kinect probe "${CMD_ARGS[@]}"
        ;;
    stream)
        echo "🚀 Starting streaming server..."
        pi-kinect stream "${CMD_ARGS[@]}"
        ;;
    viewer)
        echo "📺 Starting GUI viewer..."
        pi-kinect viewer "${CMD_ARGS[@]}"
        ;;
    help)
        show_usage
        ;;
    *)
        echo "Error: Unknown command: $COMMAND"
        show_usage
        exit 1
        ;;
esac
