from PyQt5 import Qt


class SdrStatusWindow(Qt.QWidget):
    """Status window for the SDR receiver: shows current parameter config.

    Closing the window stops the SDR and exits the process.
    """

    # key -> (中文 label, 格式化函数)
    _CONFIG_ROWS = [
        ("mode", "模式", lambda v: "信号 (signal)" if v == "signal" else "干扰 (noise)"),
        ("frequency", "频率", lambda v: f"{v / 1e6:.3f} MHz"),
        ("bandwidth", "低通带宽", lambda v: f"{v / 1e3:.0f} kHz"),
        ("sensitivity", "解调灵敏度", lambda v: f"{v:.4f}"),
        ("sdr_uri", "SDR URI", str),
        ("tcp_port", "TCP 端口", lambda v: f"{v} (noise key)"),
        ("access_code", "访问码", lambda v: f"{v[:24]}…"),
    ]

    def __init__(self):
        super().__init__()
        self.setWindowTitle("GFSK-RX SDR")
        self.setFixedSize(720, 460)

        self.label = Qt.QLabel("SDR 启动中…")
        self.label.setAlignment(Qt.Qt.AlignCenter)
        font = self.label.font()
        font.setPointSize(16)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setWordWrap(True)

        form = Qt.QFormLayout()
        form.setVerticalSpacing(10)
        self.value_labels: dict[str, Qt.QLabel] = {}
        for key, label, _fmt in self._CONFIG_ROWS:
            value = Qt.QLabel("—")
            value.setTextInteractionFlags(Qt.Qt.TextSelectableByMouse)
            value_font = value.font()
            value_font.setPointSize(14)
            value.setFont(value_font)
            name = Qt.QLabel(label)
            name_font = name.font()
            name_font.setPointSize(14)
            name.setFont(name_font)
            self.value_labels[key] = value
            form.addRow(name, value)

        hint = Qt.QLabel("关闭窗口即退出 SDR")
        hint.setAlignment(Qt.Qt.AlignCenter)
        hint.setStyleSheet("color: gray; font-size: 14px;")

        layout = Qt.QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 16)
        layout.setSpacing(14)
        layout.addWidget(self.label)
        layout.addLayout(form)
        layout.addWidget(hint)

        self.update_config(None)

    def update_status(self, text: str) -> None:
        self.label.setText(text)

    def update_config(self, config: dict | None) -> None:
        for key, _label, fmt in self._CONFIG_ROWS:
            value = config.get(key) if config else None
            text = fmt(value) if value is not None else "—"
            self.value_labels[key].setText(text)

    def closeEvent(self, event) -> None:
        print("Status window closed, shutting down SDR")
        Qt.QApplication.quit()
        event.accept()
