import pandas as pan

intercept = 'Intercept'

# NAMES
VSZN  = 'vidsz'
RQSZN = 'trsz'

# COLUMN names
CN_1M        = '1m'
CN_5M        = '5m'
CN_15M       = '15m'
CN_ARAT      = 'arate'
CN_CPU       = 'cpu'
CN_DISK      = 'disk'
CN_DISKLOG10 = 'disklog10'
CN_DLTIME    = 'dltime'
CN_DUTIL     = 'dutl'
CN_FNAME     = 'fname'
CN_IATS      = 'iats'
CN_IDL       = 'idl'
CN_INTERCEPT = 'Intercept'
CN_NET       = 'net'
CN_NETLOG10  = 'netlog10'
CN_NUTIL     = 'nutl'
CN_PWR       = 'power'
CN_READ      = 'read'
CN_RECV      = 'recv'
CN_SEND      = 'send'
CN_SYS       = 'sys'
CN_TRSZ      = 'trsz'
CN_TRSZLOG10 = 'trszlog10'
CN_USR       = 'usr'
CN_VSZ       = 'vidsz'
CN_VSZLOG10  = 'vidszlog10'
CN_WAI       = 'wai'
CN_WAIT      = 'wait'
CN_WRIT      = 'writ'
CN_X1M       = 'X1m'
CN_X5M       = 'X5m'
CN_X15M      = 'X15m'

CN_R2ADJ    = 'R^2 adj'
CN_DW       = 'Durbin-Watson'
CN_DW1_SYM  = 'DW 1%'
CN_DW5_SYM  = 'DW 5%'
CN_LAGS     = 'lags'
CN_STD_INT  = 'STD int abs'
CN_STD_REGS = 'STD reg mean abs'
CN_STEPS    = 'nobs'

# DICT keys
RUK   = 'RU'
PWRK  = 'PWR'
WLK   = 'WL'
VSZK  = 'VSZ'
ARATK = 'ARAT'
DLTMK = 'DLTM'

# TASK names
DLK = 'D'
TCK = 'T'
BMK = 'B'
DLTCK = 'C'
TCBMK = 'X'

AD    = 'ad'
KS    = 'ks'
MSE   = 'mse'
MPE   = 'mpe'
PDEV  = 'pdev'
SUMM  = 'summ'
VALS  = 'vals'
REG_S = 'regsumm'
REG_P = 'regparm'
REG_R = 'result'
OVRL_RES = 'ovrl'
OVRL_RES_IDX = 'index'

ERR_AMAX = 'err abs max'
ERR_AAVG = 'err abs avg'
ERR_AMED = 'err abs med'
ERR_PMAX = 'err perc max'
ERR_PAVG = 'err perc avg'
ERR_PMED = 'err perc med'


# DIRECTORIES 
MEAS_DIRN = 'Measurement'
RUK_DIRN = 'Performance'
PWRK_DIRN  = 'Power'
WLK_DIRN   = 'Workload'
RES_DIRN  = 'Results'

#FILE NAMES
FN_RES_STAT = 'result_stats'

# FILE EXTENSIONS
X_AD   = 'ad'
X_CSV  = 'csv'
X_ERR  = 'err'
X_FITV = 'vals'
X_KS   = 'ks'
X_MPE  = 'mpe'
X_MSE  = 'mse'
X_PDEV = 'pdev'
X_PDF  = 'pdf'
X_REGP = 'regparm'
X_REGS = 'regsumm'
X_SUMM = 'summ'
X_TIME = 'times'
X_VALS = 'vals'
X_XLOG = 'xlog'

#REGRESSION MODELS
REGR_OLS = 'ols'
REGR_GLSAR = 'glsar'

# SWITCHES, i.e. which task triggers which evaluation procedures
RSWITCHES = {DLK:0b1111, TCK:0b1111, BMK:0b1100}
EVAL_CPU  = 0b1000
EVAL_LAVG = 0b0100
EVAL_DISK = 0b0010
EVAL_NET  = 0b0001

ESWITCHES = {DLK:0b1111, TCK:0b0111, BMK:0b0011}
EV_VSZ     = 0b1000
EV_WL      = 0b0100
EV_RU      = 0b0010
EV_PWR     = 0b0001

LOGX_LIM = 1000

# DATA STRUCTURES
VSZ_PTNS = {DLK: 'vidsizes*', TCK: 'vpaths*sizes'}

