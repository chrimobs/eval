# -*- coding: utf-8 -*-

import csv
import glob
import pandas as pan
import datetime as dt
import os.path as osp
import dateutil.parser as dup

import datatypes
import formatdefs
import constants as co

class TestsetLogWriter(object):
    '''Class to write a testset log file once'''

    timef = formatdefs.times_timef
    header = ['stime', 'etime', 'msg']
    
    def write(self, fpath, testsetlog):
        with open(fpath, 'wb') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(self.header)
            for testset in testsetlog.sets:
                stime_s = testset.get_stime().astype(datetime).strftime('%Y-%m-%d %H:%M:%S.%f')
                #TODO stime_e ??
                writer.writerow(testset.get_set())


class ResultsWriter(object):
    def __init__(self, tpath, formula='', test='', res=None, lag=0,
            reg=co.REGR_OLS, steps=30):
        self._formula = '_'.join([formula, test]).replace(' ', '_')
        self._lag = lag
        self._steps = steps
        formul_str = '_'.join([
            self.formula, 
            reg, 
            str(self.steps),
            'lag', 
            str(lag),
            ])
        self._tpath = osp.join(tpath, formul_str)
        self._test = test
        self._result = res

    @property
    def formula(self):
        return self._formula

    @property
    def tpath(self):
        return self._tpath

    @property
    def test(self):
        return self._test

    @property
    def result(self):
        return self._result

    @property
    def lag(self):
        return self._lag

    @property
    def steps(self):
        return self._steps

    def get_suff(self, fsuff):
        return '.' + fsuff

    def pickle(self):
        fpath = self.tpath + self.get_suff(co.REG_R)
        self.result.save(fpath)

    def write_stats(self, stats):
        fpath = self.tpath + self.get_suff(co.SUMM)
        stats.to_csv(fpath)

    def write_regr_summ(self):
        summ_fpath = self.tpath + self.get_suff(co.REG_S)
        with open(summ_fpath, 'w') as summf:
            try:
                summf.write(self.result.summary().as_text() + '\n')
            except:
                summf.write(
                    'summarizing result failed. maybe matrix is singular?\n')
        parm_fpath = self.tpath + self.get_suff(co.REG_P)
        with open(parm_fpath, 'w') as parmf:
            parmf.write(self.result.params.to_string() + '\n')

    def write_plain(self, data, suff):
        fpath = self.tpath + self.get_suff(suff)
        with open(fpath, 'w') as df:
            try:
                for l in data:
                    df.write(str(l))
            except:
                df.write(str(data))

    def write_plain_ser(self, ser, suff):
        fpath = self.tpath + self.get_suff(suff)
        ser.to_csv(fpath)

    def write_mse(self, mse):
        self.write_plain(mse, co.MSE)

    def write_mpe(self, mpe):
        self.write_plain(mpe, co.MPE)

    def write_ks(self, ks):
        fpath = self.tpath + self.get_suff(co.X_KS)
        ks.to_csv(fpath)

    def write_ad(self, ad):
        fpath = self.tpath + self.get_suff(co.X_AD)
        ad.to_csv(fpath)

    def write_pdev(self, pdev):
        fpath = self.tpath + self.get_suff(co.X_PDEV)
        pdev.to_csv(fpath)

    def write_fitted_rvs(self, fitted_rvs):
        fpath = self.tpath + self.get_suff(co.X_VALS)
        fitted_rvs.to_csv(fpath, index=False)

    def write_model_errors(self, errors):
        fpath = self.tpath + self.get_suff(co.X_ERR)
        errors.to_csv(fpath, index=False)


class BM2ClientLogWriter(object):
    def __init__(self, dir_path, tfname=''):
        self._path = dir_path
        self._tfname = tfname

    @property
    def path(self):
        return self._path

    @property
    def tfname(self):
        return self._tfname

    def produce(self):
        xlogs = glob.glob(osp.join(self.path, '*.xlog'))
        dfs = list()
        for xlog in xlogs:
            with open(xlog) as xlogf:
                l = list(xlogf)
                stime_l = l[0]
                rspec_l = l[2]
                etime_l = l[len(l) - 1]
                stime_comps = stime_l.split()
                rspec_comps = rspec_l.split()
                etime_comps = etime_l.split()
                s_dt = dup.parse(' '.join(stime_comps[4:9])) + dt.timedelta(microseconds = 1)
                e_time = etime_comps[8]
                bm = rspec_comps[7]
                sz = rspec_comps[5].split('=')[1]
                s_dt_str = s_dt.strftime(formatdefs.clientlog_timef)
                data = ['B', bm, s_dt_str, co.BMK_SZ_MAP[sz], 0.0, e_time, 200]
                df = pan.DataFrame([data], columns = co.CLIENT_LOG_NS,
                        index=[s_dt_str])
                dfs.append(df)
        log_df = pan.concat(dfs)
        log_df.sort_index(inplace=True)
        fname = 'B_.log' if self.tfname == '' else self.tfname
        log_df.to_csv(osp.join(self.path, fname),header=False, index=False)


def write_stats(stats, colname, tpath):
    fn = '.'.join([colname, co.SUMM])
    fpath = osp.join(tpath, fn)
    stats.to_csv(fpath)

