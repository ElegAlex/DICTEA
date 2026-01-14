"""
Widget de lecture audio pour prévisualiser les fichiers.
"""
import logging
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QSlider, QLabel,
)
from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput

logger = logging.getLogger(__name__)


class AudioPlayerWidget(QWidget):
    """Widget de lecture audio compact."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._audio_path: Optional[Path] = None
        self._duration: float = 0.0

        self._setup_player()
        self._setup_ui()
        self._connect_signals()

    def _setup_player(self) -> None:
        """Configure le lecteur audio."""
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.7)

    def _setup_ui(self) -> None:
        """Configure l'interface."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        self.btn_play = QPushButton("▶")
        self.btn_play.setFixedWidth(35)
        self.btn_play.setEnabled(False)
        layout.addWidget(self.btn_play)

        self.btn_stop = QPushButton("⏹")
        self.btn_stop.setFixedWidth(35)
        self.btn_stop.setEnabled(False)
        layout.addWidget(self.btn_stop)

        self.slider_position = QSlider(Qt.Horizontal)
        self.slider_position.setEnabled(False)
        layout.addWidget(self.slider_position, stretch=1)

        self.lbl_time = QLabel("0:00 / 0:00")
        self.lbl_time.setMinimumWidth(90)
        layout.addWidget(self.lbl_time)

        self.slider_volume = QSlider(Qt.Horizontal)
        self.slider_volume.setRange(0, 100)
        self.slider_volume.setValue(70)
        self.slider_volume.setFixedWidth(80)
        self.slider_volume.setToolTip("Volume")
        layout.addWidget(self.slider_volume)

    def _connect_signals(self) -> None:
        """Connecte les signaux."""
        self.btn_play.clicked.connect(self._on_play_clicked)
        self.btn_stop.clicked.connect(self._on_stop_clicked)
        self.slider_position.sliderMoved.connect(self._on_position_changed)
        self.slider_volume.valueChanged.connect(self._on_volume_changed)

        self.player.positionChanged.connect(self._on_player_position_changed)
        self.player.durationChanged.connect(self._on_duration_changed)
        self.player.playbackStateChanged.connect(self._on_state_changed)

    def load_audio(self, path: Path) -> None:
        """Charge un fichier audio."""
        self.stop()
        self._audio_path = path
        self.player.setSource(QUrl.fromLocalFile(str(path)))
        self._enable_controls(True)

    def play(self) -> None:
        """Démarre la lecture."""
        if self._audio_path:
            self.player.play()

    def pause(self) -> None:
        """Met en pause la lecture."""
        self.player.pause()

    def stop(self) -> None:
        """Arrête la lecture."""
        self.player.stop()
        self._update_time_label(0, self._duration)

    def is_playing(self) -> bool:
        """Vérifie si la lecture est en cours."""
        return self.player.playbackState() == QMediaPlayer.PlayingState

    def clear(self) -> None:
        """Réinitialise le lecteur."""
        self.stop()
        self.player.setSource(QUrl())
        self._audio_path = None
        self._duration = 0.0
        self._enable_controls(False)
        self.lbl_time.setText("0:00 / 0:00")

    def _enable_controls(self, enabled: bool) -> None:
        """Active/désactive les contrôles."""
        self.btn_play.setEnabled(enabled)
        self.btn_stop.setEnabled(enabled)
        self.slider_position.setEnabled(enabled)

    def _on_play_clicked(self) -> None:
        """Gère le clic sur play/pause."""
        if self.is_playing():
            self.pause()
        else:
            self.play()

    def _on_stop_clicked(self) -> None:
        """Gère le clic sur stop."""
        self.stop()

    def _on_position_changed(self, position: int) -> None:
        """Gère le déplacement du slider de position."""
        self.player.setPosition(position)

    def _on_volume_changed(self, value: int) -> None:
        """Gère le changement de volume."""
        self.audio_output.setVolume(value / 100.0)

    def _on_player_position_changed(self, position: int) -> None:
        """Met à jour l'UI avec la position actuelle."""
        if not self.slider_position.isSliderDown():
            self.slider_position.setValue(position)
        self._update_time_label(position / 1000.0, self._duration)

    def _on_duration_changed(self, duration: int) -> None:
        """Met à jour la durée totale."""
        self._duration = duration / 1000.0
        self.slider_position.setRange(0, duration)
        self._update_time_label(0, self._duration)

    def _on_state_changed(self, state: QMediaPlayer.PlaybackState) -> None:
        """Met à jour le bouton play/pause."""
        if state == QMediaPlayer.PlayingState:
            self.btn_play.setText("⏸")
        else:
            self.btn_play.setText("▶")

    def _update_time_label(self, current: float, total: float) -> None:
        """Met à jour le label de temps."""
        current_str = self._format_time(current)
        total_str = self._format_time(total)
        self.lbl_time.setText(f"{current_str} / {total_str}")

    @staticmethod
    def _format_time(seconds: float) -> str:
        """Formate les secondes en MM:SS."""
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins}:{secs:02d}"
