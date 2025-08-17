"""
Shared pytest fixtures for transcribe-ffmpeg tests
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch


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
