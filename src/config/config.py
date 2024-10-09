import python_weather

import asyncio
import os
from datetime import date, time, timedelta
from pathlib import Path
from typing import Callable
import logging
import os
import yaml

from utils import jobs, conditions
if not os.environ.get('IS_DEV', False):
    from utils.pins import PinOut
from utils.schedule import Scheduler, Job, set_sun_lat_lon

log = logging.getLogger(__name__)


def get_config(yaml_file: Path, schedule: Scheduler | None = None):
    with open(yaml_file, 'r') as f:
        config = yaml.safe_load(f)

    # Setup pins
    if not os.environ.get('IS_DEV', False):
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
    if schedule:
        add_refresh_job = False
        skip_dates = set()
        if 'skip_dates' in config.get('schedule', []):
            skip_dates = set(config['schedule']['skip_dates'])
            config['schedule'].pop('skip_dates')
            schedule.add_skip_dates(skip_dates)

        for job_details in config.get('schedule', {}).get('jobs', []):
            if any(j not in job_details for j in ('job', 'name', 'runtime')):
                print(f"BAD CONFIG: {job_details}")
                continue

            if job_details['job'] is None:
                job = lambda i: None
            else:
                job: Callable = getattr(jobs, job_details['job'])

            if 'sunset' in job_details['runtime'] or 'sunrise' in job_details['runtime']:
                add_refresh_job = True

            log.info(f"Adding job: {job_details['name']}" + "\n" +
                     f"  runtime: {job_details['runtime']}" + "\n" +
                     f"  condition: {job_details.get('conditions')}" + "\n" +
                     f"  job: {job}" + "\n" +
                     f"  config: {config}" + "\n")

            job = Job(name=job_details['name'],
                      runtime=job_details['runtime'],
                      condition_func=conditions.get_condition_func(job_details.get('conditions', None)),
                      job=job,
                      kwargs={'config': config})
            schedule.add_job(job)

        if add_refresh_job:
            schedule.add_job(
                    Job(name='Refresh schedule order (for sunrise/sunset)',
                        job=lambda config: schedule.refresh_order(),
                        runtime='00:08:03',
                        kwargs={'config': config})
            )

    return config
