#!/bin/bash
# SadTalker FastAPI WebSocket Server Startup Script

# Set default values
HOST=${HOST:-"0.0.0.0"}
PORT=${PORT:-8000}
CHECKPOINT_PATH=${CHECKPOINT_PATH:-"data/checkpoints"}
CONFIG_PATH=${CONFIG_PATH:-"config"}
RESULTS_DIR=${RESULTS_DIR:-"data/results"}
STATIC_DIR=${STATIC_DIR:-"data/static"}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🎭 SadTalker FastAPI WebSocket Server${NC}"
echo -e "${BLUE}=====================================${NC}"

# Check if virtual environment exists
if [ ! -d "venv" ] && [ ! -d ".venv" ] && [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not detected. It's recommended to use one.${NC}"
    echo -e "${YELLOW}   To create one: python -m venv venv && source venv/bin/activate${NC}"
fi

# Check if checkpoints exist
if [ ! -d "$CHECKPOINT_PATH" ]; then
    echo -e "${RED}❌ Checkpoints directory not found: $CHECKPOINT_PATH${NC}"
    echo -e "${YELLOW}   Please download the SadTalker models first:${NC}"
    echo -e "${YELLOW}   bash scripts/download_models.sh${NC}"
    exit 1
fi

# Check if required checkpoint files exist
REQUIRED_FILES=(
    "$CHECKPOINT_PATH/mapping_00109-model.pth.tar"
    "$CHECKPOINT_PATH/mapping_00229-model.pth.tar"
    "$CHECKPOINT_PATH/SadTalker_V0.0.2_256.safetensors"
    "$CHECKPOINT_PATH/SadTalker_V0.0.2_512.safetensors"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo -e "${RED}❌ Required checkpoint file not found: $file${NC}"
        echo -e "${YELLOW}   Please download the SadTalker models first:${NC}"
        echo -e "${YELLOW}   bash scripts/download_models.sh${NC}"
        exit 1
    fi
done

echo -e "${GREEN}✅ Checkpoint files found${NC}"

# Check if Python dependencies are installed
echo -e "${BLUE}📦 Checking dependencies...${NC}"
if ! python -c "import fastapi, uvicorn, websockets" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Some dependencies are missing. Installing...${NC}"
    pip install fastapi uvicorn[standard] websockets python-multipart
fi

# Create necessary directories
mkdir -p "$RESULTS_DIR"
mkdir -p "$STATIC_DIR"

echo -e "${GREEN}✅ Dependencies ready${NC}"
echo -e "${BLUE}🚀 Starting SadTalker FastAPI WebSocket Server...${NC}"
echo -e "${BLUE}   Host: $HOST${NC}"
echo -e "${BLUE}   Port: $PORT${NC}"
echo -e "${BLUE}   Checkpoints: $CHECKPOINT_PATH${NC}"
echo -e "${BLUE}   Config: $CONFIG_PATH${NC}"
echo -e "${BLUE}   Results: $RESULTS_DIR${NC}"
echo -e "${BLUE}   Static: $STATIC_DIR${NC}"
echo ""
echo -e "${GREEN}🌐 Access the API at: http://localhost:$PORT${NC}"
echo -e "${GREEN}📡 WebSocket endpoint: ws://localhost:$PORT/ws${NC}"
echo -e "${GREEN}🧪 Test client: http://localhost:$PORT (serve test_client.html)${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo ""

# Start the server
python api/fastapi_server.py \
    --host "$HOST" \
    --port "$PORT" \
    --checkpoint-path "$CHECKPOINT_PATH" \
    --config-path "$CONFIG_PATH" \
    --results-dir "$RESULTS_DIR" \
    --static-dir "$STATIC_DIR"
