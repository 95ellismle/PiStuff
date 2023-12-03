from raspi_gpio import GPIO
from time import sleep
from datetime import datetime, time, timedelta
import logging
import yaml

from config import CONFIG_ROOT
from config.config import get_config

log = logging.getLogger(__name__)
logging.basicConfig(filename='blinds.log',
                    level=logging.DEBUG,
                    format='%(asctime)s %(message)s')


if __name__ == '__main__':
    log.info("Setting up")
    GPIO.setmode(GPIO.BOARD)

    schedule = Scheduler()
    try:
        config = get_config(CONFIG_ROOT / 'main.yaml', schedule)
        SCHEDULE.run()
    finally:
       GPIO.cleanup()
