from raspi_gpio import GPIO

from config.config import get_config
from config import CONFIG_ROOT

from utils import jobs


if __name__ == '__main__':
    try:
        config = get_config(CONFIG_ROOT / 'main.yaml')
        jobs.both_blinds_down(config)
    finally:
        GPIO.cleanup()
