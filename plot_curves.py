# AUTHOR:	Gyanranjan Hazarika - gyanranjanh@gmail.com
# Copyright (c) 2015-2016, All Rights Reserved.

import os
import sys
import csv
import argparse
import matplotlib

# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from mpl_toolkits.axes_grid.anchored_artists import AnchoredText


class Reader(object):
    def __init__(self, ip_file):
        self.options = {}
        self.csv_file_reader = None
        self.ip_file = ''
        try:
            if ip_file != '':
                self.fh = open(ip_file, 'r')
                self.ip_file = ip_file
            else:
                self.fh = None  # file handle
        except IOError as e:
            print 'File open failed...', e

    def parse_arguments(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-i", dest="input_csv_file", action="store", default=None, type=str,
                            help="Input file required")
        self.options = parser.parse_args()

    def process_arguments(self):
        if not self.options.input_csv_file:
            raise Exception("Please specify an input csv file.")
        if not os.path.exists(self.options.input_csv_file):
            self.options.input_csv_file = os.path.abspath(self.input_csv_file)
        if not os.path.exists(self.options.input_csv_file) or not os.path.isfile(self.options.input_csv_file):
            raise Exception("Input file does not exist: %s" % self.options.input_csv_file)
        else:
            self.ip_file = self.options.input_csv_file

    def _get_filehandle(self):
        if not self.fh:
            self.fh = open(self.options.input_csv_file, 'r')

        return self.fh

    def _release_filehandle(self):
        if self.fh:
            self.fh.close()

    def get_csv_reader(self):
        csv_reader = None
        try:
            if self.options.input_csv_file:
                fh = self._get_filehandle()
                if fh:
                    csv_reader = csv.reader(fh)
                else:
                    print "Invalid file handle"
            else:
                print 'Input file not found'
        except Exception as e:
            # does the file handle exist
            # if it does the get the csv_reader
            fh = self._get_filehandle()
            if fh:
                csv_reader = csv.reader(fh)
            else:
                print "Invalid file handle"
        return csv_reader

    def get_ip_file(self):
        return self.ip_file

    def get_csv_dict_reader(self):
        csv_dict_reader = None
        if self.options.input_csv_file:
            fh = self._get_filehandle()
            if fh:
                csv_dict_reader = csv.DictReader()
            else:
                print "Invalid file handle"
        else:
            print 'Input file not found'
        return csv_dict_reader

    def release_csv_reader(self):
        self._release_filehandle()

    def release_csv_dict_reader(self):
        self._release_filehandle()


