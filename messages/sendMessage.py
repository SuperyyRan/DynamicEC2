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
#   @filename:  sendMessage.py
#   @brief:     A interface for sending messages to running daemon of EC2 instances
#   @version:   1.0
#   @author:    Yongyi Ran (yyran@ustc.edu.cn)
#   @date:      2015-04-20
#
###################################################################################


import pika
import sys
import time
import logging

if not "/home/yyran/" in sys.path:
    sys.path.append("/home/yyran/")

from DynamicEC2.common.Task import *
from DynamicEC2.common.Config import *
from DynamicEC2.common.Logger import *
from DynamicEC2.common.Message import *

try:
    import cPickle as pickle
except:
    import pickle

#send Message to VM to exec a task
def sendMessage(routings, message):
    connection = pika.BlockingConnection(pika.ConnectionParameters(getValue('mq','rabbitMQServer')))
    channel = connection.channel()

    channel.exchange_declare(exchange='messages', type='direct')
    
    for routing in routings:
        #message = '%s message.' % routing
        channel.basic_publish(exchange='messages', routing_key=routing, body=message)
        logging.debug(message)
    connection.close()

if __name__=="__main__":
    init_log(logging.DEBUG)   
    msg = Message('Check', 'Send a test message.')
    sendMessage(['i-e6ec2a11',], pickle.dumps(msg))
