# -*- coding: utf-8 -*-

import bisect
import numpy as np
import pandas as pan
import scipy.stats.mstats as mst

import constants as co

def get_cdf(series):
    '''Calculates the CDF for a pandas.Series'''

    frqs = series.value_counts()/len(series)
    cdf = frqs.sort_index().cumsum()
    cdf = pan.Series(map(lambda x: round(x,6), cdf), index=cdf.index)
    cdf.name = series.name
    return cdf

def get_ccdf(series):
    '''Calculates the CCDF for a pandas.Series'''
    return 1 - get_cdf(series)

def get_inv_cdf(cdf):
    '''Calculate the inverse of an empirial CDF.

    Parameters
    ----------
    cdf : outcome of get_cdf(pandas.Series)

    Returns
    -------
    pandas.Series with index and values swapped
    '''
    cdf_inv =  pan.Series(map(lambda x: np.float64(x), cdf.index), 
            index=cdf.values)
    cdf_inv.name = cdf.name
    return cdf_inv

def get_quantile(cdf, p):
    idx = bisect.bisect_left(cdf.values, p)
    return cdf.index[idx]


def estimate_quantiles(dep_ser, pred_quantiles=None):
    if pred_quantiles is None:
        pred_quantiles = np.arange(0,1.001,.001)
    assert len(dep_ser) >= 2
    ## treat categorical variable specially
    ## TODO Move string to constants
    #if dep_ser.name == 'arate':
    dep_qf = get_inv_cdf(get_cdf(dep_ser))
    idx_poz = list()
    dep_est_quants = list()
    for prob in pred_quantiles:
        idx_poz.append(bisect.bisect_left(dep_qf.index, prob))
    for idx_pos in idx_poz:
        dep_est_quants.append(dep_qf.iget(idx_pos))

    # TODO predictors should also be MeasurementData type or the like so save
    # computing of STD
    #if np.round(dep_ser.std(), decimals=5) == .0:
        #dep_est_qf = pan.Series(np.full(len(pred_quantiles), dep_ser.iget(0)), 
                #pred_quantiles )
    #else:
        #dep_est_quants = mst.mquantiles(dep_ser, pred_quantiles, alphap=1/3,
                #betap=1/3)
    #print len(set(dep_est_quants))
    dep_est_qf = pan.Series(dep_est_quants, pred_quantiles)
    dep_est_qf.name = dep_ser.name

    return dep_est_qf

def rv_sum(sample1, sample2, n=1000000):
    sample1 = np.random.choice(sample1, n)
    sample2 = np.random.choice(sample2, n)
    sum = sample1 + sample2
    if type(sample1) == pan.Series and type(sample2) == pan.Series:
        sum_ser = pan.Series(sum)
        sum_ser.name = '(' + sample1.name + '+' + sample2.name + ')'
        return pan.Series(sum_ser)
    else:
        return sum

def rv_diff(sample1, sample2, n=1000000):
    smpl1 = np.random.choice(sample1, n)
    smpl2 = np.random.choice(sample2, n)
    diff = smpl1 - smpl2
    if type(sample1) == pan.Series and type(sample2) == pan.Series:
        diff_ser = pan.Series(diff)
        diff_ser.name = '(' + sample1.name + ' - ' + sample2.name + ')'
        return pan.Series(diff_ser)
    else:
        return diff

def rvs_from_cdf(cdf):
    steps = np.append(np.array(cdf.values[0]), np.diff(cdf.values))
    min_step = min(steps)
    #print 'min step', min_step, 'in', len(steps), 'steps'
    step_incs = np.int16(np.round(steps / min_step))
    l = list()
    for e, m in zip(cdf.keys(), step_incs):
        for i in range(m):
            l.append(e)
    rv_ser = pan.Series(l)
    rv_ser.name = cdf.name
    return rv_ser

def percentile_diffs(minuends, subtrahends):
    percentiles = np.arange(0, 1, 0.01)
    min_quants = estimate_quantiles(minuends, percentiles)
    sub_quants = estimate_quantiles(subtrahends, percentiles)
    diffs = np.float64(min_quants.index.values - sub_quants.index.values)
    diff_ser = pan.Series(diffs)
    return diff_ser

