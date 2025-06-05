# SadTalker Directory Restructuring Plan

## Current Issues
- Root directory is cluttered with many Python files
- Mixed API files, demo files, and core logic
- Configuration files scattered

## Proposed New Structure

```
SadTalker-WS-API/
├── README.md
├── LICENSE
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── requirements3d.txt
├── setup.py                    # New: Package configuration
│
├── api/                        # WebSocket API and web interfaces
│   ├── __init__.py
│   ├── fastapi_server.py       # Renamed from fastapi_websocket_server.py
│   ├── gradio_client.py        # Renamed from app_websocket.py  
│   └── gradio_standalone.py    # Renamed from app_sadtalker.py
│
├── cli/                        # Command-line interfaces
│   ├── __init__.py
│   ├── inference.py            # Moved from root
│   └── predict.py              # Moved from root
│
├── examples/                   # Example usage scripts
│   ├── __init__.py
│   ├── simple_example.py       # Moved from root
│   ├── batch_example.py        # Moved from root
│   ├── test_client.py          # Moved from root
│   └── test_complete_suite.py  # Moved from root
│
├── scripts/                    # Build and utility scripts
│   ├── download_models.sh
│   ├── start_server.sh         # Moved from root
│   ├── start_gradio_client.sh  # Moved from root
│   ├── extension.py
│   └── webui_launchers/        # New subdirectory
│       ├── webui.sh            # Moved from root
│       └── webui.bat           # Moved from root
│
├── web/                        # Static web assets
│   ├── index.html              # Renamed from test_client.html
│   └── assets/
│
├── config/                     # Configuration files
│   ├── facerender.yaml         # Moved from src/config/
│   ├── facerender_still.yaml   # Moved from src/config/
│   ├── auido2pose.yaml         # Moved from src/config/
│   └── auido2exp.yaml          # Moved from src/config/
│
├── src/                        # Core SadTalker modules (keep structure)
│   ├── sadtalker/              # Main package
│   │   ├── __init__.py
│   │   ├── gradio_demo.py      # Moved from src/
│   │   ├── test_audio2coeff.py # Moved from src/
│   │   ├── generate_batch.py   # Moved from src/
│   │   └── generate_facerender_batch.py # Moved from src/
│   ├── utils/
│   ├── face3d/
│   ├── facerender/
│   ├── audio2pose_models/
│   └── audio2exp_models/
│
├── data/                       # Data directories
│   ├── checkpoints/            # Moved from root
│   ├── results/                # Moved from root
│   ├── static/                 # Moved from root
│   └── examples/               # Sample data (moved from root)
│       ├── source_image/
│       ├── driven_audio/
│       └── ref_video/
│
├── tests/                      # Test files
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_cli.py
│   └── fixtures/
│
└── docs/                       # Documentation (keep existing)
    ├── best_practice.md
    ├── changlelog.md
    ├── FAQ.md
    └── install.md
```

## Migration Strategy

1. **Create new directory structure**
2. **Move files to appropriate locations**
3. **Update all import statements**
4. **Update configuration paths**
5. **Update Docker and script references**
6. **Test functionality**

## Files to Update

### Import Updates Needed:
- All API files (`api/` directory)
- CLI files (`cli/` directory)  
- Example files (`examples/` directory)
- Core modules in `src/`

### Path Updates Needed:
- Dockerfile
- Scripts in `scripts/`
- Configuration files
- README.md

### Benefits:
- Cleaner root directory
- Logical separation of concerns
- Better organization for users
- Easier to navigate and maintain
- Follows Python package standards
