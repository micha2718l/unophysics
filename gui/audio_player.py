import sounddevice as sd
import numpy as np


class AudioPlayer:
    @property
    def current_index(self):
        return self.idx

    @property
    def current_time(self):
        return self.idx / self.samplerate if self.samplerate else 0

    def __init__(self, samplerate):
        self.samplerate = samplerate
        self.stream = None
        self.data = None
        self.idx = 0
        self.on_finished = None

    def play(self, data, start_idx=0, callback=None):
        self.data = data
        self.idx = start_idx
        self.on_finished = callback
        self.stream = sd.OutputStream(
            samplerate=self.samplerate,
            channels=1,
            dtype="float32",
            callback=self._callback,
            finished_callback=self._on_finished,
        )
        self.stream.start()

    def _callback(self, outdata, frames, time_info, status):
        if self.data is None:
            outdata[:] = np.zeros((frames, 1), dtype=np.float32)
            return
        end_idx = min(self.idx + frames, len(self.data))
        chunk = self.data[self.idx : end_idx]
        if len(chunk) < frames:
            chunk = np.pad(chunk, (0, frames - len(chunk)), "constant")
        outdata[:, 0] = chunk
        self.idx += frames
        if self.idx >= len(self.data):
            self.stop()

    def _on_finished(self):
        if self.on_finished:
            self.on_finished()

    def stop(self):
        if self.stream is not None:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception:
                pass
            self.stream = None

    def is_active(self):
        return self.stream is not None and self.stream.active
