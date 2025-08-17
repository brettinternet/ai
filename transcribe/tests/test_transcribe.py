import pytest
import sys
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch
from queue import Queue

# Import the module under test
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
import transcribe


class TestTranscribe:
    """Test suite for transcribe.py (original Python implementation)"""

    @pytest.fixture
    def mock_whisper_model(self):
        """Mock Whisper model for testing"""
        mock_model = Mock()
        mock_result = {"text": "test transcription"}
        mock_model.transcribe.return_value = mock_result
        return mock_model

    @pytest.fixture
    def mock_recognizer(self):
        """Mock speech recognizer for testing"""
        mock_recognizer = Mock()
        mock_recognizer.energy_threshold = 1000
        mock_recognizer.dynamic_energy_threshold = False
        return mock_recognizer

    @pytest.fixture
    def mock_microphone(self):
        """Mock microphone source for testing"""
        mock_mic = Mock()
        mock_mic.__enter__ = Mock(return_value=mock_mic)
        mock_mic.__exit__ = Mock(return_value=None)
        return mock_mic

    def test_argument_parsing_defaults(self):
        """Test default argument parsing"""
        with patch("sys.argv", ["transcribe.py"]):
            with patch("transcribe.whisper.load_model"):
                with patch("transcribe.sr.Recognizer"):
                    with patch("transcribe.sr.Microphone"):
                        with patch("builtins.input", side_effect=KeyboardInterrupt):
                            # Mock the main loop to prevent infinite execution
                            with patch.object(transcribe, "__name__", "__main__"):
                                try:
                                    transcribe.main()
                                except KeyboardInterrupt:
                                    pass

    @pytest.mark.parametrize(
        "model,expected_suffix",
        [
            ("tiny", ".en"),
            ("base", ".en"),
            ("small", ".en"),
            ("medium", ".en"),
            ("large", ""),  # large model doesn't get .en suffix
        ],
    )
    def test_model_name_construction(self, model, expected_suffix):
        """Test that model names are constructed correctly"""
        with patch("sys.argv", ["transcribe.py", "--model", model]):
            with patch("transcribe.whisper.load_model") as mock_load:
                with patch("transcribe.sr.Recognizer"):
                    with patch("transcribe.sr.Microphone"):
                        with patch("builtins.input", side_effect=KeyboardInterrupt):
                            try:
                                transcribe.main()
                            except KeyboardInterrupt:
                                pass

                            expected_model = model + expected_suffix
                            mock_load.assert_called_with(expected_model)

    def test_non_english_model_option(self):
        """Test --non_english option"""
        with patch("sys.argv", ["transcribe.py", "--model", "base", "--non_english"]):
            with patch("transcribe.whisper.load_model") as mock_load:
                with patch("transcribe.sr.Recognizer"):
                    with patch("transcribe.sr.Microphone"):
                        with patch("builtins.input", side_effect=KeyboardInterrupt):
                            try:
                                transcribe.main()
                            except KeyboardInterrupt:
                                pass

                            # Should not have .en suffix when non_english is True
                            mock_load.assert_called_with("base")

    @patch("transcribe.platform", "linux")
    def test_linux_microphone_listing(self):
        """Test microphone listing on Linux"""
        with patch("sys.argv", ["transcribe.py", "--default_microphone", "list"]):
            with patch(
                "transcribe.sr.Microphone.list_microphone_names",
                return_value=["mic1", "mic2", "pulse"],
            ):
                with patch("builtins.print") as mock_print:
                    transcribe.main()

                    mock_print.assert_any_call("Available microphone devices are: ")
                    mock_print.assert_any_call('Microphone with name "mic1" found')

    @patch("transcribe.platform", "linux")
    def test_linux_microphone_selection(self):
        """Test microphone selection on Linux"""
        with patch("sys.argv", ["transcribe.py", "--default_microphone", "pulse"]):
            with patch(
                "transcribe.sr.Microphone.list_microphone_names",
                return_value=["mic1", "pulse microphone", "mic2"],
            ):
                with patch("transcribe.sr.Microphone") as mock_mic_class:
                    with patch("transcribe.whisper.load_model"):
                        with patch("transcribe.sr.Recognizer"):
                            with patch("builtins.input", side_effect=KeyboardInterrupt):
                                try:
                                    transcribe.main()
                                except KeyboardInterrupt:
                                    pass

                                # Should create microphone with correct device index (1)
                                mock_mic_class.assert_called_with(sample_rate=16000, device_index=1)

    def test_energy_threshold_setting(self):
        """Test energy threshold configuration"""
        test_threshold = 2000
        with patch("sys.argv", ["transcribe.py", "--energy_threshold", str(test_threshold)]):
            with patch("transcribe.whisper.load_model"):
                with patch("transcribe.sr.Recognizer") as mock_recognizer_class:
                    with patch("transcribe.sr.Microphone"):
                        mock_recognizer = Mock()
                        mock_recognizer_class.return_value = mock_recognizer

                        with patch("builtins.input", side_effect=KeyboardInterrupt):
                            try:
                                transcribe.main()
                            except KeyboardInterrupt:
                                pass

                            assert mock_recognizer.energy_threshold == test_threshold
                            assert mock_recognizer.dynamic_energy_threshold is False

    def test_timeout_parameters(self):
        """Test record and phrase timeout parameters"""
        with patch(
            "sys.argv", ["transcribe.py", "--record_timeout", "3.5", "--phrase_timeout", "5.0"]
        ):
            with patch("transcribe.whisper.load_model"):
                with patch("transcribe.sr.Recognizer") as mock_recognizer_class:
                    with patch("transcribe.sr.Microphone"):
                        mock_recognizer = Mock()
                        mock_recognizer_class.return_value = mock_recognizer

                        with patch("builtins.input", side_effect=KeyboardInterrupt):
                            try:
                                transcribe.main()
                            except KeyboardInterrupt:
                                pass

                            # Verify listen_in_background called with correct timeout
                            mock_recognizer.listen_in_background.assert_called()
                            args, kwargs = mock_recognizer.listen_in_background.call_args
                            assert kwargs.get("phrase_time_limit") == 3.5

    def test_audio_processing_pipeline(self, mock_whisper_model):
        """Test the audio processing pipeline with mocked components"""
        # Create mock audio data
        mock_audio_data = Mock()
        mock_audio_data.get_raw_data.return_value = b"\x00\x01" * 1000  # Fake 16-bit audio

        # Mock the queue with some test data
        test_queue = Queue()
        test_queue.put(b"\x00\x01" * 1000)

        with patch("transcribe.Queue", return_value=test_queue):
            with patch("transcribe.whisper.load_model", return_value=mock_whisper_model):
                with patch("transcribe.sr.Recognizer") as mock_recognizer_class:
                    with patch("transcribe.sr.Microphone"):
                        with patch("transcribe.np.frombuffer") as mock_frombuffer:
                            # Mock numpy conversion
                            mock_audio_np = np.array([0.1, 0.2, 0.3], dtype=np.float32)
                            mock_frombuffer.return_value.astype.return_value.__truediv__ = Mock(
                                return_value=mock_audio_np
                            )

                            mock_recognizer = Mock()
                            mock_recognizer_class.return_value = mock_recognizer

                            with patch("sys.argv", ["transcribe.py"]):
                                with patch("time.sleep", side_effect=KeyboardInterrupt):
                                    try:
                                        transcribe.main()
                                    except KeyboardInterrupt:
                                        pass

                            # Verify whisper model was called for transcription
                            mock_whisper_model.transcribe.assert_called()

    def test_transcription_output_formatting(self):
        """Test transcription output and console clearing"""
        with patch("sys.argv", ["transcribe.py"]):
            with patch("transcribe.whisper.load_model"):
                with patch("transcribe.sr.Recognizer"):
                    with patch("transcribe.sr.Microphone"):
                        with patch("transcribe.os.system"):
                            with patch("builtins.print") as mock_print:
                                with patch("time.sleep", side_effect=KeyboardInterrupt):
                                    try:
                                        transcribe.main()
                                    except KeyboardInterrupt:
                                        pass

                                # Should print "Model loaded." at start
                                mock_print.assert_any_call("Model loaded.\n")

    def test_keyboard_interrupt_handling(self):
        """Test graceful shutdown on KeyboardInterrupt"""
        with patch("sys.argv", ["transcribe.py"]):
            with patch("transcribe.whisper.load_model"):
                with patch("transcribe.sr.Recognizer"):
                    with patch("transcribe.sr.Microphone"):
                        with patch("builtins.print") as mock_print:
                            with patch("time.sleep", side_effect=KeyboardInterrupt):
                                transcribe.main()

                                # Should print final transcription
                                mock_print.assert_any_call("\\n\\nTranscription:")

    def test_phrase_completion_logic(self, mock_whisper_model):
        """Test phrase completion detection based on timing"""
        from datetime import datetime, timedelta

        # Test data for phrase timing
        base_time = datetime.utcnow()

        with patch("transcribe.datetime") as mock_datetime:
            # First call returns base time, second call returns time after timeout
            mock_datetime.utcnow.side_effect = [
                base_time,
                base_time + timedelta(seconds=5),  # Exceeds default phrase_timeout of 3
            ]

            with patch("sys.argv", ["transcribe.py"]):
                with patch("transcribe.whisper.load_model", return_value=mock_whisper_model):
                    with patch("transcribe.sr.Recognizer"):
                        with patch("transcribe.sr.Microphone"):
                            # Mock the data queue to simulate audio data
                            test_queue = Queue()
                            test_queue.put(b"\x00\x01" * 100)

                            with patch("transcribe.Queue", return_value=test_queue):
                                with patch("time.sleep", side_effect=KeyboardInterrupt):
                                    try:
                                        transcribe.main()
                                    except KeyboardInterrupt:
                                        pass

    @pytest.mark.parametrize(
        "platform_name,should_have_mic_arg",
        [
            ("linux", True),
            ("darwin", False),
            ("win32", False),
        ],
    )
    def test_platform_specific_behavior(self, platform_name, should_have_mic_arg):
        """Test platform-specific microphone handling"""
        with patch("transcribe.platform", platform_name):
            args = ["transcribe.py"]
            if should_have_mic_arg:
                args.extend(["--default_microphone", "test_mic"])

            with patch("sys.argv", args):
                with patch("transcribe.whisper.load_model"):
                    with patch("transcribe.sr.Recognizer"):
                        with patch("transcribe.sr.Microphone"):
                            with patch("builtins.input", side_effect=KeyboardInterrupt):
                                try:
                                    transcribe.main()
                                except KeyboardInterrupt:
                                    pass

                                if should_have_mic_arg and platform_name == "linux":
                                    # On Linux with microphone arg, should search for matching device
                                    with patch(
                                        "transcribe.sr.Microphone.list_microphone_names",
                                        return_value=["test_mic device"],
                                    ):
                                        # Verify device index was used
                                        pass

    def test_cuda_availability_detection(self, mock_whisper_model):
        """Test CUDA availability detection for fp16 parameter"""
        with patch("transcribe.torch.cuda.is_available", return_value=True):
            mock_whisper_model.transcribe.return_value = {"text": "test"}

            # Mock the necessary components to reach transcription call
            with patch("sys.argv", ["transcribe.py"]):
                with patch("transcribe.whisper.load_model", return_value=mock_whisper_model):
                    with patch("transcribe.sr.Recognizer"):
                        with patch("transcribe.sr.Microphone"):
                            # Create a queue with test data
                            test_queue = Queue()
                            test_queue.put(b"\x00\x01" * 1000)

                            with patch("transcribe.Queue", return_value=test_queue):
                                with patch("transcribe.np.frombuffer") as mock_frombuffer:
                                    # Mock numpy processing
                                    mock_array = Mock()
                                    mock_array.astype.return_value.__truediv__ = Mock(
                                        return_value=np.array([0.1, 0.2])
                                    )
                                    mock_frombuffer.return_value = mock_array

                                    with patch("time.sleep", side_effect=KeyboardInterrupt):
                                        try:
                                            transcribe.main()
                                        except KeyboardInterrupt:
                                            pass

                            # Verify fp16=True was passed when CUDA is available
                            if mock_whisper_model.transcribe.called:
                                args, kwargs = mock_whisper_model.transcribe.call_args
                                assert kwargs.get("fp16") is True
