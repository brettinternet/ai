"""
Integration tests for transcribe package (Python implementation)
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, Mock


class TestIntegration:
    """Integration tests for transcribe Python implementation"""

    def test_package_import(self):
        """Test that module can be imported successfully"""
        sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

        try:
            __import__("transcribe")
        except ImportError as e:
            pytest.fail(f"Failed to import transcribe module: {e}")

    def test_python_help_output(self):
        """Test that Python version shows help correctly"""
        sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
        import transcribe

        with patch("sys.argv", ["transcribe.py", "--help"]):
            with pytest.raises(SystemExit) as exc_info:
                transcribe.main()
            # argparse exits with code 0 for help
            assert exc_info.value.code == 0

    def test_python_version_dry_run(self):
        """Test Python version initialization without audio capture"""
        sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
        import transcribe

        with patch("sys.argv", ["transcribe.py", "--model", "tiny"]):
            with patch("transcribe.whisper.load_model") as mock_load:
                with patch("transcribe.sr.Recognizer"):
                    with patch("transcribe.sr.Microphone"):
                        with patch("time.sleep", side_effect=KeyboardInterrupt):
                            try:
                                transcribe.main()
                            except KeyboardInterrupt:
                                pass

                            # Verify model loading was attempted
                            mock_load.assert_called_once_with("tiny.en")

    def test_command_line_validation(self):
        """Test command line argument validation"""
        sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
        import transcribe

        # Test invalid model choice would be caught by argparse
        # (actual validation happens in whisper.load_model)
        with patch("sys.argv", ["transcribe.py", "--model", "invalid_model"]):
            with patch("transcribe.whisper.load_model", side_effect=Exception("Invalid model")):
                with patch("transcribe.sr.Recognizer"):
                    with patch("transcribe.sr.Microphone"):
                        with pytest.raises(Exception):
                            transcribe.main()

    def test_microphone_listing_integration(self):
        """Test microphone listing functionality"""
        sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
        import transcribe

        with patch("transcribe.platform", "linux"):
            with patch("sys.argv", ["transcribe.py", "--default_microphone", "list"]):
                with patch(
                    "transcribe.sr.Microphone.list_microphone_names",
                    return_value=["device1", "device2"],
                ):
                    with patch("builtins.print") as mock_print:
                        transcribe.main()

                        # Should print available devices
                        mock_print.assert_any_call("Available microphone devices are: ")

    def test_model_loading_integration(self):
        """Test model loading with different options"""
        sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
        import transcribe

        test_cases = [
            (["transcribe.py", "--model", "base"], "base.en"),
            (["transcribe.py", "--model", "small", "--non_english"], "small"),
            (["transcribe.py", "--model", "large"], "large"),
        ]

        for argv, expected_model in test_cases:
            with patch("sys.argv", argv):
                with patch("transcribe.whisper.load_model") as mock_load:
                    with patch("transcribe.sr.Recognizer"):
                        with patch("transcribe.sr.Microphone"):
                            with patch("time.sleep", side_effect=KeyboardInterrupt):
                                try:
                                    transcribe.main()
                                except KeyboardInterrupt:
                                    pass

                                mock_load.assert_called_with(expected_model)

    @pytest.mark.slow
    def test_signal_handling(self):
        """Test signal handling and cleanup (marked as slow test)"""
        sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
        import transcribe

        with patch("sys.argv", ["transcribe.py"]):
            with patch("transcribe.whisper.load_model"):
                with patch("transcribe.sr.Recognizer") as mock_recognizer_class:
                    with patch("transcribe.sr.Microphone"):
                        mock_recognizer = Mock()
                        mock_recognizer_class.return_value = mock_recognizer

                        # Simulate KeyboardInterrupt during main loop
                        with patch("time.sleep", side_effect=KeyboardInterrupt):
                            transcribe.main()

                            # Verify recognizer was set up
                            assert mock_recognizer.energy_threshold == 1000

    def test_platform_specific_behavior(self):
        """Test platform-specific microphone handling"""
        sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
        import transcribe

        # Test Linux-specific microphone handling
        with patch("transcribe.platform", "linux"):
            with patch("sys.argv", ["transcribe.py", "--default_microphone", "pulse"]):
                with patch(
                    "transcribe.sr.Microphone.list_microphone_names",
                    return_value=["alsa device", "pulse device", "usb device"],
                ):
                    with patch("transcribe.whisper.load_model"):
                        with patch("transcribe.sr.Recognizer"):
                            with patch("transcribe.sr.Microphone") as mock_mic:
                                with patch("time.sleep", side_effect=KeyboardInterrupt):
                                    try:
                                        transcribe.main()
                                    except KeyboardInterrupt:
                                        pass

                                    # Should create microphone with correct device index
                                    mock_mic.assert_called_with(sample_rate=16000, device_index=1)

    def test_audio_processing_parameters(self):
        """Test different audio processing parameter configurations"""
        sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
        import transcribe

        parameter_tests = [
            (["transcribe.py", "--energy_threshold", "2000"], 2000),
            (["transcribe.py", "--energy_threshold", "500"], 500),
        ]

        for argv, expected_threshold in parameter_tests:
            with patch("sys.argv", argv):
                with patch("transcribe.whisper.load_model"):
                    with patch("transcribe.sr.Recognizer") as mock_recognizer_class:
                        with patch("transcribe.sr.Microphone"):
                            mock_recognizer = Mock()
                            mock_recognizer_class.return_value = mock_recognizer

                            with patch("time.sleep", side_effect=KeyboardInterrupt):
                                try:
                                    transcribe.main()
                                except KeyboardInterrupt:
                                    pass

                                assert mock_recognizer.energy_threshold == expected_threshold
                                assert mock_recognizer.dynamic_energy_threshold is False
