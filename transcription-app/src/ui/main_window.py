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
    QStatusBar, QMessageBox, QTabWidget, QSplitter,
    QCheckBox, QFrame,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QIcon

from ..core.transcriber import Transcriber, TranscriptionResult
from ..core.diarizer import Diarizer
from ..core.audio_processor import AudioRecorder, AudioProcessor
from ..utils.config import get_config
from .workers import TranscriptionWorker, FullPipelineWorker, WorkerThread

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
        
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self) -> None:
        """Configure l'interface utilisateur."""
        self.setWindowTitle("Transcription Audio")
        self.setMinimumSize(900, 700)
        
        # Widget central
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # === SECTION SOURCE ===
        source_group = QGroupBox("Source Audio")
        source_layout = QVBoxLayout(source_group)
        
        # Boutons source
        source_buttons = QHBoxLayout()
        
        self.btn_import = QPushButton("📁 Importer un fichier")
        self.btn_import.setMinimumHeight(40)
        source_buttons.addWidget(self.btn_import)
        
        self.btn_record = QPushButton("🎙️ Enregistrer")
        self.btn_record.setMinimumHeight(40)
        self.btn_record.setCheckable(True)
        source_buttons.addWidget(self.btn_record)
        
        source_layout.addLayout(source_buttons)
        
        # Info fichier
        self.lbl_source_info = QLabel("Aucun fichier sélectionné")
        self.lbl_source_info.setStyleSheet("color: #666; padding: 5px;")
        source_layout.addWidget(self.lbl_source_info)
        
        layout.addWidget(source_group)
        
        # === SECTION OPTIONS ===
        options_group = QGroupBox("Options")
        options_layout = QHBoxLayout(options_group)
        
        # Langue
        options_layout.addWidget(QLabel("Langue:"))
        self.combo_language = QComboBox()
        self.combo_language.addItems([
            "Français (fr)", "Anglais (en)", "Auto-détection (auto)"
        ])
        self.combo_language.setCurrentIndex(0)
        options_layout.addWidget(self.combo_language)
        
        options_layout.addSpacing(20)
        
        # Mode diarization
        options_layout.addWidget(QLabel("Diarization:"))
        self.combo_diarization = QComboBox()
        self.combo_diarization.addItems([
            "Qualité (Pyannote - lent)", "Rapide (SpeechBrain)"
        ])
        options_layout.addWidget(self.combo_diarization)
        
        options_layout.addSpacing(20)
        
        # Nombre de locuteurs
        options_layout.addWidget(QLabel("Locuteurs:"))
        self.spin_speakers = QSpinBox()
        self.spin_speakers.setRange(0, 20)
        self.spin_speakers.setValue(0)
        self.spin_speakers.setSpecialValueText("Auto")
        self.spin_speakers.setToolTip("0 = détection automatique")
        options_layout.addWidget(self.spin_speakers)
        
        options_layout.addStretch()
        
        # Checkbox diarization
        self.chk_diarization = QCheckBox("Identifier les locuteurs")
        self.chk_diarization.setChecked(True)
        options_layout.addWidget(self.chk_diarization)
        
        layout.addWidget(options_group)
        
        # === BOUTON TRANSCRIRE ===
        self.btn_transcribe = QPushButton("▶️ Transcrire")
        self.btn_transcribe.setMinimumHeight(50)
        self.btn_transcribe.setEnabled(False)
        font = self.btn_transcribe.font()
        font.setPointSize(12)
        font.setBold(True)
        self.btn_transcribe.setFont(font)
        layout.addWidget(self.btn_transcribe)
        
        # === PROGRESSION ===
        progress_frame = QFrame()
        progress_layout = QVBoxLayout(progress_frame)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        
        self.lbl_progress = QLabel("Prêt")
        progress_layout.addWidget(self.lbl_progress)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        
        layout.addWidget(progress_frame)
        
        # === RÉSULTAT ===
        result_group = QGroupBox("Transcription")
        result_layout = QVBoxLayout(result_group)
        
        self.text_result = QTextEdit()
        self.text_result.setReadOnly(True)
        self.text_result.setPlaceholderText(
            "La transcription apparaîtra ici...\n\n"
            "Importez un fichier audio ou démarrez un enregistrement."
        )
        font_mono = QFont("Consolas", 10)
        self.text_result.setFont(font_mono)
        result_layout.addWidget(self.text_result)
        
        # Boutons export
        export_buttons = QHBoxLayout()
        
        self.btn_copy = QPushButton("📋 Copier")
        self.btn_copy.setEnabled(False)
        export_buttons.addWidget(self.btn_copy)
        
        self.btn_save_txt = QPushButton("💾 Sauvegarder TXT")
        self.btn_save_txt.setEnabled(False)
        export_buttons.addWidget(self.btn_save_txt)
        
        self.btn_save_srt = QPushButton("💾 Sauvegarder SRT")
        self.btn_save_srt.setEnabled(False)
        export_buttons.addWidget(self.btn_save_srt)
        
        export_buttons.addStretch()
        
        self.btn_clear = QPushButton("🗑️ Effacer")
        export_buttons.addWidget(self.btn_clear)
        
        result_layout.addLayout(export_buttons)
        
        layout.addWidget(result_group, stretch=1)
        
        # === STATUS BAR ===
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Prêt")
        
        # État initial
        self._audio_path: Optional[Path] = None
    
    def _connect_signals(self) -> None:
        """Connecte les signaux aux slots."""
        self.btn_import.clicked.connect(self._on_import_clicked)
        self.btn_record.clicked.connect(self._on_record_clicked)
        self.btn_transcribe.clicked.connect(self._on_transcribe_clicked)
        self.btn_copy.clicked.connect(self._on_copy_clicked)
        self.btn_save_txt.clicked.connect(self._on_save_txt_clicked)
        self.btn_save_srt.clicked.connect(self._on_save_srt_clicked)
        self.btn_clear.clicked.connect(self._on_clear_clicked)
        self.chk_diarization.toggled.connect(self._on_diarization_toggled)
    
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
            
            duration_str = f"{info['duration']:.1f}s"
            if info['duration'] > 60:
                mins = int(info['duration'] // 60)
                secs = int(info['duration'] % 60)
                duration_str = f"{mins}min {secs}s"
            
            self.lbl_source_info.setText(
                f"📄 {path.name} | {duration_str} | "
                f"{info['sample_rate']}Hz | {info['size_mb']:.1f} Mo"
            )
            self.lbl_source_info.setStyleSheet("color: #2196F3; padding: 5px;")
            
            self.btn_transcribe.setEnabled(True)
            self.status_bar.showMessage(f"Fichier chargé: {path.name}")
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de charger le fichier:\n{e}")
            logger.error(f"Erreur chargement audio: {e}")
    
    def _on_record_clicked(self) -> None:
        """Gère le clic sur le bouton d'enregistrement."""
        if self.recorder.is_recording:
            # Arrêter l'enregistrement
            self.btn_record.setText("🎙️ Enregistrer")
            self.btn_record.setChecked(False)
            
            if self._recording_timer:
                self._recording_timer.stop()
            
            audio_data = self.recorder.stop_recording()
            
            if audio_data is not None and len(audio_data) > 0:
                # Sauvegarder l'enregistrement
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = self.config.paths.output / f"enregistrement_{timestamp}.wav"
                self._audio_path = self.recorder.save_recording(audio_data, output_path)
                
                self.lbl_source_info.setText(f"🎙️ Enregistrement sauvegardé: {self._audio_path.name}")
                self.lbl_source_info.setStyleSheet("color: #4CAF50; padding: 5px;")
                self.btn_transcribe.setEnabled(True)
                self.status_bar.showMessage(f"Enregistrement sauvegardé: {output_path}")
            
            self.btn_import.setEnabled(True)
            
        else:
            # Démarrer l'enregistrement
            self.btn_record.setText("⏹️ Arrêter")
            self.btn_import.setEnabled(False)
            self.btn_transcribe.setEnabled(False)
            
            self._recording_duration = 0.0
            
            def update_duration(duration: float):
                self._recording_duration = duration
            
            self.recorder.start_recording(callback=update_duration)
            
            # Timer pour mettre à jour l'affichage
            self._recording_timer = QTimer()
            self._recording_timer.timeout.connect(self._update_recording_display)
            self._recording_timer.start(100)
            
            self.lbl_source_info.setText("🔴 Enregistrement en cours... 0:00")
            self.lbl_source_info.setStyleSheet("color: #f44336; padding: 5px;")
    
    def _update_recording_display(self) -> None:
        """Met à jour l'affichage de la durée d'enregistrement."""
        mins = int(self._recording_duration // 60)
        secs = int(self._recording_duration % 60)
        self.lbl_source_info.setText(f"🔴 Enregistrement en cours... {mins}:{secs:02d}")
    
    def _on_transcribe_clicked(self) -> None:
        """Lance la transcription."""
        if self._audio_path is None:
            return
        
        if self._current_worker and self._current_worker.is_running():
            # Annuler le traitement en cours
            self._current_worker.stop()
            self._reset_ui_after_transcription()
            return
        
        # Préparer les options
        lang_text = self.combo_language.currentText()
        language = lang_text.split("(")[-1].rstrip(")")
        
        use_diarization = self.chk_diarization.isChecked()
        diarization_mode = "quality" if self.combo_diarization.currentIndex() == 0 else "fast"
        self.diarizer.mode = diarization_mode
        
        # Désactiver l'UI
        self.btn_transcribe.setText("⏹️ Annuler")
        self.btn_import.setEnabled(False)
        self.btn_record.setEnabled(False)
        self.text_result.clear()
        
        # Créer et lancer le worker
        if use_diarization:
            worker = FullPipelineWorker(
                audio_path=self._audio_path,
                transcriber=self.transcriber,
                diarizer=self.diarizer,
                language=language if language != "auto" else None,
                max_speakers=self.spin_speakers.value(),
            )
            worker.transcription_done.connect(self._on_transcription_done)
        else:
            worker = TranscriptionWorker(
                audio_path=self._audio_path,
                transcriber=self.transcriber,
                language=language if language != "auto" else None,
            )
            worker.segment_ready.connect(self._on_segment_ready)
        
        worker.progress.connect(self._on_progress)
        worker.finished.connect(self._on_finished)
        worker.error.connect(self._on_error)
        
        self._current_worker = WorkerThread(worker)
        self._current_worker.start()
    
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
        
        # Afficher le résultat final avec locuteurs
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
            Path(path).write_text(
                self._current_result.to_text(include_timestamps=True, include_speakers=True),
                encoding="utf-8"
            )
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
    
    def closeEvent(self, event) -> None:
        """Gère la fermeture de la fenêtre."""
        # Arrêter tout traitement en cours
        if self._current_worker and self._current_worker.is_running():
            self._current_worker.stop()
        
        # Arrêter l'enregistrement si en cours
        if self.recorder.is_recording:
            self.recorder.stop_recording()
        
        # Décharger les modèles
        self.transcriber.unload_model()
        self.diarizer.unload()
        
        event.accept()
