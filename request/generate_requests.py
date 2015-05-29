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
#   @filename:  request_time.py
#   @brief:     generating the interval time of the requests (exponential distribution)
#   @version:   1.0
#   @author:    Yongyi Ran (yyran@ustc.edu.cn)
#   @date:      2015-04-20
#
###################################################################################

import numpy as np
import matplotlib.pyplot as plt
import time
import sys
import logging
import numpy as np
import random

if not "/home/yyran/" in sys.path:
    sys.path.append("/home/yyran/")

from DynamicEC2.common.Task import *
from DynamicEC2.common.Logger import *
from DynamicEC2.common.Config import *

try:
    import cPickle as pickle
except:
    import pickle


#Parameters:    
#   @scale :float
#           The scale parameter, \beta = 1/\lambda.
#   @size : int or tuple of ints, optional
#           Output shape. If the given shape is, e.g., (m, n, k), then m * n * k samples are drawn.
#


def generate_requests(usrid):
    init_log(logging.DEBUG)
    time_request = np.random.exponential(15,1000)
    np.savetxt('request_time.txt', time_request)

#t2 = np.loadtxt('request_time.txt')

#print t,t2

#count, bins, ignored = plt.hist(t, 10, normed=True)
#plt.show()
    
    task_set = []
    getTasktypes(task_set)
    id = 1
    cpu = 1
    all_tasks = []
    for i in time_request:
        #logging.info('The next task will arrive after %f seconds.' %(i))
        #time.sleep(float(i))
        m_task = constructTask(task_set, id, usrid, cpu)
        logging.info("send a Task to server: %d" % (id))
        m_task.printTask()
        d_task = pickle.dumps(m_task)
        all_tasks.append(d_task)
        id += 1
    #end_task
    #np.savetxt('all_task.txt', all_tasks)
    f = open('all_task.txt','w')
    for t in all_tasks:
        f.write(t)
        f.write('\n\n')

def getTasktypes(task_set):
    keys_str = getValue('task', 'keys')
    keys = keys_str.split(',')
    for k in keys:
        task_set.append(getItemsofSection(k))

def constructTask(task_set, id, usrid, cpu):
    p1 = random.sample(task_set, 1).pop()
    t_name = p1[0][1]
    t_para = int(random.sample(p1[1][1].split(','),1).pop())
    t = Task(id, usrid, cpu, t_para, t_name)
    return t

if __name__=="__main__":
    usrid = sys.argv[1:]
    if not usrid:
        usrid = [1]
    generate_requests(int(usrid.pop()))
    
    #all_tasks = []
    #str_tasks = ''
    #f = open('all_task.txt', 'r')
    #str_tasks = f.read()
    #str_list = str_tasks.split('\n\n')
    ##print str_list[0]
    #for t in str_list:
    #    if t != '':
    #        t1 = pickle.loads(t)
    #        print '----------------'
    #        print t1.id
    #        print t1.taskType
    #        print t1.execParameter
    #        print '----------------'       