PREDS = {DLK: {RUK:[
#TODO add additional column with transformed data to pred_DF
#workaround since unpickling RegressionResult with tranformed vars fails
                    #[[CN_TRSZ], CN_TRSZ],
                    #[[CN_TRSZLOG10, CN_IATS], CN_TRSZLOG10 + ':' + CN_IATS], 
                    [[CN_TRSZLOG10], CN_TRSZLOG10], 
                    [[CN_TRSZLOG10, CN_ARAT], CN_TRSZLOG10 + ':C(' + CN_ARAT + ')'], 
                    [[CN_VSZLOG10], CN_VSZLOG10],
                    [[CN_VSZLOG10, CN_ARAT], CN_VSZLOG10 + ':C(' + CN_ARAT + ')'], 
                   ],
               #PWRK :[['sys'],['usr'],['wai'],['cpu'], ['cpu','net','disk']]
               PWRK: [
                      #[[CN_CPU], CN_CPU], 
                      [[CN_X1M], CN_X1M], 
                      [[CN_X5M], CN_X5M], 
                      [[CN_X15M], CN_X15M], 
                      [[CN_SYS], CN_SYS], 
                      #[[CN_CPU,CN_NETLOG10,CN_DISKLOG10],
                          #'+'.join([CN_CPU,CN_NETLOG10,CN_DISKLOG10])],
                      #[[CN_CPU,CN_NET,CN_DISK],
                          #'+'.join([CN_CPU,CN_NET,CN_DISK])],
                     ],
               WLK: [
                    [[CN_VSZLOG10], CN_VSZLOG10],
                    #[[CN_VSZ], CN_VSZ],
                    ],
                  },
           TCK: {RUK:[
                      #[['trsz'], 'np.log(trsz)'],
                      [[CN_TRSZLOG10], CN_TRSZLOG10], 
                      #[[CN_TRSZLOG10, CN_IATS], CN_TRSZLOG10 + ':' + CN_IATS], 
                      #[['trsz','iats'], 'np.log10(trsz):iats'],
                      #[['trsz','arate'], 'np.log10(trsz):arate'],
                     ],
               #PWRK :[['usr'],['sys'],['wai'],['cpu']]
                 PWRK :[
                        [[CN_CPU], CN_CPU],
                        [[CN_USR], CN_USR],
                        [[CN_SYS], CN_SYS],
                        [[CN_X1M], CN_X1M],
                        [[CN_X5M], CN_X5M],
                        [[CN_X15M], CN_X15M], 
                        #[[CN_CPU,CN_NET,CN_DISK], '+'.join([CN_CPU,CN_NET,CN_DISK])],
                        #[[CN_SYS,CN_NET,CN_DISK], '+'.join([CN_SYS,CN_NET,CN_DISK])],
                       ]
                  },
           BMK: {RUK:[
                     ],
                 PWRK:[
                        [[CN_CPU], CN_CPU],
                        [[CN_USR], CN_USR],
                        [[CN_SYS], CN_SYS],
                        [[CN_X1M], CN_X1M], 
                        [[CN_X5M], CN_X5M], 
                        [[CN_X15M], CN_X15M],
                      ]
                  }
           }

COMBIPREDS = {DLK: {
                RUK:[
                    ],
                PWRK :[ 
                   #[[CN_CPU, CN_IATS], CN_CPU + ':' + CN_IATS], 
                   #[[CN_CPU,CN_ARAT], CN_CPU + ':C(' + CN_ARAT + ')'],
                   [[CN_SYS,CN_ARAT], CN_SYS + ':C(' + CN_ARAT + ')'],
                   [[CN_X1M,CN_ARAT], CN_X1M + ':C(' + CN_ARAT + ')'],
                   [[CN_X5M,CN_ARAT], CN_X5M + ':C(' + CN_ARAT + ')'],
                   [[CN_X15M,CN_ARAT], CN_X15M + ':C(' + CN_ARAT + ')'],
                   #[[CN_SYS,CN_NET,CN_DISK,CN_ARAT], 
                       #'(' + '+'.join([CN_SYS,CN_NET,CN_DISK]) + '):C(' + CN_ARAT + ')'],
                    #[[CN_TRSZLOG10], CN_TRSZLOG10], 
                     ],
                  },
            TCK: {
                RUK:[
                     ],
                PWRK :[
                       #[['cpu','net','disk','arate'], '(cpu+net+disk):C(arate)'],
                       #[['cpu','nutl','dutl','arate'], '(cpu+nutl+dutl):C(arate)'],
                        #[[CN_CPU, CN_IATS], CN_CPU + ':' + CN_IATS], 
                      ],
                  },
           BMK: {
                RUK:[
                    ],
                PWRK:[
                     ]
                  }
           }

MACH_MAP = {DLK:  'cndl' , TCK:  'cntc' , BMK:  'vidserver' }

DIRN_MAP = {RUK: RUK_DIRN, PWRK: PWRK_DIRN, WLK: WLK_DIRN}

BMK_SZ_MAP = {'ref': '0', 'train': '1', 'test': '2'}
TCONT_MAP = {'flv': '0', 'matroska': '1', 'webm': '2'}

CLIENT_LOG_NS = ['task', 'fname', 'datetime', 'trsz', 'wait', 'dltime',
    'status']

TCONTS = ['flv', 'matroska', 'webm']


'''Asymptotical critical values for W band, see [Doksum 1977]'''
#[a][alpha]
W_BAND_K = {0.25: {0.2: 2.109, 0.1: 2.482, 0.04: 2.879, 0.02: 3.138},
            0.1 : {0.2: 2.482, 0.1: 2.789, 0.04: 3.138, 0.02: 3.371},
           }

