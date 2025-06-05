# SadTalker FastAPI WebSocket API

This project wraps the SadTalker inference engine in a FastAPI WebSocket server, enabling real-time talking head video generation through a simple WebSocket API.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install FastAPI dependencies
pip install fastapi uvicorn[standard] websockets python-multipart

# Or install all requirements
pip install -r requirements.txt
```

### 2. Download Models

```bash
bash scripts/download_models.sh
```

### 3. Start the Server

```bash
# Using the startup script (recommended)
./start_server.sh

# Or manually
python fastapi_websocket_server.py
```

### 4. Test the API

Open your browser and go to: `http://localhost:8000/test`

## 📡 API Endpoints

### WebSocket Endpoint: `/ws`

Connect to `ws://localhost:8000/ws` for real-time inference.

#### Message Format

Send JSON messages with the following structure:

```json
{
  "image_base64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
  "audio_base64": "data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAA...",
  "return_base64": false,
  "options": {
    "preprocess": "crop",
    "still_mode": false,
    "use_enhancer": false,
    "batch_size": 2,
    "size": 256,
    "pose_style": 0,
    "expression_scale": 1.0
  }
}
```

#### Response Format

The server will send multiple messages during processing:

```json
// Ready message
{
  "type": "ready",
  "message": "SadTalker is ready for inference"
}

// Status updates
{
  "type": "status",
  "message": "Processing request..."
}

// Success response
{
  "type": "success",
  "message": "Video generated successfully",
  "video_url": "/static/video-uuid.mp4"
  // OR
  "video_base64": "data:video/mp4;base64,AAAAIGZ0eXBpc29tAAACAG..."
}

// Error response
{
  "type": "error",
  "message": "Error description"
}
```

### HTTP Endpoints

- `GET /` - API information and documentation
- `GET /test` - Interactive test client
- `GET /health` - Health check
- `GET /static/{filename}` - Serve generated videos
- `GET /download/{filename}` - Download generated videos

## 🎛️ Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `preprocess` | string | `"crop"` | How to preprocess images (`crop`, `resize`, `full`, `extcrop`, `extfull`) |
| `still_mode` | boolean | `false` | Reduce head motion for more stable videos |
| `use_enhancer` | boolean | `false` | Use GFPGAN face enhancer |
| `batch_size` | integer | `2` | Batch size for rendering (1-10) |
| `size` | integer | `256` | Model resolution (`256` or `512`) |
| `pose_style` | integer | `0` | Pose style (0-46) |
| `expression_scale` | float | `1.0` | Expression intensity multiplier |
| `return_base64` | boolean | `false` | Return video as base64 instead of URL |

## 🧪 Testing

### Python Client

```bash
# Basic usage
python test_client.py \
  --image examples/source_image/art_0.png \
  --audio examples/driven_audio/bus_chinese.wav

# With custom options
python test_client.py \
  --image examples/source_image/art_0.png \
  --audio examples/driven_audio/bus_chinese.wav \
  --output result.mp4 \
  --preprocess crop \
  --size 512 \
  --enhancer \
  --expression-scale 1.5
```

### Web Client

1. Start the server: `./start_server.sh`
2. Open: `http://localhost:8000/test`
3. Upload an image and audio file
4. Adjust settings
5. Click "Generate Talking Head Video"

### cURL Example

```bash
# This is for WebSocket, so use a WebSocket client like wscat
npm install -g wscat
echo '{"image_base64":"...","audio_base64":"..."}' | wscat -c ws://localhost:8000/ws
```

## 🏗️ Architecture

```
┌─────────────────┐    WebSocket    ┌──────────────────┐
│   Client App    │◄──────────────►│  FastAPI Server  │
└─────────────────┘                └──────────────────┘
                                            │
                                            │ Python API
                                            ▼
                                   ┌──────────────────┐
                                   │   SadTalker      │
                                   │   Inference      │
                                   │   Engine         │
                                   └──────────────────┘
                                            │
                                            ▼
                                   ┌──────────────────┐
                                   │  Generated Video │
                                   │  (MP4 file)      │
                                   └──────────────────┘
```

## 🔧 Server Configuration

### Environment Variables

```bash
export HOST="0.0.0.0"                    # Server host
export PORT="8000"                       # Server port
export CHECKPOINT_PATH="checkpoints"     # Model checkpoints directory
export CONFIG_PATH="src/config"          # Config directory
export RESULTS_DIR="results"             # Results output directory
export STATIC_DIR="static"               # Static files directory
```

### Command Line Arguments

```bash
python fastapi_websocket_server.py \
  --host 0.0.0.0 \
  --port 8000 \
  --checkpoint-path checkpoints \
  --config-path src/config \
  --results-dir results \
  --static-dir static
```

## 📁 File Structure

```
SadTalker-WS-API/
├── fastapi_websocket_server.py    # Main FastAPI server
├── test_client.py                 # Python test client
├── test_client.html               # Web test client
├── start_server.sh                # Startup script
├── requirements.txt               # Dependencies
├── checkpoints/                   # Model checkpoints
├── src/                          # SadTalker source code
├── examples/                     # Example images and audio
├── results/                      # Generated videos
└── static/                       # Served video files
```

## 🔍 Preprocessing Modes

### `crop` (Recommended)
- Crops and focuses on the face region
- Best for portrait images
- Fastest processing
- Good quality for most use cases

### `resize`
- Resizes the entire image
- Good for ID photo-like images
- Maintains original aspect ratio

### `full`
- Processes the full image
- Use with `still_mode=true`
- Best for full-body shots
- Slower processing

### `extcrop` / `extfull`
- Extended versions with larger context
- Better for complex scenes
- Longer processing time

## ⚡ Performance Tips

1. **Use `crop` mode** for fastest processing
2. **Start with 256px model** before trying 512px
3. **Enable `still_mode`** for more stable videos
4. **Use smaller batch sizes** if running out of memory
5. **Keep audio files short** (< 30 seconds) for faster processing

## 🐛 Troubleshooting

### Common Issues

**"No face is detected"**
- Ensure the image contains a clear, visible face
- Try different preprocessing modes
- Check image quality and resolution

**Memory errors**
- Reduce batch size
- Use 256px model instead of 512px
- Ensure sufficient GPU memory

**Connection refused**
- Check if the server is running: `curl http://localhost:8000/health`
- Verify the port is not in use: `lsof -i :8000`
- Check firewall settings

**Slow processing**
- Use GPU acceleration if available
- Reduce audio length
- Use `crop` preprocessing mode
- Lower the batch size

### Debug Mode

Start the server with debug logging:

```bash
PYTHONPATH=. uvicorn fastapi_websocket_server:app --host 0.0.0.0 --port 8000 --log-level debug
```

## 🚦 Production Deployment

### Docker (Recommended)

```dockerfile
FROM python:3.8-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt
RUN bash scripts/download_models.sh

EXPOSE 8000
CMD ["python", "fastapi_websocket_server.py"]
```

### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Load Balancing

For multiple instances:

```bash
# Instance 1
python fastapi_websocket_server.py --port 8001

# Instance 2  
python fastapi_websocket_server.py --port 8002

# Use nginx upstream for load balancing
```

## 📊 Monitoring

### Health Check

```bash
curl http://localhost:8000/health
```

### Metrics

The server logs processing times and can be integrated with monitoring tools:

- Prometheus metrics (can be added)
- Custom logging handlers
- Performance monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project follows the same license as SadTalker (Apache 2.0).

## 🙏 Acknowledgments

- Original SadTalker paper and implementation
- FastAPI framework
- WebSocket protocol
- The open-source community
