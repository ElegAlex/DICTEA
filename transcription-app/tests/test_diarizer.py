"""
Tests unitaires pour le module src/core/diarizer.py
"""
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.core.diarizer import (
    SpeakerSegment,
    DiarizationResult,
    Diarizer,
    assign_speakers_to_transcription,
)
from src.core.transcriber import TranscriptionResult, TranscriptionSegment


class TestSpeakerSegment:
    """Tests pour la dataclass SpeakerSegment."""

    def test_creation(self):
        """Vérifie la création d'un segment."""
        segment = SpeakerSegment(
            start=0.0,
            end=2.5,
            speaker="SPEAKER_00",
        )

        assert segment.start == 0.0
        assert segment.end == 2.5
        assert segment.speaker == "SPEAKER_00"


class TestDiarizationResult:
    """Tests pour la classe DiarizationResult."""

    @pytest.fixture
    def sample_diarization(self):
        """Crée un résultat de diarization de test."""
        return DiarizationResult(
            segments=[
                SpeakerSegment(start=0.0, end=3.0, speaker="SPEAKER_00"),
                SpeakerSegment(start=3.0, end=5.0, speaker="SPEAKER_01"),
                SpeakerSegment(start=5.0, end=8.0, speaker="SPEAKER_00"),
            ],
            num_speakers=2,
        )

    def test_get_speaker_at_beginning(self, sample_diarization):
        """Vérifie la récupération du locuteur au début."""
        speaker = sample_diarization.get_speaker_at(0.5)
        assert speaker == "SPEAKER_00"

    def test_get_speaker_at_middle(self, sample_diarization):
        """Vérifie la récupération du locuteur au milieu."""
        speaker = sample_diarization.get_speaker_at(4.0)
        assert speaker == "SPEAKER_01"

    def test_get_speaker_at_boundary(self, sample_diarization):
        """Vérifie la récupération du locuteur à une frontière."""
        speaker = sample_diarization.get_speaker_at(3.0)
        # 3.0 est inclus dans le segment de SPEAKER_00 (0-3)
        assert speaker == "SPEAKER_00"

    def test_get_speaker_at_no_speaker(self, sample_diarization):
        """Vérifie le comportement hors segments."""
        speaker = sample_diarization.get_speaker_at(10.0)
        assert speaker is None

    def test_get_speaker_for_range_single(self, sample_diarization):
        """Vérifie la récupération du locuteur pour une plage simple."""
        speaker = sample_diarization.get_speaker_for_range(0.5, 2.5)
        assert speaker == "SPEAKER_00"

    def test_get_speaker_for_range_overlap(self, sample_diarization):
        """Vérifie avec chevauchement de plusieurs locuteurs."""
        # Plage 2.5 - 4.0 chevauche SPEAKER_00 (2.5-3.0) et SPEAKER_01 (3.0-4.0)
        speaker = sample_diarization.get_speaker_for_range(2.5, 4.0)
        # SPEAKER_01 a plus de temps dans cette plage (1.0s vs 0.5s)
        assert speaker == "SPEAKER_01"

    def test_get_speaker_for_range_no_overlap(self, sample_diarization):
        """Vérifie le comportement sans chevauchement."""
        speaker = sample_diarization.get_speaker_for_range(10.0, 12.0)
        assert speaker is None

    def test_get_speaker_for_range_exact_match(self, sample_diarization):
        """Vérifie avec correspondance exacte."""
        speaker = sample_diarization.get_speaker_for_range(0.0, 3.0)
        assert speaker == "SPEAKER_00"