#[a][alpha][n]
W_BAND_K_e = {
    0.1: {
        0.05: {
            5: 2.6556, 6: 2.7436, 7: 2.8069, 8: 2.6249, 9: 2.6751, 10: 2.7156, 
            15: 2.7176, 20: 2.7139, 25: 2.7104, 30: 2.7078, 35: 2.7061, 
            40: 2.7050, 45: 2.7303, 
            50: 2.7292},
        0.02: {
             5: 3.2948,  6: 3.2660,  7: 3.0986,  8: 3.1713,  9: 3.2270, 
            10: 3.1623, 11: 3.1017, 12: 3.1395, 13: 3.1715, 14: 3.1990, 
            15: 3.0870, 16: 3.1118, 17: 3.1338, 18: 3.1534, 19: 3.1354, 
            20: 3.0910, 21: 3.1076, 22: 3.1227, 23: 3.1366, 24: 3.1300, 
            25: 3.0887, 26: 3.1010, 27: 3.1123, 28: 3.1230, 29: 3.1329, 
            30: 3.0850, 31: 3.0946, 32: 3.1037, 33: 3.1123, 34: 3.1204, 
            35: 3.0989, 36: 3.0892, 37: 3.0967, 38: 3.1038, 39: 3.1107, 
            40: 3.1172, 41: 3.0847, 42: 3.0910, 43: 3.0971, 44: 3.1030, 
            45: 3.1086, 46: 3.1141, 47: 3.0865, 48: 3.0918, 49: 3.0969, 
            50: 3.1019},
        0.01: {10: 3.4331, 15: 3.4392, 20: 3.4245, 25: 3.0480, 30: 3.3933, 35: 
            3.3808, 40: 3.3704, 45: 3.3618, 50: 3.3545},
        },
    }

#[alpha]
W_BAND_K_c = {0.05: 1.358, 0.025: 1.48, 0.02: 1.517, 0.01: 1.628, 0.005: 1.73,
        0.001: 1.949}
        
#Critical values for Durbin-Watson test, 1% sign. level. [Savin1977]
# and https://web.stanford.edu/~clint/bench/dw01a.htm
#{#regressors: {#residuals: (dL, dU), }}
dw01 = pan.read_csv('dw01', index_col=False)
dw01[['K']] = dw01[['K']].subtract(1) # we don't count Intercept as regressor
tmp_dict = dw01.to_dict()
DW_CRIT_1 = dict()
for i in range(len(dw01)):
    try:
        DW_CRIT_1[tmp_dict['K'][i]][tmp_dict['T'][i]] = (tmp_dict['dL'][i], tmp_dict['dU'][i])
    except:
        DW_CRIT_1[tmp_dict['K'][i]] = dict()
        DW_CRIT_1[tmp_dict['K'][i]][tmp_dict['T'][i]] = (tmp_dict['dL'][i], tmp_dict['dU'][i])

#Critical values for Durbin-Watson test, 5% sign. level. [Savin1977]
# and https://web.stanford.edu/~clint/bench/dw05a.htm
#{#regressors: {#residuals: (dL, dU), }}
dw05 = pan.read_csv('dw05', index_col=False)
dw05[['K']] = dw05[['K']].subtract(1) # we don't count Intercept as regressor
tmp_dict = dw05.to_dict()
DW_CRIT_5 = dict()
for i in range(len(dw01)):
    try:
        DW_CRIT_5[tmp_dict['K'][i]][tmp_dict['T'][i]] = (tmp_dict['dL'][i], tmp_dict['dU'][i])
    except:
        DW_CRIT_5[tmp_dict['K'][i]] = dict()
        DW_CRIT_5[tmp_dict['K'][i]][tmp_dict['T'][i]] = (tmp_dict['dL'][i], tmp_dict['dU'][i])

LOG_ASSOC = {
        CN_1M        : RUK,
        CN_5M        : RUK,
        CN_15M       : RUK,
        CN_ARAT      : WLK,
        CN_CPU       : RUK,
        CN_DISK      : RUK,
        CN_DISKLOG10 : RUK,
        CN_DUTIL     : RUK,
        CN_FNAME     : WLK,
        CN_IATS      : WLK,
        CN_IDL       : RUK,
        CN_NET       : RUK,
        CN_NETLOG10  : RUK,
        CN_NUTIL     : RUK,
        CN_PWR       : PWRK,
        CN_READ      : RUK,
        CN_RECV      : RUK,
        CN_SEND      : RUK,
        CN_SYS       : RUK,
        CN_TRSZ      : WLK,
        CN_TRSZLOG10 : WLK,
        CN_USR       : RUK,
        CN_VSZ       : VSZK,
        CN_VSZLOG10  : VSZK,
        CN_WAI       : RUK,
        CN_WAIT      : WLK,
        CN_WRIT      : RUK,
        CN_X1M       : RUK,
        CN_X5M       : RUK,
        CN_X15M      : RUK,
        } 
