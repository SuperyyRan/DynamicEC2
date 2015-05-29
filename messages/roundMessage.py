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

#send Message to VM and wait for response
global response

def roundMessage(routing, message):
    global response
    response = None
    connection = pika.BlockingConnection(pika.ConnectionParameters(getValue('mq','rabbitMQServer')))
    channel = connection.channel()

    channel.exchange_declare(exchange='messages', type='direct')
    result = channel.queue_declare(exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange='messages',
                        queue=queue_name,
                        routing_key='server-check')
    
    channel.basic_consume(callback, queue=queue_name, no_ack=False)
    
#    while response is None:
#        time.sleep(2)
    channel.basic_publish(exchange='messages', routing_key=routing, body=message)
    logging.debug(message)
    connection.process_data_events()
    connection.close()
    
    if response is None:
        logging.info('Check status failed, response is None.')
        return 'Error'

    content = pickle.loads(response)
    if content.type == 'ReCheck':
        status = content.arg
    return status

def callback(ch, method, props, body):
    global response
    response = body

#for test
if __name__=="__main__":
    init_log(logging.DEBUG)   
    msg = Message('Check', 'Check the status of %s' %('i-e6ec2a11'))
    status = roundMessage('i-e6ec2a11', pickle.dumps(msg))
    logging.info(status)
