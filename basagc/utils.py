#!/usr/bin/env python3
""" This module contains various utility functions and classes used by basaGC"""

import logging
import time
import math
import os

from basagc import config
if config.DEBUG:
    from pudb import set_trace  # lint:ok

LOG_VIEWER = None

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%d/%m/%y %H:%M',
                    filename=os.path.join(config.BASE_DIR, "basagc.log"),
                    filemode='a')

gc_log = logging.getLogger()


def seconds_to_time(seconds):

    """ Converts a time in seconds to days, hours, minutes and seconds
    :param seconds: time in seconds to convert
    :type seconds: int or float
    :return: tuple containing days, hours, minutes, seconds
    :rtype: tuple of ints
    """

    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    return {
        "days": days,
        "hours": hours,
        "minutes": minutes,
        "seconds": round(seconds, 2),
    }


def log(message="", log_level="DEBUG"):

    """ Logs messages to log file and log viewer
    :param message: the message to log
    :type message: string
    :param log_level: the log level for this message
    :type log_level: string
    :return: nothing
    """

    if log_level not in config.LOG_LEVELS:
        gc_log.error("Log level does not exist!")
        return
    now = time.strftime("%d/%m/%Y %H:%M:%S")

    if log_level == "DEBUG":
        gc_log.debug(message)
    elif log_level == "INFO":
        gc_log.info(message)
    elif log_level == "WARNING":
        gc_log.warning(message)
    elif log_level == "ERROR":
        gc_log.error(message)
    elif log_level == "CRITICAL":
        gc_log.critical(message)
    
    # since there is no logging window yet, print message to stdout
    print("{:20}{:10}{}".format(now, log_level, message))

def vector_magnitude(vector):
    return math.sqrt(vector[0]**2 + vector[1]**2 + vector[2]**2)

def float_to_parts(number):
    """Converts the given float into two strings, one being the whole number part and the other being the fractional
    part. The decimal point is removed. Numbers are padded out with zeros on the left. This formats data for display."""
    frac_part, whole_part = math.modf(number)
    whole_part = str(int(whole_part)).zfill(5)
    frac_part = str(round(frac_part, 5))[2:].ljust(5, "0")  # [2:] to get rid of leading 0., then padded to left
    return whole_part, frac_part
