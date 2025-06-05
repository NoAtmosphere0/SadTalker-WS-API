#!/usr/bin/env python3
"""
Gradio WebUI for SadTalker WebSocket API
Provides a web interface that connects to the WebSocket server for talking head generation
"""

import os
import sys
import json
import base64
import asyncio
import tempfile
import time
from pathlib import Path
from typing import Optional, Tuple

import gradio as gr
import websockets
import aiofiles


# WebSocket server configuration
DEFAULT_WS_URL = "ws://localhost:8000/ws"
WS_URL = os.getenv("SADTALKER_WS_URL", DEFAULT_WS_URL)
CONNECTION_TIMEOUT = 30
REQUEST_TIMEOUT = 300  # 5 minutes for video generation


try:
    import webui  # in webui

    in_webui = True
except:
    in_webui = False


class WebSocketSadTalker:
    """WebSocket client for SadTalker API"""

    def __init__(self, ws_url: str = WS_URL):
        self.ws_url = ws_url

    async def encode_file(self, file_path: str) -> str:
        """Encode file to base64"""
        async with aiofiles.open(file_path, "rb") as f:
            content = await f.read()
            return base64.b64encode(content).decode("utf-8")

    async def generate_video(
        self,
        source_image: str,
        driven_audio: str,
        preprocess: str = "crop",
        still: bool = False,
        enhancer: bool = False,
        background_enhancer: bool = False,
        expression_scale: float = 1.0,
        size_of_image: int = 256,
        pose_style: int = 0,
        batch_size: int = 2,
    ) -> Tuple[Optional[str], str]:
        """
        Generate video using WebSocket API
        Returns: (video_path, status_message)
        """
        try:
            # Validate inputs
            if not source_image or not os.path.exists(source_image):
                return None, "❌ Please provide a valid source image"

            if not driven_audio or not os.path.exists(driven_audio):
                return None, "❌ Please provide a valid audio file"

            # Encode files to base64
            image_base64 = await self.encode_file(source_image)
            audio_base64 = await self.encode_file(driven_audio)

            # Prepare request in the format expected by the WebSocket server
            request_data = {
                "image_base64": image_base64,
                "audio_base64": audio_base64,
                "return_base64": True,  # Return base64 for Gradio compatibility
                "options": {
                    "preprocess": preprocess,
                    "still_mode": still,
                    "expression_scale": expression_scale,
                    "size": size_of_image,
                    "pose_style": pose_style,
                    "batch_size": batch_size,
                    "use_enhancer": enhancer,
                },
            }

            # Add background enhancer if enabled
            if background_enhancer:
                request_data["options"]["background_enhancer"] = "realesrgan"

            # Connect to WebSocket and send request
            async with websockets.connect(
                self.ws_url,
                ping_timeout=CONNECTION_TIMEOUT,
                close_timeout=CONNECTION_TIMEOUT,
            ) as websocket:

                # Send request
                await websocket.send(json.dumps(request_data))

                # Wait for ready message
                ready_response = await websocket.recv()
                ready_result = json.loads(ready_response)

                if ready_result.get("type") != "ready":
                    return (
                        None,
                        f"❌ Server not ready: {ready_result.get('message', 'Unknown error')}",
                    )

                # Wait for final response with timeout
                try:
                    while True:
                        response = await asyncio.wait_for(
                            websocket.recv(), timeout=REQUEST_TIMEOUT
                        )
                        result = json.loads(response)

                        if result.get("type") == "success":
                            # Decode video and save to temporary file
                            if "video_base64" in result:
                                video_data = base64.b64decode(result["video_base64"])

                                # Create temporary file for video
                                temp_dir = Path("./results")
                                temp_dir.mkdir(exist_ok=True)

                                timestamp = time.strftime("%Y_%m_%d_%H.%M.%S")
                                video_path = temp_dir / f"gradio_ws_{timestamp}.mp4"

                                with open(video_path, "wb") as f:
                                    f.write(video_data)

                                return (
                                    str(video_path),
                                    f"✅ {result.get('message', 'Video generated successfully')}",
                                )

                            elif "video_url" in result:
                                # If server returns URL, construct full path
                                video_url = result["video_url"]
                                if video_url.startswith("/static/"):
                                    video_path = video_url.replace("/static/", "./")
                                    if os.path.exists(video_path):
                                        return (
                                            video_path,
                                            f"✅ {result.get('message', 'Video generated successfully')}",
                                        )

                                return None, f"❌ Video file not found: {video_url}"

                        elif result.get("type") == "error":
                            error_msg = result.get("message", "Unknown error")
                            return None, f"❌ Server error: {error_msg}"

                        elif result.get("type") == "status":
                            # Status update - continue waiting
                            continue

                        else:
                            return (
                                None,
                                f"❌ Unexpected response: {result.get('message', 'Unknown status')}",
                            )

                except asyncio.TimeoutError:
                    return (
                        None,
                        f"❌ Request timeout after {REQUEST_TIMEOUT}s. Try reducing video length or complexity.",
                    )

        except websockets.exceptions.ConnectionClosedError:
            return None, "❌ WebSocket connection closed. Is the server running?"
        except websockets.exceptions.InvalidURI:
            return None, f"❌ Invalid WebSocket URL: {self.ws_url}"
        except ConnectionRefusedError:
            return (
                None,
                f"❌ Cannot connect to WebSocket server at {self.ws_url}. Please start the server first.",
            )
        except Exception as e:
            return None, f"❌ Unexpected error: {str(e)}"