def quantile_diffs(min_cdf, sub_cdf):
    percentiles = min_cdf.values
    #print percentiles
    est_cdf = estimate_quantiles(get_inv_cdf(sub_cdf), percentiles)
    #print get_inv_cdf(min_quants).subtract(get_inv_cdf(sub_quants))
    diffs = np.float64(min_cdf.index.values - est_cdf.index.values)
    diff_ser = pan.Series(diffs)
    return diff_ser

def stat_diffs_and_pdev(orig_ser, fit_ser):
    o_stat = orig_ser.describe(percentiles=[0.05, 0.5, 0.95])
    f_stat = fit_ser.describe(percentiles=[0.05, 0.5, 0.95])
    stat_diff = f_stat.subtract(o_stat)
    stat_dev = stat_diff.divide(o_stat).multiply(100)
    return stat_diff, stat_dev

def quantile_mse(orig_ser, fit_ser):
    percentiles = np.arange(0, 1, 0.01)
    oq = get_inv_cdf(estimate_quantiles(orig_ser))
    fq = get_inv_cdf(estimate_quantiles(fit_ser))
    qd = oq.subtract(fq)
    f = lambda x: np.power(x, 2)
    mse = qd.apply(f).cumsum()[[qd.last_valid_index()]] / len(qd)
    return mse.values[0]
    
def quantile_mpe(orig_ser, fit_ser):
    percentiles = np.arange(0, 1, 0.01)
    oq = get_inv_cdf(estimate_quantiles(orig_ser))
    fq = get_inv_cdf(estimate_quantiles(fit_ser))
    qp = oq.subtract(fq).divide(oq)
    mpe = qp.cumsum()[[qp.last_valid_index()]] * (100./len(qp))
    return mpe.values[0]

def model_errors_by_shiftfun(band_u, band_l):
    '''Compute max, min, mean, and mean percentage errors of a model as computed
    by the empirical shift function.'''
    os_l = map(lambda x: float(x), band_l.index.values)
    os_u = map(lambda x: float(x), band_u.index.values)
    eas_l = map(lambda x: abs(x), band_l.values)
    eas_u = map(lambda x: abs(x), band_u.values)
    eaps_l = map(lambda (o, e): 100 * e/o, filter(lambda (o, e): o > 0,
        zip(os_l, eas_l)))
    eaps_u = map(lambda (o, e): 100 * e/o, filter(lambda (o, e): o > 0,
        zip(os_u, eas_u)))
    eas_l.extend(eas_u)
    eaps_l.extend(eaps_u)
    eas = sorted(eas_l)
    eaps = sorted(eaps_l)
    ea_max = eas[-1]
    ea_avg = sum(eas)/len(eas)
    eas_midx = len(eas)/2
    if len(eas)%2 == 1:
        ea_med = eas[eas_midx]
    else:
        ea_med = (eas[eas_midx] + eas[eas_midx + 1])/2.
    eap_max = eaps[-1]
    eap_avg = sum(eaps)/len(eaps)
    eaps_midx = len(eaps)/2
    if len(eaps)%2 == 1:
        eap_med = eaps[eaps_midx]
    else:
        eap_med = (eaps[eaps_midx] + eaps[eaps_midx + 1])/2.
    df = pan.DataFrame(columns=[co.ERR_AMAX,
                           co.ERR_AAVG,
                           co.ERR_AMED,
                           co.ERR_PMAX,
                           co.ERR_PAVG,
                           co.ERR_PMED])
    df.loc[0] = [ea_max, ea_avg, ea_med, eap_max, eap_avg, eap_med]
    return df

def dummy_errors():
    return pan.Series([0.0, 0.0, 0.0, 0.0, 0.0, 0.0], 
            index=[co.ERR_AMAX,
                   co.ERR_AAVG,
                   co.ERR_AMED,
                   co.ERR_PMAX,
                   co.ERR_PAVG,
                   co.ERR_PMED])

def emp_shift_qf(x_cdf, y_cdf):
    '''Compute the empirical shift function 
    $\hat{Delta}(x) = G^{-1}(F(x)) - x$ following [Doksum 1796]
    See http://projecteuclid.org/euclid.aos/1176342662 
    or http://biomet.oxfordjournals.org/content/63/3/421.short'''

    shifts = list()
    #for x in x_cdf.index.values:
    for i in range(len(x_cdf)):
        s = get_quantile(y_cdf, x_cdf.iget(i)) - x_cdf.index[i]
        shifts.append(s)
    return (x_cdf.index.values, shifts)

