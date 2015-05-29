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
#   @filename:  Task.py
#   @brief:     A class for task
#   @version:   1.0
#   @author:    Yongyi Ran (yyran@ustc.edu.cn)
#   @date:      2015-04-20
#
###################################################################################


import time
import logging

class Task:
    def __init__(self, id, usrid, cpu, execParameter, taskType):
        self.id = id
        self.userId = usrid
        #cpu requirement
        self.cpu = cpu
        #list of exec parameters indicating the computation complexity
        self.execParameter = execParameter
        #the type of task
        self.taskType = taskType
        self.arrival_time = -1.0
        self.start_time = -1.0
        self.end_time = -1.0
        self.allocated_vms = []
        self.finish_flags = -1
    
    def printTask(self):
        logging.info('-----Task user id:-----%d' %(self.userId))
        logging.info('-----Task id:-----%d' %(self.id))
        logging.info('-----Task cpu:-----%d' %(self.cpu))
        logging.info('-----Task para:-----%d' % (self.execParameter))
        logging.info('-----Task type:-----%s' % (self.taskType))
        logging.info('-----Task arrival time:-----%f' % (self.arrival_time))
        if self.start_time != -1.0:
            logging.info('-----Task start time:-----%f' % (self.start_time))
        if self.end_time != -1.0:
            logging.info('-----Task end time:-----%f' % (self.end_time))
        if self.finish_flags != -1:
            logging.info('-----Task finish flag:-----%d' % (self.finish_flags))
    
    def printAllocatedVMsofTask(self):
        logging.info('-----The allocated VMs for Task: %d' %(self.id))
        for vm in self.allocated_vms:
            logging.info(vm.vId)