def create_websocket_interface():
    """Create Gradio interface for WebSocket SadTalker"""

    ws_client = WebSocketSadTalker()

    def sync_generate_video(*args):
        """Synchronous wrapper for async video generation"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(ws_client.generate_video(*args))
            loop.close()
            return result
        except Exception as e:
            return None, f"❌ Error: {str(e)}"

    with gr.Blocks(
        analytics_enabled=False, title="SadTalker WebSocket API"
    ) as interface:
        gr.Markdown(
            """
        <div align='center'>
        <h2>🌐 SadTalker WebSocket API Client</h2>
        <p>Generate talking head videos using WebSocket API</p>
        <p style='color: #888;'>Make sure the WebSocket server is running on <code>{}</code></p>
        </div>
        """.format(
                WS_URL
            )
        )

        with gr.Row(equal_height=False):
            with gr.Column(variant="panel"):
                gr.Markdown("### 📂 Input Files")

                with gr.Tabs(elem_id="websocket_source_image"):
                    with gr.TabItem("Source Image"):
                        source_image = gr.Image(
                            label="Upload source image",
                            source="upload",
                            type="filepath",
                            elem_id="ws_source_image",
                        )

                with gr.Tabs(elem_id="websocket_driven_audio"):
                    with gr.TabItem("Audio Input"):
                        driven_audio = gr.Audio(
                            label="Upload audio file", source="upload", type="filepath"
                        )

                        # Optional TTS integration (if available)
                        if sys.platform != "win32" and not in_webui:
                            try:
                                from src.utils.text2speech import TTSTalker

                                tts_talker = TTSTalker()

                                gr.Markdown("**Or generate audio from text:**")
                                input_text = gr.Textbox(
                                    label="Text to Speech",
                                    lines=3,
                                    placeholder="Enter text to generate audio using TTS...",
                                )
                                tts_button = gr.Button(
                                    "🎤 Generate Audio", variant="secondary"
                                )
                                tts_button.click(
                                    fn=tts_talker.test,
                                    inputs=[input_text],
                                    outputs=[driven_audio],
                                )
                            except ImportError:
                                gr.Markdown("*TTS not available*")

            with gr.Column(variant="panel"):
                gr.Markdown("### ⚙️ Settings")

                with gr.Tabs(elem_id="websocket_settings"):
                    with gr.TabItem("Basic Settings"):
                        preprocess_type = gr.Radio(
                            choices=["crop", "resize", "full"],
                            value="crop",
                            label="Preprocessing Mode",
                            info="How to handle input image",
                        )

                        expression_scale = gr.Slider(
                            minimum=0.0,
                            maximum=3.0,
                            step=0.1,
                            value=1.0,
                            label="Expression Scale",
                            info="Higher = stronger expressions",
                        )

                        is_still_mode = gr.Checkbox(
                            label="Still Mode",
                            info="Reduce head motion (works best with 'full' preprocess)",
                        )

                    with gr.TabItem("Advanced Settings"):
                        size_of_image = gr.Radio(
                            choices=[256, 512],
                            value=256,
                            label="Model Resolution",
                            info="Higher resolution = better quality but slower",
                        )

                        pose_style = gr.Slider(
                            minimum=0,
                            maximum=46,
                            step=1,
                            value=0,
                            label="Pose Style",
                            info="Reference pose style",
                        )

                        batch_size = gr.Slider(
                            minimum=1,
                            maximum=10,
                            step=1,
                            value=2,
                            label="Batch Size",
                            info="Processing batch size",
                        )

                    with gr.TabItem("Enhancement"):
                        enhancer = gr.Checkbox(
                            label="Face Enhancement (GFPGAN)",
                            info="Improve face quality",
                        )

                        background_enhancer = gr.Checkbox(
                            label="Background Enhancement (Real-ESRGAN)",
                            info="Improve background quality",
                        )

                gr.Markdown("### 🚀 Generation")

                with gr.Row():
                    submit_button = gr.Button(
                        "🎬 Generate Video",
                        elem_id="websocket_generate",
                        variant="primary",
                        size="lg",
                    )

                    clear_button = gr.Button("🗑️ Clear", variant="secondary")

                # Status display
                status_text = gr.Textbox(
                    label="Status",
                    value="Ready to generate video...",
                    interactive=False,
                )

        # Output section
        gr.Markdown("### 📹 Generated Video")
        gen_video = gr.Video(
            label="Result", format="mp4", elem_id="websocket_output_video"
        )

        # Server connection info
        with gr.Accordion("🔧 Server Info", open=False):
            gr.Markdown(
                f"""
            **WebSocket URL:** `{WS_URL}`
            
            **Server Commands:**
            ```bash
            # Start WebSocket server
            python fastapi_websocket_server.py
            
            # Or with uvicorn
            uvicorn fastapi_websocket_server:app --host 0.0.0.0 --port 8000
            ```
            
            **Health Check:**
            ```bash
            curl http://localhost:8000/health
            ```
            """
            )

        # Event handlers
        submit_button.click(
            fn=sync_generate_video,
            inputs=[
                source_image,
                driven_audio,
                preprocess_type,
                is_still_mode,
                enhancer,
                background_enhancer,
                expression_scale,
                size_of_image,
                pose_style,
                batch_size,
            ],
            outputs=[gen_video, status_text],
        )

        clear_button.click(
            fn=lambda: (None, None, "Ready to generate video..."),
            outputs=[source_image, driven_audio, status_text],
        )

        # Update status when files are uploaded
        source_image.change(
            fn=lambda x: (
                "Source image uploaded ✓" if x else "Please upload source image"
            ),
            inputs=[source_image],
            outputs=[status_text],
        )

        driven_audio.change(
            fn=lambda x: "Audio file uploaded ✓" if x else "Please upload audio file",
            inputs=[driven_audio],
            outputs=[status_text],
        )

    return interface


def main():
    """Main function to launch the Gradio interface"""
    print(f"🌐 SadTalker WebSocket API Client")
    print(f"📡 Connecting to: {WS_URL}")
    print(f"🚀 Starting Gradio interface...")

    # Create and launch interface
    demo = create_websocket_interface()
    demo.queue(max_size=10)

    # Launch with appropriate settings
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=False,
        show_api=False,
    )


if __name__ == "__main__":
    main()
