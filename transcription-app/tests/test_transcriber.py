"""
Tests unitaires pour le module src/core/transcriber.py
"""
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.core.transcriber import (
    TranscriptionSegment,
    TranscriptionResult,
    Transcriber,
    _format_time,
    _format_srt_time,
)


class TestFormatTime:
    """Tests pour la fonction _format_time."""

    def test_format_seconds(self):
        """Vérifie le formatage des secondes."""
        assert _format_time(0) == "00:00"
        assert _format_time(30) == "00:30"
        assert _format_time(59) == "00:59"

    def test_format_minutes(self):
        """Vérifie le formatage des minutes."""
        assert _format_time(60) == "01:00"
        assert _format_time(90) == "01:30"
        assert _format_time(125) == "02:05"

    def test_format_hours(self):
        """Vérifie le formatage au-delà d'une heure."""
        assert _format_time(3600) == "60:00"
        assert _format_time(3661) == "61:01"


class TestFormatSrtTime:
    """Tests pour la fonction _format_srt_time."""

    def test_format_basic(self):
        """Vérifie le formatage SRT de base."""
        assert _format_srt_time(0) == "00:00:00,000"
        assert _format_srt_time(1.5) == "00:00:01,500"

    def test_format_with_milliseconds(self):
        """Vérifie le formatage avec millisecondes."""
        assert _format_srt_time(1.234) == "00:00:01,234"
        assert _format_srt_time(10.567) == "00:00:10,567"

    def test_format_minutes_and_hours(self):
        """Vérifie le formatage avec minutes et heures."""
        assert _format_srt_time(61.5) == "00:01:01,500"
        assert _format_srt_time(3661.123) == "01:01:01,123"


class TestTranscriptionSegment:
    """Tests pour la dataclass TranscriptionSegment."""

    def test_creation(self):
        """Vérifie la création d'un segment."""
        segment = TranscriptionSegment(
            start=0.0,
            end=2.5,
            text="Bonjour le monde",
        )

        assert segment.start == 0.0
        assert segment.end == 2.5
        assert segment.text == "Bonjour le monde"
        assert segment.words is None
        assert segment.speaker is None
        assert segment.confidence == 0.0

    def test_creation_with_all_fields(self):
        """Vérifie la création avec tous les champs."""
        words = [{"word": "Bonjour", "start": 0.0, "end": 0.5}]
        segment = TranscriptionSegment(
            start=0.0,
            end=2.5,
            text="Bonjour",
            words=words,
            speaker="SPEAKER_00",
            confidence=0.95,
        )

        assert segment.words == words
        assert segment.speaker == "SPEAKER_00"
        assert segment.confidence == 0.95


