from PyQt5 import Qt


class SdrStatusWindow(Qt.QWidget):
    """Status window for the SDR receiver: shows current parameter config.

    Closing the window only hides it; the receiver keeps running in the
    background. Use the "退出 SDR" button, Ctrl+C or SIGTERM to stop.
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

        self.label = Qt.QLabel("SDR 启动中…")
        self.label.setAlignment(Qt.Qt.AlignCenter)
        font = self.label.font()
        font.setPointSize(14)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setWordWrap(True)

        form = Qt.QFormLayout()
        form.setVerticalSpacing(8)
        self.form = form
        self.value_labels: dict[str, Qt.QLabel] = {}
        for key, label_text, _fmt in self._CONFIG_ROWS:
            value = Qt.QLabel("—")
            value.setTextInteractionFlags(Qt.Qt.TextSelectableByMouse)
            value_font = value.font()
            value_font.setPointSize(13)
            value.setFont(value_font)
            self.value_labels[key] = value
            form.addRow(self._make_name_label(label_text), value)

        self.exit_button = Qt.QPushButton("退出 SDR")
        self.exit_button.setFixedWidth(160)
        self.exit_button.clicked.connect(self._request_exit)

        hint = Qt.QLabel("关闭窗口仅隐藏, SDR 后台继续运行")
        hint.setAlignment(Qt.Qt.AlignCenter)
        hint.setStyleSheet("color: gray; font-size: 12px;")
        self.hint = hint

        layout = Qt.QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 12)
        layout.setSpacing(10)
        layout.addWidget(self.label)
        layout.addLayout(form)
        layout.addSpacing(4)
        layout.addWidget(self.exit_button, 0, Qt.Qt.AlignHCenter)
        layout.addWidget(hint)

        self.update_config(None)
        self._resize_to_fit()

    def _resize_to_fit(self, width: int = 640) -> None:
        """Size the window to its content using real font metrics.

        The environment may run at 2x DPI scaling, so fixed pixel sizes
        are unreliable; compute heights from actual font metrics instead.
        """
        layout = self.layout()
        margins = layout.contentsMargins()
        inner_w = width - margins.left() - margins.right()
        status_two_lines = 2 * Qt.QFontMetrics(self.label.font()).lineSpacing() + 8
        status_h = max(self.label.heightForWidth(inner_w), status_two_lines)
        height = (
            margins.top()
            + status_h
            + layout.spacing()
            + self.form.sizeHint().height()
            + layout.spacing()
            + 4
            + self.exit_button.sizeHint().height()
            + layout.spacing()
            + self.hint.sizeHint().height()
            + margins.bottom()
        )
        self.setFixedSize(width, int(height))

    def _make_name_label(self, text: str) -> Qt.QLabel:
        name = Qt.QLabel(text)
        font = name.font()
        font.setPointSize(13)
        name.setFont(font)
        return name

    def _request_exit(self) -> None:
        print("Exit requested, shutting down SDR")
        Qt.QApplication.quit()

    def update_status(self, text: str) -> None:
        self.label.setText(text)

    def update_config(self, config: dict | None) -> None:
        for key, _label, fmt in self._CONFIG_ROWS:
            value = config.get(key) if config else None
            text = fmt(value) if value is not None else "—"
            self.value_labels[key].setText(text)

    def closeEvent(self, event) -> None:
        event.ignore()
        self.hide()
        print("Status window hidden (SDR keeps running, 退出 button / Ctrl+C to stop)")
