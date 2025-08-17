import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch
import tempfile

# Import the module under test
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
import transcribe_main as transcribe


class TestTranscribe:
    """Test suite for transcribe.py (FFmpeg implementation)"""

    def test_argument_parsing_defaults(self):
        """Test default argument parsing"""
        with patch("sys.argv", ["transcribe.py"]):
            with patch("transcribe.subprocess.Popen"):
                with patch("transcribe.monitor_transcription_file"):
                    with patch("pathlib.Path.exists", return_value=True):
                        # This will test the argument parsing without actually running FFmpeg
                        pass

    @pytest.mark.parametrize(
        "platform,expected_format",
        [
            ("linux", "alsa"),
            ("darwin", "avfoundation"),
            ("win32", "dshow"),
        ],
    )
    def test_platform_specific_audio_input(self, platform, expected_format):
        """Test that correct audio input format is selected based on platform"""
        with patch("sys.platform", platform):
            with patch("subprocess.Popen") as mock_popen:
                with patch("transcribe.monitor_transcription_file"):
                    with patch("pathlib.Path.exists", return_value=True):
                        with patch("sys.argv", ["transcribe.py"]):
                            mock_process = Mock()
                            mock_popen.return_value = mock_process
                            mock_process.wait.return_value = 0

                            transcribe.main()

                            # Check that correct format was used in FFmpeg command
                            args, kwargs = mock_popen.call_args
                            cmd = args[0]
                            assert expected_format in cmd

    def test_model_path_validation(self):
        """Test model path validation and error handling"""
        with patch("sys.argv", ["transcribe.py", "--model", "nonexistent"]):
            with patch("pathlib.Path.exists", return_value=False):
                with patch("builtins.print") as mock_print:
                    transcribe.main()

                    # Should print model not found message
                    mock_print.assert_any_call(
                        pytest.approx("Model not found at", abs=0),
                        pytest.approx(Path.home() / ".whisper" / "models" / "ggml-nonexistent.bin"),
                    )

    def test_custom_model_path(self):
        """Test using custom model path"""
        custom_path = "/custom/path/model.bin"
        with patch("sys.argv", ["transcribe.py", "--model-path", custom_path]):
            with patch("subprocess.Popen") as mock_popen:
                with patch("transcribe.monitor_transcription_file"):
                    mock_process = Mock()
                    mock_popen.return_value = mock_process
                    mock_process.wait.return_value = 0

                    transcribe.main()

                    args, kwargs = mock_popen.call_args
                    cmd = args[0]
                    assert custom_path in " ".join(cmd)

    def test_vad_option(self):
        """Test Voice Activity Detection option"""
        with patch("sys.argv", ["transcribe.py", "--vad"]):
            with patch("subprocess.Popen") as mock_popen:
                with patch("transcribe.monitor_transcription_file"):
                    with patch("pathlib.Path.exists", return_value=True):
                        mock_process = Mock()
                        mock_popen.return_value = mock_process
                        mock_process.wait.return_value = 0

                        transcribe.main()

                        args, kwargs = mock_popen.call_args
                        cmd = args[0]
                        assert ":vad=1" in " ".join(cmd)

    def test_output_formats(self):
        """Test different output format options"""
        formats = ["txt", "srt", "json"]

        for fmt in formats:
            with patch("sys.argv", ["transcribe.py", "--format", fmt]):
                with patch("subprocess.Popen") as mock_popen:
                    with patch("transcribe.monitor_transcription_file"):
                        with patch("pathlib.Path.exists", return_value=True):
                            mock_process = Mock()
                            mock_popen.return_value = mock_process
                            mock_process.wait.return_value = 0

                            transcribe.main()

                            args, kwargs = mock_popen.call_args
                            cmd = args[0]
                            if fmt != "txt":  # txt is default, won't appear in command
                                assert f":format={fmt}" in " ".join(cmd)

    def test_keyboard_interrupt_handling(self):
        """Test graceful handling of KeyboardInterrupt"""
        with patch("sys.argv", ["transcribe.py"]):
            with patch("subprocess.Popen") as mock_popen:
                with patch("transcribe.monitor_transcription_file", side_effect=KeyboardInterrupt):
                    with patch("pathlib.Path.exists", return_value=True):
                        with patch("builtins.print") as mock_print:
                            mock_process = Mock()
                            mock_popen.return_value = mock_process

                            transcribe.main()

                            mock_process.terminate.assert_called_once()
                            mock_process.wait.assert_called()
                            mock_print.assert_any_call("\nStopping transcription...")

    def test_ffmpeg_not_found_error(self):
        """Test handling when FFmpeg is not installed"""
        with patch("sys.argv", ["transcribe.py"]):
            with patch("subprocess.Popen", side_effect=FileNotFoundError):
                with patch("pathlib.Path.exists", return_value=True):
                    with patch("builtins.print") as mock_print:
                        transcribe.main()

                        mock_print.assert_any_call(
                            "Error: FFmpeg not found. Please install FFmpeg 8+ with Whisper support."
                        )

    @pytest.mark.parametrize(
        "platform,expected_calls",
        [
            ("linux", [["arecord", "-l"]]),
            ("darwin", [["ffmpeg", "-f", "avfoundation", "-list_devices", "true", "-i", ""]]),
            ("win32", [["ffmpeg", "-f", "dshow", "-list_devices", "true", "-i", "dummy"]]),
        ],
    )
    def test_list_audio_devices(self, platform, expected_calls):
        """Test device listing for different platforms"""
        with patch("sys.platform", platform):
            with patch("subprocess.run") as mock_run:
                mock_result = Mock()
                mock_result.stdout = "device list output"
                mock_result.stderr = "device list output"
                mock_run.return_value = mock_result

                transcribe.list_audio_devices()

                mock_run.assert_called_once_with(expected_calls[0], capture_output=True, text=True)

    def test_device_list_option(self):
        """Test --device list option"""
        with patch("sys.argv", ["transcribe.py", "--device", "list"]):
            with patch("transcribe.list_audio_devices") as mock_list:
                transcribe.main()
                mock_list.assert_called_once()

    def test_unsupported_platform(self):
        """Test handling of unsupported platforms"""
        with patch("sys.platform", "unsupported_os"):
            with patch("sys.argv", ["transcribe.py"]):
                with patch("pathlib.Path.exists", return_value=True):
                    with patch("builtins.print") as mock_print:
                        transcribe.main()

                        mock_print.assert_any_call("Unsupported platform: unsupported_os")

    def test_monitor_transcription_file(self):
        """Test transcription file monitoring function"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as tf:
            tf.write("Initial content")
            tf.flush()
            temp_path = tf.name

        try:
            with patch("builtins.print") as mock_print:
                # Simulate adding content to file
                def add_content():
                    with open(temp_path, "a") as f:
                        f.write("\nNew transcription")
                    raise KeyboardInterrupt  # Stop the monitoring loop

                with patch("time.sleep", side_effect=add_content):
                    transcribe.monitor_transcription_file(temp_path)

                # Should have printed the new content
                mock_print.assert_called()
        finally:
            os.unlink(temp_path)

    def test_model_choices_validation(self):
        """Test that model choices are validated correctly"""
        valid_models = [
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
        ]

        for model in valid_models:
            with patch("sys.argv", ["transcribe.py", "--model", model]):
                with patch("subprocess.Popen") as mock_popen:
                    with patch("transcribe.monitor_transcription_file"):
                        with patch("pathlib.Path.exists", return_value=True):
                            mock_process = Mock()
                            mock_popen.return_value = mock_process
                            mock_process.wait.return_value = 0

                            # Should not raise an exception
                            transcribe.main()

    def test_whisper_filter_construction(self):
        """Test that whisper filter string is constructed correctly"""
        test_cases = [
            {
                "args": ["transcribe.py", "--language", "es", "--vad"],
                "expected_parts": [":language=es", ":vad=1"],
            },
            {
                "args": ["transcribe.py", "--format", "srt", "--output", "test.srt"],
                "expected_parts": [":format=srt", ":destination=test.srt"],
            },
        ]

        for test_case in test_cases:
            with patch("sys.argv", test_case["args"]):
                with patch("subprocess.Popen") as mock_popen:
                    with patch("transcribe.monitor_transcription_file"):
                        with patch("pathlib.Path.exists", return_value=True):
                            mock_process = Mock()
                            mock_popen.return_value = mock_process
                            mock_process.wait.return_value = 0

                            transcribe.main()

                            args, kwargs = mock_popen.call_args
                            cmd = args[0]
                            cmd_str = " ".join(cmd)

                            for expected_part in test_case["expected_parts"]:
                                assert expected_part in cmd_str