class TestTranscriptionResult:
    """Tests pour la classe TranscriptionResult."""

    @pytest.fixture
    def sample_result(self):
        """Crée un résultat de transcription de test."""
        return TranscriptionResult(
            segments=[
                TranscriptionSegment(
                    start=0.0,
                    end=2.0,
                    text="Bonjour, comment allez-vous?",
                    speaker="SPEAKER_00",
                ),
                TranscriptionSegment(
                    start=2.5,
                    end=5.0,
                    text="Je vais très bien, merci.",
                    speaker="SPEAKER_01",
                ),
            ],
            language="fr",
            language_probability=0.98,
            duration=5.0,
        )

    def test_to_text_basic(self, sample_result):
        """Vérifie la conversion en texte simple."""
        text = sample_result.to_text(include_timestamps=False, include_speakers=False)

        assert "Bonjour, comment allez-vous?" in text
        assert "Je vais très bien, merci." in text
        assert "SPEAKER" not in text

    def test_to_text_with_speakers(self, sample_result):
        """Vérifie la conversion avec locuteurs."""
        text = sample_result.to_text(include_timestamps=False, include_speakers=True)

        assert "[SPEAKER_00]" in text
        assert "[SPEAKER_01]" in text

    def test_to_text_with_timestamps(self, sample_result):
        """Vérifie la conversion avec timestamps."""
        text = sample_result.to_text(include_timestamps=True, include_speakers=False)

        assert "[00:00 - 00:02]" in text
        assert "[00:02 - 00:05]" in text

    def test_to_text_with_all(self, sample_result):
        """Vérifie la conversion avec tout."""
        text = sample_result.to_text(include_timestamps=True, include_speakers=True)

        assert "[SPEAKER_00]" in text
        assert "[00:00 - 00:02]" in text

    def test_to_srt(self, sample_result):
        """Vérifie l'export SRT."""
        srt = sample_result.to_srt()

        # Vérifier la structure SRT
        lines = srt.strip().split("\n")

        # Premier sous-titre
        assert lines[0] == "1"
        assert "-->" in lines[1]
        assert "Bonjour" in lines[2]

        # Deuxième sous-titre
        assert "2" in srt
        assert "Je vais" in srt

    def test_to_srt_with_speakers(self, sample_result):
        """Vérifie l'export SRT inclut les locuteurs."""
        srt = sample_result.to_srt()

        assert "[SPEAKER_00]" in srt
        assert "[SPEAKER_01]" in srt

    def test_to_srt_format(self, sample_result):
        """Vérifie le format des timestamps SRT."""
        srt = sample_result.to_srt()

        # Format: HH:MM:SS,mmm --> HH:MM:SS,mmm
        assert "00:00:00,000 --> 00:00:02,000" in srt


