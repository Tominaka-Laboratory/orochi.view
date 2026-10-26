try:
    import matplotlib
    try:
        from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
        from PyQt6.QtWidgets import QWidget, QVBoxLayout
    except ImportError:
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
        from PyQt5.QtWidgets import QWidget, QVBoxLayout
except ImportError:
    QWidget = object
    FigureCanvas = None
    QVBoxLayout = None


class QtWindow(QWidget):
    def __init__(self, figure):
        super().__init__()
        self.figure = figure
        if FigureCanvas is not None:
            self.canvas = FigureCanvas(self.figure)
            layout = QVBoxLayout()
            layout.addWidget(self.canvas)
            self.setLayout(layout)


