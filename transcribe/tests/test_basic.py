"""
Basic functionality tests for transcribe
"""

import sys
from pathlib import Path


def test_module_import():
    """Test that the module can be imported"""
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
    import transcribe

    assert transcribe.main is not None


def test_help_option():
    """Test --help option doesn't crash"""
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
    import transcribe

    # Mock sys.argv for help
    original_argv = sys.argv[:]
    sys.argv = ["transcribe", "--help"]

    try:
        transcribe.main()
        assert False, "Should have raised SystemExit"
    except SystemExit as e:
        # Help should exit with code 0
        assert e.code == 0
    finally:
        sys.argv = original_argv
