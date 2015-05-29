#!/usr/bin/env python
# -*- coding:utf-8 -*-
###################################################################################
#
#   Copyright 2015-2016 University Of Science and Technology of China (USTC)
#   Licensed under the Apache License, Version 2.0 (the "License"); you may 
#   not use this file except in compliance with the License. You may obtain 
#   a copy of the License at
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   @filename:  rate_function.py
#   @brief:     calculate the value of l(a_0)
#   @version:   1.0
#   @author:    Yongyi Ran (yyran@ustc.edu.cn)
#   @date:      2015-04-20
#
###################################################################################


import sys
from math import exp as exp
from math import log as log
import logging

if not "/home/yyran/" in sys.path:
    sys.path.append("/home/yyran/") 

from DynamicEC2.common.Task import *
from DynamicEC2.common.VM import *
from DynamicEC2.common.VmList import *
from DynamicEC2.common.Logger import *
from DynamicEC2.common.Config import *


def function(x, a, pi_delta):
    M_x = 0
    for i in pi_delta.keys():
        M_x = M_x + pi_delta[i]*exp(i*x)
    f = a * x - log(M_x)
    return f

def max_f(a, pi_delta):
    i = 0
    x0 = -5.0
    step = 0.01
    x1 = x0+step
    x2 = x1+step

    while(i < 10000):
        i = i+1
        fx0 = function(x0, a, pi_delta)
        fx1 = function(x1, a, pi_delta)
        fx2 = function(x2, a, pi_delta)
    
        if fx0 < fx1 and fx1 < fx2:
            x0 = x1
            x1 = x2
            x2 = x1 + step
        elif fx0 <= fx1 and fx1 >= fx2:
            logging.info('The value of x0 x1 x2: %f %f %f' %(x0, x1, x2))
            break
        else:
            logging.info('input error, no solution!')
            return -1
  
    while((x2 - x0) > 0.00001):
        x1 = (x2 + x0)/2
        if function(x0, a, pi_delta) < function(x1, a, pi_delta) and function(x1, a, pi_delta) < function(x2, a, pi_delta):
            x0 = x1
        if function(x0, a, pi_delta) > function(x1, a, pi_delta) and function(x1, a, pi_delta) > function(x2, a, pi_delta):
            x2 = x1
        if function(x0, a, pi_delta) <= function(x1, a, pi_delta) and function(x1, a, pi_delta) >= function(x2, a, pi_delta):
            x0 = (x0 + x1)/2
            x2 = (x2 + x1)/2

    #return x1
    logging.info('The point of max value: %f' %(x1))
    logging.info('The max value: %f' %(function(x1, a, pi_delta)))
    return function(x1, a, pi_delta)

#for test
if __name__ == '__main__':
    init_log(logging.DEBUG)
    a = 6
    pi_delta = {-10:0.15, -8:0.2, -6:0.1, -3:0.05, 1:0.1, 4:0.1, 6:0.05, 8:0.1, 9:0.05, 11:0.1}
    result = max_f(a, pi_delta)
    logging.info("The max value is: " + str(result))
    logging.info('The probility is: %f' %(exp(-10*result)))