class PlotGraph(object):
    def __init__(self, file_reader=None):
        self.file_reader = file_reader
        self.pp = None
        self.pdffacecolor = 'lightblue'

    def init_multipage_pdf(self, file_name='power_frequency_stats.pdf'):
        self.pp = PdfPages(file_name)
        return self.pp

    def deinit_multipage_pdf(self):
        if self.pp:
            self.pp.close()

    @staticmethod
    def millicent_to_cent(ip_array):
        for _indx_, _item_ in enumerate(ip_array):
            if _item_ and not _item_.isspace():
                ip_array[_indx_] = float(_item_) / 10 ** 3
            else:
                # print 'temp value not available at time instant: ', _timestamps[indx], '- normalizing'
                avg = 0
                if _indx_ > 0:
                    avg = float(ip_array[_indx_ - 1])
                if len(ip_array) > (_indx_ + 1) \
                        and ip_array[_indx_ + 1] \
                        and not ip_array[_indx_ + 1].isspace:  # check whether the list element exists or not
                    avg += float(ip_array[_indx_ + 1]) / 10 ** 3
                    avg /= 2
                ip_array[_indx_] = avg
            # print 'value after normalization: ', avg

    @staticmethod
    def count_digit(number):
        """
		:param number:
		:return: no of digits in number
		"""
        no_of_digit = 0
        while number > 0:
            number = int(number / 10)
            no_of_digit += 1
        return no_of_digit

    @staticmethod
    def process_timestamps(timestamps):
        """
		:param timestamps:
		:return: nothing
		process timestamps to get rid of unwanted start offset.
		Python timestamps are typically from epoch, given by time.time()
		"""
        count_timestamps = len(timestamps)
        # print count_timestamps

        '''How many digits are there in count_timestamp'''
        no_digit_ctimestamps = PlotGraph.count_digit(count_timestamps)
        timestamp_adjust_factor = 10 ** no_digit_ctimestamps

        '''Readjust 'timestamp_adjust_factor' by checking whether the
		(count_timestamps+1)th digit has changed or not'''
        # grab timestamps[0] and timestamps[-1] first
        timestamp_first = int(float(timestamps[0]) / timestamp_adjust_factor)
        timestamp_last = int(float(timestamps[-1]) / timestamp_adjust_factor)
        # readjust incrementally depending on the dissimilar digits
        while timestamp_first and timestamp_last:
            # grab the last digits
            lastdgt_timestamp_first = timestamp_first - (timestamp_first / 10) * 10
            timestamp_first /= 10
            lastdgt_timestamp_last = timestamp_last - (timestamp_last / 10) * 10
            timestamp_last /= 10
            if lastdgt_timestamp_first != lastdgt_timestamp_last:
                timestamp_adjust_factor *= 10
            else:
                break

        for indx, elem in enumerate(timestamps):
            timestamps[indx] = float(elem) % timestamp_adjust_factor

        '''code for scaling the timestamps to start at an offset of 0'''
        init_timestamp = timestamps[0]
        for indx, elem in enumerate(timestamps):
            timestamps[indx] = float(elem) - init_timestamp

    @staticmethod
    def chunks(l, n):
        for i in range(1, len(l), n):
            yield l[i:i + n]

    @staticmethod
    def add_text(axes, text):
        at = AnchoredText(text,
                          prop=dict(size=8), frameon=True,
                          loc=2,
                          )
        at.patch.set_boxstyle("round,pad=0.1,rounding_size=0.2")
        axes.add_artist(at)

    @staticmethod
    def hz_to_mhz(freq):
        for _idx_, _item_ in enumerate(freq):
            freq[_idx_] = float(_item_) / 10 ** 6

    @staticmethod
    def khz_to_mhz(freq):
        for _idx_, _item_ in enumerate(freq):
            freq[_idx_] = float(_item_) / 10 ** 3

    @staticmethod
    def min_max(yarray):
        y = []
        for item in yarray:
            y.append(float(item))
        return min(y), max(y)

    @staticmethod
    def average(yarray):
        y = []
        for item in yarray:
            y.append(float(item))
        return sum(y) / len(y)

    @staticmethod
    def fill_area_under_curve(axes, xarray, yarray, color, transparency, apply_ylimit=False):
        y = []
        for item in yarray:
            y.append(float(item))

        x = []
        for item in xarray:
            x.append(float(item))

        if apply_ylimit == True:
            plt.ylim((min(y), max(y)))
        axes.fill_between(x, y, alpha=transparency, color=color)

    def plot(self, *args, **kwargs):
        """ Plot as many as seven parameters in a single plot. The first
			parameter must be xarray
		"""
        try:
            if 2 > len(args) or len(args) > 8:
                print 'Must have more than or 2 and less than or 8 arguments'
            else:
                '''retrieve xarray and yarrays as _args'''
                xarray = args[0]
                _args = args[1:]

                '''Retrieve title, legends etc.'''
                if kwargs:
                    try:
                        title = u'{0}'.format(kwargs['title'])
                    except KeyError:
                        title = 'Unknown'
                    try:
                        multipagepdf = kwargs['multipagepdf']
                    except KeyError:
                        multipagepdf = None
                    try:
                        xlabel = u'{0}'.format(kwargs['xlabel'])
                    except KeyError:
                        xlabel = 'xlabel'
                    try:
                        mkr = u'{0}'.format(kwargs['marker'])
                    except KeyError:
                        mkr = '.'
                    try:
                        lstyle = u'{0}'.format(kwargs['linestyle'])
                    except KeyError:
                        lstyle = ''

                '''create a figure'''
                fig = plt.figure()
                fig.patch.set_facecolor(self.pdffacecolor)

                ax = fig.add_subplot(111)
                ax.set_title(title, fontsize=10, fontweight='bold')
                ax.set_xlabel(xlabel, fontsize=8, color='b')

                color = ['red', 'blue', 'green', 'darkorange', 'firebrick', 'k', 'darkcyan']

                '''Handle rest of the arguments by plotting along y-axis'''
                idx = 0
                text = ''
                for arg in _args:
                    if type(arg) is list:
                        if kwargs:
                            try:
                                ax.plot(xarray, arg, color=color[idx],
                                        label=kwargs['legend{0}'.format(idx)], alpha=0.8, linewidth=0.5,
                                        marker=mkr, linestyle=lstyle)
                                avg = PlotGraph.average(arg)
                                text1 = "=".join(['average_' + kwargs['legend{0}'.format(idx)], str(int(avg))])
                                if text == '':
                                    text = text1
                                else:
                                    text = ', '.join([text, text1])
                            except KeyError:
                                ax.plot(xarray, arg, color=color[idx],
                                        label='_'.join(['unknown', idx]), alpha=0.8, linewidth=0.5,
                                        marker=mkr, linestyle=lstyle)
                                avg = PlotGraph.average(arg),
                                text1 = "=".join(['average_' + '_'.join(['unknown', idx]), str(int(avg))])
                                text = ', '.join([text, text1])
                        else:  # TBD
                            ax.plot(xarray, arg, color=color[idx],
                                    label='_'.join(['unknown', idx]), alpha=0.8, linewidth=0.5)
                            avg = PlotGraph.average(arg),
                            text1 = "=".join(['average_' + '_'.join(['unknown', idx]), str(int(avg))])
                            text = ', '.join([text, text1])
                    idx += 1

                '''annotations'''
                #PlotGraph.add_text(ax, text)

                '''Limit control'''
                min_x, max_x = PlotGraph.min_max(xarray)
                plt.xlim(min_x, max_x + 10)

                '''Legend control'''
                ax.legend(bbox_to_anchor=(1, 1), loc='best', borderaxespad=0.5, prop={'size': 8})

                '''grid control'''
                ax.grid(True)
                gridlines = ax.get_xgridlines() + ax.get_ygridlines()
                for line in gridlines:
                    line.set_linestyle('dotted')

                '''tickcontrol'''
                ticks = ax.xaxis.get_major_ticks() + ax.yaxis.get_major_ticks()
                for tick in ticks:
                    tick.label.set_fontsize(6)

                '''plt.savefig('temperature stats', format='png', facecolor=self.pdffacecolor)
				sys.exit(1)'''
                if multipagepdf:
                    plt.savefig(multipagepdf, format='pdf', facecolor=self.pdffacecolor)
                else:
                    plt.savefig(title, format='png', facecolor=self.pdffacecolor)

                plt.close()

        except Exception as e:
            print 'An exception occurred', e
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
