import logging
import logging.config
import logging.handlers

def init_log(log_level):

    logging.config.fileConfig("../config/logger.conf")
    logging.getLogger().setLevel(log_level)
    #logger = logging.getLogger(logger_name)

    logging.info("The logger is initilized.")

def init_vm_log(log_level):

    logging.config.fileConfig("../config/vm_logger.conf")
    logging.getLogger().setLevel(log_level)
    #logger = logging.getLogger(logger_name)

    logging.info("The logger is initilized.")
