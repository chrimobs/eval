# -*- coding: utf-8 -*-
import numpy as np
import pandas as pan

import constants as co

class TestsetLog():
    '''Class intended to be used by logwriters.TestsetLogWriter.'''

    def __init__(self, testsets):
        assert testsets is not None and len(testsets) > 0
        self._sets = testsets

    @property
    def sets(self):
        return self._sets

    def firstset(self):
        return self.sets[0]

    def lastset(self):
        return self.sets[len(self.sets) - 1]


class Testset():

    def __init__(self, stime, etime, msg):
        self._stime = stime
        self._etime = etime
        self._msg = msg
    
    @property
    def stime(self):
        return self._stime

    @property
    def etime(self):
        return self._etime

    @property
    def msg(self):
        return self._msg

    def get_set(self):
        return self.stime, self.etime, self.msg


class MeasurementData(object):
    '''Bundles any measurement data and its CDF, its fitted CDF, the formula
    used for fitting and the source that caused the data (i.e. the application
    or service).
    
    Parameters
    ----------
    series : pandas.Series
        The original measurements
    cdf : pandas.Series
        The empirical CDF for series.
    fitted_cdf : pandas.Series
        The empirical CDF fitted to some other empirical CDF
    formula : string or patsy.Formula
        Formula used to produce fitted_cdf
    source : string
        Denotes the application or service that produced the original series
    '''
    def __init__(self, series, cdf=None, fitted_cdf=None, formula = None,
            source='', test=''):
        self._series = series
        self._cdf = cdf
        self._fitted_cdf = fitted_cdf
        self._formula = formula
        self._source = source
        self._test = test
        self._STD = np.round(self.series.std(), decimals = 5)
        #if self.STD < 1e-6:
            #self.STD = 0.

    @property
    def series(self):
        return self._series

    @series.setter
    def series(self, series):
        self._series = series

    @property
    def cdf(self):
        return self._cdf

    @cdf.setter
    def cdf(self, cdf):
        self._cdf = cdf

    @property
    def fitted_cdf(self):
        return self._fitted_cdf

    @fitted_cdf.setter
    def fitted_cdf(self, fitted):
        self._fitted_cdf = fitted

    @property
    def formula(self):
        return self._formula

    @formula.setter
    def formula(self, formula):
        self._formula = formula

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, source):
        self._source = source

    @property
    def test(self):
        return self._test

    @property
    def STD(self):
        return self._STD


class MeasurementDataContainer(object):
    '''Bundles several MeasurementData. Its purpose become visible by
    subclasses.'''
    def __init__(self, source, test=''):
        self._mds = dict()
        self._source = source
        self._test = test

    @property
    def mds(self):
        return self._mds

    @mds.setter
    def mds(self, mds):
        self.mds = mds

    def add_md(self, md, name):
        '''Add MeasurementData to this container'''
        assert type(md) == MeasurementData
        self._mds[name] = md

    @property
    def source(self):
        return self._source

    @property
    def test(self):
        return self._test


class CPUMeasurementDataContainer(MeasurementDataContainer):
    '''Bundle MeasurementData for CPU utilization measurements.

    Extracts the following columns from a dstat log file:
    usr, sys, wai, idl
    Additionally, it computes another column, cpu, as:
    cpu = 100 - idl
    All five columns are represented as MeasurementData, each.
    
    Parameters
    ----------
    dlogreader : logreaders.DstatLogReader
        Contains log data from dstat as pandas.DataFrame
    '''
    def __init__(self, dlogreader):
        super(CPUMeasurementDataContainer, self).__init__(
                dlogreader.source,
                dlogreader.test)
        names = [co.CN_USR, co.CN_SYS, co.CN_CPU]
        for name in names:
            self.mds[name] = MeasurementData(
                    dlogreader.log[name], 
                    source = dlogreader.source,
                    test = dlogreader.test)


class DiskMeasurementDataContainer(MeasurementDataContainer):
    def __init__(self, dlogreader):
        super(DiskMeasurementDataContainer, self).__init__(
                dlogreader.source,
                dlogreader.test)
        #names = ['read', 'writ', 'disk', 'dutl']
        names = [co.CN_DISKLOG10, co.CN_DUTIL]
        for name in names:
            self.mds[name] = MeasurementData(
                    dlogreader.log[name],
                    source = dlogreader.source,
                    test = dlogreader.test)


