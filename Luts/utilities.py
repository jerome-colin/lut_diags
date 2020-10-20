"""
Utilities
"""

__author__ = "jerome.colin'at'cesbio.cnes.fr"
__license__ = "MIT"
__version__ = "0.1.0"

import logging
import os
from datetime import datetime


def get_logger(name, with_timestamp=False, verbose=False):
    """
    Simple logger
    :param name: eg. the app name
    :param verbose: sets DEBUG level if True
    :return: logger object
    """
    logger = logging.getLogger(name)
    if with_timestamp:
        logging_file = name + '_' + datetime.now().strftime("%y%m%d%H%M") + '.log'
    else:
        logging_file = name + '.log'

    try:
        os.remove(logging_file)
    except FileNotFoundError:
        pass

    logging_handler = logging.FileHandler(logging_file)
    logging_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    logging_handler.setFormatter(logging_formatter)
    logger.addHandler(logging_handler)
    if verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    logger.info("Generated with lut_diags version : " + __version__ + ". For help, please contact " + __author__)

    return logger
