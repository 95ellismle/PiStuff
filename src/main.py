import RPi.GPIO as GPIO
from time import sleep
from datetime import datetime, time, timedelta
import logging
import yaml

from config import get_config, SCHEDULE

log = logging.getLogger(__name__)
logging.basicConfig(filename='blinds.log',
                    level=logging.DEBUG,
                    format='%(asctime)s %(message)s')


if __name__ == '__main__':
    log.info("Setting up")
    try:
        GPIO.setmode(GPIO.BOARD)
        SCHEDULE, CONFIG = get_config()
        SCHEDULE.run()
    finally:
       GPIO.cleanup()
