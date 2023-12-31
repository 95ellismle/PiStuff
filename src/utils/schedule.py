from typing import Any, Callable
from datetime import datetime, time, timedelta, date
from dataclasses import dataclass, field
import logging
import suntime
from time import sleep

log = logging.getLogger(__name__)
SUN: suntime.Sun | None = None


def set_sun_lat_lon(latitude: float, longitude: float):
    global SUN
    if SUN is None:
        SUN = suntime.Sun(latitude, longitude)


def get_sun():
    global SUN
    return SUN


@dataclass
class Job:
    runtime: time
    job: Callable | None = None
    name: str = 'NO NAME'
    id_: int | None = None
    args: tuple[Any] = ()
    kwargs: dict[str, Any] | None = None

    def _parse_time(self, time_str: str|time):
        if isinstance(time_str, time):
            return time_str

        elif 'sunset' in time_str:
            return SUN.get_local_sunset_time().time()

        elif 'sunrise' in time_str:
            return SUN.get_local_sunrise_time().time()

        else:
            t = time(*map(int, time_str.split(':')))
            self.runtime = t
            return t

    def __getattribute__(self, name: str):
        val = object.__getattribute__(self, name)
        if name == 'runtime':
            return self._parse_time(val)
        else:
            return val


class Scheduler:
    _jobs: list[Job]  # The jobs we run
    _last_proc_id: int  # An incrementor for setting proc ID
    dates_to_skip: set[date]  # Any dates that should be skipped

    def __init__(self):
        self._jobs = []
        self._last_proc_id = -1
        self.dates_to_skip = set()

    def _get_next_job(self, m_time: time | None = None) -> Job | None:
        """Get the next job to be run (default from now)"""
        if not self._jobs:
            return

        if m_time is None:
            m_time = datetime.now().time()

        ind = self.find_schedule_index(m_time)
        if ind < len(self._jobs) and self._jobs[ind].runtime == m_time:
            ind += 1

        # This is after the last job for the day -so wait until the first tomorrow.
        if ind >= len(self._jobs):
            ind = 0

        return self._jobs[ind]

    def _get_sleep_time_to(self,
                           next_job: Job,
                           m_time: time|None = None,
                           m_date: date|None = None):
        """How long should we sleep to get from m_time -> job.runtime

        Args:
            next_job: The next job to run
            m_time: The current time (optional). Mostly useful for testing.
            m_date: The current date (optional). Mostly useful for testing.
        """
        if m_time is None:
            m_time = datetime.now().time()

        run_date = datetime.now().date()
        if m_date is not None:
            run_date = m_date

        current_datetime = datetime.combine(run_date, m_time)
        if next_job.runtime < m_time:
            run_date += timedelta(days=1)

        # Skip any required dates
        while run_date in self.dates_to_skip:
            run_date += timedelta(days=1)

        run_datetime = datetime.combine(run_date, next_job.runtime)

        assert run_datetime > current_datetime, "Something has gone wrong with the schedule. The next run datetime should always be more than that current datetime"
        return (run_datetime - current_datetime).total_seconds()

    def run(self):
        """Run the schedule"""
        while True:
            next_job = self._get_next_job()
            if not next_job:
                log.info(f"No next job, sleeping for 15 seconds and looking again")
                # Sleep for 15 seconds and try again -maybe we've added to the schedule
                sleep(15)
                continue

            sleep_time = self._get_sleep_time_to(next_job)
            runtime = datetime.now() + timedelta(seconds=sleep_time)
            log.info(f"Sleeping for {sleep_time}s (next run at {runtime:%Y/%m/%d %H:%M:%S})")
            sleep(sleep_time)

            kwargs = next_job.kwargs or {}
            log.info(f"Running job {next_job} with args: {next_job.args} and kwargs: {kwargs}")
            next_job.job(*next_job.args, **kwargs)

            sleep(1)  # make sure we don't get the same job twice

    def _tot_sec(self, m_time):
        return m_time.hour * 3600 + m_time.minute*60  + m_time.second + m_time.microsecond

    def find_schedule_index(self, m_time):
        """Find the schedule index (to keep list sorted) using binary search"""
        if len(self._jobs) == 0:
            return 0

        if len(self._jobs) == 1:
            if self._jobs[0].runtime > m_time:
                return 0
            return 1

        st, ed = 0, len(self._jobs)-1
        while (st != ed):
            mid = (st + ed) // 2
            mid_time = self._jobs[mid].runtime

            if m_time < mid_time:
                ed = mid
            elif m_time > mid_time:
                st = mid
            else:
                return mid

            if ed - st == 1:
                if m_time < self._jobs[st].runtime:
                    return st
                if m_time < self._jobs[ed].runtime:
                    return ed
                if m_time > self._jobs[ed].runtime:
                    return ed + 1

        return st

    def add_skip_dates(self, skip_dates: set[str]):
        """Add dates to skip to scheduler"""
        for m_date in skip_dates:
            self.dates_to_skip.add(datetime.strptime(m_date, '%Y-%m-%d').date())

    def refresh_order(self):
        """If sunrise and sunset are used then we should refresh these times at the start of the day"""
        self._jobs.sort(key=lambda i: i.runtime)

    def add_job(self, job: Job):
        """Add a job to the schedule"""
        ind = self.find_schedule_index(job.runtime)
        proc_id = self._last_proc_id + 1
        job.id_ = proc_id
        self._jobs.insert(ind, job)
