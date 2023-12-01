from datetime import date, time, timedelta
from pathlib import Path
from typing import Callable
import yaml

from utils import jobs
from utils.pins import PinOut
from utils.schedule import Scheduler, Job

CONFIG_ROOT = Path(__file__).parent
SCHEDULE = Scheduler()


def get_config():
    global SCHEDULE

    with open(CONFIG_ROOT / 'main.yaml', 'r') as f:
        config = yaml.safe_load(f)

    # Setup pins
    for pin_name, pin_num in config.get('pins', {}).items():
        config['pins'][pin_name] = PinOut(pin_num, pin_name)

    # Setup schedule
    for job_details in config.get('schedule', {}):
        runtime: time = time(*(int(i) for i in job_details['runtime'].split(':')))
        job: Callable = getattr(jobs, job_details['job'])

        job = Job(name=job_details['name'],
                  runtime=runtime,
                  job=job,
                  kwargs={'config': config})
        SCHEDULE.add_job(job)


    return SCHEDULE, config
