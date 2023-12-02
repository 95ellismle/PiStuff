from datetime import date, time, timedelta
from pathlib import Path
from typing import Callable
import yaml

from utils import jobs
from utils.pins import PinOut
from utils.schedule import Scheduler, Job, set_sun_lat_lon

CONFIG_ROOT = Path(__file__).parent
SCHEDULE = Scheduler()


def get_config():
    global SCHEDULE

    with open(CONFIG_ROOT / 'main.yaml', 'r') as f:
        config = yaml.safe_load(f)

    # Setup pins
    for pin_name, pin_num in config.get('pins', {}).items():
        config['pins'][pin_name] = PinOut(pin_num, pin_name)

    # Settings
    settings = config['settings']
    latitude = settings.get('latitude')
    longitude = settings.get('longitude')
    if latitude and longitude:
        set_sun_lat_lon(latitude, longitude)


    # Setup schedule
    for job_details in config.get('schedule', {}):
        job: Callable = getattr(jobs, job_details['job'])
        job = Job(name=job_details['name'],
                  runtime=job_details['runtime'],
                  job=job)
        SCHEDULE.add_job(job)


    return SCHEDULE, config
