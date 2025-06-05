#!/usr/bin/env python3
"""
Simple SadTalker WebSocket API Example

This script demonstrates the basic usage of the SadTalker WebSocket API.
It loads a sample image and audio file, sends them to the server, and
displays the result.
"""

import asyncio
import websockets
import json
import base64
import os
import sys


async def run_simple_example():
    """Run a simple example with the sample files"""

    # Check if sample files exist
    image_path = "data/examples/source_image/art_0.png"
    audio_path = "data/examples/driven_audio/bus_chinese.wav"

    if not os.path.exists(image_path):
        print(f"❌ Sample image not found: {image_path}")
        print("Please make sure you have the examples directory with sample files.")
        return

    if not os.path.exists(audio_path):
        print(f"❌ Sample audio not found: {audio_path}")
        print("Please make sure you have the examples directory with sample files.")
        return

    print("🎭 SadTalker WebSocket API - Simple Example")
    print("=" * 50)
    print(f"📸 Using image: {image_path}")
    print(f"🎵 Using audio: {audio_path}")
    print("")

    # Convert files to base64
    print("📦 Encoding files...")
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")

    with open(audio_path, "rb") as f:
        audio_data = base64.b64encode(f.read()).decode("utf-8")

    # Prepare request
    request = {
        "image_base64": image_data,
        "audio_base64": audio_data,
        "return_base64": False,  # Get URL instead of base64
        "options": {
            "preprocess": "crop",
            "still_mode": False,
            "use_enhancer": False,
            "batch_size": 2,
            "size": 256,
            "pose_style": 0,
            "expression_scale": 1.0,
        },
    }

    # Connect to server
    server_url = "ws://localhost:8000/ws"
    print(f"🔗 Connecting to {server_url}...")

    try:
        async with websockets.connect(server_url) as websocket:
            print("✅ Connected!")

            # Wait for ready message
            ready_msg = await websocket.recv()
            ready_data = json.loads(ready_msg)
            if ready_data["type"] == "ready":
                print(f"🚀 {ready_data['message']}")

            # Send request
            print("📤 Sending request...")
            await websocket.send(json.dumps(request))

            # Listen for responses
            while True:
                response = await websocket.recv()
                data = json.loads(response)

                if data["type"] == "status":
                    print(f"⏳ {data['message']}")
                elif data["type"] == "success":
                    print(f"🎉 {data['message']}")

                    if "video_url" in data:
                        print(f"🎬 Video URL: http://localhost:8000{data['video_url']}")
                        print("📱 You can now view the video in your browser!")

                    break
                elif data["type"] == "error":
                    print(f"❌ Error: {data['message']}")
                    break

    except ConnectionRefusedError:
        print("❌ Connection refused. Is the server running?")
        print("   Start the server with: ./start_server.sh")
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Main function"""
    print("🎭 SadTalker WebSocket API - Simple Example")
    print("")

    # Check if we're in the right directory
    if not os.path.exists("fastapi_websocket_server.py"):
        print("❌ Please run this script from the SadTalker-WS-API directory")
        sys.exit(1)

    # Run the example
    asyncio.run(run_simple_example())


if __name__ == "__main__":
    main()
