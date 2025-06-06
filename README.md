# SadTalker WebSocket API: Real-time Talking Head Generation

[![ArXiv](https://img.shields.io/badge/ArXiv-PDF-red)](https://arxiv.org/abs/2211.12194) [![Project Page](https://img.shields.io/badge/Project-Page-Green)](https://sadtalker.github.io) [![Hugging Face Spaces](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Spaces-blue)](https://huggingface.co/spaces/vinthony/SadTalker)

**TL;DR:** Generate talking head videos from a single portrait image and audio file via WebSocket API.

**Input:** Single portrait image 🙎‍♂️ + Audio 🎤 = Talking head video 🎞

> ⚠️ **Note:** Our model only works on REAL people or portrait images similar to real persons. Anime talking head generation will be released in the future.

## Features

### WebSocket API
- **Real-time processing** via WebSocket connections  
- **Base64 input/output** for seamless integration
- **Concurrent request handling** with configurable limits
- **Docker deployment** ready with CUDA support
- **Interactive test client** for easy testing

### Core Capabilities
- Generate realistic talking head animations from a single image
- Support for various preprocessing modes (crop, resize, full)
- Face enhancement options (GFPGAN, RestoreFormer)
- Background enhancement (Real-ESRGAN)
- Expression control and pose manipulation
- 3D face visualization and free-view 4D generation

## 🏗️ Architecture

```
┌─────────────────┐    WebSocket    ┌──────────────────┐
│   Client App    │◄──────────────► │  FastAPI Server  │
└─────────────────┘                 └──────────────────┘
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


## Quick Start

Choose your preferred deployment method:

### 🐳 Option A: Docker (Recommended)

**One-command setup with all dependencies included:**

```bash
# Clone and start with Docker Compose
git clone https://github.com/NoAtmosphere0/SadTalker-WS-API
cd SadTalker
docker-compose up --build
```

**✅ What you get:**
- ✨ **Instant setup** - No manual dependency installation
- 🔄 **Auto model downloads** - Smart caching and error recovery
- 🚀 **GPU acceleration** - CUDA 11.8 support out of the box
- 🌐 **Ready-to-use API** - WebSocket server at `http://localhost:8000`
- 🎨 **Web interface** - Test client at `http://localhost:8000/test`

### 💻 Option B: Local Installation

**For development or custom setups:**

```bash
# 1. Clone repository
git clone https://github.com/NoAtmosphere0/SadTalker-WS-API
cd SadTalker

# 2. Setup environment
conda create -n sadtalker python==3.10
conda activate sadtalker

# 3. Install dependencies
pip install -r requirements.txt

# 4. Download models
bash scripts/download_models.sh

# 5. Start WebSocket API server
python -m api.fastapi_server
```

---

### 🔗 API Endpoints

Once running (either method), access these endpoints:

| Endpoint | Purpose | URL |
|----------|---------|-----|
| **WebSocket API** | Real-time video generation | `ws://localhost:8000/ws` |
| **Web Test Client** | Interactive testing interface | `http://localhost:8000/test` |
| **Health Check** | Service status monitoring | `http://localhost:8000/health` |
| **API Documentation** | OpenAPI/Swagger docs | `http://localhost:8000/docs` |

### 🎯 Quick Test

**Try the web interface (easiest):**
```bash
# Open in your browser
open http://localhost:8000/test
```

**Or use Python client:**
```python
import asyncio, websockets, json, base64

async def generate_video():
    uri = "ws://localhost:8000/ws"
    
    # Read and encode files
    with open("image.jpg", "rb") as f:
        image_base64 = base64.b64encode(f.read()).decode()
    with open("audio.wav", "rb") as f:
        audio_base64 = base64.b64encode(f.read()).decode()
    
    async with websockets.connect(uri) as websocket:
        request = {
            "image_base64": image_base64,
            "audio_base64": audio_base64,
            "preprocess": "crop",
            "expression_scale": 1.0
        }
        await websocket.send(json.dumps(request))
        
        response = await websocket.recv()
        result = json.loads(response)
        
        if result["status"] == "success":
            video_data = base64.b64decode(result["video_base64"])
            with open("output.mp4", "wb") as f:
                f.write(video_data)

asyncio.run(generate_video())
```

**Command-line examples:**
```bash
# Python test clients (included)
python examples/simple_example.py
python examples/test_client.py --image examples/source_image/art_0.png --audio examples/driven_audio/bus_chinese.wav
```

## API Documentation

### Endpoints

| Endpoint | Purpose | URL |
|----------|---------|-----|
| **WebSocket API** | Real-time video generation | `ws://localhost:8000/ws` |
| **Web Test Client** | Interactive testing interface | `http://localhost:8000/test` |
| **Health Check** | Service status monitoring | `http://localhost:8000/health` |
| **API Documentation** | OpenAPI/Swagger docs | `http://localhost:8000/docs` |

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

### Response Format

```json
{
  "status": "success|processing|error",
  "video_base64": "base64_encoded_video_data",
  "processing_time": 15.23
}
```

## Advanced Usage
```

### Command Line Interface

### Command Line Interface

**Basic CLI usage:**

```bash
python inference.py --driven_audio <audio.wav> \
                    --source_image <image.png> \
                    ### Command Line Interface

**Basic CLI usage:**
```bash
python cli/inference.py --driven_audio <audio.wav> \
                        --source_image <image.png> \
                        --result_dir ./results
```

**Advanced options:**
```bash
# High quality with enhancement
python cli/inference.py --driven_audio examples/driven_audio/bus_chinese.wav \
                        --source_image examples/source_image/art_0.png \
                        --enhancer gfpgan --background_enhancer realesrgan

# Full image mode with still pose  
python cli/inference.py --driven_audio examples/driven_audio/bus_chinese.wav \
                        --source_image examples/source_image/full_body_2.png \
                        --preprocess full --still
```

**Key parameters:**
- `--preprocess`: `crop` (recommended), `resize`, or `full`
- `--enhancer`: `gfpgan` or `RestoreFormer` for face enhancement
- `--background_enhancer`: `realesrgan` for background enhancement
- `--expression_scale`: Expression strength (0.0-3.0)
- `--still`: Reduce head motion

### Configuration

**Environment variables:**
```bash
export SADTALKER_HOST="0.0.0.0"
export SADTALKER_PORT="8000"
export SADTALKER_MAX_CONCURRENT="3"
```

**Docker rebuild commands:**
```bash
# Quick rebuild
docker-compose up --build

# Complete rebuild
docker-compose build --no-cache && docker-compose up
```

## Integration Examples

**JavaScript/Node.js:**
```javascript
const WebSocket = require('ws');
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

## Troubleshooting

**Common issues:**
```bash
# Container won't start
docker-compose build --no-cache && docker-compose up

# Check logs  
docker-compose logs -f sadtalker-api

# Health check
curl http://localhost:8000/health

# GPU issues
python -c "import torch; print(torch.cuda.is_available())"
```

**Performance:**
- Reduce `SADTALKER_MAX_CONCURRENT` for limited GPU memory
- Use `TORCH_DEVICE="cpu"` for CPU-only inference
- Monitor with `docker stats`

## Requirements

- Python 3.8+, PyTorch 2.0+, CUDA (recommended)
- FastAPI, uvicorn, websockets (see `requirements.txt`)

## Models (For manual download)
Pre-trained models are required for inference. Download them from the links below and place them in the `data/checkpoints/` directory.
Download from:
- [Google Drive](https://drive.google.com/file/d/1gwWh45pF7aelNP_P78uDJL8Sycep-K7j/view?usp=sharing)
- [GitHub Releases](https://github.com/OpenTalker/SadTalker/releases)
- [Baidu Cloud](https://pan.baidu.com/s/1kb1BCPaLOWX1JJb9Czbn6w?pwd=sadt) (Password: `sadt`)

## Directory Structure

```
├── README.md                     # Main documentation
├── README.original.md            # Original SadTalker README
├── WEBSOCKET_API.md              # Detailed API documentation
├── RESTRUCTURE_SUMMARY.md        # Repository restructure summary
├── restructure_plan.md           # Restructure planning document
├── docker-compose.yml            # Docker deployment
├── Dockerfile                    # Container configuration
├── nginx.conf                    # Reverse proxy config
├── cog.yaml                      # Cog model configuration
├── check_unused_packages.py      # Package usage analyzer
├── quick_demo.ipynb              # Jupyter notebook demo
├── requirements.txt              # Python dependencies
├── requirements3d.txt            # 3D visualization dependencies
├── req.txt                       # Additional requirements
├── LICENSE                       # License file
├── .gitignore                    # Git ignore patterns
├── api/                          # WebSocket and API servers
│   ├── __init__.py
│   └── fastapi_server.py         # Main FastAPI WebSocket server
├── cli/                          # Command-line interface
│   ├── __init__.py
│   ├── inference.py              # Main inference CLI
│   └── predict.py                # Prediction utilities
├── config/                       # Configuration files
│   ├── auido2exp.yaml            # Audio to expression config
│   ├── auido2pose.yaml           # Audio to pose config
│   ├── facerender.yaml           # Face rendering config
│   ├── facerender_still.yaml     # Still face rendering config
│   └── similarity_Lm3D_all.mat   # 3D landmark similarity matrix
├── checkpoints/                  # Legacy checkpoint directory
├── data/                         # Data directory
│   ├── checkpoints/              # Pre-trained models
│   │   ├── mapping_00109-model.pth.tar
│   │   ├── mapping_00229-model.pth.tar
│   │   ├── SadTalker_V0.0.2_256.safetensors
│   │   └── SadTalker_V0.0.2_512.safetensors
│   ├── examples/                 # Sample images and audio
│   │   ├── driven_audio/         # Sample audio files
│   │   ├── ref_video/            # Reference videos
│   │   └── source_image/         # Sample portrait images
│   ├── results/                  # Generated videos and outputs
│   └── static/                   # Static files for web serving
├── docs/                         # Documentation
│   ├── best_practice.md          # Best practices guide
│   ├── changlelog.md             # Change log
│   ├── FAQ.md                    # Frequently asked questions
│   ├── face3d.md                 # 3D face documentation
│   ├── install.md                # Installation guide
│   ├── webui_extension.md        # WebUI extension guide
│   └── *.gif                     # Example animations
├── examples/                     # Example scripts and test clients
│   ├── __init__.py
│   ├── batch_example.py          # Batch processing example
│   ├── simple_example.py         # Basic usage example
│   ├── test_client.py            # Python CLI test client
│   └── test_complete_suite.py    # Complete test suite
├── gfpgan/                       # GFPGAN face enhancement
│   └── weights/                  # GFPGAN model weights
├── results/                      # Top-level results directory
├── scripts/                      # Utility scripts
│   ├── download_models.sh        # Model download script
│   ├── extension.py              # Extension utilities
│   ├── start_gradio_client.sh    # Gradio client startup script
│   ├── start_server.sh           # Server startup script
│   ├── test.sh                   # Test script
│   └── webui_launchers/          # WebUI launcher scripts
├── src/                          # Source code modules
│   ├── audio2exp_models/         # Audio to expression models
│   ├── audio2pose_models/        # Audio to pose models
│   ├── config/                   # Source configuration
│   ├── face3d/                   # 3D face processing
│   ├── facerender/               # Face rendering pipeline
│   ├── sadtalker/                # Core SadTalker implementation
│   └── utils/                    # Utility functions
├── static/                       # Static files for web serving
├── tests/                        # Test suite
│   └── __init__.py
└── web/                          # Web interface files
    └── index.html                # Web test client
```
## Citation

```bibtex
@InProceedings{zhang2023sadtalker,
    author    = {Zhang, Wenxuan and Cun, Xiaodong and Wang, Fei and Zhang, Yong and Shen, Ji and Yu, Guangyong and Huang, Chunbo and Cao, Feiying and Zhong, Ran and Zhao, Hao and Ding, Shuai and Lei, Jie},
    title     = {SadTalker: Learning Realistic 3D Motion Coefficients for Stylized Audio-Driven Single Image Talking Face Animation},
    booktitle = {Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)},
    year      = {2023},
    pages     = {8652-8661}
}
```

## Additional Resources

- [WebSocket API Documentation](WEBSOCKET_API.md) - Detailed API reference
- [Original SadTalker Repository](https://github.com/OpenTalker/SadTalker) - Core implementation  
- [Project Documentation](docs/) - Guides and tutorials