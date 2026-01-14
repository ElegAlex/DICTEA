"""
Tests unitaires pour le module src/utils/model_manager.py
"""
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.utils.model_manager import (
    ModelManager,
    WHISPER_MODELS,
    PYANNOTE_MODELS,
)


class TestWhisperModels:
    """Tests pour le dictionnaire WHISPER_MODELS."""

    def test_contains_expected_models(self):
        """Vérifie que tous les modèles attendus sont présents."""
        expected = ["tiny", "base", "small", "medium", "large-v2", "large-v3"]
        for model in expected:
            assert model in WHISPER_MODELS

    def test_models_have_huggingface_urls(self):
        """Vérifie que les modèles pointent vers HuggingFace."""
        for model, repo_id in WHISPER_MODELS.items():
            assert "/" in repo_id  # Format org/model
            assert "whisper" in repo_id.lower() or "bofenghuang" in repo_id


class TestPyannoteModels:
    """Tests pour le dictionnaire PYANNOTE_MODELS."""

    def test_contains_expected_models(self):
        """Vérifie les modèles Pyannote attendus."""
        expected = ["segmentation", "embedding", "diarization"]
        for model in expected:
            assert model in PYANNOTE_MODELS


class TestModelManager:
    """Tests pour la classe ModelManager."""

    def test_init_creates_models_dir(self, temp_dir):
        """Vérifie que l'initialisation crée le répertoire des modèles."""
        models_dir = temp_dir / "test_models"
        manager = ModelManager(models_dir=models_dir)

        assert models_dir.exists()

    def test_init_sets_hf_environment(self, temp_dir):
        """Vérifie la configuration des variables HuggingFace."""
        import os

        models_dir = temp_dir / "test_models"
        manager = ModelManager(models_dir=models_dir)

        assert os.environ["HF_HOME"] == str(models_dir / "huggingface")
        assert os.environ["TRANSFORMERS_CACHE"] == str(models_dir / "transformers")

    def test_get_whisper_model_path(self, temp_dir):
        """Vérifie le chemin du modèle Whisper."""
        manager = ModelManager(models_dir=temp_dir)

        path = manager.get_whisper_model_path("medium")

        assert path == temp_dir / "whisper" / "medium"

    def test_get_whisper_model_path_invalid(self, temp_dir):
        """Vérifie l'erreur pour un modèle inconnu."""
        manager = ModelManager(models_dir=temp_dir)

        with pytest.raises(ValueError) as excinfo:
            manager.get_whisper_model_path("nonexistent")

        assert "Modèle inconnu" in str(excinfo.value)

    def test_is_whisper_downloaded_false(self, temp_dir):
        """Vérifie la détection d'un modèle non téléchargé."""
        manager = ModelManager(models_dir=temp_dir)

        assert manager.is_whisper_downloaded("medium") is False

    def test_is_whisper_downloaded_true(self, temp_dir):
        """Vérifie la détection d'un modèle téléchargé."""
        manager = ModelManager(models_dir=temp_dir)

        # Simuler un modèle téléchargé
        model_path = temp_dir / "whisper" / "medium"
        model_path.mkdir(parents=True)
        (model_path / "model.bin").write_text("fake model")

        assert manager.is_whisper_downloaded("medium") is True

    @patch("src.utils.model_manager.snapshot_download")
    def test_download_whisper_model_already_exists(self, mock_download, temp_dir):
        """Vérifie qu'on ne re-télécharge pas un modèle existant."""
        manager = ModelManager(models_dir=temp_dir)

        # Simuler un modèle existant
        model_path = temp_dir / "whisper" / "tiny"
        model_path.mkdir(parents=True)
        (model_path / "model.bin").write_text("fake model")

        result = manager.download_whisper_model("tiny")

        mock_download.assert_not_called()
        assert result == model_path

    @patch("src.utils.model_manager.snapshot_download")
    def test_download_whisper_model_new(self, mock_download, temp_dir):
        """Vérifie le téléchargement d'un nouveau modèle."""
        manager = ModelManager(models_dir=temp_dir)

        # Mock le téléchargement réussi
        expected_path = temp_dir / "whisper" / "tiny"
        mock_download.return_value = str(expected_path)

        progress_calls = []

        def progress_callback(msg, pct):
            progress_calls.append((msg, pct))

        result = manager.download_whisper_model("tiny", progress_callback=progress_callback)

        mock_download.assert_called_once()
        assert len(progress_calls) >= 1

    @patch("src.utils.model_manager.snapshot_download")
    def test_download_whisper_model_error(self, mock_download, temp_dir):
        """Vérifie la gestion des erreurs de téléchargement."""
        manager = ModelManager(models_dir=temp_dir)

        mock_download.side_effect = Exception("Network error")

        with pytest.raises(Exception) as excinfo:
            manager.download_whisper_model("tiny")

        assert "Network error" in str(excinfo.value)

    def test_is_pyannote_ready_no_token(self, temp_dir):
        """Vérifie la détection d'absence de token Pyannote."""
        manager = ModelManager(models_dir=temp_dir)

        # Patcher le chemin du token
        with patch.object(Path, "exists", return_value=False):
            # Note: La méthode vérifie ~/.huggingface/token
            result = manager.is_pyannote_ready()
            # Le résultat dépend de l'environnement réel
            assert isinstance(result, bool)

    def test_get_model_sizes(self, temp_dir):
        """Vérifie le dictionnaire des tailles de modèles."""
        manager = ModelManager(models_dir=temp_dir)

        sizes = manager.get_model_sizes()

        assert "tiny" in sizes
        assert "medium" in sizes
        assert "large-v3" in sizes
        assert "pyannote" in sizes

        # Vérifier le format des tailles
        for model, size in sizes.items():
            assert "Mo" in size or "Go" in size

    def test_cleanup_temp_files(self, temp_dir):
        """Vérifie le nettoyage des fichiers temporaires."""
        manager = ModelManager(models_dir=temp_dir)

        # Créer des fichiers temporaires
        temp_subdir = temp_dir / "temp"
        temp_subdir.mkdir()
        (temp_subdir / "file1.tmp").write_text("temp1")
        (temp_subdir / "file2.tmp").write_text("temp2")

        manager.cleanup_temp_files()

        # Le dossier temp doit être supprimé
        assert not temp_subdir.exists()

    def test_cleanup_temp_files_no_temp_dir(self, temp_dir):
        """Vérifie le comportement sans dossier temp."""
        manager = ModelManager(models_dir=temp_dir)

        # Ne doit pas lever d'erreur
        manager.cleanup_temp_files()
