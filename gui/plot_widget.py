import pyqtgraph as pg


class PlotWidget(pg.PlotWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cursor_line = None
        # UI improvements
        self.setBackground("w")
        self.showGrid(x=True, y=True, alpha=0.2)
        self.setMenuEnabled(False)
        self.setMouseEnabled(x=False, y=False)
        self.hideButtons()

    def plot_waveform(self, data, fs, current_pos):
        self.set_waveform(data, fs)
        self.add_cursor(current_pos, fs)

    def set_waveform(self, data, fs):
        self.clear()
        pen = pg.mkPen(color=(0, 102, 204), width=1.5)
        # Downsample if data is too large for the widget
        max_points = 2000
        n = len(data)
        if n > max_points:
            # Compute downsampling factor
            step = n // max_points
            # Use min/max envelope for better visual fidelity
            import numpy as np

            data = data[: (max_points * step)]  # Trim to even multiple
            data = data.reshape(-1, step)
            data_min = data.min(axis=1)
            data_max = data.max(axis=1)
            # Interleave min and max for envelope
            data_ds = np.empty((data_min.size + data_max.size,), dtype=data_min.dtype)
            data_ds[0::2] = data_min
            data_ds[1::2] = data_max
            data = data_ds
        self.plot(data, pen=pen)
        # Do not add cursor here

    def reset_xrange(self):
        self.enableAutoRange(axis=pg.ViewBox.XAxis)

    def add_cursor(self, current_pos, fs, on_dragged=None):
        if self.cursor_line:
            self.removeItem(self.cursor_line)
        idx = int(current_pos * fs)
        self.cursor_line = pg.InfiniteLine(
            pos=idx, angle=90, movable=True, pen=pg.mkPen("r", width=2)
        )
        self.addItem(self.cursor_line)
        if on_dragged:
            self.cursor_line.sigPositionChanged.connect(
                lambda line: on_dragged(line.value())
            )

    def update_cursor(self, current_pos, fs):
        if self.cursor_line:
            idx = int(current_pos * fs)
            self.cursor_line.setValue(idx)
