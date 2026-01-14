"""
Tests unitaires pour le module src/core/audio_processor.py
"""
import pytest
import numpy as np
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.core.audio_processor import (
    AudioDevice,
    AudioRecorder,
    AudioProcessor,
)


class TestAudioDevice:
    """Tests pour la dataclass AudioDevice."""

    def test_creation(self):
        """Vérifie la création d'un AudioDevice."""
        device = AudioDevice(
            index=0,
            name="Test Microphone",
            channels=2,
            sample_rate=44100.0,
            is_input=True,
        )

        assert device.index == 0
        assert device.name == "Test Microphone"
        assert device.channels == 2
        assert device.sample_rate == 44100.0
        assert device.is_input is True


class TestAudioRecorder:
    """Tests pour la classe AudioRecorder."""

    def test_init_default_config(self, mock_config):
        """Vérifie l'initialisation avec la configuration par défaut."""
        with patch("src.core.audio_processor.get_config", return_value=mock_config):
            recorder = AudioRecorder()

            assert recorder.config.sample_rate == 16000
            assert recorder.config.channels == 1
            assert recorder._recording is False

    def test_init_custom_config(self):
        """Vérifie l'initialisation avec une configuration personnalisée."""
        from src.utils.config import AudioConfig

        custom = AudioConfig(sample_rate=48000, channels=2)
        recorder = AudioRecorder(config=custom)

        assert recorder.config.sample_rate == 48000
        assert recorder.config.channels == 2

    @patch("src.core.audio_processor.sd.query_devices")
    def test_list_input_devices(self, mock_query):
        """Vérifie la liste des périphériques d'entrée."""
        mock_query.return_value = [
            {
                "name": "Built-in Microphone",
                "max_input_channels": 2,
                "max_output_channels": 0,
                "default_samplerate": 44100.0,
            },
            {
                "name": "USB Headset",
                "max_input_channels": 1,
                "max_output_channels": 2,
                "default_samplerate": 48000.0,
            },
            {
                "name": "Speakers",
                "max_input_channels": 0,
                "max_output_channels": 2,
                "default_samplerate": 44100.0,
            },
        ]

        devices = AudioRecorder.list_input_devices()

        # Seuls les périphériques avec input_channels > 0
        assert len(devices) == 2
        assert devices[0].name == "Built-in Microphone"
        assert devices[1].name == "USB Headset"

    @patch("src.core.audio_processor.sd.default")
    @patch("src.core.audio_processor.sd.query_devices")
    def test_get_default_input_device(self, mock_query, mock_default):
        """Vérifie la récupération du périphérique par défaut."""
        mock_default.device = [0, 1]
        mock_query.return_value = {
            "name": "Default Mic",
            "max_input_channels": 2,
            "default_samplerate": 44100.0,
        }

        device = AudioRecorder.get_default_input_device()

        assert device is not None
        assert device.name == "Default Mic"
        assert device.index == 0

    def test_is_recording_property(self, mock_config):
        """Vérifie la propriété is_recording."""
        with patch("src.core.audio_processor.get_config", return_value=mock_config):
            recorder = AudioRecorder()

            assert recorder.is_recording is False
            recorder._recording = True
            assert recorder.is_recording is True

    @patch("src.core.audio_processor.sd.InputStream")
    def test_start_recording(self, mock_stream_class, mock_config):
        """Vérifie le démarrage de l'enregistrement."""
        mock_stream = MagicMock()
        mock_stream_class.return_value = mock_stream

        with patch("src.core.audio_processor.get_config", return_value=mock_config):
            recorder = AudioRecorder()
            recorder.start_recording()

            assert recorder._recording is True
            mock_stream.start.assert_called_once()

    @patch("src.core.audio_processor.sd.InputStream")
    def test_start_recording_while_recording(self, mock_stream_class, mock_config):
        """Vérifie qu'on ne peut pas démarrer deux enregistrements."""
        with patch("src.core.audio_processor.get_config", return_value=mock_config):
            recorder = AudioRecorder()
            recorder._recording = True

            recorder.start_recording()

            # Ne doit pas créer de nouveau stream
            mock_stream_class.assert_not_called()

    def test_stop_recording_not_recording(self, mock_config):
        """Vérifie l'arrêt quand pas d'enregistrement."""
        with patch("src.core.audio_processor.get_config", return_value=mock_config):
            recorder = AudioRecorder()

            result = recorder.stop_recording()

            assert result is None

    def test_stop_recording_returns_audio(self, mock_config):
        """Vérifie que l'arrêt retourne les données audio."""
        with patch("src.core.audio_processor.get_config", return_value=mock_config):
            recorder = AudioRecorder()
            recorder._recording = True

            # Simuler des données enregistrées
            recorder._recorded_frames = [
                np.zeros((1600,), dtype=np.float32),
                np.zeros((1600,), dtype=np.float32),
            ]

            result = recorder.stop_recording()

            assert result is not None
            assert len(result) == 3200

    def test_save_recording(self, mock_config, temp_dir, sample_audio_data):
        """Vérifie la sauvegarde de l'enregistrement."""
        audio, sample_rate = sample_audio_data

        with patch("src.core.audio_processor.get_config", return_value=mock_config):
            recorder = AudioRecorder()
            output_path = temp_dir / "recording.wav"

            result = recorder.save_recording(audio, output_path)

            assert result.exists()
            assert result.suffix == ".wav"

    def test_save_recording_adds_extension(self, mock_config, temp_dir, sample_audio_data):
        """Vérifie que l'extension est ajoutée si manquante."""
        audio, sample_rate = sample_audio_data

        with patch("src.core.audio_processor.get_config", return_value=mock_config):
            recorder = AudioRecorder()
            output_path = temp_dir / "recording"  # Sans extension

            result = recorder.save_recording(audio, output_path)

            assert result.suffix == ".wav"


