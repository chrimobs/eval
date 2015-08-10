# -*- coding: utf-8 -*-

import dateutil.parser as dup
import operator as op
import os.path as osp
import datetime as dt
import pandas as pan
import numpy as np

from datatypes import TestsetLog, Testset
import formatdefs
import parsers
import constants as co
import printing

class LogReader(object):
    def __init__(self, fpath, source='', test=''):
        self._timef = formatdefs.default_timef
        self._fpath = fpath
        self._source = source
        self._log = None
        self._test = test

    @property
    def fpath(self):
        return self._fpath

    @property
    def source(self):
        return self._source

    @source.setter
    def source(source):
        self._source = source

    @property
    def timef(self):
        return self._timef

    @property
    def test(self):
        return self._test

    @timef.setter
    def timef(self, timef):
        self._timef = timef

    @property
    def log(self):
        return self._log

    @log.setter
    def log(self, log):
        self._log = log

    def read(self):
        '''
        Parameters
        ----------
        fpath: path to the log file
        source: string representing the application/process/service that for
        that the log file was produced
        '''
        self.log = pan.read_csv(self.fpath)

class DstatLogReader(LogReader):
    def __init__(self, fpath='', source='', year='', test=''):
        super(DstatLogReader, self).__init__(fpath, source, test)
        self.timef = formatdefs.dstat_timef
        self.time_parser = parsers.DstatTimeParser(year)
        self.year = year
        self.diskmax = 485490688.0 #B/s
        self.netmax = 1252942130.0 #B/s

    def read(self):
        assert self.fpath != ''
        raw_df = pan.read_csv(
                self.fpath, 
                skiprows=1, 
                parse_dates=0, 
                date_parser=self.time_parser.parse, 
                index_col='time')
        cpu_ser = 100.0 - raw_df[co.CN_IDL]
        cpu_ser.name = co.CN_CPU
        
        disk_ser = raw_df[co.CN_READ] + raw_df[co.CN_WRIT]
        disk_ser.name = co.CN_DISK
#workaround since unpickling RegressionResult with tranformed variables (e.g.
#np.log10(var) fails as of 2015-04 (statsmodels < 0.7)
#FIXME check with statsmodels 0.7
        disk_ser_cpy = disk_ser
#necessary sincw otherwise OLS.fit() will run forever
        disk_ser_cpy[disk_ser_cpy < 1.] = 1.
        disk_log10_ser = pan.Series(np.log10(disk_ser_cpy))
        disk_log10_ser.name = co.CN_DISKLOG10
        del disk_ser_cpy
        
        dutil_ser = 100 * disk_ser / self.diskmax
        dutil_ser.name = co.CN_DUTIL

        net_ser = raw_df[co.CN_RECV] + raw_df[co.CN_SEND]
        net_ser.name = co.CN_NET
#workaround since unpickling RegressionResult with tranformed variables (e.g.
#np.log10(var) fails as of 2015-04 (statsmodels < 0.7)
#FIXME check with statsmodels 0.7
        net_ser_cpy = net_ser
#necessary sincw otherwise OLS.fit() will run forever
        net_ser_cpy[net_ser_cpy < 1.] = 1.
        net_log10_ser = pan.Series(np.log10(net_ser_cpy))
        net_log10_ser.name = co.CN_NETLOG10
        del net_ser_cpy
        
        nutil_ser = 100 * net_ser / self.netmax
        nutil_ser.name = co.CN_NUTIL
        
        extra_df = pan.concat(
                [cpu_ser, 
                    disk_ser, 
                    net_ser, 
                    disk_log10_ser, 
                    net_log10_ser, 
                    dutil_ser, 
                    nutil_ser,
                    raw_df['1m'],
                    raw_df['5m'],
                    raw_df['15m'],
                    ],
                axis=1)
        renames = {'1m': co.CN_X1M, '5m': co.CN_X5M, '15m': co.CN_X15M}
        extra_df.rename(columns=renames, inplace = True)
        self.log = raw_df.join(extra_df)


class PowerLogReader(LogReader):
    def __init__(self, fpath='', source='', test=''):
        super(PowerLogReader, self).__init__(fpath, source, test)
        self.timef = formatdefs.pwrsmplr_timef

    def read(self):
        assert self.fpath != ''
        self.log = pan.read_csv(self.fpath, parse_dates=0, index_col='timestamp')
        #self.log = self.log.resample('S', how='median')

class VideoSizesReader(LogReader):
    def __init__(self, fpath='', source='', test=''):
        super(VideoSizesReader, self).__init__(fpath, source, test)

    def read(self):
        assert self.fpath != ''
        if self.source == 'D':
            df = pan.read_csv(self.fpath, header=False, names=[co.CN_VSZ])
            vsz_log10_ser = np.log10(df[co.CN_VSZ])
            vsz_log10_ser.name = co.CN_VSZLOG10
            df = df.join(vsz_log10_ser)
        elif self.source == 'T':
            df = pan.read_csv(self.fpath, header=False, sep=' ', names=['fname',
                co.VSZN])
            vsz_log10_ser = np.log10(df[co.CN_VSZ])
            vsz_log10_ser.name = co.CN_VSZLOG10
            df = df.join(vsz_log10_ser)
        else:
            raise NotImplementedError, 'cannot read video sizes for task ' \
                    + self.source
        self.log = df


