# -*- coding: utf-8 -*-

import os.path as osp
import sys

#stats stuff
import numpy as np
import pandas as pan
import statsmodels.api as smapi
import statsmodels.formula.api as smfapi
from patsy import dmatrices
from scipy.linalg import toeplitz

#own eval helper stuff
import stats_helper as shelp
import constants as co
import plotting
import printing
import logwriters as writing
from datatypes import MeasurementData


class EDFRegressionEvaluator(object):
    def __init__(self, steps=30):
        start = 0.001
        self._steps = steps
        self._q_ords = np.linspace(0, 1, self.steps)
        self._q_ords[0] = start

    @property
    def q_ords(self):
        return self._q_ords

    @property
    def steps(self):
        return self._steps

    def fit_model(self, formula, resp_ser, predictors_df, lag=0, reg=co.REGR_OLS):
        '''
        Since the number of samples in the predictors_df and self are most
        probably different this method will not evaluate the model directly on
        the data, i.e. linear regression is not sample-wise. Rather, we take one
        empirical distribution function (EDF) as reference which gives us 
        quantiles and their associated p-orders. Then we take the other EPD and
        estimate the quantiles that have exactly the same p-orders as we got
        from the first EDF. Thus, we obtain pairs of qauntiles with matching
        p-orders and can apply regression.
        
        Parameters
        ----------
        formula : a patsy formula (R-style, but with some differences). See
            https://patsy.readthedocs.org/en/latest/formulas.html
        resp_ser : pan.Series
            Keeps the regressand column
        predictors_df : pandas.Dataframe
            Keeps at least all the columns specified in the model
            
        Returns
        -------
        result : statsmodels.regression.linear_model.RegressionResults OR None
        
        '''
        pred_est_qfs = list()
        resp_est_inv_cdfs = list()
        for coln in predictors_df.columns:
            pred_ser = predictors_df[coln]
            pred_ser.dropna(inplace=True)

            #we change the role of response and predictor for the purpose of 
            #quantile estimation. The reason is that we take the quantiles of the
            #respone variable as single reference to estimate the quantiles of 
            #all components in the predictor
            pred_est_qf = shelp.estimate_quantiles(pred_ser, self.q_ords)

            pred_est_qfs.append(pred_est_qf)
        
        pred_est_qfs_df = pan.concat(pred_est_qfs, axis=1)
        resp_qf = shelp.estimate_quantiles(resp_ser, self.q_ords)
        resp_qf_df = pan.DataFrame(resp_qf )
        combi_df = pan.concat([pred_est_qfs_df, resp_qf_df], axis=1)

        if reg == co.REGR_OLS:
            model = smfapi.ols(formula = formula, data=combi_df)
            res = model.fit(
                    cov_type='HAC', 
                    cov_kwds={'maxlags':lag, 'use_correction': False}
                    )
        elif reg == co.REGR_GLSAR:
            model = smfapi.glsar(formula=formula, data=combi_df, rho=lag)
            res = model.iterative_fit(maxiter=6)
        else: res = None
        return res


class SimpleModel(object):
    def __init__(self, resp_ser, pred_ser, tpath, formula=None, test='', lag=0,
            reg=co.REGR_OLS, steps=30):
        assert type(resp_ser) == pan.Series
        assert type(pred_ser) == pan.Series
        self.lhs = resp_ser.name
        self.resp = resp_ser
        self.rhs = pred_ser.name
        self.pred = pred_ser
        self.tpath = tpath
        self.formula = formula
        self._test = test
        self._lag = lag
        self._reg = reg
        self._steps = steps

    @property
    def test():
        return self._test

    @property
    def steps(self):
        return self._steps

    def model(self):

        if self.formula: rhs = self.formula
        elif self.rhs == '': self.rhs = 'pred'
        formula = lhs + ' ~ ' + rhs
        print self.test, formula
        pred_df = self.pred.to_frame()
        ere = EDFRegressionEvaluator(self.steps)
        res = ere.fit_model(formula, self.resp, pred_df, self._lag, self._reg)

        return res, formula


