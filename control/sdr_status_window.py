from PyQt5 import Qt


class SdrStatusWindow(Qt.QWidget):
    """Minimal startup/status window for the SDR receiver (no qtgui).

    Closing the window only hides it; the receiver keeps running in the
    background. Exit via Ctrl+C.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("GFSK-RX SDR")
        self.setFixedSize(420, 180)

        self.label = Qt.QLabel("SDR 启动中…")
        self.label.setAlignment(Qt.Qt.AlignCenter)
        font = self.label.font()
        font.setPointSize(14)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setWordWrap(True)

        layout = Qt.QVBoxLayout(self)
        layout.addWidget(self.label)

    def update_status(self, text: str) -> None:
        self.label.setText(text)

    def closeEvent(self, event) -> None:
        event.ignore()
        self.hide()
        print("Status window hidden (SDR keeps running, Ctrl+C to exit)")