class NetMeasurementDataContainer(MeasurementDataContainer):
    def __init__(self, dlogreader):
        super(NetMeasurementDataContainer, self).__init__(
                dlogreader.source,
                dlogreader.test)
        #names = ['send', 'recv', 'net', 'nutl']
        names = [co.CN_NETLOG10, co.CN_NUTIL]
        for name in names:
            self.mds[name] = MeasurementData(
                    dlogreader.log[name],
                    source = dlogreader.source,
                    test = dlogreader.test)


class LoadAverageMeasurementDataContainer(MeasurementDataContainer):
    def __init__(self, dlogreader):
        super(LoadAverageMeasurementDataContainer,
                self).__init__(dlogreader.source, dlogreader.test)
        names = [co.CN_1M, co.CN_5M, co.CN_15M]
        alt_names = [co.CN_X1M, co.CN_X5M, co.CN_X15M]
        df = pan.DataFrame(dlogreader.log, columns=names)
        df.columns = alt_names
        for name in df.columns:
            self.mds[name] = MeasurementData(
                    df[name], 
                    source = dlogreader.source,
                    test = dlogreader.test)


class PowerMeasurementDataContainer(MeasurementDataContainer):
    def __init__(self, pwrlogreader):
        super(PowerMeasurementDataContainer, self).__init__(
                pwrlogreader.source,
                pwrlogreader.test)
        name = co.CN_PWR
        pwr_ser = pwrlogreader.log[name]
        self.mds[name] = MeasurementData(
                pwr_ser, 
                source = pwrlogreader.source,
                test = pwrlogreader.test)


class RequestSizeMeasurementDataContainer(MeasurementDataContainer):
    def __init__(self, client_logreader):
        super(RequestSizeMeasurementDataContainer,
                self).__init__(client_logreader.source, client_logreader.test)
        #name = 'trsz'
        names = [co.CN_TRSZLOG10]
        #rqsz_ser = client_logreader.log[names]
        #self.mds[name] = MeasurementData(rqsz_ser, source=client_logreader.source)
        for name in names:
            self.mds[name] = MeasurementData(
                    client_logreader.log[name],
                    source = client_logreader.source,
                    test = client_logreader.test)


class IATMeasurementDataContainer(MeasurementDataContainer):
    def __init__(self, client_logreader):
        super(IATMeasurementDataContainer,
                self).__init__(client_logreader.source, client_logreader.test)
        name = co.CN_IATS
        iats_ser = client_logreader.log[name]
        self.mds[name] = MeasurementData(
                iats_ser, 
                source=client_logreader.source,
                test = client_logreader.test)


class ARateMeasurementDataContainer(MeasurementDataContainer):
    def __init__(self, client_logreader):
        super(ARateMeasurementDataContainer,
                self).__init__(client_logreader.source, client_logreader.test)
        name = co.CN_ARAT
        arat_ser = client_logreader.log[name]
        self.mds[name] = MeasurementData(
                arat_ser, 
                source=client_logreader.source,
                test=client_logreader.test)


class DLTimeMeasurementDataContainer(MeasurementDataContainer):
    def __init__(self, client_logreader):
        super(DLTimeMeasurementDataContainer,
                self).__init__(client_logreader.source, client_logreader.test)
        name = co.CN_DLTIME
        dltime_ser = client_logreader.log[name]
        self.mds[name] = MeasurementData(
                dltime_ser, 
                source=client_logreader.source,
                test=client_logreader.test)


class VideoSizeMeasurementDataContainer(MeasurementDataContainer):
    def __init__(self, vsz_logreader):
        super(VideoSizeMeasurementDataContainer,
                self).__init__(vsz_logreader.source, vsz_logreader.test)
        name = co.CN_VSZLOG10
        vsz_ser = vsz_logreader.log[name]
        self.mds[co.VSZN] = MeasurementData(
                vsz_ser, 
                source=vsz_logreader.source,
                test=vsz_logreader.test)


class VideoNameMeasurementDataContainer(MeasurementDataContainer):
    def __init__(self, client_logreader):
        super(VideoNameMeasurementDataContainer,
                self).__init__(client_logreader.source, client_logreader.test)
        name = co.CN_FNAME
        fname_ser = client_logreader.log[name]
        self.mds[name] = MeasurementData(
                fname_ser, 
                source=client_logreader.source,
                test=client_logreader.test)