class MultipleModel(object):
    def __init__(self, resp_ser, pred_df, tpath, formula=None, test='', lag=0,
            reg=co.REGR_OLS, steps=30):
        assert type(resp_ser) == pan.Series
        assert type(pred_df) == pan.DataFrame
        self.lhs = resp_ser.name
        self.resp = resp_ser
        self.pred = pred_df
        self.tpath = tpath
        self.formula = formula
        self._test = test
        self._lag = lag
        self._reg = reg
        self._steps = steps

    @property
    def test(self):
        return self._test

    @property
    def steps(self):
        return self._steps

    def model(self):
        lhs = self.lhs
        if self.formula:
            rhs = self.formula
        else:
            rhs_terms = list()
            rhs = ':'.join(self.pred.columns)
        formula = lhs + ' ~ ' + rhs
        print self.test, formula
        ere = EDFRegressionEvaluator(self.steps)
        res = ere.fit_model(formula, self.resp, self.pred, self._lag, self._reg)
        return res, formula


class MeasurementDataEvaluator(object):
    def __init__(self, md, tpath):
        self._md = md
        self.md.cdf = shelp.get_cdf(self.md.series)
        self._tpath = tpath

    @property
    def md(self):
        return self._md

    @md.setter
    def md(self, md):
        self._md = md

    @property
    def tpath(self):
        return self._tpath

    @tpath.setter
    def tpath(self, tpath):
        self._tpath = tpath

    def summarize(self):
        try:
            plotting.plot_cdf(self.md.cdf, self.md.series.name, self.tpath)
        except TypeError:
            print 'WARNING: summarize', self.md.series.name, 'skipped. Appears \
                    empty.'
        writing.write_stats(self.md.series.describe(percentiles=[.05, .5, .95]), 
                self.md.series.name, self.tpath)

    def model(self, pred, formula=None, lag=0, reg=co.REGR_OLS, steps=30):
        if np.isnan(self.md.STD):
            print 'WARNING: modeling', self.md.series.name, 'skipped. Appears \
                    empty.'
            return None
        if self.md.STD == 0.:
            print 'WARNING: modeling', self.md.series.name, 'skipped. Appears \
                    constant.'
            return None

        if type(pred) == pan.DataFrame:
            model = MultipleModel(
                    self.md.series, 
                    pred, 
                    self.tpath, 
                    formula,
                    self.md.test,
                    lag,
                    reg,
                    steps)
        elif type(pred) == pan.Series:
            model = SimpleModel(
                    self.md.series, 
                    pred, 
                    self.tpath, 
                    formula,
                    self.md.test,
                    lag, 
                    reg,
                    steps)
        else:
            raise TypeError, '\"pred\" must be pandas.Series or pandas.DataFrame'
        sys.stdout.flush()
        res, formula = model.model()

        res_writer = writing.ResultsWriter(
                self.tpath, 
                formula, 
                self.md.test,
                res, 
                lag, 
                reg,
                steps)
        #res_writer.pickle()
        res_writer.write_regr_summ()

        if self.md.series.name in printing.logxs:
        #if LHS was logarithmically transformed for the fitting we need to
        #compute the fitted CDF manually. Just taking res.fittedvalues
        #leads to high deviation between the original CDF and the fit.
            if type(pred) == pan.Series:
                coef = res.params[printing.cond_wrap_term_log10(pred.name) ] 
                fit_cdf = shelp.get_inv_cdf(shelp.get_cdf(pred)) * coef +\
                    res.params['Intercept']
                fit_cdf = shelp.get_inv_cdf(fit_cdf)
            else:
                raise NotImplementedError, 'manually computing fitted CDF if \
                predictor is a pandas.DataFrame is not implemented.'
        else:
            # for some brilliant reason the fitted values are sometimes out of 
            # order in the upper quantiles if multiple regression is applied
            # thus, we need to sort it
            res.fittedvalues.values.sort()
            fit_cdf = shelp.get_inv_cdf(res.fittedvalues)

        fit_cdf.name = self.md.series.name + ' (estimated)'
        self.md.fitted_cdf = fit_cdf
        self.md.formula = formula

        fname = ' '.join([
            formula, 
            self.md.source,
            reg,
            str(steps),
            'lag', 
            str(lag),
            ]).replace(' ', '_')
        fpath = osp.join(self.tpath, fname)
        plotting.plot_multi_cdf([self.md.cdf, self.md.fitted_cdf], 
                [self.md.series.name, self.md.fitted_cdf.name],
                fpath)

        if type(pred) == pan.Series:
            fpath = osp.join(self.tpath, fname.replace('~', 'vs'))
            plotting.plot_multi_cdf([self.md.cdf, shelp.get_cdf(pred)], 
                    [self.md.series.name, pred.name],
                    fpath)

        fitted_rvs = shelp.rvs_from_cdf(self.md.fitted_cdf)

        res_writer.write_stats(fitted_rvs.describe(percentiles=[.05, .5, .95]))

        shift_xs, shift_ys = shelp.emp_shift_os(self.md.series, fitted_rvs)
        w_band_u, w_band_l = shelp.w_band(self.md.series, fitted_rvs)
        plotting.plot_shiftfun(shift_xs, shift_ys, w_band_u, w_band_l, fpath)

        errs = shelp.model_errors_by_shiftfun(w_band_u, w_band_l)
        res_writer.write_model_errors(errs)
        #errs = shelp.dummy_errors()
        
        plotting.plot_resid_acf(res.resid, fpath)
        plotting.plot_resid_pacf(res.resid, fpath)

        #res_fit_parms_dict = dict(zip(res.params.index, res.params.values))
        #fit_meas_dict = {co.MSE: quant_mse, co.MPE: quant_mpe}
        #fit_meas_dict.update(res_fit_parms_dict)

        return (res, formula, errs)


