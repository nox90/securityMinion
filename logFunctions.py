#
# Log functions
#

import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def log(log_text):
    logger.info(log_text)
