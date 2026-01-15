"""
Dialogue pour le traitement par lots (batch processing).
"""
import logging
from pathlib import Path
from typing import List, Optional

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox,
    QPushButton, QLabel, QListWidget, QListWidgetItem,
    QProgressBar, QComboBox, QCheckBox, QSpinBox,
    QFileDialog, QMessageBox, QAbstractItemView,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from ..core.transcriber import Transcriber
from ..core.diarizer import Diarizer
from ..core.batch_processor import get_audio_files_from_directory
from ..utils.config import get_config
from .workers import BatchWorker, WorkerThread

logger = logging.getLogger(__name__)


class BatchDialog(QDialog):
    """Dialogue pour configurer et lancer le traitement par lots."""

    def __init__(
        self,
        transcriber: Transcriber,
        diarizer: Diarizer,
        parent=None,
    ):
        super().__init__(parent)
        self.transcriber = transcriber
        self.diarizer = diarizer
        self.config = get_config()
        self._files: List[Path] = []
        self._worker: Optional[WorkerThread] = None

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Configure l'interface du dialogue."""
        self.setWindowTitle("Traitement par lots")
        self.setMinimumSize(700, 600)

        layout = QVBoxLayout(self)

        layout.addWidget(self._create_files_section())
        layout.addWidget(self._create_options_section())
        layout.addWidget(self._create_output_section())
        layout.addWidget(self._create_progress_section())
        layout.addLayout(self._create_buttons())

    def _create_files_section(self) -> QGroupBox:
        """Crée la section de sélection des fichiers."""
        group = QGroupBox("Fichiers à traiter")
        layout = QVBoxLayout(group)

        buttons = QHBoxLayout()

        self.btn_add_files = QPushButton("Ajouter des fichiers...")
        buttons.addWidget(self.btn_add_files)

        self.btn_add_folder = QPushButton("Ajouter un dossier...")
        buttons.addWidget(self.btn_add_folder)

        self.btn_remove = QPushButton("Retirer")
        self.btn_remove.setEnabled(False)
        buttons.addWidget(self.btn_remove)

        self.btn_clear = QPushButton("Tout effacer")
        self.btn_clear.setEnabled(False)
        buttons.addWidget(self.btn_clear)

        buttons.addStretch()

        layout.addLayout(buttons)

        self.list_files = QListWidget()
        self.list_files.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.list_files.setAlternatingRowColors(True)
        layout.addWidget(self.list_files)

        self.lbl_file_count = QLabel("0 fichier(s)")
        layout.addWidget(self.lbl_file_count)

        return group

    def _create_options_section(self) -> QGroupBox:
        """Crée la section des options."""
        group = QGroupBox("Options")
        layout = QHBoxLayout(group)

        layout.addWidget(QLabel("Langue:"))
        self.combo_language = QComboBox()
        self.combo_language.addItems([
            "Français (fr)", "Anglais (en)", "Auto-détection (auto)"
        ])
        layout.addWidget(self.combo_language)

        layout.addSpacing(20)

        self.chk_diarization = QCheckBox("Identifier les locuteurs")
        self.chk_diarization.setChecked(True)
        layout.addWidget(self.chk_diarization)

        layout.addWidget(QLabel("Max locuteurs:"))
        self.spin_speakers = QSpinBox()
        self.spin_speakers.setRange(0, 20)
        self.spin_speakers.setSpecialValueText("Auto")
        layout.addWidget(self.spin_speakers)

        layout.addStretch()

        return group

    def _create_output_section(self) -> QGroupBox:
        """Crée la section des options de sortie."""
        group = QGroupBox("Sortie")
        layout = QHBoxLayout(group)

        layout.addWidget(QLabel("Format:"))
        self.combo_format = QComboBox()
        self.combo_format.addItems(["Texte (.txt)", "Sous-titres (.srt)", "Les deux"])
        layout.addWidget(self.combo_format)

        layout.addSpacing(20)

        self.chk_timestamps = QCheckBox("Inclure timestamps")
        self.chk_timestamps.setChecked(True)
        layout.addWidget(self.chk_timestamps)

        self.chk_skip_existing = QCheckBox("Ignorer existants")
        layout.addWidget(self.chk_skip_existing)

        layout.addStretch()

        self.btn_output_dir = QPushButton("Dossier de sortie...")
        layout.addWidget(self.btn_output_dir)

        self.lbl_output_dir = QLabel("(même dossier que les fichiers)")
        self.lbl_output_dir.setStyleSheet("color: #666;")
        layout.addWidget(self.lbl_output_dir)

        return group

    def _create_progress_section(self) -> QGroupBox:
        """Crée la section de progression."""
        group = QGroupBox("Progression")
        layout = QVBoxLayout(group)

        progress_layout = QHBoxLayout()
        self.lbl_progress = QLabel("En attente...")
        progress_layout.addWidget(self.lbl_progress)

        self.lbl_current_file = QLabel("")
        self.lbl_current_file.setStyleSheet("color: #2196F3;")
        progress_layout.addStretch()
        progress_layout.addWidget(self.lbl_current_file)

        layout.addLayout(progress_layout)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)

        return group

    def _create_buttons(self) -> QHBoxLayout:
        """Crée les boutons d'action."""
        layout = QHBoxLayout()

        self.btn_start = QPushButton("Démarrer le traitement")
        self.btn_start.setMinimumHeight(40)
        self.btn_start.setEnabled(False)
        layout.addWidget(self.btn_start)

        self.btn_cancel = QPushButton("Annuler")
        self.btn_cancel.setEnabled(False)
        layout.addWidget(self.btn_cancel)

        self.btn_close = QPushButton("Fermer")
        layout.addWidget(self.btn_close)

        return layout

    def _connect_signals(self) -> None:
        """Connecte les signaux."""
        self.btn_add_files.clicked.connect(self._on_add_files)
        self.btn_add_folder.clicked.connect(self._on_add_folder)
        self.btn_remove.clicked.connect(self._on_remove_files)
        self.btn_clear.clicked.connect(self._on_clear_files)
        self.btn_output_dir.clicked.connect(self._on_select_output_dir)
        self.btn_start.clicked.connect(self._on_start)
        self.btn_cancel.clicked.connect(self._on_cancel)
        self.btn_close.clicked.connect(self.close)
        self.list_files.itemSelectionChanged.connect(self._on_selection_changed)
        self.chk_diarization.toggled.connect(self._on_diarization_toggled)

    def _on_add_files(self) -> None:
        """Ajoute des fichiers audio."""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Sélectionner des fichiers audio",
            "",
            "Audio (*.wav *.mp3 *.m4a *.flac *.ogg *.wma *.aac);;Tous (*.*)",
        )
        for f in files:
            self._add_file(Path(f))
        self._update_file_count()

    def _on_add_folder(self) -> None:
        """Ajoute tous les fichiers d'un dossier."""
        folder = QFileDialog.getExistingDirectory(self, "Sélectionner un dossier")
        if folder:
            files = get_audio_files_from_directory(Path(folder), recursive=True)
            for f in files:
                self._add_file(f)
            self._update_file_count()

    def _add_file(self, path: Path) -> None:
        """Ajoute un fichier à la liste."""
        if path in self._files:
            return
        self._files.append(path)
        item = QListWidgetItem(f"{path.name}  ({path.parent})")
        item.setData(Qt.UserRole, str(path))
        self.list_files.addItem(item)

    def _on_remove_files(self) -> None:
        """Retire les fichiers sélectionnés."""
        for item in self.list_files.selectedItems():
            path = Path(item.data(Qt.UserRole))
            if path in self._files:
                self._files.remove(path)
            self.list_files.takeItem(self.list_files.row(item))
        self._update_file_count()

    def _on_clear_files(self) -> None:
        """Efface tous les fichiers."""
        self._files.clear()
        self.list_files.clear()
        self._update_file_count()

    def _on_selection_changed(self) -> None:
        """Gère le changement de sélection."""
        self.btn_remove.setEnabled(len(self.list_files.selectedItems()) > 0)

    def _on_diarization_toggled(self, checked: bool) -> None:
        """Active/désactive les options de diarization."""
        self.spin_speakers.setEnabled(checked)

    def _on_select_output_dir(self) -> None:
        """Sélectionne le dossier de sortie."""
        folder = QFileDialog.getExistingDirectory(self, "Dossier de sortie")
        if folder:
            self._output_dir = Path(folder)
            self.lbl_output_dir.setText(str(folder))
            self.lbl_output_dir.setStyleSheet("color: #4CAF50;")
        else:
            self._output_dir = None
            self.lbl_output_dir.setText("(même dossier que les fichiers)")
            self.lbl_output_dir.setStyleSheet("color: #666;")

    def _update_file_count(self) -> None:
        """Met à jour le compteur de fichiers."""
        count = len(self._files)
        self.lbl_file_count.setText(f"{count} fichier(s)")
        self.btn_start.setEnabled(count > 0)
        self.btn_clear.setEnabled(count > 0)

    def _on_start(self) -> None:
        """Démarre le traitement."""
        if not self._files:
            return

        self._set_ui_processing(True)

        lang_text = self.combo_language.currentText()
        language = lang_text.split("(")[-1].rstrip(")")

        format_map = {"Texte (.txt)": "txt", "Sous-titres (.srt)": "srt", "Les deux": "both"}

        options = {
            "language": language if language != "auto" else None,
            "use_diarization": self.chk_diarization.isChecked(),
            "max_speakers": self.spin_speakers.value(),
            "output_dir": getattr(self, "_output_dir", None),
            "output_format": format_map.get(self.combo_format.currentText(), "txt"),
            "include_timestamps": self.chk_timestamps.isChecked(),
            "include_speakers": self.chk_diarization.isChecked(),
            "skip_existing": self.chk_skip_existing.isChecked(),
        }

        worker = BatchWorker(
            files=self._files.copy(),
            transcriber=self.transcriber,
            diarizer=self.diarizer if options["use_diarization"] else None,
            options=options,
        )

        worker.progress.connect(self._on_progress)
        worker.item_completed.connect(self._on_item_completed)
        worker.finished.connect(self._on_finished)
        worker.error.connect(self._on_error)

        self._worker = WorkerThread(worker)
        self._worker.start()

    def _on_cancel(self) -> None:
        """Annule le traitement."""
        if self._worker:
            self._worker.stop()
        self._set_ui_processing(False)
        self.lbl_progress.setText("Annulé")

    def _on_progress(self, current: int, total: int, filename: str, percent: float) -> None:
        """Met à jour la progression."""
        overall = ((current - 1) / total * 100) + (percent / total)
        self.progress_bar.setValue(int(overall))
        self.lbl_progress.setText(f"Fichier {current}/{total}")
        self.lbl_current_file.setText(filename)

    def _on_item_completed(self, index: int, success: bool, message: str) -> None:
        """Met à jour l'état d'un fichier."""
        item = self.list_files.item(index)
        if item:
            if success:
                item.setBackground(QColor("#E8F5E9"))
                item.setText(f"✓ {item.text()}")
            else:
                item.setBackground(QColor("#FFEBEE"))
                item.setText(f"✗ {item.text()}")

    def _on_finished(self, result) -> None:
        """Appelé quand le batch est terminé."""
        self._set_ui_processing(False)
        self.progress_bar.setValue(100)
        self.lbl_progress.setText(
            f"Terminé: {result.completed_count}/{result.total_count} réussis "
            f"({result.total_time:.1f}s)"
        )

        QMessageBox.information(
            self,
            "Traitement terminé",
            f"Traitement par lots terminé.\n\n"
            f"Fichiers traités: {result.completed_count}/{result.total_count}\n"
            f"Échecs: {result.failed_count}\n"
            f"Temps total: {result.total_time:.1f}s",
        )

    def _on_error(self, error_msg: str) -> None:
        """Gère les erreurs."""
        self._set_ui_processing(False)
        QMessageBox.critical(self, "Erreur", f"Erreur lors du traitement:\n{error_msg}")

    def _set_ui_processing(self, processing: bool) -> None:
        """Active/désactive l'UI pendant le traitement."""
        self.btn_start.setEnabled(not processing)
        self.btn_cancel.setEnabled(processing)
        self.btn_add_files.setEnabled(not processing)
        self.btn_add_folder.setEnabled(not processing)
        self.btn_remove.setEnabled(not processing)
        self.btn_clear.setEnabled(not processing)

    def closeEvent(self, event) -> None:
        """Gère la fermeture du dialogue."""
        if self._worker and self._worker.is_running():
            reply = QMessageBox.question(
                self,
                "Traitement en cours",
                "Un traitement est en cours. Voulez-vous l'annuler et fermer?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply == QMessageBox.No:
                event.ignore()
                return
            self._worker.stop()
        event.accept()