class MeasurementDataContainerEvaluator(object):
    def __init__(self, mdc, tpath):
        self._mdc = mdc
        self._tpath = tpath
        self._mdes = dict()
        for name, md in self.mdc.mds.items():
            self._mdes[name] = MeasurementDataEvaluator(md, self._tpath)

    @property
    def mdc(self):
        return self._mdc

    @mdc.setter
    def mdc(self, mdc):
        self._mdc = mdc

    @property
    def tpath(self):
        return self._tpath

    @tpath.setter
    def tpath(self, tpath):
        self._tpath = tpath

    @property
    def mdes(self):
        return self._mdes

    @mdes.setter
    def mdes(self, mdes):
        self._mdes = mdes

    def summarize(self):
        for name, mde in self.mdes.items():
            mde.summarize()

    def model(self, pred, formula=None, lag=0, reg=co.REGR_OLS, steps=30):
        results = dict()
        for name, mde in self.mdes.items():
            results[name] = mde.model(pred, formula, lag, reg, steps)
        return results


class CPUUtilEvaluator(MeasurementDataContainerEvaluator):
    def __init__(self, cpu_mdc, tpath):
        super(CPUUtilEvaluator, self).__init__(cpu_mdc, tpath)


class DiskUtilEvaluator(MeasurementDataContainerEvaluator):
    def __init__(self, disk_mdc, tpath):
        super(DiskUtilEvaluator, self).__init__(disk_mdc, tpath)


class NetUtilEvaluator(MeasurementDataContainerEvaluator):
    def __init__(self, net_mdc, tpath):
        super(NetUtilEvaluator, self).__init__(net_mdc, tpath)


class LoadAverageEvaluator(MeasurementDataContainerEvaluator):
    def __init__(self, disk_mdc, tpath):
        super(LoadAverageEvaluator, self).__init__(disk_mdc, tpath)


class PowerLevelEvaluator(MeasurementDataContainerEvaluator):
    def __init__(self, pwr_mdc, tpath):
        super(PowerLevelEvaluator, self).__init__(pwr_mdc, tpath)


class RequestSizeEvaluator(MeasurementDataContainerEvaluator):
    def __init__(self, rqsz_mdc, tpath):
        super(RequestSizeEvaluator, self).__init__(rqsz_mdc, tpath)


class VideoSizeEvaluator(MeasurementDataContainerEvaluator):
    def __init__(self, vsz_mdc, tpath):
        super(VideoSizeEvaluator, self).__init__(vsz_mdc, tpath)

    def model(self):
        return None


class ARateEvaluator(MeasurementDataContainerEvaluator):
    def __init__(self, arate_mdc, tpath):
        super(ARateEvaluator, self).__init__(arate_mdc, tpath)

    def model(self):
        return None


class DLTimeEvaluator(MeasurementDataContainerEvaluator):
    def __init__(self, dltm_mdc, tpath):
        super(DLTimeEvaluator, self).__init__(dltm_mdc, tpath)

    def model(self):
        return None


class InterferenceEvaluator():
    def __init__(self, emp_cdf, fitted_cdfs_df, tpath):
        self.cdf = emp_cdf
        self.fitted = fitted_cdfs_df
        self.tpath = tpath

    def summarize(self):
        '''Plot empirical data vs fitted data. Also plot empirical data vs. 
        expected sum of fitted data.'''
        emp_label = 'empirical'
        #fit_labels = 


    def analyze(self):
        '''Compute deviation between expected sum of fitted data and empirical
        data. To be implemented by subclasses in order to be meaningful.'''
        pass

class CPUInterferenceEvaluator(InterferenceEvaluator):
    def __init__(self):
        pass


