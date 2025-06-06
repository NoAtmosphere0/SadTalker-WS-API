#!/usr/bin/env python3
"""
FastAPI WebSocket Server for SadTalker
Provides WebSocket API for real-time talking head video generation
"""

import os
import sys
import json
import base64
import uuid
import tempfile
import asyncio
import shutil
from pathlib import Path
from typing import Optional

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

# Import SadTalker components
from src.sadtalker.gradio_demo import SadTalker

app = FastAPI(title="SadTalker WebSocket API", version="1.0.0")

# Configure paths
CHECKPOINT_PATH = "data/checkpoints"
CONFIG_PATH = "config"
RESULTS_DIR = "data/results"
STATIC_DIR = "data/static"

# Ensure directories exist
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

# Mount static files for serving generated videos
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Global SadTalker instance (lazy loaded)
sad_talker = None


def get_sad_talker():
    """Get or initialize the SadTalker instance"""
    global sad_talker
    if sad_talker is None:
        print("Initializing SadTalker...")
        sad_talker = SadTalker(
            checkpoint_path=CHECKPOINT_PATH, config_path=CONFIG_PATH, lazy_load=True
        )
        print("SadTalker initialized successfully!")
    return sad_talker


def decode_base64_to_file(base64_data: str, file_extension: str) -> str:
    """Decode base64 data and save to a temporary file"""
    try:
        # Remove data URL prefix if present (e.g., "data:image/png;base64,")
        if "," in base64_data:
            base64_data = base64_data.split(",", 1)[1]

        # Decode base64
        file_data = base64.b64decode(base64_data)

        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(
            delete=False, suffix=f".{file_extension}"
        )
        temp_file.write(file_data)
        temp_file.close()

        return temp_file.name
    except Exception as e:
        raise ValueError(f"Failed to decode base64 data: {str(e)}")


def encode_file_to_base64(file_path: str) -> str:
    """Encode a file to base64"""
    try:
        with open(file_path, "rb") as f:
            file_data = f.read()
        return base64.b64encode(file_data).decode("utf-8")
    except Exception as e:
        raise ValueError(f"Failed to encode file to base64: {str(e)}")


def copy_to_static(file_path: str) -> str:
    """Copy file to static directory and return URL"""
    try:
        filename = f"{uuid.uuid4()}.mp4"
        static_path = os.path.join(STATIC_DIR, filename)
        shutil.copy2(file_path, static_path)
        return f"/static/{filename}"
    except Exception as e:
        raise ValueError(f"Failed to copy file to static: {str(e)}")


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "SadTalker FastAPI WebSocket Server",
        "version": "1.0.0",
        "endpoints": {
            "websocket": "/ws",
            "test_client": "/test",
            "static_files": "/static/{filename}",
        },
        "usage": {
            "websocket_url": "ws://localhost:8000/ws",
            "message_format": {
                "image_base64": "base64 encoded image",
                "audio_base64": "base64 encoded audio",
                "options": {
                    "preprocess": "crop|resize|full",
                    "still_mode": "boolean",
                    "use_enhancer": "boolean",
                    "batch_size": "integer",
                    "size": "256|512",
                    "pose_style": "integer 0-46",
                    "expression_scale": "float",
                },
            },
        },
    }