class TestDiarizer:
    """Tests pour la classe Diarizer."""

    @pytest.fixture
    def mock_diarizer_deps(self, mock_config):
        """Configure les mocks pour Diarizer."""
        with patch("src.core.diarizer.get_config", return_value=mock_config):
            yield mock_config

    def test_init_default(self, mock_diarizer_deps):
        """Vérifie l'initialisation par défaut."""
        diarizer = Diarizer()

        assert diarizer.pipeline is None
        assert diarizer.mode == "fast"  # mode de mock_config

    def test_mode_property(self, mock_diarizer_deps):
        """Vérifie la propriété mode."""
        diarizer = Diarizer()

        assert diarizer.mode == "fast"

    def test_mode_setter_valid(self, mock_diarizer_deps):
        """Vérifie le setter avec valeur valide."""
        diarizer = Diarizer()
        diarizer.mode = "quality"

        assert diarizer.mode == "quality"

    def test_mode_setter_invalid(self, mock_diarizer_deps):
        """Vérifie le setter avec valeur invalide."""
        diarizer = Diarizer()

        with pytest.raises(ValueError) as excinfo:
            diarizer.mode = "invalid"

        assert "quality" in str(excinfo.value) or "fast" in str(excinfo.value)

    def test_mode_change_unloads_pipeline(self, mock_diarizer_deps):
        """Vérifie que changer de mode décharge le pipeline."""
        diarizer = Diarizer()
        diarizer.pipeline = MagicMock()

        diarizer.mode = "quality"

        assert diarizer.pipeline is None

    def test_unload(self, mock_diarizer_deps):
        """Vérifie le déchargement."""
        diarizer = Diarizer()
        diarizer.pipeline = MagicMock()
        diarizer._embedder = MagicMock()
        diarizer._vad = MagicMock()

        diarizer.unload()

        assert diarizer.pipeline is None
        assert not hasattr(diarizer, "_embedder") or diarizer._embedder is None

    @patch("pyannote.audio.Pipeline")
    def test_load_pyannote(self, mock_pipeline, mock_diarizer_deps):
        """Vérifie le chargement de Pyannote."""
        mock_pipeline_instance = MagicMock()
        mock_pipeline.from_pretrained.return_value = mock_pipeline_instance

        diarizer = Diarizer()
        diarizer._mode = "quality"

        diarizer.load()

        mock_pipeline.from_pretrained.assert_called_once()
        assert diarizer.pipeline is not None

    @pytest.mark.slow
    def test_load_speechbrain_mock(self, mock_diarizer_deps):
        """Vérifie le chargement de SpeechBrain (mocké)."""
        pytest.importorskip("speechbrain")

        with patch("speechbrain.inference.VAD") as mock_vad:
            with patch("speechbrain.inference.SpeakerRecognition") as mock_sr:
                mock_sr.from_hparams.return_value = MagicMock()
                mock_vad.from_hparams.return_value = MagicMock()

                diarizer = Diarizer()
                diarizer._mode = "fast"

                diarizer._load_speechbrain()

                mock_sr.from_hparams.assert_called_once()
                mock_vad.from_hparams.assert_called_once()

    def test_diarize_loads_if_needed(self, mock_diarizer_deps, sample_audio_file):
        """Vérifie que diarize charge le pipeline si nécessaire."""
        diarizer = Diarizer()

        with patch.object(diarizer, "load") as mock_load:
            with patch.object(diarizer, "_diarize_speechbrain") as mock_diarize:
                mock_diarize.return_value = DiarizationResult(segments=[], num_speakers=0)

                diarizer.diarize(sample_audio_file)

                mock_load.assert_called_once()

    def test_diarize_skips_load_if_loaded(self, mock_diarizer_deps, sample_audio_file):
        """Vérifie que diarize ne recharge pas si déjà chargé."""
        diarizer = Diarizer()
        diarizer.pipeline = MagicMock()
        diarizer._mode = "fast"

        with patch.object(diarizer, "load") as mock_load:
            with patch.object(diarizer, "_diarize_speechbrain") as mock_diarize:
                mock_diarize.return_value = DiarizationResult(segments=[], num_speakers=0)

                diarizer.diarize(sample_audio_file)

                mock_load.assert_not_called()

    def test_diarize_converts_zero_speakers(self, mock_diarizer_deps, sample_audio_file):
        """Vérifie la conversion de 0 en None pour auto-detection."""
        diarizer = Diarizer()
        diarizer.pipeline = MagicMock()
        diarizer._mode = "quality"

        with patch.object(diarizer, "_diarize_pyannote") as mock_diarize:
            mock_diarize.return_value = DiarizationResult(segments=[], num_speakers=0)

            diarizer.diarize(sample_audio_file, min_speakers=0, max_speakers=0)

            call_args = mock_diarize.call_args
            assert call_args[0][1] is None  # min_speakers
            assert call_args[0][2] is None  # max_speakers

    def test_diarize_pyannote(self, mock_diarizer_deps, sample_audio_file):
        """Vérifie la diarization Pyannote."""
        diarizer = Diarizer()
        diarizer._mode = "quality"

        # Mock du pipeline Pyannote
        mock_pipeline = MagicMock()

        # Créer un mock pour itertracks
        mock_turn1 = MagicMock()
        mock_turn1.start = 0.0
        mock_turn1.end = 2.0

        mock_turn2 = MagicMock()
        mock_turn2.start = 2.0
        mock_turn2.end = 4.0

        mock_pipeline.return_value.itertracks.return_value = [
            (mock_turn1, None, "SPEAKER_00"),
            (mock_turn2, None, "SPEAKER_01"),
        ]

        mock_pipeline.return_value = MagicMock()
        mock_pipeline.return_value.itertracks.return_value = [
            (mock_turn1, None, "SPEAKER_00"),
            (mock_turn2, None, "SPEAKER_01"),
        ]

        diarizer.pipeline = mock_pipeline.return_value

        result = diarizer._diarize_pyannote(
            sample_audio_file, min_speakers=None, max_speakers=None, progress_callback=None
        )

        assert isinstance(result, DiarizationResult)


