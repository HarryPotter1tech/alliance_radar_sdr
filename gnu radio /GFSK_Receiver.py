#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: GFSK_Receiver
# Author: huangziang
# GNU Radio version: 3.10.1.1

from packaging.version import Version as StrictVersion

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print("Warning: failed to XInitThreads()")

from PyQt5 import Qt
from PyQt5.QtCore import QObject, pyqtSlot
from gnuradio import qtgui
from gnuradio.filter import firdes
import sip
from gnuradio import blocks
import math
from gnuradio import digital
from gnuradio import filter
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import iio
from gnuradio import network



from gnuradio import qtgui

class GFSK_Receiver(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "GFSK_Receiver", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("GFSK_Receiver")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
            pass
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "GFSK_Receiver")

        try:
            if StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
                self.restoreGeometry(self.settings.value("geometry").toByteArray())
            else:
                self.restoreGeometry(self.settings.value("geometry"))
        except:
            pass

        ##################################################
        # Variables
        ##################################################
        self.noise_grade_chooser = noise_grade_chooser = 'noise_1'
        self.configs = configs = {
            "noise_1"
                : {"noise_sensitivity" : 2.8323, "noise_frequency" : 432200000, "noise_bandwidth" : 940000}
                , "noise_2"
                : {"noise_sensitivity" : 2.5809, "noise_frequency" : 432500000, "noise_bandwidth" : 860000}
                , "noise_3"
                : {"noise_sensitivity" : 0.6646, "noise_frequency" : 432800000, "noise_bandwidth" : 250000}
        }
        self.signal_sensitivity = signal_sensitivity = 1.5756
        self.signal_frequency = signal_frequency = 433200000
        self.signal_bandwidth = signal_bandwidth = 540000
        self.selector_port = selector_port = 1
        self.sample_rate = sample_rate = 1000000
        self.noise_sensitivity = noise_sensitivity = configs[noise_grade_chooser]["noise_sensitivity"]
        self.noise_frequency = noise_frequency = configs[noise_grade_chooser]["noise_frequency"]
        self.noise_bandwidth = noise_bandwidth = configs[noise_grade_chooser]["noise_bandwidth"]
        self.SPS = SPS = 52

        ##################################################
        # Blocks
        ##################################################
        self.qtgui_time_sink_x_0_0_0_0_0_0_0_2_0_0 = qtgui.time_sink_c(
            2048, #size
            sample_rate*2, #samp_rate
            "noise滤波输出", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_0_0_0_0_0_0_0_2_0_0.set_update_time(1)
        self.qtgui_time_sink_x_0_0_0_0_0_0_0_2_0_0.set_y_axis(-6, 6)

        self.qtgui_time_sink_x_0_0_0_0_0_0_0_2_0_0.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0_0_0_0_0_0_0_2_0_0.enable_tags(True)
        self.qtgui_time_sink_x_0_0_0_0_0_0_0_2_0_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_0_0_0_0_0_0_0_2_0_0.enable_autoscale(True)
        self.qtgui_time_sink_x_0_0_0_0_0_0_0_2_0_0.enable_grid(True)
        self.qtgui_time_sink_x_0_0_0_0_0_0_0_2_0_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0_0_0_0_0_0_0_2_0_0.enable_control_panel(True)
        self.qtgui_time_sink_x_0_0_0_0_0_0_0_2_0_0.enable_stem_plot(False)


        labels = ['signal_output_re', 'signal_output_im', 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['cyan', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [4, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(2):
            if len(labels[i]) == 0:
                if (i % 2 == 0):
                    self.qtgui_time_sink_x_0_0_0_0_0_0_0_2_0_0.set_line_label(i, "Re{{Data {0}}}".format(i/2))
                else:
                    self.qtgui_time_sink_x_0_0_0_0_0_0_0_2_0_0.set_line_label(i, "Im{{Data {0}}}".format(i/2))
            else:
                self.qtgui_time_sink_x_0_0_0_0_0_0_0_2_0_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0_0_0_0_0_0_0_2_0_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0_0_0_0_0_0_0_2_0_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0_0_0_0_0_0_0_2_0_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0_0_0_0_0_0_0_2_0_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0_0_0_0_0_0_0_2_0_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_0_0_0_0_0_0_2_0_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0_0_0_0_0_0_0_2_0_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_0_0_0_0_0_0_0_2_0_0_win)
        self.qtgui_time_sink_x_0_0_0_0_0_0_0_2 = qtgui.time_sink_c(
            2048, #size
            sample_rate*2, #samp_rate
            "signal滤波输出", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_0_0_0_0_0_0_0_2.set_update_time(1)
        self.qtgui_time_sink_x_0_0_0_0_0_0_0_2.set_y_axis(-6, 6)

        self.qtgui_time_sink_x_0_0_0_0_0_0_0_2.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0_0_0_0_0_0_0_2.enable_tags(True)
        self.qtgui_time_sink_x_0_0_0_0_0_0_0_2.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_0_0_0_0_0_0_0_2.enable_autoscale(True)
        self.qtgui_time_sink_x_0_0_0_0_0_0_0_2.enable_grid(True)
        self.qtgui_time_sink_x_0_0_0_0_0_0_0_2.enable_axis_labels(True)
        self.qtgui_time_sink_x_0_0_0_0_0_0_0_2.enable_control_panel(True)
        self.qtgui_time_sink_x_0_0_0_0_0_0_0_2.enable_stem_plot(False)


        labels = ['signal_output_re', 'signal_output_im', 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['cyan', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [4, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(2):
            if len(labels[i]) == 0:
                if (i % 2 == 0):
                    self.qtgui_time_sink_x_0_0_0_0_0_0_0_2.set_line_label(i, "Re{{Data {0}}}".format(i/2))
                else:
                    self.qtgui_time_sink_x_0_0_0_0_0_0_0_2.set_line_label(i, "Im{{Data {0}}}".format(i/2))
            else:
                self.qtgui_time_sink_x_0_0_0_0_0_0_0_2.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0_0_0_0_0_0_0_2.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0_0_0_0_0_0_0_2.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0_0_0_0_0_0_0_2.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0_0_0_0_0_0_0_2.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0_0_0_0_0_0_0_2.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_0_0_0_0_0_0_2_win = sip.wrapinstance(self.qtgui_time_sink_x_0_0_0_0_0_0_0_2.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_0_0_0_0_0_0_0_2_win)
        self.qtgui_time_sink_x_0_0_0_0_0_0_0_1_0_0 = qtgui.time_sink_f(
            2048, #size
            sample_rate / SPS, #samp_rate
            "noise接收bits", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_0_0_0_0_0_0_0_1_0_0.set_update_time(1)
        self.qtgui_time_sink_x_0_0_0_0_0_0_0_1_0_0.set_y_axis(-6, 6)

        self.qtgui_time_sink_x_0_0_0_0_0_0_0_1_0_0.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0_0_0_0_0_0_0_1_0_0.enable_tags(True)
        self.qtgui_time_sink_x_0_0_0_0_0_0_0_1_0_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_0_0_0_0_0_0_0_1_0_0.enable_autoscale(True)
        self.qtgui_time_sink_x_0_0_0_0_0_0_0_1_0_0.enable_grid(True)
        self.qtgui_time_sink_x_0_0_0_0_0_0_0_1_0_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0_0_0_0_0_0_0_1_0_0.enable_control_panel(True)
        self.qtgui_time_sink_x_0_0_0_0_0_0_0_1_0_0.enable_stem_plot(False)


        labels = ['signal_output_re', 'signal_output_im', 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['cyan', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [4, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_time_sink_x_0_0_0_0_0_0_0_1_0_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_0_0_0_0_0_0_0_1_0_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0_0_0_0_0_0_0_1_0_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0_0_0_0_0_0_0_1_0_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0_0_0_0_0_0_0_1_0_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0_0_0_0_0_0_0_1_0_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0_0_0_0_0_0_0_1_0_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_0_0_0_0_0_0_1_0_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0_0_0_0_0_0_0_1_0_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_0_0_0_0_0_0_0_1_0_0_win)
        self.qtgui_time_sink_x_0_0_0_0_0_0_0_1 = qtgui.time_sink_f(
            2048, #size
            sample_rate / SPS, #samp_rate
            "signal接收bits", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_0_0_0_0_0_0_0_1.set_update_time(1)
        self.qtgui_time_sink_x_0_0_0_0_0_0_0_1.set_y_axis(-6, 6)

        self.qtgui_time_sink_x_0_0_0_0_0_0_0_1.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0_0_0_0_0_0_0_1.enable_tags(True)
        self.qtgui_time_sink_x_0_0_0_0_0_0_0_1.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_0_0_0_0_0_0_0_1.enable_autoscale(True)
        self.qtgui_time_sink_x_0_0_0_0_0_0_0_1.enable_grid(True)
        self.qtgui_time_sink_x_0_0_0_0_0_0_0_1.enable_axis_labels(True)
        self.qtgui_time_sink_x_0_0_0_0_0_0_0_1.enable_control_panel(True)
        self.qtgui_time_sink_x_0_0_0_0_0_0_0_1.enable_stem_plot(False)


        labels = ['signal_output_re', 'signal_output_im', 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['cyan', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [4, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_time_sink_x_0_0_0_0_0_0_0_1.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_0_0_0_0_0_0_0_1.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0_0_0_0_0_0_0_1.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0_0_0_0_0_0_0_1.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0_0_0_0_0_0_0_1.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0_0_0_0_0_0_0_1.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0_0_0_0_0_0_0_1.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_0_0_0_0_0_0_1_win = sip.wrapinstance(self.qtgui_time_sink_x_0_0_0_0_0_0_0_1.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_0_0_0_0_0_0_0_1_win)
        self.qtgui_freq_sink_x_0_0_1_0 = qtgui.freq_sink_c(
            8192, #size
            window.WIN_HAMMING, #wintype
            noise_frequency, #fc
            sample_rate*2, #bw
            "GFSK-noise滤波后频率图", #name
            1,
            None # parent
        )
        self.qtgui_freq_sink_x_0_0_1_0.set_update_time(1)
        self.qtgui_freq_sink_x_0_0_1_0.set_y_axis(-70, 0)
        self.qtgui_freq_sink_x_0_0_1_0.set_y_label('db', 'dB')
        self.qtgui_freq_sink_x_0_0_1_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_0_0_1_0.enable_autoscale(True)
        self.qtgui_freq_sink_x_0_0_1_0.enable_grid(False)
        self.qtgui_freq_sink_x_0_0_1_0.set_fft_average(0.05)
        self.qtgui_freq_sink_x_0_0_1_0.enable_axis_labels(True)
        self.qtgui_freq_sink_x_0_0_1_0.enable_control_panel(True)
        self.qtgui_freq_sink_x_0_0_1_0.set_fft_window_normalized(False)



        labels = ['frequency', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["dark blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_0_0_1_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_0_0_1_0.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_0_0_1_0.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_0_0_1_0.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_0_0_1_0.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_0_0_1_0_win = sip.wrapinstance(self.qtgui_freq_sink_x_0_0_1_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_freq_sink_x_0_0_1_0_win)
        self.qtgui_freq_sink_x_0_0_0 = qtgui.freq_sink_c(
            8192, #size
            window.WIN_HAMMING, #wintype
            signal_frequency, #fc
            sample_rate*2, #bw
            "GFSK-频率图", #name
            1,
            None # parent
        )
        self.qtgui_freq_sink_x_0_0_0.set_update_time(1)
        self.qtgui_freq_sink_x_0_0_0.set_y_axis(-70, 0)
        self.qtgui_freq_sink_x_0_0_0.set_y_label('db', 'dB')
        self.qtgui_freq_sink_x_0_0_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_0_0_0.enable_autoscale(True)
        self.qtgui_freq_sink_x_0_0_0.enable_grid(False)
        self.qtgui_freq_sink_x_0_0_0.set_fft_average(0.05)
        self.qtgui_freq_sink_x_0_0_0.enable_axis_labels(True)
        self.qtgui_freq_sink_x_0_0_0.enable_control_panel(True)
        self.qtgui_freq_sink_x_0_0_0.set_fft_window_normalized(False)



        labels = ['frequency', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["dark blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_0_0_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_0_0_0.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_0_0_0.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_0_0_0.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_0_0_0.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_0_0_0_win = sip.wrapinstance(self.qtgui_freq_sink_x_0_0_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_freq_sink_x_0_0_0_win)
        self.qtgui_freq_sink_x_0_0 = qtgui.freq_sink_c(
            8192, #size
            window.WIN_HAMMING, #wintype
            signal_frequency, #fc
            sample_rate*2, #bw
            "GFSK-signal滤波后频率图", #name
            1,
            None # parent
        )
        self.qtgui_freq_sink_x_0_0.set_update_time(1)
        self.qtgui_freq_sink_x_0_0.set_y_axis(-70, 0)
        self.qtgui_freq_sink_x_0_0.set_y_label('db', 'dB')
        self.qtgui_freq_sink_x_0_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_0_0.enable_autoscale(True)
        self.qtgui_freq_sink_x_0_0.enable_grid(False)
        self.qtgui_freq_sink_x_0_0.set_fft_average(0.05)
        self.qtgui_freq_sink_x_0_0.enable_axis_labels(True)
        self.qtgui_freq_sink_x_0_0.enable_control_panel(True)
        self.qtgui_freq_sink_x_0_0.set_fft_window_normalized(False)



        labels = ['frequency', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["dark blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_0_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_0_0.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_0_0.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_0_0.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_0_0.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_0_0_win = sip.wrapinstance(self.qtgui_freq_sink_x_0_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_freq_sink_x_0_0_win)
        # Create the options list
        self._noise_grade_chooser_options = ['noise_1', 'noise_2', 'noise_3']
        # Create the labels list
        self._noise_grade_chooser_labels = ['一级干扰源', '二级干扰源', '三级干扰源']
        # Create the combo box
        # Create the radio buttons
        self._noise_grade_chooser_group_box = Qt.QGroupBox("干扰源等级" + ": ")
        self._noise_grade_chooser_box = Qt.QVBoxLayout()
        class variable_chooser_button_group(Qt.QButtonGroup):
            def __init__(self, parent=None):
                Qt.QButtonGroup.__init__(self, parent)
            @pyqtSlot(int)
            def updateButtonChecked(self, button_id):
                self.button(button_id).setChecked(True)
        self._noise_grade_chooser_button_group = variable_chooser_button_group()
        self._noise_grade_chooser_group_box.setLayout(self._noise_grade_chooser_box)
        for i, _label in enumerate(self._noise_grade_chooser_labels):
            radio_button = Qt.QRadioButton(_label)
            self._noise_grade_chooser_box.addWidget(radio_button)
            self._noise_grade_chooser_button_group.addButton(radio_button, i)
        self._noise_grade_chooser_callback = lambda i: Qt.QMetaObject.invokeMethod(self._noise_grade_chooser_button_group, "updateButtonChecked", Qt.Q_ARG("int", self._noise_grade_chooser_options.index(i)))
        self._noise_grade_chooser_callback(self.noise_grade_chooser)
        self._noise_grade_chooser_button_group.buttonClicked[int].connect(
            lambda i: self.set_noise_grade_chooser(self._noise_grade_chooser_options[i]))
        self.top_layout.addWidget(self._noise_grade_chooser_group_box)
        self.network_tcp_sink_0_0_0 = network.tcp_sink(gr.sizeof_char, 1, '127.0.0.1', 2500,2)
        self.network_tcp_sink_0 = network.tcp_sink(gr.sizeof_char, 1, '127.0.0.1', 2000,2)
        self.low_pass_filter_0_0_0 = filter.fir_filter_ccf(
            1,
            firdes.low_pass(
                1,
                sample_rate,
                500000,
                10000,
                window.WIN_HAMMING,
                6.76))
        self.low_pass_filter_0 = filter.fir_filter_ccf(
            1,
            firdes.low_pass(
                1,
                sample_rate,
                260000,
                10000,
                window.WIN_HAMMING,
                6.76))
        self.iio_pluto_source_0 = iio.fmcomms2_source_fc32('192.168.1.10' if '192.168.1.10' else iio.get_pluto_uri(), [True, True], 32768)
        self.iio_pluto_source_0.set_len_tag_key('packet_len')
        self.iio_pluto_source_0.set_frequency(signal_frequency)
        self.iio_pluto_source_0.set_samplerate(sample_rate*4)
        self.iio_pluto_source_0.set_gain_mode(0, 'manual')
        self.iio_pluto_source_0.set_gain(0, 60)
        self.iio_pluto_source_0.set_quadrature(True)
        self.iio_pluto_source_0.set_rfdc(True)
        self.iio_pluto_source_0.set_bbdc(True)
        self.iio_pluto_source_0.set_filter_params('Auto', '', 0, 0)
        self.digital_gfsk_demod_0_0_0 = digital.gfsk_demod(
            samples_per_symbol=SPS,
            sensitivity=1/noise_sensitivity,
            gain_mu=0.175,
            mu=0.5,
            omega_relative_limit=0.05,
            freq_error=0.05,
            verbose=False,
            log=False)
        self.digital_gfsk_demod_0 = digital.gfsk_demod(
            samples_per_symbol=SPS,
            sensitivity=1/signal_sensitivity,
            gain_mu=0.175,
            mu=0.5,
            omega_relative_limit=0.05,
            freq_error=0.05,
            verbose=False,
            log=False)
        self.digital_correlate_access_code_xx_ts_0_0_0 = digital.correlate_access_code_bb_ts('0001011011101000110100110111011100010101000111000111000100101101',
          12, 'access_code+header')
        self.digital_correlate_access_code_xx_ts_0 = digital.correlate_access_code_bb_ts('0010111101101111010011000111010010111001000101000100100100101110',
          12, 'access_code+header')
        self.blocks_stream_to_tagged_stream_0_0_0 = blocks.stream_to_tagged_stream(gr.sizeof_char, 1, 15, "packet_len")
        self.blocks_stream_to_tagged_stream_0 = blocks.stream_to_tagged_stream(gr.sizeof_char, 1, 15, "packet_len")
        self.blocks_pack_k_bits_bb_0_0_0 = blocks.pack_k_bits_bb(8)
        self.blocks_pack_k_bits_bb_0 = blocks.pack_k_bits_bb(8)
        self.blocks_freqshift_cc_0 = blocks.rotator_cc(2.0*math.pi*1000000/sample_rate*4)
        self.blocks_file_sink_0_0 = blocks.file_sink(gr.sizeof_char*1, '/home/pinkpanda/linux-RADAR/RADAR-2026/RADAR-SDR/receive.bin', False)
        self.blocks_file_sink_0_0.set_unbuffered(False)
        self.blocks_char_to_float_0_0_0_0 = blocks.char_to_float(1, 1)
        self.blocks_char_to_float_0_0 = blocks.char_to_float(1, 1)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_char_to_float_0_0, 0), (self.qtgui_time_sink_x_0_0_0_0_0_0_0_1, 0))
        self.connect((self.blocks_char_to_float_0_0_0_0, 0), (self.qtgui_time_sink_x_0_0_0_0_0_0_0_1_0_0, 0))
        self.connect((self.blocks_freqshift_cc_0, 0), (self.low_pass_filter_0_0_0, 0))
        self.connect((self.blocks_pack_k_bits_bb_0, 0), (self.blocks_stream_to_tagged_stream_0, 0))
        self.connect((self.blocks_pack_k_bits_bb_0_0_0, 0), (self.blocks_stream_to_tagged_stream_0_0_0, 0))
        self.connect((self.blocks_stream_to_tagged_stream_0, 0), (self.network_tcp_sink_0, 0))
        self.connect((self.blocks_stream_to_tagged_stream_0_0_0, 0), (self.blocks_file_sink_0_0, 0))
        self.connect((self.blocks_stream_to_tagged_stream_0_0_0, 0), (self.network_tcp_sink_0_0_0, 0))
        self.connect((self.digital_correlate_access_code_xx_ts_0, 0), (self.blocks_pack_k_bits_bb_0, 0))
        self.connect((self.digital_correlate_access_code_xx_ts_0_0_0, 0), (self.blocks_pack_k_bits_bb_0_0_0, 0))
        self.connect((self.digital_gfsk_demod_0, 0), (self.blocks_char_to_float_0_0, 0))
        self.connect((self.digital_gfsk_demod_0, 0), (self.digital_correlate_access_code_xx_ts_0, 0))
        self.connect((self.digital_gfsk_demod_0_0_0, 0), (self.blocks_char_to_float_0_0_0_0, 0))
        self.connect((self.digital_gfsk_demod_0_0_0, 0), (self.digital_correlate_access_code_xx_ts_0_0_0, 0))
        self.connect((self.iio_pluto_source_0, 0), (self.blocks_freqshift_cc_0, 0))
        self.connect((self.iio_pluto_source_0, 0), (self.low_pass_filter_0, 0))
        self.connect((self.iio_pluto_source_0, 0), (self.qtgui_freq_sink_x_0_0_0, 0))
        self.connect((self.low_pass_filter_0, 0), (self.digital_gfsk_demod_0, 0))
        self.connect((self.low_pass_filter_0, 0), (self.qtgui_freq_sink_x_0_0, 0))
        self.connect((self.low_pass_filter_0, 0), (self.qtgui_time_sink_x_0_0_0_0_0_0_0_2, 0))
        self.connect((self.low_pass_filter_0_0_0, 0), (self.digital_gfsk_demod_0_0_0, 0))
        self.connect((self.low_pass_filter_0_0_0, 0), (self.qtgui_freq_sink_x_0_0_1_0, 0))
        self.connect((self.low_pass_filter_0_0_0, 0), (self.qtgui_time_sink_x_0_0_0_0_0_0_0_2_0_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "GFSK_Receiver")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_noise_grade_chooser(self):
        return self.noise_grade_chooser

    def set_noise_grade_chooser(self, noise_grade_chooser):
        self.noise_grade_chooser = noise_grade_chooser
        self.set_noise_bandwidth(self.configs[self.noise_grade_chooser]["noise_bandwidth"])
        self.set_noise_frequency(self.configs[self.noise_grade_chooser]["noise_frequency"])
        self._noise_grade_chooser_callback(self.noise_grade_chooser)
        self.set_noise_sensitivity(self.configs[self.noise_grade_chooser]["noise_sensitivity"])

    def get_configs(self):
        return self.configs

    def set_configs(self, configs):
        self.configs = configs
        self.set_noise_bandwidth(self.configs[self.noise_grade_chooser]["noise_bandwidth"])
        self.set_noise_frequency(self.configs[self.noise_grade_chooser]["noise_frequency"])
        self.set_noise_sensitivity(self.configs[self.noise_grade_chooser]["noise_sensitivity"])

    def get_signal_sensitivity(self):
        return self.signal_sensitivity

    def set_signal_sensitivity(self, signal_sensitivity):
        self.signal_sensitivity = signal_sensitivity

    def get_signal_frequency(self):
        return self.signal_frequency

    def set_signal_frequency(self, signal_frequency):
        self.signal_frequency = signal_frequency
        self.iio_pluto_source_0.set_frequency(self.signal_frequency)
        self.qtgui_freq_sink_x_0_0.set_frequency_range(self.signal_frequency, self.sample_rate*2)
        self.qtgui_freq_sink_x_0_0_0.set_frequency_range(self.signal_frequency, self.sample_rate*2)

    def get_signal_bandwidth(self):
        return self.signal_bandwidth

    def set_signal_bandwidth(self, signal_bandwidth):
        self.signal_bandwidth = signal_bandwidth

    def get_selector_port(self):
        return self.selector_port

    def set_selector_port(self, selector_port):
        self.selector_port = selector_port

    def get_sample_rate(self):
        return self.sample_rate

    def set_sample_rate(self, sample_rate):
        self.sample_rate = sample_rate
        self.blocks_freqshift_cc_0.set_phase_inc(2.0*math.pi*1000000/self.sample_rate*4)
        self.iio_pluto_source_0.set_samplerate(self.sample_rate*4)
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.sample_rate, 260000, 10000, window.WIN_HAMMING, 6.76))
        self.low_pass_filter_0_0_0.set_taps(firdes.low_pass(1, self.sample_rate, 500000, 10000, window.WIN_HAMMING, 6.76))
        self.qtgui_freq_sink_x_0_0.set_frequency_range(self.signal_frequency, self.sample_rate*2)
        self.qtgui_freq_sink_x_0_0_0.set_frequency_range(self.signal_frequency, self.sample_rate*2)
        self.qtgui_freq_sink_x_0_0_1_0.set_frequency_range(self.noise_frequency, self.sample_rate*2)
        self.qtgui_time_sink_x_0_0_0_0_0_0_0_1.set_samp_rate(self.sample_rate / self.SPS)
        self.qtgui_time_sink_x_0_0_0_0_0_0_0_1_0_0.set_samp_rate(self.sample_rate / self.SPS)
        self.qtgui_time_sink_x_0_0_0_0_0_0_0_2.set_samp_rate(self.sample_rate*2)
        self.qtgui_time_sink_x_0_0_0_0_0_0_0_2_0_0.set_samp_rate(self.sample_rate*2)

    def get_noise_sensitivity(self):
        return self.noise_sensitivity

    def set_noise_sensitivity(self, noise_sensitivity):
        self.noise_sensitivity = noise_sensitivity

    def get_noise_frequency(self):
        return self.noise_frequency

    def set_noise_frequency(self, noise_frequency):
        self.noise_frequency = noise_frequency
        self.qtgui_freq_sink_x_0_0_1_0.set_frequency_range(self.noise_frequency, self.sample_rate*2)

    def get_noise_bandwidth(self):
        return self.noise_bandwidth

    def set_noise_bandwidth(self, noise_bandwidth):
        self.noise_bandwidth = noise_bandwidth

    def get_SPS(self):
        return self.SPS

    def set_SPS(self, SPS):
        self.SPS = SPS
        self.qtgui_time_sink_x_0_0_0_0_0_0_0_1.set_samp_rate(self.sample_rate / self.SPS)
        self.qtgui_time_sink_x_0_0_0_0_0_0_0_1_0_0.set_samp_rate(self.sample_rate / self.SPS)




def main(top_block_cls=GFSK_Receiver, options=None):

    if StrictVersion("4.5.0") <= StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
