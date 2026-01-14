"""
Fenêtre principale de l'application de transcription.
"""
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QProgressBar,
    QFileDialog, QComboBox, QSpinBox, QGroupBox,
    QStatusBar, QMessageBox, QCheckBox, QFrame,
)
from PySide6.QtCore import QTimer
from PySide6.QtGui import QFont

from ..core.transcriber import Transcriber, TranscriptionResult
from ..core.diarizer import Diarizer
from ..core.audio_processor import AudioRecorder, AudioProcessor
from ..utils.config import get_config
from .workers import TranscriptionWorker, FullPipelineWorker, WorkerThread
from .batch_dialog import BatchDialog
from .audio_player import AudioPlayerWidget

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Fenêtre principale de l'application."""

    def __init__(self):
        super().__init__()

        self.config = get_config()
        self.transcriber = Transcriber()
        self.diarizer = Diarizer()
        self.recorder = AudioRecorder()
        self.processor = AudioProcessor()

        self._current_worker: Optional[WorkerThread] = None
        self._recording_timer: Optional[QTimer] = None
        self._current_result: Optional[TranscriptionResult] = None
        self._audio_path: Optional[Path] = None
        self._recording_duration: float = 0.0

        self._setup_ui()
        self._connect_signals()

    # =========================================================================
    # Setup UI - Méthodes de construction de l'interface
    # =========================================================================

    def _setup_ui(self) -> None:
        """Configure l'interface utilisateur."""
        self.setWindowTitle("Transcription Audio")
        self.setMinimumSize(900, 700)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        layout.addWidget(self._create_source_section())
        layout.addWidget(self._create_options_section())
        layout.addWidget(self._create_transcribe_button())
        layout.addWidget(self._create_progress_section())
        layout.addWidget(self._create_result_section(), stretch=1)
        self._create_status_bar()

    def _create_source_section(self) -> QGroupBox:
        """Crée la section source audio."""
        group = QGroupBox("Source Audio")
        layout = QVBoxLayout(group)

        buttons_layout = QHBoxLayout()

        self.btn_import = QPushButton("📁 Importer un fichier")
        self.btn_import.setMinimumHeight(40)
        buttons_layout.addWidget(self.btn_import)

        self.btn_record = QPushButton("🎙️ Enregistrer")
        self.btn_record.setMinimumHeight(40)
        self.btn_record.setCheckable(True)
        buttons_layout.addWidget(self.btn_record)

        buttons_layout.addStretch()

        self.btn_batch = QPushButton("📦 Traitement par lots")
        self.btn_batch.setMinimumHeight(40)
        buttons_layout.addWidget(self.btn_batch)

        layout.addLayout(buttons_layout)

        self.lbl_source_info = QLabel("Aucun fichier sélectionné")
        self.lbl_source_info.setStyleSheet("color: #666; padding: 5px;")
        layout.addWidget(self.lbl_source_info)

        self.audio_player = AudioPlayerWidget()
        layout.addWidget(self.audio_player)

        return group

    def _create_options_section(self) -> QGroupBox:
        """Crée la section des options de transcription."""
        group = QGroupBox("Options")
        layout = QHBoxLayout(group)

        # Langue
        layout.addWidget(QLabel("Langue:"))
        self.combo_language = QComboBox()
        self.combo_language.addItems([
            "Français (fr)", "Anglais (en)", "Auto-détection (auto)"
        ])
        self.combo_language.setCurrentIndex(0)
        layout.addWidget(self.combo_language)

        layout.addSpacing(20)

        # Mode diarization
        layout.addWidget(QLabel("Diarization:"))
        self.combo_diarization = QComboBox()
        self.combo_diarization.addItems([
            "Qualité (Pyannote - lent)", "Rapide (SpeechBrain)"
        ])
        layout.addWidget(self.combo_diarization)

        layout.addSpacing(20)

        # Nombre de locuteurs
        layout.addWidget(QLabel("Locuteurs:"))
        self.spin_speakers = QSpinBox()
        self.spin_speakers.setRange(0, 20)
        self.spin_speakers.setValue(0)
        self.spin_speakers.setSpecialValueText("Auto")
        self.spin_speakers.setToolTip("0 = détection automatique")
        layout.addWidget(self.spin_speakers)

        layout.addStretch()

        # Checkbox diarization
        self.chk_diarization = QCheckBox("Identifier les locuteurs")
        self.chk_diarization.setChecked(True)
        layout.addWidget(self.chk_diarization)

        return group

    def _create_transcribe_button(self) -> QPushButton:
        """Crée le bouton principal de transcription."""
        self.btn_transcribe = QPushButton("▶️ Transcrire")
        self.btn_transcribe.setMinimumHeight(50)
        self.btn_transcribe.setEnabled(False)

        font = self.btn_transcribe.font()
        font.setPointSize(12)
        font.setBold(True)
        self.btn_transcribe.setFont(font)

        return self.btn_transcribe

    def _create_progress_section(self) -> QFrame:
        """Crée la section de progression."""
        frame = QFrame()
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)

        self.lbl_progress = QLabel("Prêt")
        layout.addWidget(self.lbl_progress)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        return frame

    def _create_result_section(self) -> QGroupBox:
        """Crée la section des résultats."""
        group = QGroupBox("Transcription")
        layout = QVBoxLayout(group)

        self.text_result = QTextEdit()
        self.text_result.setReadOnly(True)
        self.text_result.setPlaceholderText(
            "La transcription apparaîtra ici...\n\n"
            "Importez un fichier audio ou démarrez un enregistrement."
        )
        self.text_result.setFont(QFont("Consolas", 10))
        layout.addWidget(self.text_result)

        layout.addLayout(self._create_export_buttons())

        return group

    def _create_export_buttons(self) -> QHBoxLayout:
        """Crée les boutons d'export."""
        layout = QHBoxLayout()

        self.btn_copy = QPushButton("📋 Copier")
        self.btn_copy.setEnabled(False)
        layout.addWidget(self.btn_copy)

        self.btn_save_txt = QPushButton("💾 Sauvegarder TXT")
        self.btn_save_txt.setEnabled(False)
        layout.addWidget(self.btn_save_txt)

        self.btn_save_srt = QPushButton("💾 Sauvegarder SRT")
        self.btn_save_srt.setEnabled(False)
        layout.addWidget(self.btn_save_srt)

        layout.addStretch()

        self.btn_clear = QPushButton("🗑️ Effacer")
        layout.addWidget(self.btn_clear)

        return layout

    def _create_status_bar(self) -> None:
        """Crée la barre de statut."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Prêt")

    # =========================================================================
    # Connexion des signaux
    # =========================================================================

    def _connect_signals(self) -> None:
        """Connecte les signaux aux slots."""
        self.btn_import.clicked.connect(self._on_import_clicked)
        self.btn_record.clicked.connect(self._on_record_clicked)
        self.btn_batch.clicked.connect(self._on_batch_clicked)
        self.btn_transcribe.clicked.connect(self._on_transcribe_clicked)
        self.btn_copy.clicked.connect(self._on_copy_clicked)
        self.btn_save_txt.clicked.connect(self._on_save_txt_clicked)
        self.btn_save_srt.clicked.connect(self._on_save_srt_clicked)
        self.btn_clear.clicked.connect(self._on_clear_clicked)
        self.chk_diarization.toggled.connect(self._on_diarization_toggled)

    # =========================================================================
    # Handlers - Import de fichier
    # =========================================================================

    def _on_import_clicked(self) -> None:
        """Ouvre le dialogue d'import de fichier."""
        file_filter = "Audio (*.wav *.mp3 *.m4a *.flac *.ogg *.wma *.aac);;Tous (*.*)"
        path, _ = QFileDialog.getOpenFileName(
            self, "Importer un fichier audio", "", file_filter
        )
        if path:
            self._load_audio_file(Path(path))

    def _load_audio_file(self, path: Path) -> None:
        """Charge un fichier audio."""
        try:
            info = self.processor.get_audio_info(path)
            self._audio_path = path
            self._update_source_info_for_file(path, info)
            self.audio_player.load_audio(path)
            self.btn_transcribe.setEnabled(True)
            self.status_bar.showMessage(f"Fichier chargé: {path.name}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de charger le fichier:\n{e}")
            logger.error(f"Erreur chargement audio: {e}")

    def _update_source_info_for_file(self, path: Path, info: dict) -> None:
        """Met à jour l'affichage des infos du fichier source."""
        duration_str = self._format_duration(info['duration'])
        self.lbl_source_info.setText(
            f"📄 {path.name} | {duration_str} | "
            f"{info['sample_rate']}Hz | {info['size_mb']:.1f} Mo"
        )
        self.lbl_source_info.setStyleSheet("color: #2196F3; padding: 5px;")

    @staticmethod
    def _format_duration(seconds: float) -> str:
        """Formate une durée en secondes vers une chaîne lisible."""
        if seconds <= 60:
            return f"{seconds:.1f}s"
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins}min {secs}s"

    # =========================================================================
    # Handlers - Batch Processing
    # =========================================================================

    def _on_batch_clicked(self) -> None:
        """Ouvre le dialogue de traitement par lots."""
        dialog = BatchDialog(self.transcriber, self.diarizer, parent=self)
        dialog.exec()

    # =========================================================================
    # Handlers - Enregistrement
    # =========================================================================

    def _on_record_clicked(self) -> None:
        """Gère le clic sur le bouton d'enregistrement."""
        if self.recorder.is_recording:
            self._stop_recording()
        else:
            self._start_recording()

    def _start_recording(self) -> None:
        """Démarre l'enregistrement audio."""
        self.btn_record.setText("⏹️ Arrêter")
        self.btn_import.setEnabled(False)
        self.btn_transcribe.setEnabled(False)

        self._recording_duration = 0.0

        def update_duration(duration: float):
            self._recording_duration = duration

        self.recorder.start_recording(callback=update_duration)

        self._recording_timer = QTimer()
        self._recording_timer.timeout.connect(self._update_recording_display)
        self._recording_timer.start(100)

        self.lbl_source_info.setText("🔴 Enregistrement en cours... 0:00")
        self.lbl_source_info.setStyleSheet("color: #f44336; padding: 5px;")

    def _stop_recording(self) -> None:
        """Arrête l'enregistrement et sauvegarde le fichier."""
        self.btn_record.setText("🎙️ Enregistrer")
        self.btn_record.setChecked(False)

        if self._recording_timer:
            self._recording_timer.stop()

        audio_data = self.recorder.stop_recording()

        if audio_data is not None and len(audio_data) > 0:
            self._save_recording(audio_data)

        self.btn_import.setEnabled(True)

    def _save_recording(self, audio_data) -> None:
        """Sauvegarde les données audio enregistrées."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = self.config.paths.output / f"enregistrement_{timestamp}.wav"
        self._audio_path = self.recorder.save_recording(audio_data, output_path)

        self.lbl_source_info.setText(f"🎙️ Enregistrement sauvegardé: {self._audio_path.name}")
        self.lbl_source_info.setStyleSheet("color: #4CAF50; padding: 5px;")
        self.audio_player.load_audio(self._audio_path)
        self.btn_transcribe.setEnabled(True)
        self.status_bar.showMessage(f"Enregistrement sauvegardé: {output_path}")

    def _update_recording_display(self) -> None:
        """Met à jour l'affichage de la durée d'enregistrement."""
        mins = int(self._recording_duration // 60)
        secs = int(self._recording_duration % 60)
        self.lbl_source_info.setText(f"🔴 Enregistrement en cours... {mins}:{secs:02d}")

    # =========================================================================
    # Handlers - Transcription
    # =========================================================================

    def _on_transcribe_clicked(self) -> None:
        """Lance la transcription."""
        if self._audio_path is None:
            return

        if self._current_worker and self._current_worker.is_running():
            self._cancel_transcription()
            return

        self._start_transcription()

    def _cancel_transcription(self) -> None:
        """Annule la transcription en cours."""
        self._current_worker.stop()
        self._reset_ui_after_transcription()

    def _start_transcription(self) -> None:
        """Démarre le processus de transcription."""
        options = self._get_transcription_options()
        self._disable_ui_for_transcription()
        self._create_and_start_worker(options)

    def _get_transcription_options(self) -> dict:
        """Récupère les options de transcription depuis l'UI."""
        lang_text = self.combo_language.currentText()
        language = lang_text.split("(")[-1].rstrip(")")

        return {
            "language": language if language != "auto" else None,
            "use_diarization": self.chk_diarization.isChecked(),
            "diarization_mode": "quality" if self.combo_diarization.currentIndex() == 0 else "fast",
            "max_speakers": self.spin_speakers.value(),
        }

    def _disable_ui_for_transcription(self) -> None:
        """Désactive l'UI pendant la transcription."""
        self.audio_player.stop()
        self.btn_transcribe.setText("⏹️ Annuler")
        self.btn_import.setEnabled(False)
        self.btn_record.setEnabled(False)
        self.text_result.clear()

    def _create_and_start_worker(self, options: dict) -> None:
        """Crée et démarre le worker de transcription."""
        self.diarizer.mode = options["diarization_mode"]

        if options["use_diarization"]:
            worker = self._create_full_pipeline_worker(options)
        else:
            worker = self._create_transcription_worker(options)

        worker.progress.connect(self._on_progress)
        worker.finished.connect(self._on_finished)
        worker.error.connect(self._on_error)

        self._current_worker = WorkerThread(worker)
        self._current_worker.start()

    def _create_full_pipeline_worker(self, options: dict) -> FullPipelineWorker:
        """Crée un worker pour le pipeline complet (transcription + diarization)."""
        worker = FullPipelineWorker(
            audio_path=self._audio_path,
            transcriber=self.transcriber,
            diarizer=self.diarizer,
            language=options["language"],
            max_speakers=options["max_speakers"],
        )
        worker.transcription_done.connect(self._on_transcription_done)
        return worker

    def _create_transcription_worker(self, options: dict) -> TranscriptionWorker:
        """Crée un worker pour la transcription seule."""
        worker = TranscriptionWorker(
            audio_path=self._audio_path,
            transcriber=self.transcriber,
            language=options["language"],
        )
        worker.segment_ready.connect(self._on_segment_ready)
        return worker

    # =========================================================================
    # Callbacks de transcription
    # =========================================================================

    def _on_progress(self, step: str, percent: float, detail: str) -> None:
        """Met à jour la progression."""
        self.lbl_progress.setText(f"{step}: {detail}")
        self.progress_bar.setValue(int(percent))
        self.status_bar.showMessage(f"{step} - {percent:.0f}%")

    def _on_segment_ready(self, index: int, text: str) -> None:
        """Affiche un segment au fur et à mesure."""
        self.text_result.append(text.strip())

    def _on_transcription_done(self, result: TranscriptionResult) -> None:
        """Appelé quand la transcription est finie (avant diarization)."""
        self.text_result.setPlainText(result.to_text(include_speakers=False))
        self.status_bar.showMessage("Transcription terminée, identification des locuteurs...")

    def _on_finished(self, result: TranscriptionResult) -> None:
        """Appelé quand tout le traitement est terminé."""
        self._current_result = result
        self.text_result.setPlainText(result.to_text(
            include_timestamps=True,
            include_speakers=True,
        ))
        self._reset_ui_after_transcription()
        self._enable_export_buttons()
        self.status_bar.showMessage(
            f"Terminé: {len(result.segments)} segments, "
            f"durée {result.duration:.1f}s, langue {result.language}"
        )

    def _on_error(self, error_msg: str) -> None:
        """Gère les erreurs."""
        self._reset_ui_after_transcription()
        QMessageBox.critical(self, "Erreur", f"Erreur lors du traitement:\n{error_msg}")
        self.status_bar.showMessage(f"Erreur: {error_msg}")

    # =========================================================================
    # Helpers UI
    # =========================================================================

    def _reset_ui_after_transcription(self) -> None:
        """Remet l'UI dans son état initial après transcription."""
        self.btn_transcribe.setText("▶️ Transcrire")
        self.btn_transcribe.setEnabled(True)
        self.btn_import.setEnabled(True)
        self.btn_record.setEnabled(True)
        self.progress_bar.setValue(0)
        self.lbl_progress.setText("Prêt")

    def _enable_export_buttons(self) -> None:
        """Active les boutons d'export."""
        self.btn_copy.setEnabled(True)
        self.btn_save_txt.setEnabled(True)
        self.btn_save_srt.setEnabled(True)

    def _on_diarization_toggled(self, checked: bool) -> None:
        """Active/désactive les options de diarization."""
        self.combo_diarization.setEnabled(checked)
        self.spin_speakers.setEnabled(checked)

    # =========================================================================
    # Handlers - Export
    # =========================================================================

    def _on_copy_clicked(self) -> None:
        """Copie le résultat dans le presse-papier."""
        from PySide6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(self.text_result.toPlainText())
        self.status_bar.showMessage("Texte copié dans le presse-papier")

    def _on_save_txt_clicked(self) -> None:
        """Sauvegarde en TXT."""
        if self._current_result is None:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Sauvegarder en TXT", "", "Fichier texte (*.txt)"
        )
        if path:
            content = self._current_result.to_text(include_timestamps=True, include_speakers=True)
            Path(path).write_text(content, encoding="utf-8")
            self.status_bar.showMessage(f"Sauvegardé: {path}")

    def _on_save_srt_clicked(self) -> None:
        """Sauvegarde en SRT."""
        if self._current_result is None:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Sauvegarder en SRT", "", "Sous-titres (*.srt)"
        )
        if path:
            Path(path).write_text(self._current_result.to_srt(), encoding="utf-8")
            self.status_bar.showMessage(f"Sauvegardé: {path}")

    def _on_clear_clicked(self) -> None:
        """Efface le résultat."""
        self.text_result.clear()
        self._current_result = None
        self.btn_copy.setEnabled(False)
        self.btn_save_txt.setEnabled(False)
        self.btn_save_srt.setEnabled(False)

    # =========================================================================
    # Lifecycle
    # =========================================================================

    def closeEvent(self, event) -> None:
        """Gère la fermeture de la fenêtre."""
        self.audio_player.stop()

        if self._current_worker and self._current_worker.is_running():
            self._current_worker.stop()

        if self.recorder.is_recording:
            self.recorder.stop_recording()

        self.transcriber.unload_model()
        self.diarizer.unload()

        event.accept()