@app.get("/test", response_class=HTMLResponse)
async def test_client():
    """Serve the test client HTML page"""
    try:
        with open("web/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Test client not found")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "sad_talker_loaded": sad_talker is not None}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Main WebSocket endpoint for SadTalker inference"""
    await websocket.accept()

    try:
        # Initialize SadTalker
        talker = get_sad_talker()

        await websocket.send_json(
            {"type": "ready", "message": "SadTalker is ready for inference"}
        )

        while True:
            # Receive message from client
            try:
                data = await websocket.receive_json()
            except Exception as e:
                await websocket.send_json(
                    {"type": "error", "message": f"Invalid JSON data: {str(e)}"}
                )
                continue

            # Validate required fields
            if "image_base64" not in data or "audio_base64" not in data:
                await websocket.send_json(
                    {
                        "type": "error",
                        "message": "Missing required fields: image_base64 and audio_base64",
                    }
                )
                continue

            try:
                await websocket.send_json(
                    {"type": "status", "message": "Processing request..."}
                )

                # Decode input data
                await websocket.send_json(
                    {"type": "status", "message": "Decoding input files..."}
                )

                image_file = decode_base64_to_file(data["image_base64"], "png")
                audio_file = decode_base64_to_file(data["audio_base64"], "wav")

                # Extract options
                options = data.get("options", {})
                preprocess = options.get("preprocess", "crop")
                still_mode = options.get("still_mode", False)
                use_enhancer = options.get("use_enhancer", False)
                batch_size = options.get("batch_size", 2)
                size = options.get("size", 256)
                pose_style = options.get("pose_style", 0)
                expression_scale = options.get("expression_scale", 1.0)

                await websocket.send_json(
                    {"type": "status", "message": "Running SadTalker inference..."}
                )

                # Run SadTalker inference
                result_path = talker.test(
                    source_image=image_file,
                    driven_audio=audio_file,
                    preprocess=preprocess,
                    still_mode=still_mode,
                    use_enhancer=use_enhancer,
                    batch_size=batch_size,
                    size=size,
                    pose_style=pose_style,
                    exp_scale=expression_scale,
                    result_dir=RESULTS_DIR,
                )

                await websocket.send_json(
                    {"type": "status", "message": "Encoding result..."}
                )

                # Check if return_with_base64 is requested
                return_base64 = data.get("return_base64", False)

                response = {
                    "type": "success",
                    "message": "Video generated successfully",
                }

                if return_base64:
                    # Encode video as base64
                    video_base64 = encode_file_to_base64(result_path)
                    response["video_base64"] = video_base64
                else:
                    # Copy to static directory and return URL
                    video_url = copy_to_static(result_path)
                    response["video_url"] = video_url

                # Clean up temporary files
                try:
                    os.unlink(image_file)
                    os.unlink(audio_file)
                except:
                    pass

                await websocket.send_json(response)

            except Exception as e:
                await websocket.send_json(
                    {"type": "error", "message": f"Processing failed: {str(e)}"}
                )

                # Clean up on error
                try:
                    if "image_file" in locals():
                        os.unlink(image_file)
                    if "audio_file" in locals():
                        os.unlink(audio_file)
                except:
                    pass

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
        try:
            await websocket.send_json(
                {"type": "error", "message": f"Server error: {str(e)}"}
            )
        except:
            pass


@app.get("/download/{filename}")
async def download_file(filename: str):
    """Download generated video files"""
    file_path = os.path.join(STATIC_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(path=file_path, filename=filename, media_type="video/mp4")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="SadTalker FastAPI WebSocket Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument(
        "--checkpoint-path",
        default="data/checkpoints",
        help="Path to SadTalker checkpoints",
    )
    parser.add_argument(
        "--config-path", default="config", help="Path to SadTalker config"
    )
    parser.add_argument(
        "--results-dir", default="data/results", help="Directory to save results"
    )
    parser.add_argument(
        "--static-dir", default="data/static", help="Directory for static files"
    )

    args = parser.parse_args()

    # Update global paths
    CHECKPOINT_PATH = args.checkpoint_path
    CONFIG_PATH = args.config_path
    RESULTS_DIR = args.results_dir
    STATIC_DIR = args.static_dir

    # Ensure directories exist
    os.makedirs(RESULTS_DIR, exist_ok=True)
    os.makedirs(STATIC_DIR, exist_ok=True)

    print(f"Starting SadTalker FastAPI WebSocket Server...")
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    print(f"Checkpoint Path: {CHECKPOINT_PATH}")
    print(f"Config Path: {CONFIG_PATH}")
    print(f"Results Directory: {RESULTS_DIR}")
    print(f"Static Directory: {STATIC_DIR}")

    uvicorn.run(
        "api.fastapi_server:app",
        host=args.host,
        port=args.port,
        reload=False,
        log_level="info",
    )
