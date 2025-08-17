#!/usr/bin/env python3

import argparse
import subprocess
import sys
import os
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="Real-time transcription using FFmpeg 8+ Whisper support"
    )
    parser.add_argument(
        "--model",
        default="base.en",
        help="Whisper model to use",
        choices=[
            "tiny",
            "tiny.en",
            "base",
            "base.en",
            "small",
            "small.en",
            "medium",
            "medium.en",
            "large",
            "large-v1",
            "large-v2",
            "large-v3",
        ],
    )
    parser.add_argument(
        "--language", default="auto", help="Language for transcription (auto-detect by default)"
    )
    parser.add_argument(
        "--output", default="transcription.txt", help="Output file for transcription"
    )
    parser.add_argument(
        "--format", default="txt", choices=["txt", "srt", "json"], help="Output format"
    )
    parser.add_argument("--model-path", help="Custom path to whisper.cpp model file")
    parser.add_argument(
        "--device", help="Audio input device (use 'list' to show available devices)"
    )
    parser.add_argument("--vad", action="store_true", help="Enable Voice Activity Detection")

    args = parser.parse_args()

    # Handle device listing
    if args.device == "list":
        list_audio_devices()
        return

    # Determine model path
    if args.model_path:
        model_path = args.model_path
    else:
        # Default whisper.cpp model path - user needs to download models
        models_dir = Path.home() / ".whisper" / "models"
        model_path = models_dir / f"ggml-{args.model}.bin"

        if not model_path.exists():
            print(f"Model not found at {model_path}")
            print("Please download whisper.cpp models or specify --model-path")
            print("See: https://github.com/ggerganov/whisper.cpp#quick-start")
            return

    # Build FFmpeg command
    cmd = ["ffmpeg", "-f"]

    # Platform-specific audio input
    if sys.platform.startswith("linux"):
        cmd.extend(["alsa", "-i", args.device or "default"])
    elif sys.platform == "darwin":  # macOS
        cmd.extend(["avfoundation", "-i", args.device or ":0"])
    elif sys.platform.startswith("win"):
        cmd.extend(["dshow", "-i", f"audio={args.device or 'default'}"])
    else:
        print(f"Unsupported platform: {sys.platform}")
        return

    # Audio processing and whisper filter
    whisper_filter = (
        f"whisper=model={model_path}:language={args.language}:destination={args.output}"
    )

    if args.format != "txt":
        whisper_filter += f":format={args.format}"

    if args.vad:
        whisper_filter += ":vad=1"

    cmd.extend(["-af", whisper_filter, "-f", "null", "-"])

    print("Starting real-time transcription...")
    print(f"Model: {args.model}")
    print(f"Language: {args.language}")
    print(f"Output: {args.output} ({args.format})")
    print(f"VAD: {'enabled' if args.vad else 'disabled'}")
    print("Press Ctrl+C to stop\n")

    try:
        # Run FFmpeg command
        process = subprocess.Popen(cmd, stderr=subprocess.PIPE, text=True)

        # Monitor for transcription updates (simple tail-like behavior)
        if args.format == "txt":
            monitor_transcription_file(args.output)

        process.wait()

    except KeyboardInterrupt:
        print("\nStopping transcription...")
        process.terminate()
        process.wait()
    except FileNotFoundError:
        print("Error: FFmpeg not found. Please install FFmpeg 8+ with Whisper support.")
        print("See: https://ffmpeg.org/download.html")
    except Exception as e:
        print(f"Error: {e}")


def list_audio_devices():
    """List available audio input devices"""
    print("Available audio input devices:")

    try:
        if sys.platform.startswith("linux"):
            # List ALSA devices
            result = subprocess.run(["arecord", "-l"], capture_output=True, text=True)
            print(result.stdout)
        elif sys.platform == "darwin":  # macOS
            # List AVFoundation devices
            result = subprocess.run(
                ["ffmpeg", "-f", "avfoundation", "-list_devices", "true", "-i", ""],
                capture_output=True,
                text=True,
            )
            print(result.stderr)  # FFmpeg outputs device list to stderr
        elif sys.platform.startswith("win"):
            # List DirectShow devices
            result = subprocess.run(
                ["ffmpeg", "-f", "dshow", "-list_devices", "true", "-i", "dummy"],
                capture_output=True,
                text=True,
            )
            print(result.stderr)
    except FileNotFoundError:
        print("FFmpeg not found. Please install FFmpeg to list devices.")


def monitor_transcription_file(filepath):
    """Simple file monitoring for real-time transcription display"""
    import time

    last_size = 0
    while True:
        try:
            if os.path.exists(filepath):
                current_size = os.path.getsize(filepath)
                if current_size > last_size:
                    with open(filepath, "r") as f:
                        f.seek(last_size)
                        new_content = f.read()
                        if new_content.strip():
                            print(new_content, end="")
                    last_size = current_size
            time.sleep(0.5)
        except KeyboardInterrupt:
            break
        except Exception:
            # File might be temporarily locked
            time.sleep(0.5)


if __name__ == "__main__":
    main()
