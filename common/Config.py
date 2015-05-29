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
#   @filename:  Config.py
#   @brief:     parser the config files in ../config
#   @version:   1.0
#   @author:    Yongyi Ran (yyran@ustc.edu.cn)
#   @date:      2015-04-20
#
###################################################################################


from ConfigParser import SafeConfigParser
import codecs
import logging
import sys
import random

from Logger import *

def getAllsections():
    try:
        parser =SafeConfigParser()
        # Open the file with the correctencoding
        with codecs.open('../config/run.conf','r',encoding='utf-8') as f:
            parser.readfp(f)
    except Exception as e:
        logging.error(e)
        sys.exit(1)
    return parser.sections()

def getOptionsofSection(section):
    try:
        parser =SafeConfigParser()
        # Open the file with the correctencoding
        with codecs.open('../config/run.conf','r',encoding='utf-8') as f:
            parser.readfp(f)
    except Exception as e:
        logging.error(e)
        sys.exit(1)
    try:
        options = parser.options(section)
    except Exception as e:
        logging.error(e)
        sys.exit(1)
    return options

def getValue(section,option):
    try:
        parser =SafeConfigParser()
        with codecs.open('../config/run.conf','r',encoding='utf-8') as f:
            parser.readfp(f)
    except Exception as e:
        logging.error(e)
        sys.exit(1)
    try:
        str_value = parser.get(section, option)
    except Exception as e:
        logging.error(e)
        sys.exit(1)
    return str_value

def getItemsofSection(section):
    try:
        parser =SafeConfigParser()
        # Open the file with the correctencoding
        with codecs.open('../config/run.conf','r',encoding='utf-8') as f:
            parser.readfp(f)
    except Exception as e:
        logging.error(e)
        sys.exit(1)
    try:
        items = parser.items(section)
    except Exception as e:
        logging.error(e)
        sys.exit(1)
    return items

#for test
if __name__ == '__main__':
    init_log(logging.DEBUG)
    items = getItemsofSection('t1')
    options = getOptionsofSection('t2')
    print items[1][1]
    print options
    sections = getAllsections()
    if 'task' in sections:
        keys = getValue('t1','execparameter')
    for k in keys:
        print k

    keys = getValue('task', 'keys')
    task_set = []
    for k in keys:
        task_set.append(getItemsofSection(k))
    p1 = random.sample(task_set,1).pop()
    print p1
    print random.sample(p1[1][1].split(','),1).pop()
