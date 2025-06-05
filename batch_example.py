#!/usr/bin/env python3
"""
Batch Processing Example for SadTalker WebSocket API

This script demonstrates how to process multiple image-audio pairs
through the WebSocket API efficiently.
"""

import asyncio
import websockets
import json
import base64
import os
import glob
from pathlib import Path
import time


class SadTalkerBatchProcessor:
    def __init__(self, server_url="ws://localhost:8000/ws"):
        self.server_url = server_url
        self.processed_count = 0
        self.failed_count = 0

    async def process_file_pair(self, image_path, audio_path, output_dir, options=None):
        """Process a single image-audio pair"""
        try:
            print(
                f"📦 Processing: {os.path.basename(image_path)} + {os.path.basename(audio_path)}"
            )

            # Read and encode files
            with open(image_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode("utf-8")

            with open(audio_path, "rb") as f:
                audio_data = base64.b64encode(f.read()).decode("utf-8")

            # Prepare request
            request = {
                "image_base64": image_data,
                "audio_base64": audio_data,
                "return_base64": True,  # Get base64 for batch processing
                "options": options
                or {
                    "preprocess": "crop",
                    "still_mode": False,
                    "use_enhancer": False,
                    "batch_size": 1,  # Use smaller batch for parallel processing
                    "size": 256,
                    "pose_style": 0,
                    "expression_scale": 1.0,
                },
            }

            # Connect and process
            async with websockets.connect(self.server_url) as websocket:
                # Wait for ready message
                ready_msg = await websocket.recv()
                ready_data = json.loads(ready_msg)

                if ready_data["type"] != "ready":
                    raise Exception("Server not ready")

                # Send request
                await websocket.send(json.dumps(request))

                # Listen for response
                while True:
                    response = await websocket.recv()
                    data = json.loads(response)

                    if data["type"] == "status":
                        print(f"   ⏳ {data['message']}")
                    elif data["type"] == "success":
                        print(f"   ✅ {data['message']}")

                        if "video_base64" in data:
                            # Save video
                            video_data = base64.b64decode(data["video_base64"])
                            output_filename = (
                                f"{Path(image_path).stem}_{Path(audio_path).stem}.mp4"
                            )
                            output_path = os.path.join(output_dir, output_filename)

                            with open(output_path, "wb") as f:
                                f.write(video_data)

                            print(f"   💾 Saved: {output_path}")
                            self.processed_count += 1
                            return output_path
                        break
                    elif data["type"] == "error":
                        print(f"   ❌ Error: {data['message']}")
                        self.failed_count += 1
                        return None

        except Exception as e:
            print(f"   ❌ Failed to process {image_path}: {e}")
            self.failed_count += 1
            return None

    async def process_directory(
        self, images_dir, audios_dir, output_dir, max_concurrent=3
    ):
        """Process all image-audio combinations in directories"""

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Find all images and audios
        image_extensions = ["*.png", "*.jpg", "*.jpeg"]
        audio_extensions = ["*.wav", "*.mp3"]

        images = []
        for ext in image_extensions:
            images.extend(glob.glob(os.path.join(images_dir, ext)))

        audios = []
        for ext in audio_extensions:
            audios.extend(glob.glob(os.path.join(audios_dir, ext)))

        if not images:
            print(f"❌ No images found in {images_dir}")
            return

        if not audios:
            print(f"❌ No audio files found in {audios_dir}")
            return

        print(f"📂 Found {len(images)} images and {len(audios)} audio files")
        print(f"🔄 Will process {len(images) * len(audios)} combinations")
        print(f"⚡ Max concurrent: {max_concurrent}")
        print("")

        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_with_semaphore(image_path, audio_path):
            async with semaphore:
                return await self.process_file_pair(image_path, audio_path, output_dir)

        # Create all tasks
        tasks = []
        for image_path in images:
            for audio_path in audios:
                task = process_with_semaphore(image_path, audio_path)
                tasks.append(task)

        # Process all tasks
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()

        # Print summary
        print("")
        print("=" * 50)
        print("📊 BATCH PROCESSING SUMMARY")
        print("=" * 50)
        print(f"✅ Successful: {self.processed_count}")
        print(f"❌ Failed: {self.failed_count}")
        print(f"⏱️  Total time: {end_time - start_time:.2f} seconds")
        print(f"📁 Output directory: {output_dir}")


async def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Batch process images and audio with SadTalker"
    )
    parser.add_argument(
        "--images-dir", required=True, help="Directory containing source images"
    )
    parser.add_argument(
        "--audios-dir", required=True, help="Directory containing audio files"
    )
    parser.add_argument(
        "--output-dir", required=True, help="Output directory for videos"
    )
    parser.add_argument(
        "--server", default="ws://localhost:8000/ws", help="WebSocket server URL"
    )
    parser.add_argument(
        "--max-concurrent", type=int, default=3, help="Maximum concurrent processes"
    )
    parser.add_argument(
        "--preprocess",
        default="crop",
        choices=["crop", "resize", "full"],
        help="Preprocess mode",
    )
    parser.add_argument(
        "--size", type=int, choices=[256, 512], default=256, help="Model size"
    )
    parser.add_argument("--enhancer", action="store_true", help="Use enhancer")

    args = parser.parse_args()

    # Validate directories
    if not os.path.exists(args.images_dir):
        print(f"❌ Images directory not found: {args.images_dir}")
        return

    if not os.path.exists(args.audios_dir):
        print(f"❌ Audio directory not found: {args.audios_dir}")
        return

    # Set up options
    options = {
        "preprocess": args.preprocess,
        "still_mode": False,
        "use_enhancer": args.enhancer,
        "batch_size": 1,
        "size": args.size,
        "pose_style": 0,
        "expression_scale": 1.0,
    }

    # Create processor and run
    processor = SadTalkerBatchProcessor(args.server)
    await processor.process_directory(
        args.images_dir, args.audios_dir, args.output_dir, args.max_concurrent
    )


if __name__ == "__main__":
    print("🎭 SadTalker Batch Processor")
    print("=" * 50)
    asyncio.run(main())
