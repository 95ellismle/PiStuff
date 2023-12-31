from raspi_gpio import GPIO
from time import sleep
from datetime import datetime, time, timedelta
import logging
import yaml

from utils.schedule import Scheduler
from config import CONFIG_ROOT
from config.config import get_config

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s')


if __name__ == '__main__':
    log.info("Setting up")
    schedule = Scheduler()
    try:
        config = get_config(CONFIG_ROOT / 'main.yaml', schedule)
        schedule.run()
    finally:
       GPIO.cleanup()
