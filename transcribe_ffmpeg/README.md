# Transcribe (FFmpeg)

A lightweight real-time audio transcription tool using FFmpeg 8+'s native Whisper support.

## Installation

```bash
uv pip install -e .
```

## Requirements

- FFmpeg 8+ with Whisper support
- whisper.cpp models (downloaded separately)

## Setup

1. **Install FFmpeg 8+** with Whisper support:
   ```bash
   # macOS with Homebrew
   brew install ffmpeg

   # Linux (compile from source or use recent packages)
   # Windows (download from ffmpeg.org)
   ```

2. **Download whisper.cpp models**:
   ```bash
   # Create models directory
   mkdir -p ~/.whisper/models
   cd ~/.whisper/models

   # Download desired models (examples)
   wget https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin
   wget https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-medium.en.bin
   ```

## Usage

### Basic Usage

```bash
transcribe-ffmpeg
```

### With Options

```bash
# List available audio devices
transcribe-ffmpeg --device list

# Use specific model and enable VAD
transcribe-ffmpeg --model medium.en --vad --output my_transcription.txt

# Output as SRT subtitles
transcribe-ffmpeg --format srt --output subtitles.srt

# Specify custom model path
transcribe-ffmpeg --model-path /path/to/ggml-large-v3.bin
```

### Available Models

- `tiny`, `tiny.en` - Fastest, least accurate
- `base`, `base.en` - Good balance of speed and accuracy
- `small`, `small.en` - Better accuracy
- `medium`, `medium.en` - High accuracy (default)
- `large`, `large-v1`, `large-v2`, `large-v3` - Best accuracy, slower

## Advantages over Python-only approach

1. **Simpler dependencies** - Only FFmpeg required, no Python audio libraries
2. **Better performance** - Native C++ implementation via whisper.cpp
3. **Built-in VAD** - Voice Activity Detection included
4. **Multiple output formats** - Text, SRT, JSON support
5. **Cross-platform** - Unified approach across Linux, macOS, Windows
6. **Real-time streaming** - Optimized for live audio processing

## Task Commands

This project uses [Taskfile](https://taskfile.dev) for automation. Available commands:

### Development Setup

```bash
task dev          # Complete development setup (install + FFmpeg check)
task install:dev  # Install with test dependencies
```

### Testing

```bash
task test         # Run all tests with coverage
task test:basic   # Run basic functionality tests (fastest)
task test:unit    # Run unit tests
task test:watch   # Run tests in watch mode
```

### Code Quality

```bash
task lint         # Check code with ruff
task lint:fix     # Fix linting issues automatically
task format       # Format code with ruff  
task format:check # Check formatting without changes
task fix          # Fix both linting and formatting issues
task check        # Run all checks (lint, format, test, build)
```

### Running

```bash
task run          # Run with default settings
task run:tiny     # Run with tiny model (fastest)
task run:base     # Run with base model (balanced)
task run:medium   # Run with medium model (recommended)
task run:vad      # Run with Voice Activity Detection
task run:srt      # Output as SRT subtitles
task devices      # List available audio devices
```

### Model Management

```bash
task models:setup # Download common Whisper models
task models:list  # List downloaded models
```

### System Checks

```bash
task ffmpeg:check # Check FFmpeg version and Whisper support
```

### Building

```bash
task build        # Build package for distribution
task clean        # Clean build artifacts and caches
```

## Notes

- The script monitors the output file for real-time display
- Press Ctrl+C to stop transcription
- Models are cached after first download
- VAD (Voice Activity Detection) helps reduce false transcriptions
