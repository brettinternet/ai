# Transcribe (Python)

Real-time audio transcription using OpenAI Whisper with Python.

## Installation

```bash
uv pip install -e .
```

## Usage

```bash
transcribe --model medium --energy_threshold 1000
```

**Features:**
- Real-time microphone input processing
- Granular control over audio processing parameters
- Custom phrase detection and timing logic
- Platform-specific microphone device selection (Linux)
- Configurable energy thresholds and timeouts

## Command Line Options

```bash
# Basic usage
transcribe

# Specify model
transcribe --model small

# Adjust energy threshold (higher = less sensitive)
transcribe --energy_threshold 2000

# Adjust timing parameters  
transcribe --record_timeout 3.0 --phrase_timeout 5.0

# Non-English models
transcribe --model medium --non_english

# Linux: specify microphone device
transcribe --default_microphone pulse
transcribe --default_microphone list  # Show available devices
```

## Model Comparison

| Model | Speed | Accuracy | Use Case |
|-------|-------|----------|----------|
| tiny  | Fastest | Basic | Testing, low-resource |
| base  | Fast | Good | General use |
| small | Medium | Better | Balanced |
| medium| Slower | High | Default recommendation |
| large | Slowest | Best | High-accuracy needs |

## Task Commands

This project uses [Taskfile](https://taskfile.dev) for automation. Available commands:

### Development Setup
```bash
task dev          # Complete development setup (install + test)
task install:dev  # Install with test dependencies
```

### Testing
```bash
task test         # Run all tests with coverage
task test:basic   # Run basic functionality tests (fastest)
task test:unit    # Run unit tests 
task test:integration  # Run integration tests
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
task devices      # List available audio devices (Linux)
```

### Building
```bash
task build        # Build package for distribution
task clean        # Clean build artifacts and caches
```

## Requirements

- Python 3.8+
- PyTorch with CUDA support (recommended)
- PyAudio for microphone input
- OpenAI Whisper model
- SpeechRecognition library

## Alternative: FFmpeg Version

For a lighter-weight alternative that doesn't require Python ML dependencies, see the `transcribe_ffmpeg/` directory for an FFmpeg 8+ based implementation.