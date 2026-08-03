from PyQt5 import Qt


class SdrStatusWindow(Qt.QWidget):
    """Status window for the SDR receiver: shows current parameter config.

    Closing the window only hides it; the receiver keeps running in the
    background. Use the "退出 SDR" button, Ctrl+C or SIGTERM to stop.
    """

    # key -> (中文 label, 格式化函数)
    _CONFIG_ROWS = [
        ("side", "阵营", lambda v: "红方 (red)" if v == "red" else "蓝方 (blue)"),
        ("mode", "模式", lambda v: "信号 (signal)" if v == "signal" else "干扰 (noise)"),
        ("frequency", "频率", lambda v: f"{v / 1e6:.3f} MHz"),
        ("bandwidth", "低通带宽", lambda v: f"{v / 1e3:.0f} kHz"),
        ("sensitivity", "解调灵敏度", lambda v: f"{v:.4f}"),
        ("sdr_uri", "SDR URI", str),
        ("tcp_port", "TCP 端口", lambda v: f"{v} (noise key)"),
        ("access_code", "访问码", lambda v: f"{v[:24]}…"),
    ]

    # rows whose value cell carries a color swatch indicator
    _SWATCH_ROWS = ("side", "mode")
    # per-row swatch size; the side indicator is the emphasis
    _SWATCH_SIZES = {"side": 32, "mode": 22}

    _COLOR_RED = "#E64C3C"
    _COLOR_BLUE = "#3B82F6"
    _COLOR_NOISE = "#F5A623"
    _COLOR_SIGNAL = "#2ECC71"

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
        self.swatches: dict[str, Qt.QLabel] = {}
        for key, label_text, _fmt in self._CONFIG_ROWS:
            value = Qt.QLabel("—")
            value.setTextInteractionFlags(Qt.Qt.TextSelectableByMouse)
            value_font = value.font()
            value_font.setPointSize(13)
            value.setFont(value_font)
            self.value_labels[key] = value
            if key in self._SWATCH_ROWS:
                cell = Qt.QWidget()
                cell_layout = Qt.QHBoxLayout(cell)
                cell_layout.setContentsMargins(0, 0, 0, 0)
                cell_layout.setSpacing(8)
                swatch = self._make_swatch(self._SWATCH_SIZES[key])
                self.swatches[key] = swatch
                cell_layout.addWidget(swatch)
                cell_layout.addWidget(value)
                form.addRow(self._make_name_label(label_text), cell)
            else:
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

    def _make_swatch(self, size: int) -> Qt.QLabel:
        swatch = Qt.QLabel()
        swatch.setFixedSize(size, size)
        self._set_swatch_color(swatch, None)
        return swatch

    @staticmethod
    def _set_swatch_color(swatch: Qt.QLabel, color: str | None) -> None:
        if color:
            swatch.setStyleSheet(
                f"background-color: {color}; border-radius: {SdrStatusWindow._SWATCH_SIZES['side'] // 5}px;"
            )
        else:
            swatch.setStyleSheet("background-color: transparent;")

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
        self._apply_swatches(config)

    def _apply_swatches(self, config: dict | None) -> None:
        side = config.get("side") if config else None
        mode = config.get("mode") if config else None
        side_swatch = self.swatches.get("side")
        mode_swatch = self.swatches.get("mode")
        if side_swatch is not None:
            self._set_swatch_color(
                side_swatch,
                {
                    "red": self._COLOR_RED,
                    "blue": self._COLOR_BLUE,
                }.get(side),
            )
        if mode_swatch is not None:
            self._set_swatch_color(
                mode_swatch,
                {
                    "signal": self._COLOR_SIGNAL,
                    "noise": self._COLOR_NOISE,
                }.get(mode),
            )

    def closeEvent(self, event) -> None:
        event.ignore()
        self.hide()
        print("Status window hidden (SDR keeps running, 退出 button / Ctrl+C to stop)")