def emp_shift_os(sample_x, sample_y):
    '''Estimator for $\Delta$ using order statistics following [Doksum 1977]'''
    xs = sorted(sample_x)
    ys = sorted(sample_y)
    m = len(xs)
    n = float(len(ys))
    shifts = list()
    for i in range(1, m + 1):
        y_idx = int(np.ceil(i * n/m)) - 1
        try:
            d = ys[y_idx] - xs[i - 1]
        except:
            print m, n, i, y_idx
        shifts.append(d)

    assert len(xs) == len(shifts)
    return (xs, shifts)

def h(u, m, n, k):
    '''h+/- from [Doksum 1977] (2.4)'''
    N = m + n
    l = m/N
    nl = 1 - l
    nlsq = nl * nl
    c = ( N * k * k ) / (n * m)
    n1 = u + .5 * c * nl * (1 - 2 * l * u)
    n2 = .5 * np.sqrt(c * c * nlsq + 4 * c * u * (1 - u))
    num_u = n1 + n2
    num_l = n1 - n2
    d = 1 + c * nlsq
    return num_u/d, num_l/d

def w_band(sample_x, sample_y, a=0.1, alpha=0.02):
    '''W confidence band for $\Delta(x)$ taken from [Doksum 1977].'''
    xs = sorted(set(sample_x))
    m = float(len(xs))
    ys = sorted(set(sample_y))
    n = float(len(ys))
    valid_ns = range(5,51)
    valid_ns.extend(range(60,101,10))
    if n in valid_ns:
        try:
            k = co.W_BAND_K_e[a][alpha][n]
        except:
            raise NotImplementedError, 'critical value for a {0}, alpha {1}, n {2} \
                not defined'.format(a, alpha, n)
    else:
        try:
            c = co.W_BAND_K[a][alpha]
        except:
            raise NotImplementedError, 'Approximate critical value for alpha \
                    {0} and a {1] not defined'.format(alpha, a)
    b = 1 - a
    r = int(np.floor(m * a))
    s = int(np.floor(m * b)) - 1 #+1 to simplify notation afterwards
    d_us, d_ls = list(), list()
    z = s - r
    idxs_l = list()
    idxs_u = list()
    for i in range(r, s):
        h_u, h_l = h((i+1)/m, m, n, k)
        if h_l >= 0. and h_l <= 1.: 
            idxs_l.append(i)
            #Keep in mind that in Doksum1977 the indices start at 1, but ours 
            #at 0. Thus, $\lceil x \rceil \rightarrow$ floor(x), and 
            #$\lfloor x \rfloor + 1 \rightarrow$ floor(x)
            i_l = int( np.floor(n * h_l) )
            if i_l >= 0: 
                y_l = ys[i_l]
                d_ls.append(y_l - xs[i - 1])
            else:
                d_ls.append(-np.inf)
        if h_u >= 0. and h_u <= 1.: 
            idxs_u.append(i)
            i_u = int( np.floor(n * h_u) )
            if i_u <= n: 
                y_u = ys[i_u]
                d_us.append(y_u - xs[i - 1])
            else:
                d_us.append(np.inf)
    d_l_idxs = list()
    for idx in idxs_l:
        d_l_idxs.append(xs[idx])
    try:
        d_l = pan.Series(d_ls, index=d_l_idxs)
    except:
        print 'WARNING: no valid lower band'
        d_l = pan.Series([])
    d_u_idxs = list()
    for idx in idxs_u:
        d_u_idxs.append(xs[idx])
    try:
        d_u = pan.Series(d_us, index=d_u_idxs)
    except:
        print 'WARNING: no valid upper band'
        d_u = pan.Series([])
    return d_u, d_l

def s_band():
    pass


class Sample(object):
    def __init__(self, data):
        self._sample = pan.Series(data)
        self._cdf = get_cdf(self.sample)

    @property
    def sample():
        return self._sample

    @property
    def cdf():
        return self._cdf

    def quantile(p):
        idx = bisect.bisect_left(self.cdf.values, p)
        return self.cdf.index[idx]

