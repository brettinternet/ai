"""
Shared pytest fixtures for transcribe tests
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch
import numpy as np


@pytest.fixture
def temp_audio_file():
    """Create a temporary audio file for testing"""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        # Write minimal WAV header + some dummy data
        wav_header = b"RIFF\x24\x08\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x40\x1f\x00\x00\x80\x3e\x00\x00\x02\x00\x10\x00data\x00\x08\x00\x00"
        dummy_audio = b"\x00\x01" * 1000  # Simple 16-bit PCM data
        f.write(wav_header + dummy_audio)
        f.flush()
        yield f.name
    os.unlink(f.name)


@pytest.fixture
def temp_model_file():
    """Create a temporary model file for testing"""
    with tempfile.NamedTemporaryFile(suffix=".bin", delete=False) as f:
        f.write(b"fake_model_data")
        f.flush()
        yield f.name
    os.unlink(f.name)


@pytest.fixture
def temp_output_dir():
    """Create a temporary directory for output files"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_audio_data():
    """Mock audio data for testing"""
    mock_data = Mock()
    mock_data.get_raw_data.return_value = b"\x00\x01" * 1000  # 16-bit PCM data
    return mock_data


@pytest.fixture
def mock_numpy_audio():
    """Mock numpy audio array for whisper processing"""
    return np.array([0.1, 0.2, 0.3, -0.1, -0.2], dtype=np.float32)


@pytest.fixture
def mock_whisper_result():
    """Mock Whisper transcription result"""
    return {
        "text": "This is a test transcription.",
        "segments": [{"start": 0.0, "end": 2.5, "text": "This is a test transcription."}],
    }


@pytest.fixture
def sample_transcriptions():
    """Sample transcription data for testing"""
    return ["", "Hello world", "This is a test", "Final transcription line"]


@pytest.fixture
def mock_subprocess_success():
    """Mock successful subprocess execution"""
    with patch("subprocess.Popen") as mock_popen:
        mock_process = Mock()
        mock_process.wait.return_value = 0
        mock_process.returncode = 0
        mock_process.communicate.return_value = ("success", "")
        mock_popen.return_value = mock_process
        yield mock_popen


@pytest.fixture
def mock_subprocess_failure():
    """Mock failed subprocess execution"""
    with patch("subprocess.Popen") as mock_popen:
        mock_process = Mock()
        mock_process.wait.return_value = 1
        mock_process.returncode = 1
        mock_process.communicate.return_value = ("", "error")
        mock_popen.return_value = mock_process
        yield mock_popen


@pytest.fixture(autouse=True)
def cleanup_environment():
    """Clean up environment after each test"""
    yield
    # Clean up any temporary files or processes that might be left behind
    # This is a safety net for tests that might not clean up properly
