from PySide6.QtCore import Qt, QTimer, QThread, Signal
import numpy as np


class CleaningThread(QThread):
    finished = Signal(np.ndarray, int)

    def __init__(self, data, thresh):
        super().__init__()
        self.data = data
        self.thresh = thresh

    def run(self):
        from unophysics import wavefuncs

        cleaned = wavefuncs.wave_clean(self.data, wavelet_thresh=self.thresh)
        self.finished.emit(cleaned, self.thresh)


import numpy as np
from PySide6.QtWidgets import (
    QMainWindow,
    QFileDialog,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QSlider,
    QHBoxLayout,
    QComboBox,
)
from PySide6.QtCore import Qt, QTimer
from unophysics.ladc import EARS
from unophysics import wavefuncs
from .audio_player import AudioPlayer
from .plot_widget import PlotWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.cleaning_thread = None
        self.setWindowTitle("LADC EARS Audio Explorer")
        self.resize(1000, 600)
        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.layout = QVBoxLayout(self.central)

        # File open button
        self.open_btn = QPushButton("Open EARS File")
        self.open_btn.clicked.connect(self.open_file)
        self.layout.addWidget(self.open_btn)

        # Info label
        self.info_label = QLabel("No file loaded.")
        self.layout.addWidget(self.info_label)

        # Plot widget
        self.plot_widget = PlotWidget()
        self.layout.addWidget(self.plot_widget)

        # Controls
        controls = QHBoxLayout()
        self.cleaning_slider = QSlider(Qt.Horizontal)
        self.cleaning_slider.setMinimum(1)
        self.cleaning_slider.setMaximum(500)
        self.cleaning_slider.setValue(50)
        self.cleaning_slider.setTickInterval(10)
        self.cleaning_slider.valueChanged.connect(self.cleaning_slider_changed)
        controls.addWidget(QLabel("Threshold:"))
        controls.addWidget(self.cleaning_slider)

        self.audio_select = QComboBox()
        self.audio_select.addItems(["Raw", "Cleaned"])
        self.audio_select.currentIndexChanged.connect(self.audio_select_changed)
        controls.addWidget(QLabel("Audio:"))
        controls.addWidget(self.audio_select)

        self.play_btn = QPushButton("Play")
        self.play_btn.setCheckable(True)
        self.play_btn.clicked.connect(self.toggle_play)
        controls.addWidget(self.play_btn)

        self.layout.addLayout(controls)

        # Data holders and playback state
        self.data = None
        self.cleaned = None
        self.fs = 192000  # Default, will be updated
        self.audio_length = 0
        self.is_playing = False
        self.current_pos = 0.0  # seconds
        self.timer = QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update_progress)
        self.audio_player = AudioPlayer(self.fs)
        self._last_clean_thresh = None

    def open_file(self):
        import os

        sample_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "sample_data")
        )
        # Find a default file in sample_data
        default_file = ""
        if os.path.isdir(sample_dir):
            for fname in os.listdir(sample_dir):
                if fname.lower().endswith((".190", ".010", ".dat", ".bin")):
                    default_file = os.path.join(sample_dir, fname)
                    break
        start_dir = sample_dir if os.path.isdir(sample_dir) else ""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open EARS File",
            default_file if default_file else start_dir,
            "EARS Files (*.190 *.010 *.dat *.bin);;All Files (*)",
        )
        if not file_path:
            return
        try:
            ears = EARS(file_path)
            self.data = np.array(ears.data, dtype=np.float32)
            self.fs = getattr(ears, "fs", 192000)
            self.audio_length = len(self.data) / self.fs
            self.cleaned = None  # Reset cleaned data
            self.info_label.setText(
                f"Loaded: {file_path}\nSamples: {len(self.data)}  Fs: {self.fs}"
            )
            # No progress slider: handled by draggable cursor
            self.current_pos = 0.0
            self.update_plot()
            self.plot_widget.reset_xrange()
        except Exception as e:
            self.info_label.setText(f"Failed to load file: {e}")

    def update_plot(self):
        import time

        t0 = time.perf_counter()
        if self.data is None:
            return
        if self.audio_select.currentText() == "Cleaned":
            thresh = self.cleaning_slider.value()
            if self.cleaned is None or self._last_clean_thresh != thresh:
                # Show busy indicator
                self.setEnabled(False)
                # Start cleaning in background
                if (
                    hasattr(self, "cleaning_thread")
                    and self.cleaning_thread is not None
                ):
                    self.cleaning_thread.quit()
                self.cleaning_thread = CleaningThread(self.data, thresh)
                self.cleaning_thread.finished.connect(self.on_cleaning_finished)
                self.cleaning_thread.start()
                return  # Will update plot when cleaning is done
            plot_data = self.cleaned
        else:
            plot_data = self.data
        self.plot_widget.set_waveform(plot_data, self.fs)
        self.plot_widget.add_cursor(self.current_pos, self.fs, self.on_cursor_dragged)
        t3 = time.perf_counter()
        print(f"[DEBUG] update_plot total {t3-t0:.4f} seconds")

    def on_cursor_dragged(self, idx):
        # idx is in samples
        self.current_pos = idx / self.fs
        if self.is_playing:
            self.pause_playback()
            self.start_playback()

    def on_cleaning_finished(self, cleaned, thresh):
        self.cleaned = cleaned
        self._last_clean_thresh = thresh
        self.plot_widget.set_waveform(self.cleaned, self.fs)
        self.plot_widget.reset_xrange()
        self.plot_widget.add_cursor(self.current_pos, self.fs)
        self.setEnabled(True)

    def cleaning_slider_changed(self):
        if self.data is None:
            return
        self.cleaned = None
        self.update_plot()
        if self.is_playing and self.audio_select.currentText() == "Cleaned":
            self.pause_playback()
            self.start_playback()

    def audio_select_changed(self):
        if self.data is None:
            return
        self.update_plot()
        if self.is_playing:
            self.pause_playback()
            self.start_playback()

    def toggle_play(self):
        if not self.is_playing:
            self.start_playback()
        else:
            self.pause_playback()

    def start_playback(self):
        if self.data is None:
            return
        self.is_playing = True
        self.play_btn.setText("Pause")
        if self.audio_select.currentText() == "Cleaned":
            thresh = self.cleaning_slider.value()
            if self.cleaned is None or self._last_clean_thresh != thresh:
                self.cleaned = wavefuncs.wave_clean(self.data, wavelet_thresh=thresh)
                self._last_clean_thresh = thresh
            play_data = self.cleaned
        else:
            play_data = self.data
        self.audio_player.samplerate = self.fs
        self.audio_player.play(
            play_data, int(self.current_pos * self.fs), callback=self.on_audio_finished
        )
        self.timer.start()

    def pause_playback(self):
        self.is_playing = False
        self.play_btn.setText("Play")
        self.audio_player.stop()
        if self.timer.isActive():
            self.timer.stop()

    def on_audio_finished(self):
        QTimer.singleShot(0, self.pause_playback)

    def update_progress(self):
        import time

        t0 = time.perf_counter()
        if self.data is None:
            return
        # If playing, get current playback position from AudioPlayer
        if self.is_playing and self.audio_player.is_active():
            self.current_pos = self.audio_player.current_time
        # Only move the cursor, do not redraw waveform
        self.plot_widget.update_cursor(self.current_pos, self.fs)
        t1 = time.perf_counter()
        print(f"[DEBUG] update_progress took {t1-t0:.4f} seconds")
        if self.current_pos >= self.audio_length:
            # Only stop timer from main thread
            QTimer.singleShot(0, self.pause_playback)

    # Removed scrub_audio; scrubbing is now handled by dragging the cursor on the plot
