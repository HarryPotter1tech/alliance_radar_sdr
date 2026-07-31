#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: GFSK-RX
# Author: huangziang
# GNU Radio version: 3.10.7.0

from gnuradio import blocks
from gnuradio import digital
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import iio
from gnuradio import network




class GFSK_RX(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "GFSK-RX", catch_exceptions=True)

        ##################################################
        # Variables
        ##################################################
        self.tcp_port = tcp_port = globals().get('CONFIG', {}).get('tcp_port', 2500)
        self.sdr_uri = sdr_uri = globals().get('CONFIG', {}).get('sdr_uri', '192.168.1.10')
        self.sample_rate = sample_rate = 1000000
        self.rx_frequency = rx_frequency = globals().get('CONFIG', {}).get('frequency', 432200000)
        self.pi = pi = 3.141592653589793
        self.lpf_cutoff = lpf_cutoff = globals().get('CONFIG', {}).get('bandwidth', 500000)
        self.demod_sensitivity = demod_sensitivity = globals().get('CONFIG', {}).get('sensitivity', 2.8194)
        self.access_code = access_code = globals().get('CONFIG', {}).get('access_code', '0001011011101000110100110111011100010101000111000111000100101101')
        self.SPS = SPS = 47

        ##################################################
        # Blocks
        ##################################################

        self.network_tcp_sink_0_0 = network.tcp_sink(gr.sizeof_char, 1, '127.0.0.1', tcp_port,2)
        self.low_pass_filter_0_0 = filter.fir_filter_ccf(
            1,
            firdes.low_pass(
                1,
                sample_rate,
                lpf_cutoff,
                10000,
                window.WIN_HAMMING,
                6.76))
        self.iio_pluto_source_1 = iio.fmcomms2_source_fc32(sdr_uri if sdr_uri else iio.get_pluto_uri(), [True, True], 32768)
        self.iio_pluto_source_1.set_len_tag_key('packet_len')
        self.iio_pluto_source_1.set_frequency(rx_frequency)
        self.iio_pluto_source_1.set_samplerate(sample_rate)
        self.iio_pluto_source_1.set_gain_mode(0, 'manual')
        self.iio_pluto_source_1.set_gain(0, 60)
        self.iio_pluto_source_1.set_quadrature(True)
        self.iio_pluto_source_1.set_rfdc(True)
        self.iio_pluto_source_1.set_bbdc(True)
        self.iio_pluto_source_1.set_filter_params('Auto', '', 0, 0)
        self.digital_gfsk_demod_0_0 = digital.gfsk_demod(
            samples_per_symbol=SPS,
            sensitivity=(1/demod_sensitivity),
            gain_mu=0.175,
            mu=0.5,
            omega_relative_limit=0.005,
            freq_error=0.0,
            verbose=False,
            log=False)
        self.digital_correlate_access_code_xx_ts_0_0 = digital.correlate_access_code_bb_ts(access_code,
          12, 'access_code+header')
        self.blocks_stream_to_tagged_stream_0_0 = blocks.stream_to_tagged_stream(gr.sizeof_char, 1, 15, "packet_len")
        self.blocks_pack_k_bits_bb_0 = blocks.pack_k_bits_bb(8)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_pack_k_bits_bb_0, 0), (self.blocks_stream_to_tagged_stream_0_0, 0))
        self.connect((self.blocks_stream_to_tagged_stream_0_0, 0), (self.network_tcp_sink_0_0, 0))
        self.connect((self.digital_correlate_access_code_xx_ts_0_0, 0), (self.blocks_pack_k_bits_bb_0, 0))
        self.connect((self.digital_gfsk_demod_0_0, 0), (self.digital_correlate_access_code_xx_ts_0_0, 0))
        self.connect((self.iio_pluto_source_1, 0), (self.low_pass_filter_0_0, 0))
        self.connect((self.low_pass_filter_0_0, 0), (self.digital_gfsk_demod_0_0, 0))


    def get_tcp_port(self):
        return self.tcp_port

    def set_tcp_port(self, tcp_port):
        self.tcp_port = tcp_port

    def get_sdr_uri(self):
        return self.sdr_uri

    def set_sdr_uri(self, sdr_uri):
        self.sdr_uri = sdr_uri

    def get_sample_rate(self):
        return self.sample_rate

    def set_sample_rate(self, sample_rate):
        self.sample_rate = sample_rate
        self.iio_pluto_source_1.set_samplerate(self.sample_rate)
        self.low_pass_filter_0_0.set_taps(firdes.low_pass(1, self.sample_rate, self.lpf_cutoff, 10000, window.WIN_HAMMING, 6.76))

    def get_rx_frequency(self):
        return self.rx_frequency

    def set_rx_frequency(self, rx_frequency):
        self.rx_frequency = rx_frequency
        self.iio_pluto_source_1.set_frequency(self.rx_frequency)

    def get_pi(self):
        return self.pi

    def set_pi(self, pi):
        self.pi = pi

    def get_lpf_cutoff(self):
        return self.lpf_cutoff

    def set_lpf_cutoff(self, lpf_cutoff):
        self.lpf_cutoff = lpf_cutoff
        self.low_pass_filter_0_0.set_taps(firdes.low_pass(1, self.sample_rate, self.lpf_cutoff, 10000, window.WIN_HAMMING, 6.76))

    def get_demod_sensitivity(self):
        return self.demod_sensitivity

    def set_demod_sensitivity(self, demod_sensitivity):
        self.demod_sensitivity = demod_sensitivity

    def get_access_code(self):
        return self.access_code

    def set_access_code(self, access_code):
        self.access_code = access_code

    def get_SPS(self):
        return self.SPS

    def set_SPS(self, SPS):
        self.SPS = SPS




def main(top_block_cls=GFSK_RX, options=None):
    tb = top_block_cls()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()

    try:
        input('Press Enter to quit: ')
    except EOFError:
        pass
    tb.stop()
    tb.wait()


if __name__ == '__main__':
    main()
