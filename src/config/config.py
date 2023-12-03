from datetime import date, time, timedelta
from pathlib import Path
from typing import Callable
import yaml

from utils import jobs
from utils.pins import PinOut
from utils.schedule import Scheduler, Job, set_sun_lat_lon


def get_config(yaml_file: Path, schedule: Scheduler):
    with open(yaml_file, 'r') as f:
        config = yaml.safe_load(f)

    # Setup pins
    for pin_name, pin_num in config.get('pins', {}).items():
        config['pins'][pin_name] = PinOut(pin_num, pin_name)

    # Settings
    settings = config.get('settings')
    if settings:
        latitude = settings.get('latitude')
        longitude = settings.get('longitude')
        if latitude and longitude:
            set_sun_lat_lon(latitude, longitude)

    # Setup schedule
    add_refresh_job = False
    for job_details in config.get('schedule', []):
        if job_details['job'] is None:
            job = lambda i: None
        else:
            job: Callable = getattr(jobs, job_details['job'])

        if 'sunset' in job_details['runtime'] or 'sunrise' in job_details['runtime']:
            add_refresh_job = True

        job = Job(name=job_details['name'],
                  runtime=job_details['runtime'],
                  job=job,
                  kwargs={'config': config})
        schedule.add_job(job)

    if add_refresh_job:
        schedule.add_job(
                Job(name='Refresh schedule order (for sunrise/sunset)',
                    job=lambda i: schedule.refresh_order(),
                    runtime='00:08:03')
        )

    return config