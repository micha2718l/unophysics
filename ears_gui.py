import sys
from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow

if __name__ == "__main__":
    import cProfile
    import pstats

    profiler = cProfile.Profile()
    profiler.enable()
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    exit_code = app.exec()
    profiler.disable()
    with open("ears_gui_profile.txt", "w") as f:
        ps = pstats.Stats(profiler, stream=f)
        ps.sort_stats("cumtime").print_stats(50)
    sys.exit(exit_code)

    sys.exit(app.exec())