class TestTranscriber:
    """Tests pour la classe Transcriber."""

    @pytest.fixture
    def mock_transcriber_deps(self, mock_config, temp_dir):
        """Configure les mocks pour Transcriber."""
        mock_config.paths.models = temp_dir / "models"
        mock_config.paths.models.mkdir(parents=True, exist_ok=True)

        with patch("src.core.transcriber.get_config", return_value=mock_config):
            with patch("src.core.transcriber.ModelManager") as mock_mm:
                mock_mm_instance = MagicMock()
                mock_mm.return_value = mock_mm_instance
                yield mock_config, mock_mm_instance

    def test_init_default(self, mock_transcriber_deps):
        """Vérifie l'initialisation par défaut."""
        mock_config, mock_mm = mock_transcriber_deps

        transcriber = Transcriber()

        assert transcriber.model_name == mock_config.transcription.model
        assert transcriber.model is None

    def test_init_custom_model(self, mock_transcriber_deps):
        """Vérifie l'initialisation avec modèle personnalisé."""
        mock_config, mock_mm = mock_transcriber_deps

        transcriber = Transcriber(model_name="large-v3")

        assert transcriber.model_name == "large-v3"

    @patch("src.core.transcriber.WhisperModel")
    def test_load_model(self, mock_whisper_class, mock_transcriber_deps, temp_dir):
        """Vérifie le chargement du modèle."""
        mock_config, mock_mm = mock_transcriber_deps

        # Simuler le chemin du modèle
        model_path = temp_dir / "models" / "whisper" / "tiny"
        model_path.mkdir(parents=True, exist_ok=True)
        mock_mm.download_whisper_model.return_value = model_path

        transcriber = Transcriber(model_name="tiny")
        transcriber.load_model()

        mock_whisper_class.assert_called_once()
        assert transcriber.model is not None

    @patch("src.core.transcriber.WhisperModel")
    def test_load_model_already_loaded(self, mock_whisper_class, mock_transcriber_deps):
        """Vérifie qu'on ne recharge pas un modèle déjà chargé."""
        mock_config, mock_mm = mock_transcriber_deps

        transcriber = Transcriber()
        transcriber.model = MagicMock()  # Simuler modèle déjà chargé

        transcriber.load_model()

        mock_whisper_class.assert_not_called()

    def test_unload_model(self, mock_transcriber_deps):
        """Vérifie le déchargement du modèle."""
        mock_config, mock_mm = mock_transcriber_deps

        transcriber = Transcriber()
        transcriber.model = MagicMock()

        transcriber.unload_model()

        assert transcriber.model is None

    def test_unload_model_not_loaded(self, mock_transcriber_deps):
        """Vérifie le déchargement quand pas de modèle."""
        mock_config, mock_mm = mock_transcriber_deps

        transcriber = Transcriber()

        # Ne doit pas lever d'erreur
        transcriber.unload_model()

    @patch("src.core.transcriber.WhisperModel")
    def test_transcribe(
        self, mock_whisper_class, mock_transcriber_deps, mock_whisper_model, sample_audio_file
    ):
        """Vérifie la transcription."""
        mock_config, mock_mm = mock_transcriber_deps
        mock_whisper_class.return_value = mock_whisper_model

        transcriber = Transcriber()
        transcriber.model = mock_whisper_model

        result = transcriber.transcribe(sample_audio_file)

        assert isinstance(result, TranscriptionResult)
        assert len(result.segments) == 1
        assert result.language == "fr"

    @patch("src.core.transcriber.WhisperModel")
    def test_transcribe_auto_load(
        self, mock_whisper_class, mock_transcriber_deps, mock_whisper_model, sample_audio_file, temp_dir
    ):
        """Vérifie le chargement automatique du modèle."""
        mock_config, mock_mm = mock_transcriber_deps
        mock_whisper_class.return_value = mock_whisper_model

        model_path = temp_dir / "models" / "whisper" / "tiny"
        model_path.mkdir(parents=True, exist_ok=True)
        mock_mm.download_whisper_model.return_value = model_path

        transcriber = Transcriber(model_name="tiny")
        result = transcriber.transcribe(sample_audio_file)

        assert isinstance(result, TranscriptionResult)

    @patch("src.core.transcriber.WhisperModel")
    def test_transcribe_with_language(
        self, mock_whisper_class, mock_transcriber_deps, mock_whisper_model, sample_audio_file
    ):
        """Vérifie la transcription avec langue spécifiée."""
        mock_config, mock_mm = mock_transcriber_deps

        transcriber = Transcriber()
        transcriber.model = mock_whisper_model

        result = transcriber.transcribe(sample_audio_file, language="en")

        # Vérifier que la langue est passée au modèle
        mock_whisper_model.transcribe.assert_called()
        call_kwargs = mock_whisper_model.transcribe.call_args[1]
        assert call_kwargs.get("language") == "en"

    @patch("src.core.transcriber.WhisperModel")
    def test_transcribe_auto_language(
        self, mock_whisper_class, mock_transcriber_deps, mock_whisper_model, sample_audio_file
    ):
        """Vérifie la détection automatique de langue."""
        mock_config, mock_mm = mock_transcriber_deps

        transcriber = Transcriber()
        transcriber.model = mock_whisper_model

        result = transcriber.transcribe(sample_audio_file, language="auto")

        call_kwargs = mock_whisper_model.transcribe.call_args[1]
        assert call_kwargs.get("language") is None  # None = auto-detect

    @patch("src.core.transcriber.WhisperModel")
    def test_transcribe_with_progress(
        self, mock_whisper_class, mock_transcriber_deps, mock_whisper_model, sample_audio_file
    ):
        """Vérifie le callback de progression."""
        mock_config, mock_mm = mock_transcriber_deps

        progress_calls = []

        def progress_callback(idx, text):
            progress_calls.append((idx, text))

        transcriber = Transcriber()
        transcriber.model = mock_whisper_model

        result = transcriber.transcribe(
            sample_audio_file, progress_callback=progress_callback
        )

        assert len(progress_calls) == 1
        assert progress_calls[0][0] == 0

    @patch("src.core.transcriber.WhisperModel")
    def test_transcribe_stream(
        self, mock_whisper_class, mock_transcriber_deps, mock_whisper_model, sample_audio_file
    ):
        """Vérifie la transcription en streaming."""
        mock_config, mock_mm = mock_transcriber_deps

        transcriber = Transcriber()
        transcriber.model = mock_whisper_model

        segments = list(transcriber.transcribe_stream(sample_audio_file))

        assert len(segments) == 1
        assert isinstance(segments[0], TranscriptionSegment)
