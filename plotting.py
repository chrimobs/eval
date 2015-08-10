# -*- coding: utf-8 -*-

import pandas as pan
import os.path as osp
import matplotlib.pyplot as plt
import statsmodels.api as smapi
from matplotlib.backends.backend_pdf import PdfPages

import printing
import constants as co
import stats_helper as shelp

def plot_rankview(series, fpath):
    fig = PdfPages(fpath + '.pdf')
    ax = plt.subplot(111)
    if type(series) == dict:
        for lbl in sorted(series.iterkeys()):
            sercpy = pan.Series(series[lbl])
            sercpy.sort()
            plt.loglog(range(1, len(sercpy) + 1), sercpy[::-1], '-', label=lbl)
            del sercpy
        ax.legend(loc='best')
    elif type(series) == pan.Series:
        sercpy = pan.Series(series)
        sercpy.sort()
        plt.loglog(range(1, len(sercpy) + 1), sercpy[::-1], 'b-')
        del sercpy
    ax.set_xlabel(printing.get_xlabel( 'rvp' ))
    ax.set_ylabel(printing.get_ylabel( 'rvp' ))
    fig.savefig()
    fig.close()
    plt.close()

def plot_multi_rankview(series, labels, fpath, fig=None):
    '''Plot multiple stats_helper.get_cdf()'s
    
    Parameters
    ----------
    cdfs : list of stats_helper.get_cdf()
    labels : list of strings
    fpath : file path were to save the plot
    '''
    if fig == None:
        fig = PdfPages(fpath + '.pdf')
    ax = plt.subplot(111)
    for ser, labl in zip(series, labels):
        cdf.plot(label=labl)
        if cdf.index.values.std() > co.LOGX_LIM:
            logx = True
    if logx:
        ax.semilogx()
    ax.set_ylabel(printing.get_ylabel( 'cdf' ))
    ax.legend(loc='best')
    fig.savefig()
    fig.close()
    plt.close()

def plot_emp_dist(dist_type, emp_dist, colname, fpath):
    '''Plot a CDF or CCDF'''
    fig = PdfPages(fpath + '.pdf')
    ax = emp_dist.plot()
    if emp_dist.index.values.std() > co.LOGX_LIM:
        try:
            ax.semilogx()
        except:
            ax.set_xscale(u'linear')
            print 'Data seems not to be heavy-tailed. No log-scaling.'
    ax.set_xlabel(printing.get_xlabel( colname ))
    ax.set_ylabel(printing.get_ylabel( dist_type ))
    fig.savefig()
    fig.close()
    plt.close()

def plot_cdf(cdf, colname, tpath):
    '''Plot a stats_helper.get_cdf()'''
    islog = ''
    if cdf.index.values.std() > co.LOGX_LIM:
        islog = 'log'
    fn = '_'.join([colname, islog, 'CDF'])
    fpath = osp.join(tpath, fn)
    plot_emp_dist('cdf', cdf, colname, fpath)

def plot_ccdf(ccdf, colname, tpath):
    '''Plot a stats_helper.get_ccdf()'''
    islog = ''
    if ccdf.index.values.std() > co.LOGX_LIM:
        islog = 'log'
    fn = '_'.join([colname, islog, 'CCDF'])
    fpath = osp.join(tpath, fn)
    plot_emp_dist('ccdf', ccdf, colname, fpath)
    
def plot_multi_cdf(cdfs, labels, fpath, fig=None):
    '''Plot multiple stats_helper.get_cdf()'s
    
    Parameters
    ----------
    cdfs : list of stats_helper.get_cdf()
    labels : list of strings
    fpath : file path were to save the plot
    '''
    if fig == None:
        fig = PdfPages(fpath + '.pdf')
    ax = plt.subplot(111)
    logx = False
    for cdf, labl in zip(cdfs, labels):
        cdf.plot(label=labl)
        if cdf.index.values.std() > co.LOGX_LIM:
            logx = True
    if logx:
        ax.semilogx()
    ax.set_ylabel(printing.get_ylabel( 'cdf' ))
    ax.legend(loc='best')
    fig.savefig()
    fig.close()
    plt.close()

def plot_df_cdfs(df, fpath, return_plot=False):
    fig = PdfPages(fpath + '.pdf')
    ax = plt.subplot(111)
    logx = False
    for col in df.names:
        col_cdf = shelp.get_cdf(df[col])
        col_cdf.plot(label=col)
        if col_cdf.index.values.std() > co.LOGX_LIM:
            logx = True
    if logx:
        ax.semilogx()
    ax.set_ylabel(printing.get_ylabel( 'cdf' ))
    ax.legend(loc='best')
   
    if return_plot:
        return fig
    else:
        fig.savefig()
        fig.close()
        plt.close()

def plot_shiftfun(xs, ys, w_u=None, w_l=None, fpath='./shift'):
    fig = PdfPages(fpath + '_shift.pdf')
    ax = plt.subplot(111)
    plt.plot(xs, ys, label=r'$\hat{\Delta}(x)$')
    if w_u is not None:
        w_u.plot(label=r'$\Delta^*(x)$')
    if w_l is not None:
        w_l.plot(label=r'$\Delta_*(x)$')
    ax.legend(loc='best')
    fig.savefig()
    fig.close()
    plt.close()

def plot_resid_acf(ser, fpath='./acf'):
    fig = PdfPages(fpath + '_resid_ACF.pdf')
    ax = plt.subplot(111)
    smapi.graphics.tsa.plot_acf(ser.values.squeeze())
    fig.savefig()
    fig.close()
    plt.close()

def plot_resid_pacf(ser, fpath='./pacf'):
    fig = PdfPages(fpath + '_resid_PACF.pdf')
    ax = plt.subplot(111)
    smapi.graphics.tsa.plot_pacf(ser.values.squeeze())
    fig.savefig()
    fig.close()
    plt.close()

