#!/usr/bin/env python3
"""
Complete Test Suite for SadTalker WebSocket API and Gradio Client
Tests both the WebSocket server and Gradio client functionality
"""

import os
import sys
import json
import base64
import asyncio
import time
import subprocess
import signal
from pathlib import Path
from typing import Optional, List, Tuple

import requests
import websockets


class SadTalkerTestSuite:
    """Test suite for SadTalker WebSocket API"""

    def __init__(self):
        self.ws_url = "ws://localhost:8000/ws"
        self.http_url = "http://localhost:8000"
        self.gradio_url = "http://localhost:7860"
        self.server_process = None
        self.gradio_process = None

    def print_header(self, title: str):
        """Print a formatted header"""
        print(f"\n{'='*60}")
        print(f"🧪 {title}")
        print(f"{'='*60}")

    def print_step(self, step: str):
        """Print a test step"""
        print(f"\n📋 {step}")

    def print_success(self, message: str):
        """Print success message"""
        print(f"✅ {message}")

    def print_error(self, message: str):
        """Print error message"""
        print(f"❌ {message}")

    def print_warning(self, message: str):
        """Print warning message"""
        print(f"⚠️  {message}")

    def check_prerequisites(self) -> bool:
        """Check if all required files and dependencies exist"""
        self.print_step("Checking prerequisites...")

        required_files = [
            "fastapi_websocket_server.py",
            "app_websocket.py",
            "examples/source_image/art_0.png",
            "examples/driven_audio/bus_chinese.wav",
        ]

        missing_files = []
        for file_path in required_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)

        if missing_files:
            self.print_error(f"Missing required files: {missing_files}")
            return False

        # Check Python dependencies
        try:
            import fastapi
            import uvicorn
            import websockets
            import gradio
            import aiofiles

            self.print_success("All dependencies are installed")
            return True
        except ImportError as e:
            self.print_error(f"Missing Python dependency: {e}")
            return False

    def start_websocket_server(self) -> bool:
        """Start the WebSocket server"""
        self.print_step("Starting WebSocket server...")

        try:
            # Start server in background
            self.server_process = subprocess.Popen(
                [sys.executable, "fastapi_websocket_server.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            # Wait for server to start
            max_retries = 30
            for i in range(max_retries):
                try:
                    response = requests.get(f"{self.http_url}/health", timeout=5)
                    if response.status_code == 200:
                        self.print_success("WebSocket server started successfully")
                        return True
                except requests.exceptions.RequestException:
                    time.sleep(1)

            self.print_error("WebSocket server failed to start within 30 seconds")
            return False

        except Exception as e:
            self.print_error(f"Failed to start WebSocket server: {e}")
            return False

    def test_health_endpoint(self) -> bool:
        """Test the health endpoint"""
        self.print_step("Testing health endpoint...")

        try:
            response = requests.get(f"{self.http_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.print_success(f"Health check passed: {data}")
                return True
            else:
                self.print_error(
                    f"Health check failed with status {response.status_code}"
                )
                return False
        except Exception as e:
            self.print_error(f"Health check error: {e}")
            return False

    def test_api_info_endpoint(self) -> bool:
        """Test the API info endpoint"""
        self.print_step("Testing API info endpoint...")

        try:
            response = requests.get(f"{self.http_url}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.print_success(
                    f"API info retrieved: {data.get('title', 'Unknown')}"
                )
                return True
            else:
                self.print_error(f"API info failed with status {response.status_code}")
                return False
        except Exception as e:
            self.print_error(f"API info error: {e}")
            return False

    async def test_websocket_connection(self) -> bool:
        """Test basic WebSocket connection"""
        self.print_step("Testing WebSocket connection...")

        try:
            async with websockets.connect(self.ws_url, ping_timeout=10) as websocket:
                self.print_success("WebSocket connection established")
                return True
        except Exception as e:
            self.print_error(f"WebSocket connection failed: {e}")
            return False

    async def encode_test_files(self) -> Tuple[Optional[str], Optional[str]]:
        """Encode test files to base64"""
        self.print_step("Encoding test files...")

        try:
            # Read and encode image
            with open("examples/source_image/art_0.png", "rb") as f:
                image_data = f.read()
                image_base64 = base64.b64encode(image_data).decode("utf-8")

            # Read and encode audio
            with open("examples/driven_audio/bus_chinese.wav", "rb") as f:
                audio_data = f.read()
                audio_base64 = base64.b64encode(audio_data).decode("utf-8")

            self.print_success("Test files encoded successfully")
            return image_base64, audio_base64

        except Exception as e:
            self.print_error(f"Failed to encode test files: {e}")
            return None, None

    async def test_video_generation(self) -> bool:
        """Test actual video generation via WebSocket"""
        self.print_step("Testing video generation...")

        try:
            # Encode test files
            image_base64, audio_base64 = await self.encode_test_files()
            if not image_base64 or not audio_base64:
                return False

            # Prepare request in the format expected by the WebSocket server
            request_data = {
                "image_base64": image_base64,
                "audio_base64": audio_base64,
                "return_base64": False,  # Use URL instead of base64 for faster response
                "options": {
                    "preprocess": "crop",
                    "expression_scale": 1.0,
                    "still_mode": False,
                    "use_enhancer": False,
                    "batch_size": 2,
                    "size": 256,
                    "pose_style": 0,
                },
            }

            # Connect and send request
            async with websockets.connect(self.ws_url, ping_timeout=20) as websocket:
                await websocket.send(json.dumps(request_data))

                # Wait for response (up to 5 minutes)
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=300)
                    result = json.loads(response)

                    if result.get("status") == "success":
                        processing_time = result.get("processing_time", 0)
                        self.print_success(
                            f"Video generated successfully in {processing_time:.1f}s"
                        )

                        # Check if video data or URL is provided
                        if "video_base64" in result:
                            video_size = len(result["video_base64"])
                            self.print_success(
                                f"Video data received: {video_size} characters"
                            )
                        elif "video_url" in result:
                            self.print_success(
                                f"Video URL received: {result['video_url']}"
                            )

                        return True
                    else:
                        error_msg = result.get("message", "Unknown error")
                        self.print_error(f"Video generation failed: {error_msg}")
                        return False

                except asyncio.TimeoutError:
                    self.print_error("Video generation timed out after 5 minutes")
                    return False

        except Exception as e:
            self.print_error(f"Video generation test failed: {e}")
            return False

    def start_gradio_client(self) -> bool:
        """Start the Gradio client"""
        self.print_step("Starting Gradio client...")

        try:
            # Start Gradio client in background
            self.gradio_process = subprocess.Popen(
                [sys.executable, "app_websocket.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            # Wait for Gradio to start
            max_retries = 30
            for i in range(max_retries):
                try:
                    response = requests.get(self.gradio_url, timeout=5)
                    if response.status_code == 200:
                        self.print_success("Gradio client started successfully")
                        return True
                except requests.exceptions.RequestException:
                    time.sleep(1)

            self.print_error("Gradio client failed to start within 30 seconds")
            return False

        except Exception as e:
            self.print_error(f"Failed to start Gradio client: {e}")
            return False

    def test_gradio_accessibility(self) -> bool:
        """Test if Gradio interface is accessible"""
        self.print_step("Testing Gradio accessibility...")

        try:
            response = requests.get(self.gradio_url, timeout=10)
            if response.status_code == 200:
                self.print_success("Gradio interface is accessible")
                return True
            else:
                self.print_error(
                    f"Gradio interface returned status {response.status_code}"
                )
                return False
        except Exception as e:
            self.print_error(f"Gradio accessibility test failed: {e}")
            return False

    def cleanup(self):
        """Clean up processes"""
        self.print_step("Cleaning up...")

        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()
            self.print_success("WebSocket server stopped")

        if self.gradio_process:
            self.gradio_process.terminate()
            self.gradio_process.wait()
            self.print_success("Gradio client stopped")

    async def run_websocket_tests(self) -> bool:
        """Run all WebSocket-related tests"""
        self.print_header("WebSocket API Tests")

        # Check prerequisites
        if not self.check_prerequisites():
            return False

        # Start WebSocket server
        if not self.start_websocket_server():
            return False

        try:
            # Test endpoints
            if not self.test_health_endpoint():
                return False

            if not self.test_api_info_endpoint():
                return False

            # Test WebSocket connection
            if not await self.test_websocket_connection():
                return False

            # Test video generation
            if not await self.test_video_generation():
                return False

            self.print_success("All WebSocket tests passed!")
            return True

        except KeyboardInterrupt:
            self.print_warning("Tests interrupted by user")
            return False
        except Exception as e:
            self.print_error(f"Unexpected error during tests: {e}")
            return False

    def run_gradio_tests(self) -> bool:
        """Run Gradio client tests"""
        self.print_header("Gradio Client Tests")

        # Start Gradio client
        if not self.start_gradio_client():
            return False

        # Test accessibility
        if not self.test_gradio_accessibility():
            return False

        self.print_success("All Gradio tests passed!")
        return True

    async def run_all_tests(self):
        """Run complete test suite"""
        print("🚀 SadTalker WebSocket API & Gradio Client Test Suite")
        print("🔧 This will test the complete pipeline from WebSocket API to Gradio UI")

        try:
            # Run WebSocket tests
            ws_success = await self.run_websocket_tests()

            if ws_success:
                # Run Gradio tests (only if WebSocket tests pass)
                gradio_success = self.run_gradio_tests()

                if gradio_success:
                    self.print_header("🎉 ALL TESTS PASSED!")
                    print("✅ WebSocket API is working correctly")
                    print("✅ Gradio client is working correctly")
                    print("✅ Video generation pipeline is functional")
                    print(f"\n🌐 Access the interfaces:")
                    print(f"   • WebSocket API: {self.http_url}")
                    print(f"   • Test Client: {self.http_url}/test")
                    print(f"   • Gradio UI: {self.gradio_url}")
                else:
                    self.print_error("Gradio tests failed")
            else:
                self.print_error("WebSocket tests failed - skipping Gradio tests")

        except KeyboardInterrupt:
            self.print_warning("Test suite interrupted by user")
        finally:
            self.cleanup()


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="SadTalker WebSocket API Test Suite")
    parser.add_argument(
        "--websocket-only", action="store_true", help="Run only WebSocket tests"
    )
    parser.add_argument(
        "--gradio-only", action="store_true", help="Run only Gradio tests"
    )
    parser.add_argument(
        "--quick", action="store_true", help="Skip video generation test (faster)"
    )

    args = parser.parse_args()

    test_suite = SadTalkerTestSuite()

    try:
        if args.websocket_only:
            asyncio.run(test_suite.run_websocket_tests())
        elif args.gradio_only:
            test_suite.run_gradio_tests()
        else:
            asyncio.run(test_suite.run_all_tests())
    except KeyboardInterrupt:
        print("\n⚠️  Test suite interrupted")
    finally:
        test_suite.cleanup()


if __name__ == "__main__":
    main()
