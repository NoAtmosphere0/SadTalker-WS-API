#!/bin/bash
# SadTalker Gradio WebSocket Client Startup Script

# Set default values
HOST=${HOST:-"0.0.0.0"}
PORT=${PORT:-7860}
WS_URL=${SADTALKER_WS_URL:-"ws://localhost:8000/ws"}
START_SERVER=${START_SERVER:-false}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🌐 SadTalker Gradio WebSocket Client${NC}"
echo -e "${BLUE}====================================${NC}"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -s|--start-server)
            START_SERVER=true
            shift
            ;;
        -h|--host)
            HOST="$2"
            shift 2
            ;;
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        -w|--ws-url)
            WS_URL="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  -s, --start-server    Start WebSocket server alongside client"
            echo "  -h, --host HOST       Host address (default: 0.0.0.0)"
            echo "  -p, --port PORT       Port number (default: 7860)"
            echo "  -w, --ws-url URL      WebSocket server URL (default: ws://localhost:8000/ws)"
            echo "  --help                Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Check if virtual environment exists
if [ ! -d "venv" ] && [ ! -d ".venv" ] && [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not detected. It's recommended to use one.${NC}"
fi

# Check if Python dependencies are installed
echo -e "${BLUE}📦 Checking dependencies...${NC}"
if ! python -c "import gradio, websockets, aiofiles" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Some dependencies are missing. Installing...${NC}"
    pip install gradio websockets aiofiles
fi

# Start WebSocket server if requested
if [ "$START_SERVER" = true ]; then
    echo -e "${BLUE}🚀 Starting WebSocket server first...${NC}"
    python api/fastapi_server.py &
    SERVER_PID=$!
    
    # Wait for server to start
    echo -e "${YELLOW}⏳ Waiting for WebSocket server to start...${NC}"
    sleep 5
    
    # Check if server is running
    if curl -f http://localhost:8000/health >/dev/null 2>&1; then
        echo -e "${GREEN}✅ WebSocket server is running${NC}"
    else
        echo -e "${RED}❌ Failed to start WebSocket server${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✅ Dependencies ready${NC}"
echo -e "${BLUE}🚀 Starting SadTalker Gradio WebSocket Client...${NC}"
echo -e "${BLUE}   Host: $HOST${NC}"
echo -e "${BLUE}   Port: $PORT${NC}"
echo -e "${BLUE}   WebSocket URL: $WS_URL${NC}"
echo -e

export SADTALKER_WS_URL="$WS_URL"

# Start Gradio client
python api/gradio_client.py

# Cleanup server if we started it
if [ "$START_SERVER" = true ] && [ ! -z "$SERVER_PID" ]; then
    echo -e "${BLUE}🛑 Stopping WebSocket server...${NC}"
    kill $SERVER_PID 2>/dev/null
    echo -e "${GREEN}✅ Server stopped${NC}"
fi