class TestAudioProcessor:
    """Tests pour la classe AudioProcessor."""

    def test_supported_formats(self):
        """Vérifie les formats audio supportés."""
        expected = {".wav", ".mp3", ".m4a", ".flac", ".ogg", ".wma", ".aac"}
        assert AudioProcessor.SUPPORTED_FORMATS == expected

    def test_whisper_sample_rate(self):
        """Vérifie le sample rate pour Whisper."""
        assert AudioProcessor.WHISPER_SAMPLE_RATE == 16000

    def test_is_supported_valid_format(self):
        """Vérifie la détection des formats supportés."""
        assert AudioProcessor.is_supported(Path("test.wav")) is True
        assert AudioProcessor.is_supported(Path("test.mp3")) is True
        assert AudioProcessor.is_supported(Path("test.m4a")) is True
        assert AudioProcessor.is_supported(Path("test.flac")) is True

    def test_is_supported_invalid_format(self):
        """Vérifie la détection des formats non supportés."""
        assert AudioProcessor.is_supported(Path("test.txt")) is False
        assert AudioProcessor.is_supported(Path("test.doc")) is False
        assert AudioProcessor.is_supported(Path("test.xyz")) is False

    def test_is_supported_case_insensitive(self):
        """Vérifie que la détection est insensible à la casse."""
        assert AudioProcessor.is_supported(Path("test.WAV")) is True
        assert AudioProcessor.is_supported(Path("test.Mp3")) is True

    def test_get_audio_info(self, mock_config, sample_audio_file):
        """Vérifie la récupération des informations audio."""
        with patch("src.core.audio_processor.get_config", return_value=mock_config):
            processor = AudioProcessor()
            info = processor.get_audio_info(sample_audio_file)

            assert "duration" in info
            assert "sample_rate" in info
            assert "channels" in info
            assert "format" in info
            assert "size_mb" in info

            assert info["sample_rate"] == 16000
            assert info["channels"] == 1
            assert info["format"] == "wav"

    def test_get_audio_info_invalid_file(self, mock_config, temp_dir):
        """Vérifie l'erreur pour un fichier invalide."""
        with patch("src.core.audio_processor.get_config", return_value=mock_config):
            processor = AudioProcessor()
            invalid_path = temp_dir / "nonexistent.wav"

            with pytest.raises(Exception):
                processor.get_audio_info(invalid_path)

    def test_convert_for_whisper(self, mock_config, sample_audio_file, temp_dir):
        """Vérifie la conversion au format Whisper."""
        mock_config.paths.temp = temp_dir / "temp"
        mock_config.paths.temp.mkdir(parents=True, exist_ok=True)

        with patch("src.core.audio_processor.get_config", return_value=mock_config):
            processor = AudioProcessor()
            output_path = temp_dir / "converted.wav"

            result = processor.convert_for_whisper(sample_audio_file, output_path)

            assert result.exists()
            assert result == output_path

    def test_convert_for_whisper_auto_output(self, mock_config, sample_audio_file, temp_dir):
        """Vérifie la conversion avec chemin de sortie automatique."""
        mock_config.paths.temp = temp_dir / "temp"
        mock_config.paths.temp.mkdir(parents=True, exist_ok=True)

        with patch("src.core.audio_processor.get_config", return_value=mock_config):
            processor = AudioProcessor()

            result = processor.convert_for_whisper(sample_audio_file)

            assert result.exists()
            assert "_converted" in result.name

    def test_convert_for_whisper_unsupported_format(self, mock_config, temp_dir):
        """Vérifie l'erreur pour un format non supporté."""
        with patch("src.core.audio_processor.get_config", return_value=mock_config):
            processor = AudioProcessor()
            invalid_file = temp_dir / "test.xyz"
            invalid_file.write_text("not audio")

            with pytest.raises(ValueError) as excinfo:
                processor.convert_for_whisper(invalid_file)

            assert "Format non supporté" in str(excinfo.value)

    def test_convert_for_whisper_with_progress(self, mock_config, sample_audio_file, temp_dir):
        """Vérifie le callback de progression."""
        mock_config.paths.temp = temp_dir / "temp"
        mock_config.paths.temp.mkdir(parents=True, exist_ok=True)

        progress_calls = []

        def progress_callback(msg, pct):
            progress_calls.append((msg, pct))

        with patch("src.core.audio_processor.get_config", return_value=mock_config):
            processor = AudioProcessor()
            output_path = temp_dir / "converted.wav"

            processor.convert_for_whisper(
                sample_audio_file, output_path, progress_callback=progress_callback
            )

            assert len(progress_calls) >= 2
            assert progress_calls[-1][1] == 100.0

    def test_split_audio(self, mock_config, longer_audio_file, temp_dir):
        """Vérifie le découpage audio en chunks."""
        mock_config.paths.temp = temp_dir / "temp"

        with patch("src.core.audio_processor.get_config", return_value=mock_config):
            processor = AudioProcessor()

            # Découper en chunks de 2 secondes (pour le test)
            # Note: chunk_minutes=1/30 = 2 secondes
            chunks = processor.split_audio(
                longer_audio_file,
                chunk_minutes=1,  # 1 minute par chunk (le fichier fait 5s)
                output_dir=temp_dir / "chunks",
            )

            # Avec 5s d'audio et chunks de 60s, on devrait avoir 1 chunk
            assert len(chunks) >= 1
            assert all(c.exists() for c in chunks)

    def test_cleanup_temp_files(self, mock_config, temp_dir):
        """Vérifie le nettoyage des fichiers temporaires."""
        mock_config.paths.temp = temp_dir / "temp"
        mock_config.paths.temp.mkdir(parents=True, exist_ok=True)

        # Créer des fichiers temporaires
        (mock_config.paths.temp / "test1.wav").write_text("fake audio")
        (mock_config.paths.temp / "test2.tmp").write_text("temp data")
        (mock_config.paths.temp / "keep.txt").write_text("keep this")

        with patch("src.core.audio_processor.get_config", return_value=mock_config):
            processor = AudioProcessor()
            count = processor.cleanup_temp_files()

            assert count == 2  # .wav et .tmp supprimés
            assert not (mock_config.paths.temp / "test1.wav").exists()
            assert not (mock_config.paths.temp / "test2.tmp").exists()
            assert (mock_config.paths.temp / "keep.txt").exists()

    def test_cleanup_temp_files_no_temp_dir(self, mock_config, temp_dir):
        """Vérifie le comportement sans dossier temp."""
        mock_config.paths.temp = temp_dir / "nonexistent_temp"

        with patch("src.core.audio_processor.get_config", return_value=mock_config):
            processor = AudioProcessor()
            count = processor.cleanup_temp_files()

            assert count == 0
