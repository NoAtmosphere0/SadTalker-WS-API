#!/usr/bin/env python3
"""
Python WebSocket Client for SadTalker API
Example usage of the FastAPI WebSocket server
"""

import asyncio
import websockets
import json
import base64
import argparse
import os


async def file_to_base64(file_path):
    """Convert file to base64 string"""
    with open(file_path, "rb") as f:
        file_data = f.read()
    return base64.b64encode(file_data).decode("utf-8")


async def base64_to_file(base64_data, output_path):
    """Convert base64 string to file"""
    file_data = base64.b64decode(base64_data)
    with open(output_path, "wb") as f:
        f.write(file_data)


async def test_sadtalker_api(
    server_url, image_path, audio_path, output_path=None, options=None
):
    """Test the SadTalker WebSocket API"""

    if not os.path.exists(image_path):
        print(f"Error: Image file not found: {image_path}")
        return

    if not os.path.exists(audio_path):
        print(f"Error: Audio file not found: {audio_path}")
        return

    print(f"Connecting to {server_url}...")

    try:
        async with websockets.connect(server_url) as websocket:
            print("Connected to SadTalker WebSocket server!")

            # Wait for ready message
            ready_msg = await websocket.recv()
            ready_data = json.loads(ready_msg)
            print(f"Server: {ready_data['message']}")

            # Prepare files
            print("Encoding files to base64...")
            image_base64 = await file_to_base64(image_path)
            audio_base64 = await file_to_base64(audio_path)

            # Prepare request
            request_data = {
                "image_base64": image_base64,
                "audio_base64": audio_base64,
                "return_base64": output_path
                is not None,  # Return base64 if output path is specified
                "options": options
                or {
                    "preprocess": "crop",
                    "still_mode": False,
                    "use_enhancer": False,
                    "batch_size": 2,
                    "size": 256,
                    "pose_style": 0,
                    "expression_scale": 1.0,
                },
            }

            print("Sending request to SadTalker...")
            await websocket.send(json.dumps(request_data))

            # Listen for responses
            while True:
                response = await websocket.recv()
                data = json.loads(response)

                if data["type"] == "status":
                    print(f"Status: {data['message']}")
                elif data["type"] == "success":
                    print(f"Success: {data['message']}")

                    if "video_base64" in data and output_path:
                        print(f"Saving video to {output_path}...")
                        await base64_to_file(data["video_base64"], output_path)
                        print(f"Video saved to {output_path}")
                    elif "video_url" in data:
                        print(f"Video available at: {data['video_url']}")
                        print(f"Full URL: http://localhost:8000{data['video_url']}")

                    break
                elif data["type"] == "error":
                    print(f"Error: {data['message']}")
                    break
                else:
                    print(f"Unknown message type: {data}")

    except websockets.exceptions.ConnectionClosed:
        print("Connection closed by server")
    except Exception as e:
        print(f"Error: {e}")


async def main():
    parser = argparse.ArgumentParser(description="Test SadTalker WebSocket API")
    parser.add_argument(
        "--server", default="ws://localhost:8000/ws", help="WebSocket server URL"
    )
    parser.add_argument("--image", required=True, help="Path to source image")
    parser.add_argument("--audio", required=True, help="Path to driven audio")
    parser.add_argument(
        "--output",
        help="Output video path (if specified, video will be downloaded as base64)",
    )
    parser.add_argument(
        "--preprocess",
        default="crop",
        choices=["crop", "resize", "full", "extcrop", "extfull"],
        help="Preprocess mode",
    )
    parser.add_argument(
        "--still", action="store_true", help="Still mode (less head motion)"
    )
    parser.add_argument("--enhancer", action="store_true", help="Use GFPGAN enhancer")
    parser.add_argument("--batch-size", type=int, default=2, help="Batch size")
    parser.add_argument(
        "--size", type=int, choices=[256, 512], default=256, help="Model size"
    )
    parser.add_argument("--pose-style", type=int, default=0, help="Pose style (0-46)")
    parser.add_argument(
        "--expression-scale", type=float, default=1.0, help="Expression scale"
    )

    args = parser.parse_args()

    options = {
        "preprocess": args.preprocess,
        "still_mode": args.still,
        "use_enhancer": args.enhancer,
        "batch_size": args.batch_size,
        "size": args.size,
        "pose_style": args.pose_style,
        "expression_scale": args.expression_scale,
    }

    await test_sadtalker_api(args.server, args.image, args.audio, args.output, options)


if __name__ == "__main__":
    asyncio.run(main())