class ClientLogReader(LogReader):
    def __init__(self, fpath='', source='', test=''):
        super(ClientLogReader, self).__init__(fpath, source, test)
        self.TASK = 'task'
        self.FNAM = co.CN_FNAME
        self.DTIM = 'datetime'
        self.TRSZ = co.CN_TRSZ
        self.WAIT = co.CN_WAIT
        self.DLTM = co.CN_DLTIME
        self.STAT = 'status'
        self.IATS = co.CN_IATS
        self.ARAT = co.CN_ARAT
        self._raw_names = [self.TASK, self.FNAM, self.DTIM, self.TRSZ,
                self.WAIT, self.DLTM, self.STAT]
        self._raw_dtypes = {self.TASK: str, self.FNAM: str, self.DTIM: str, 
                self.TRSZ: np.uint64, self.WAIT: np.float16, self.DLTM: np.float16, 
                self.STAT: np.uint16}
        self.timef = formatdefs.clientlog_timef

    def read(self):
        assert self.fpath != ''
        raw_df = pan.read_csv(self.fpath, header=None, names=self._raw_names,
                parse_dates=[self.DTIM], index_col=self.DTIM)

        vidn_ser = raw_df[self.FNAM].apply(lambda x: x[0:4])
        dtms = raw_df.index.values#[self.DTIM].apply(lambda x: dt.datetime.strptime(x,
            #self.timef)).values
        
        iats = [op.sub(*l).item()/1.0e+9 for l in zip(dtms[1:], 
            dtms[0:len(dtms)]) ]
        iats = [1.] + iats
        iats_ser = pan.Series(iats, index=raw_df.index)
        iats_ser.name = self.IATS
        
        arate =  round(len(iats)/sum(iats))
        arate_ser = pan.Series(np.full(len(iats), arate), index=raw_df.index)
        arate_ser.name = self.ARAT

        trsz_log10_ser = np.log10(raw_df[co.CN_TRSZ])
        trsz_log10_ser.name = co.CN_TRSZLOG10

        self.log = pan.concat([
            vidn_ser, 
            iats_ser, 
            arate_ser, 
            trsz_log10_ser,
            raw_df[self.TRSZ],
            raw_df[self.WAIT],
            raw_df[self.DLTM]], axis=1)


class TCLogReader(ClientLogReader):
    def __init__(self, fpath='', source='', tcont='flv', test=''):
        super(TCLogReader, self).__init__(fpath, source, test)
        self._tcont = tcont

    @property
    def tcont(self):
        return self._tcont

    def read(self):
        super(TCLogReader, self).read()
        tcont_ser = pan.Series([self.tcont]*len(self.log),
                index=self.log.index)
        tcont_ser.name = 'tcont'
        self.log = self.log.join(tcont_ser)


class BMLogReader(LogReader):
    '''This class is inteded to read .xlog files that collect log data from SPEC
    benchmark runs.'''
    def __init__(self, fpath='', bm='', source='', test=''):
        super(BMLogReader, self).__init__(fpath, source, test)
        self._bm = bm

    @property
    def bm(self):
        return self._bm

    def extract_task(self):
        t_id = osp.basename(self.fpath)[0]
        if t_id == co.BMK or t_id == co.TCBMK:
            self.source = t_id

    def read(self):
        assert self.fpath != ''
        if not self.source:
            self.extract_task()
        if not self.source:
            raise NotImplementedError, 'unknown task'

        testsets = list()
        with open(self.fpath) as xlog:
            for line in xlog.readlines():
                if line.startswith('runspec finished'):
                    comps = line.strip().split()
                    dt_str = ' '.join(comps[3:8])
                    dt = dup.parse(dt_str)
                    e_time = dt - timedelta(microseconds=1)
                    s_time = dt - timedelta(seconds=int(comps[8]), microseconds=1)
                    msg = ' '.join([self.source, self.bmk,
                        s_time.strftime(formatdefs.default_timef)])
                    testsets.append(Testset(s_time, e_time, msg))
        self.log = TestsetLog(testsets)


class TestsetLogReader(LogReader):
    def __init__(self, fpath=''):
        super(TestsetLogReader, self).__init__(fpath)

    def read(self):
        '''returns datatypes.TestsetLog'''
        assert self.fpath != ''

        self.log = pan.read_csv(self.fpath, parse_dates=[0], header=None)

        testsets = []
        for i in range(0, len(self.log) - 1, 2):
            stime, smsg, s = self.log.irow(i)
            etime, emsg, e = self.log.irow(i + 1)
            assert smsg == emsg
            testsets.append( Testset(stime, etime, smsg) )
        return TestsetLog(testsets)

def get_task_datetime_slots(dirn):
    comps = dirn.split('_')
    offs = 0
    if len(comps[0]) < 4: # dirn starts with experiment ID
        offs = 1
    dt_str = comps[0 + offs] + '_' + comps[1 + offs]
    runtimes = list()
    try:
        for i in range(5):
            runtimes.append(int (comps[offs + i + 3] ))
    except:
        runtimes = list()
        for i in range(3):
            runtimes.append( int( comps[offs + i + 3] ))
    runtimes = map(lambda x: str(x), runtimes)
    return dt_str, runtimes
