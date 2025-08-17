"""
Basic functionality tests for transcribe_ffmpeg
"""

import sys
from pathlib import Path


def test_module_import():
    """Test that the module can be imported"""
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
    import transcribe_main

    assert transcribe_main.main is not None


def test_help_option():
    """Test --help option doesn't crash"""
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
    import transcribe_main

    # Mock sys.argv for help
    original_argv = sys.argv[:]
    sys.argv = ["transcribe-ffmpeg", "--help"]

    try:
        transcribe_main.main()
        assert False, "Should have raised SystemExit"
    except SystemExit as e:
        # Help should exit with code 0
        assert e.code == 0
    finally:
        sys.argv = original_argv


def test_list_audio_devices_function():
    """Test that list_audio_devices function exists"""
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
    import transcribe_main

    # Function should exist and be callable
    assert hasattr(transcribe_main, "list_audio_devices")
    assert callable(transcribe_main.list_audio_devices)


def test_monitor_function_exists():
    """Test that monitor_transcription_file function exists"""
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
    import transcribe_main

    # Function should exist and be callable
    assert hasattr(transcribe_main, "monitor_transcription_file")
    assert callable(transcribe_main.monitor_transcription_file)
