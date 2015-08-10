# -*- coding: utf-8 -*-

vsz = 'vidsz'


xlabels = { 'used' : 'memory in MB', 
            'free' : 'memory in MB',
            'buff' : 'memory in MB', 
            'cach' : 'memory in MB', 
            'recv' : 'data volume in MB/s', 
            'send' : 'data volume in MB/s',
            'read' : 'data volume in MB/s', 
            'writ' : 'data volume in MB/s',
            'disk' : 'data volume in MB/s',
            'usr'  : 'CPU time in %',
            'sys'  : 'CPU time in %',
            'idl'  : 'CPU time in %',
            'wai'  : 'CPU time in %', 
            'siq'  : 'CPU time in %', 
            'hiq'  : 'CPU time in %', 
            'cpu'  : 'CPU time in %', 
            'X1m'  : 'run queue length', 
            'X5m'  : 'run queue length', 
            'X15m' : 'run queue length',
            'power': 'power consumption in Watt',
            'rvp'  : 'Rank',
            vsz    : 'File Size in MB',
            'trsz' : 'File Size in MB',
          }

ylabels = { 'cdf' : 'Pr[X <= x]',
            'ccdf': 'Pr[X > x]',
            'rvp' : 'View Count',
          }

col_groups = { 'usr'  : 'CPU'  ,
               'sys'  : 'CPU'  ,
               'idl'  : 'CPU'  ,
               'wai'  : 'CPU'  ,
               'siq'  : 'CPU'  ,
               'hiq'  : 'CPU'  ,
               'cpu'  : 'CPU'  ,
               '1m'   : 'LOAD' ,
               '5m'   : 'LOAD' ,
               '15m'  : 'LOAD',
               'used' : 'MEM' ,
               'buff' : 'MEM' , 
               'cach' : 'MEM' ,
               'free' : 'MEM' ,
               'recv' : 'NET' ,
               'send' : 'NET' ,
               'read' : 'DISK',
               'writ' : 'DISK',
               'disk' : 'DISK',
               'power': 'PWR',
               'trsz' : 'RQSZ',
             }

scales = { 'used' : 1000000,
           'free' : 1000000,
           'buff' : 1000000,
           'cach' : 1000000,
           'recv' : 1000000,
           'send' : 1000000,
           'read' : 1000000,
           'writ' : 1000000,
           'disk' : 1000000,
           'usr'  : 1,
           'sys'  : 1,
           'idl'  : 1,
           'wai'  : 1,
           'siq'  : 1,
           'hiq'  : 1,
           'cpu'  : 1,
           'X1m'  : 1,
           'X5m'  : 1,
           'X15m' : 1,
           'power': 1,
           'trsz' : 1,
          }

#logxs = ['rqsz', 'trsz', 'vidsz']
logxs = []


def wrap_term_log10(factor):
    return 'np.log10(' + factor + ')'

def cond_wrap_term_log10(factor):
    if factor in logxs:
        return wrap_term_log10(factor)
    else:
        return factor

def unwrap_factor(factor):
    l_par_idx = factor.rfind('(')
    r_par_idx = factor.find(')')
    if l_par_idx > -1 and r_par_idx > -1:
        return factor[l_par_idx + 1: r_par_idx]
    else:
        return factor

def get_xlabel(colname):
    if colname in xlabels:
        return xlabels[colname]
    else:
        return colname

def get_ylabel(plt_type):
    if plt_type in ylabels:
        return ylabels[plt_type]
    else:
        return plt_type

def get_col_group(colname):
    if colname in col_groups:
        return col_groups[colname]
    else:
        return 'DEFAULT'

def get_scale(colname):
    if colname in scales:
        return scales[colname]
    else:
        return 1
