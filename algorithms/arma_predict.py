#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
if not "/home/yyran/" in sys.path:
    sys.path.append("/home/yyran/") 


from statsmodels.tsa.arima_model import _arma_predict_out_of_sample
import statsmodels.api as sm

def arma_predict(data, step):
    #res = sm.tsa.ARMA(data, (2, 1)).fit(trend="nc")
    res = sm.tsa.ARMA(data, (2, 1)).fit()
    
    # get what you need for predicting one-step ahead
    params = res.params
    residuals = res.resid
    p = res.k_ar
    q = res.k_ma
    k_exog = res.k_exog
    k_trend = res.k_trend
    steps = step

    return _arma_predict_out_of_sample(params, steps, residuals, p, q, k_trend, k_exog, endog=data, exog=None, start=len(data))


#for test
if __name__ == '__main__':
    #data = [5,7,9,12,15,6,5,-3,15,18,22,6,2,7,9,11,13,15,16,15,23,27,14,16,11,10,4,3,-1,3,6,8,9,12,16]
    data = [5,7,12,15,9,15]
    print arma_predict(data, 1)