class TestAssignSpeakersToTranscription:
    """Tests pour la fonction assign_speakers_to_transcription."""

    def test_assign_basic(self, mock_transcription_result, mock_diarization_result):
        """Vérifie l'assignation basique des locuteurs."""
        result = assign_speakers_to_transcription(
            mock_transcription_result, mock_diarization_result
        )

        assert result.segments[0].speaker == "SPEAKER_00"
        assert result.segments[1].speaker == "SPEAKER_01"

    def test_assign_no_modification_original(self):
        """Vérifie que les originaux sont modifiés (par référence)."""
        transcription = TranscriptionResult(
            segments=[
                TranscriptionSegment(start=0.0, end=1.0, text="Test"),
            ],
            language="fr",
            language_probability=0.9,
            duration=1.0,
        )

        diarization = DiarizationResult(
            segments=[
                SpeakerSegment(start=0.0, end=2.0, speaker="SPEAKER_00"),
            ],
            num_speakers=1,
        )

        result = assign_speakers_to_transcription(transcription, diarization)

        # Le résultat retourné est la même instance (modifiée)
        assert result is transcription
        assert result.segments[0].speaker == "SPEAKER_00"

    def test_assign_uses_range_first(self):
        """Vérifie que get_speaker_for_range est utilisé en priorité."""
        transcription = TranscriptionResult(
            segments=[
                TranscriptionSegment(start=0.0, end=3.0, text="Test"),
            ],
            language="fr",
            language_probability=0.9,
            duration=3.0,
        )

        diarization = DiarizationResult(
            segments=[
                SpeakerSegment(start=0.0, end=1.0, speaker="SPEAKER_00"),
                SpeakerSegment(start=1.0, end=3.0, speaker="SPEAKER_01"),
            ],
            num_speakers=2,
        )

        result = assign_speakers_to_transcription(transcription, diarization)

        # SPEAKER_01 a plus de temps (2s vs 1s)
        assert result.segments[0].speaker == "SPEAKER_01"

    def test_assign_falls_back_to_midpoint(self):
        """Vérifie le fallback sur le point médian."""
        transcription = TranscriptionResult(
            segments=[
                TranscriptionSegment(start=5.0, end=6.0, text="Test"),
            ],
            language="fr",
            language_probability=0.9,
            duration=6.0,
        )

        diarization = DiarizationResult(
            segments=[
                # Segment ne chevauche pas directement mais contient le midpoint
                SpeakerSegment(start=5.0, end=6.0, speaker="SPEAKER_00"),
            ],
            num_speakers=1,
        )

        result = assign_speakers_to_transcription(transcription, diarization)

        assert result.segments[0].speaker == "SPEAKER_00"

    def test_assign_no_speaker_found(self):
        """Vérifie le comportement quand aucun locuteur n'est trouvé."""
        transcription = TranscriptionResult(
            segments=[
                TranscriptionSegment(start=10.0, end=11.0, text="Test"),
            ],
            language="fr",
            language_probability=0.9,
            duration=11.0,
        )

        diarization = DiarizationResult(
            segments=[
                SpeakerSegment(start=0.0, end=2.0, speaker="SPEAKER_00"),
            ],
            num_speakers=1,
        )

        result = assign_speakers_to_transcription(transcription, diarization)

        # Pas de locuteur trouvé
        assert result.segments[0].speaker is None
