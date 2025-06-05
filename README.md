# SadTalker WebSocket API: Real-time Talking Head Generation

[![ArXiv](https://img.shields.io/badge/ArXiv-PDF-red)](https://arxiv.org/abs/2211.12194) [![Project Page](https://img.shields.io/badge/Project-Page-Green)](https://sadtalker.github.io) [![Hugging Face Spaces](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Spaces-blue)](https://huggingface.co/spaces/vinthony/SadTalker)

**TL;DR:** Generate talking head videos from a single portrait image and audio file via WebSocket API.

**Input:** Single portrait image 🙎‍♂️ + Audio 🎤 = Talking head video 🎞

> ⚠️ **Note:** Our model only works on REAL people or portrait images similar to real persons. Anime talking head generation will be released in the future.

## 🚀 New: WebSocket API Server

This repository now includes a **FastAPI WebSocket server** for real-time talking head video generation with base64 input/output support.

### WebSocket API Features

- **Real-time processing** via WebSocket connections
- **Base64 input/output** for seamless integration
- **Concurrent request handling** with configurable limits
- **Progress tracking** and status updates
- **Docker deployment** ready with CUDA support
- **Interactive test client** for easy testing
- **Batch processing** capabilities
- **Error handling** and recovery

## Core Features

- Generate realistic talking head animations from a single image
- Support for various preprocessing modes (crop, resize, full)
- Face enhancement options (GFPGAN, RestoreFormer)
- Background enhancement (Real-ESRGAN)
- Expression control and pose manipulation
- 3D face visualization support
- Free-view 4D talking head generation

## Quick Start

### WebSocket API Server

Start the FastAPI WebSocket server:

```bash
# Install WebSocket dependencies
pip install fastapi uvicorn[standard] websockets

# Start the server
python fastapi_websocket_server.py
# or
uvicorn fastapi_websocket_server:app --host 0.0.0.0 --port 8000

# Or use the startup script
bash start_server.sh
```

**API Endpoints:**
- `ws://localhost:8000/ws` - WebSocket endpoint for inference
- `http://localhost:8000/` - API information
- `http://localhost:8000/test` - Interactive test client
- `http://localhost:8000/health` - Health check

### WebSocket API Usage

**Python Client Example:**
```python
import asyncio
import websockets
import json
import base64

async def generate_video():
    uri = "ws://localhost:8000/ws"
    
    # Read and encode files
    with open("image.jpg", "rb") as f:
        image_base64 = base64.b64encode(f.read()).decode()
    with open("audio.wav", "rb") as f:
        audio_base64 = base64.b64encode(f.read()).decode()
    
    async with websockets.connect(uri) as websocket:
        # Send request
        request = {
            "image_base64": image_base64,
            "audio_base64": audio_base64,
            "preprocess": "crop",
            "expression_scale": 1.0
        }
        await websocket.send(json.dumps(request))
        
        # Receive response
        response = await websocket.recv()
        result = json.loads(response)
        
        if result["status"] == "success":
            # Decode video
            video_data = base64.b64decode(result["video_base64"])
            with open("output.mp4", "wb") as f:
                f.write(video_data)

asyncio.run(generate_video())
```

**Test Clients:**
```bash
# Interactive web client
open http://localhost:8000/test

# Gradio WebSocket client (recommended)
python app_websocket.py
# or
bash start_gradio_client.sh

# Python CLI client
python test_client.py --image examples/source_image/art_0.png --audio examples/driven_audio/bus_chinese.wav

# Simple example
python simple_example.py

# Batch processing
python batch_example.py

# Complete test suite
python test_complete_suite.py
```

### Gradio WebSocket Client

Launch the **Gradio interface** that connects to the WebSocket API:

```bash
# Start WebSocket server first
python fastapi_websocket_server.py

# Then start Gradio client (in another terminal)
python app_websocket.py

# Or start both together
bash start_gradio_client.sh -s
```

**Features:**
- 🎨 **Beautiful web interface** with drag-and-drop file upload
- 🔄 **Real-time status updates** and progress tracking  
- ⚙️ **Full parameter control** (preprocessing, enhancement, etc.)
- 🎤 **Text-to-Speech integration** (when available)
- 📱 **Responsive design** for desktop and mobile
- 🔧 **Connection monitoring** with automatic retry

**Access URLs:**
- Gradio UI: `http://localhost:7860`
- WebSocket API: `http://localhost:8000`

## Installation

### Linux/macOS

1. Install [Anaconda](https://www.anaconda.com/), Python 3.8+, and `git`

2. Clone the repository:
```bash
git clone https://github.com/OpenTalker/SadTalker.git
cd SadTalker
```

3. Create environment and install dependencies:
```bash
conda create -n sadtalker python=3.8
conda activate sadtalker
pip install -r requirements.txt
```

4. Download models:
```bash
bash scripts/download_models.sh
```

5. Install WebSocket API dependencies:
```bash
pip install fastapi uvicorn[standard] websockets
```

### Docker Deployment

Build and run with Docker:

```bash
# Build image
docker build -t sadtalker-websocket .

# Run container
docker run -p 8000:8000 --gpus all sadtalker-websocket

# Or use docker-compose
docker-compose up -d
```

**Production with Nginx:**
```bash
# Use the included nginx.conf for reverse proxy
docker-compose -f docker-compose.yml up -d
```

### Windows

1. Install [Python 3.8](https://www.python.org/downloads/windows/) and [git](https://git-scm.com/download/win)
2. Clone repository: `git clone https://github.com/OpenTalker/SadTalker.git`
3. Download models (see [Download Models](#download-models))
4. Run `start.bat` for WebUI demo

### Download Models

**Pre-trained Models:**
- [Google Drive](https://drive.google.com/file/d/1gwWh45pF7aelNP_P78uDJL8Sycep-K7j/view?usp=sharing)
- [GitHub Releases](https://github.com/OpenTalker/SadTalker/releases)
- [Baidu Cloud](https://pan.baidu.com/s/1kb1BCPaLOWX1JJb9Czbn6w?pwd=sadt) (Password: `sadt`)

## Usage

### WebSocket API Parameters

| Parameter | Description | Type | Default |
|-----------|-------------|------|---------|
| `image_base64` | Base64 encoded source image | string | **required** |
| `audio_base64` | Base64 encoded audio file | string | **required** |
| `preprocess` | Processing mode (`crop`, `resize`, `full`) | string | `crop` |
| `expression_scale` | Expression strength (0.0-3.0) | float | `1.0` |
| `still` | Reduce head motion | boolean | `false` |
| `enhancer` | Face enhancer (`gfpgan`, `RestoreFormer`) | string | `null` |
| `background_enhancer` | Background enhancer (`realesrgan`) | string | `null` |

### WebSocket Response Format

```json
{
  "status": "success|processing|error",
  "message": "Status description",
  "video_base64": "base64_encoded_video_data",
  "video_url": "/static/results/filename.mp4",
  "request_id": "unique_request_identifier",
  "processing_time": 15.23
}
```

### Command Line Interface

### Command Line Interface

**Basic CLI usage:**

```bash
python inference.py --driven_audio <audio.wav> \
                    --source_image <image.png> \
                    --result_dir ./results
```

### Advanced Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--enhancer` | Face enhancement (`gfpgan`, `RestoreFormer`) | None |
| `--background_enhancer` | Background enhancement (`realesrgan`) | None |
| `--still` | Reduce head motion, use original pose | False |
| `--expression_scale` | Expression motion strength (higher = stronger) | 1.0 |
| `--preprocess` | Input processing (`crop`, `resize`, `full`) | `crop` |
| `--ref_eyeblink` | Reference video for natural eyeblink | None |
| `--ref_pose` | Reference video for head pose | None |
| `--face3dvis` | Generate 3D face visualization | False |

### Preprocessing Modes

- **`crop`**: Generate cropped facial animation (recommended for most cases)
- **`resize`**: Resize entire image (good for ID photo-like images)
- **`full`**: Process cropped region and paste back to original (use with `--still`)

### Examples

**Basic generation:**
```bash
python inference.py --driven_audio examples/driven_audio/bus_chinese.wav \
                    --source_image examples/source_image/art_0.png
```

**High quality with enhancement:**
```bash
python inference.py --driven_audio examples/driven_audio/bus_chinese.wav \
                    --source_image examples/source_image/art_0.png \
                    --enhancer gfpgan --background_enhancer realesrgan
```

**Full image mode with still pose:**
```bash
python inference.py --driven_audio examples/driven_audio/bus_chinese.wav \
                    --source_image examples/source_image/full_body_2.png \
                    --preprocess full --still
```

**Free-view 4D generation:**
```bash
python inference.py --driven_audio examples/driven_audio/bus_chinese.wav \
                    --source_image examples/source_image/art_0.png \
                    --input_yaw -20 30 10
```

### Gradio WebUI

Launch the original Gradio web interface:
```bash
python app.py
```

## Advanced Configuration

### WebSocket Server Configuration

The server can be configured via environment variables:

```bash
export SADTALKER_HOST="0.0.0.0"
export SADTALKER_PORT="8000"
export SADTALKER_MAX_CONCURRENT="3"
export SADTALKER_RESULTS_DIR="./results"
export SADTALKER_STATIC_DIR="./static"
```

### Performance Tuning

**GPU Memory Optimization:**
```python
# In fastapi_websocket_server.py
TORCH_DEVICE = "cuda"  # or "cpu"
MAX_CONCURRENT_REQUESTS = 3  # Adjust based on GPU memory
```

**Concurrent Processing:**
```bash
# Process multiple requests simultaneously
python batch_example.py --concurrent 5 --input_dir ./batch_inputs
```

## Examples & Tutorials

### Interactive Testing

1. **Web Test Client:**
   ```bash
   # Start server and open test page
   python fastapi_websocket_server.py
   # Navigate to http://localhost:8000/test
   ```

2. **Python Test Client:**
   ```bash
   python test_client.py \
     --image examples/source_image/art_0.png \
     --audio examples/driven_audio/bus_chinese.wav \
     --preprocess crop \
     --expression_scale 1.5
   ```

3. **Batch Processing:**
   ```bash
   python batch_example.py \
     --image_dir ./input_images \
     --audio_dir ./input_audios \
     --output_dir ./batch_results
   ```

### Integration Examples

**JavaScript/Node.js:**
```javascript
const WebSocket = require('ws');
const fs = require('fs');

const ws = new WebSocket('ws://localhost:8000/ws');

ws.on('open', function() {
    const imageBase64 = fs.readFileSync('image.jpg', 'base64');
    const audioBase64 = fs.readFileSync('audio.wav', 'base64');
    
    ws.send(JSON.stringify({
        image_base64: imageBase64,
        audio_base64: audioBase64,
        preprocess: 'crop'
    }));
});

ws.on('message', function(data) {
    const result = JSON.parse(data);
    if (result.status === 'success') {
        fs.writeFileSync('output.mp4', 
            Buffer.from(result.video_base64, 'base64'));
    }
});
```

**cURL Example:**
```bash
# Health check
curl http://localhost:8000/health

# Get API info
curl http://localhost:8000/
```

## Monitoring & Debugging

### Health Checks
```bash
# Server health
curl http://localhost:8000/health

# WebSocket connection test
wscat -c ws://localhost:8000/ws
```

### Logging
The server provides detailed logging for debugging:
```bash
# Start with debug logging
python fastapi_websocket_server.py --log-level debug

# View logs in Docker
docker logs sadtalker-websocket
```

### Performance Metrics
- Request processing time
- Concurrent request count
- GPU memory usage
- Queue status

## Requirements

### Core Dependencies
- Python 3.8+
- PyTorch 1.12+
- CUDA (recommended for GPU acceleration)
- FFmpeg

### WebSocket API Dependencies
```bash
pip install fastapi>=0.104.0
pip install uvicorn[standard]>=0.24.0
pip install websockets>=11.0.0
```

### Optional Enhancements
```bash
# Face enhancement
pip install gfpgan realesrgan

# 3D visualization
pip install -r requirements3d.txt
```

## File Structure

```
SadTalker-WS-API/
├── fastapi_websocket_server.py    # Main WebSocket server
├── app_websocket.py              # Gradio WebSocket client
├── test_client.html               # Interactive web test client
├── test_client.py                # Python CLI test client
├── simple_example.py             # Basic usage example
├── batch_example.py              # Batch processing example
├── test_complete_suite.py        # Complete test suite
├── start_server.sh               # Server startup script
├── start_gradio_client.sh        # Gradio client startup script
├── WEBSOCKET_API.md              # Detailed API documentation
├── docker-compose.yml            # Docker deployment
├── Dockerfile                    # Container configuration
├── nginx.conf                    # Reverse proxy config
├── requirements.txt              # Python dependencies
├── src/                          # SadTalker core modules
├── checkpoints/                  # Pre-trained models
├── examples/                     # Sample images and audio
└── results/                      # Generated videos
```

## Troubleshooting

### Common Issues

**Test the complete setup:**
```bash
# Run complete test suite
python test_complete_suite.py

# Test only WebSocket API
python test_complete_suite.py --websocket-only

# Test only Gradio client
python test_complete_suite.py --gradio-only

# Quick test (skip video generation)
python test_complete_suite.py --quick
```

**Server won't start:**
```bash
# Check Python environment
which python
python --version

# Install dependencies
pip install -r requirements.txt
pip install fastapi uvicorn[standard] websockets

# Check port availability
lsof -i :8000
```

**GPU/CUDA issues:**
```bash
# Check CUDA availability
python -c "import torch; print(torch.cuda.is_available())"

# Use CPU fallback
export TORCH_DEVICE="cpu"
```

**Memory errors:**
```bash
# Reduce concurrent requests
export SADTALKER_MAX_CONCURRENT="1"

# Use smaller models
export SADTALKER_MODEL_SIZE="256"
```

**Gradio client issues:**
```bash
# Check if WebSocket server is running
curl http://localhost:8000/health

# Start both servers together
bash start_gradio_client.sh -s

# Check Gradio logs
python app_websocket.py

# Test Gradio accessibility
curl http://localhost:7860
```

**WebSocket connection fails:**
```bash
# Test WebSocket endpoint
wscat -c ws://localhost:8000/ws

# Check firewall/proxy settings
curl -I http://localhost:8000/health
```

### Performance Optimization

1. **GPU Memory:** Reduce `MAX_CONCURRENT_REQUESTS` for limited VRAM
2. **CPU Processing:** Set `TORCH_DEVICE="cpu"` for CPU-only inference
3. **Batch Size:** Process multiple files concurrently with `batch_example.py`
4. **Caching:** Enable model caching for faster subsequent requests

## API Documentation

For detailed API documentation, see [WEBSOCKET_API.md](WEBSOCKET_API.md).

Key endpoints:
- **WebSocket:** `ws://localhost:8000/ws` - Main inference endpoint
- **Health:** `GET /health` - Server health check
- **Test:** `GET /test` - Interactive test client
- **Static:** `GET /static/*` - Generated video files

## License

This project is licensed under the Apache 2.0 License.

## Citation

If you find this work useful for your research, please cite:

```bibtex
@InProceedings{zhang2023sadtalker,
    author    = {Zhang, Wenxuan and Cun, Xiaodong and Wang, Fei and Zhang, Yong and Shen, Ji and Yu, Guangyong and Huang, Chunbo and Cao, Feiying and Zhong, Ran and Zhao, Hao and Ding, Shuai and Lei, Jie},
    title     = {SadTalker: Learning Realistic 3D Motion Coefficients for Stylized Audio-Driven Single Image Talking Face Animation},
    booktitle = {Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)},
    month     = {June},
    year      = {2023},
    pages     = {8652-8661}
}
```

## Acknowledgments

- Authors: Wenxuan Zhang, Fei Wang
- Affiliations: Xi'an Jiaotong University, Tencent AI Lab, Ant Group
- Conference: CVPR 2023

For more details, troubleshooting, and advanced features, please refer to:
- [WebSocket API Documentation](WEBSOCKET_API.md) - Comprehensive API guide
- [Original SadTalker Repository](https://github.com/OpenTalker/SadTalker) - Core implementation
- [Project Documentation](docs/) - Additional guides and tutorials