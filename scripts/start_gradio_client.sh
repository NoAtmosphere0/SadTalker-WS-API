#!/bin/bash

# SadTalker WebSocket Gradio Client Startup Script
# This script starts the Gradio web interface that connects to the WebSocket API

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
WS_URL="${SADTALKER_WS_URL:-ws://localhost:8000/ws}"
GRADIO_PORT="${GRADIO_PORT:-7860}"
GRADIO_HOST="${GRADIO_HOST:-0.0.0.0}"

echo -e "${BLUE}🌐 SadTalker WebSocket Gradio Client${NC}"
echo -e "${BLUE}=====================================${NC}"

# Function to check if WebSocket server is running
check_websocket_server() {
    local server_url="http://localhost:8000/health"
    echo -e "${YELLOW}📡 Checking WebSocket server at $server_url...${NC}"
    
    if curl -s --connect-timeout 5 "$server_url" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ WebSocket server is running${NC}"
        return 0
    else
        echo -e "${RED}❌ WebSocket server is not running${NC}"
        return 1
    fi
}

# Function to check Python dependencies
check_dependencies() {
    echo -e "${YELLOW}📦 Checking dependencies...${NC}"
    
    local missing_deps=()
    
    # Check core dependencies
    if ! python -c "import gradio" 2>/dev/null; then
        missing_deps+=("gradio")
    fi
    
    if ! python -c "import websockets" 2>/dev/null; then
        missing_deps+=("websockets")
    fi
    
    if ! python -c "import aiofiles" 2>/dev/null; then
        missing_deps+=("aiofiles")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        echo -e "${RED}❌ Missing dependencies: ${missing_deps[*]}${NC}"
        echo -e "${YELLOW}📥 Installing missing dependencies...${NC}"
        pip install "${missing_deps[@]}"
    else
        echo -e "${GREEN}✅ All dependencies are installed${NC}"
    fi
}

# Function to start Gradio app
start_gradio_app() {
    echo -e "${YELLOW}🚀 Starting Gradio WebSocket client...${NC}"
    echo -e "${BLUE}   WebSocket URL: $WS_URL${NC}"
    echo -e "${BLUE}   Gradio URL: http://$GRADIO_HOST:$GRADIO_PORT${NC}"
    echo ""
    
    export SADTALKER_WS_URL="$WS_URL"
    
    python app_websocket.py
}

# Function to show help
show_help() {
    echo -e "${BLUE}SadTalker WebSocket Gradio Client${NC}"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help              Show this help message"
    echo "  -c, --check-server      Only check if WebSocket server is running"
    echo "  -s, --start-server      Start WebSocket server first (in background)"
    echo "  --ws-url URL           WebSocket server URL (default: ws://localhost:8000/ws)"
    echo "  --port PORT            Gradio port (default: 7860)"
    echo "  --host HOST            Gradio host (default: 0.0.0.0)"
    echo ""
    echo "Environment Variables:"
    echo "  SADTALKER_WS_URL       WebSocket server URL"
    echo "  GRADIO_PORT            Gradio server port"
    echo "  GRADIO_HOST            Gradio server host"
    echo ""
    echo "Examples:"
    echo "  $0                     Start Gradio client"
    echo "  $0 -s                  Start WebSocket server then Gradio client"
    echo "  $0 -c                  Check if WebSocket server is running"
    echo "  $0 --port 8080         Start on port 8080"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -c|--check-server)
            check_websocket_server
            exit $?
            ;;
        -s|--start-server)
            echo -e "${YELLOW}🔄 Starting WebSocket server first...${NC}"
            if [ -f "fastapi_websocket_server.py" ]; then
                python fastapi_websocket_server.py &
                SERVER_PID=$!
                echo -e "${GREEN}✅ WebSocket server started with PID $SERVER_PID${NC}"
                sleep 3  # Give server time to start
            else
                echo -e "${RED}❌ fastapi_websocket_server.py not found${NC}"
                exit 1
            fi
            ;;
        --ws-url)
            WS_URL="$2"
            shift
            ;;
        --port)
            GRADIO_PORT="$2"
            shift
            ;;
        --host)
            GRADIO_HOST="$2"
            shift
            ;;
        *)
            echo -e "${RED}❌ Unknown option: $1${NC}"
            show_help
            exit 1
            ;;
    esac
    shift
done

# Main execution
main() {
    # Check if app_websocket.py exists
    if [ ! -f "app_websocket.py" ]; then
        echo -e "${RED}❌ app_websocket.py not found in current directory${NC}"
        exit 1
    fi
    
    # Check dependencies
    check_dependencies
    
    # Check WebSocket server (warning if not running)
    if ! check_websocket_server; then
        echo -e "${YELLOW}⚠️  WebSocket server is not running${NC}"
        echo -e "${YELLOW}   Start it with: python fastapi_websocket_server.py${NC}"
        echo -e "${YELLOW}   Or use: $0 -s to start both servers${NC}"
        echo ""
        echo -e "${YELLOW}🔄 Continuing anyway... (will show connection errors in UI)${NC}"
        echo ""
    fi
    
    # Start Gradio app
    start_gradio_app
}

# Cleanup function
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down...${NC}"
    if [ ! -z "$SERVER_PID" ]; then
        echo -e "${YELLOW}🔄 Stopping WebSocket server (PID $SERVER_PID)...${NC}"
        kill $SERVER_PID 2>/dev/null || true
    fi
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Run main function
main
