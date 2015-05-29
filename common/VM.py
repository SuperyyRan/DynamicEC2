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
#   @filename:  VM.py
#   @brief:     A class definition of VM
#   @version:   1.0
#   @author:    Yongyi Ran (yyran@ustc.edu.cn)
#   @date:      2015-04-20
#
###################################################################################


class VM:
    def __init__(self, vId, vcpu):
        self.vId = vId
        self.vcpu = vcpu
        # busy or nor ready:false or idle:true
        self.vstatus = True
        self.vtaskId = -1
        self.vusr = -1
        #running:true or stop:false
        self.vflag = True
