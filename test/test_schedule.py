from datetime import date
import suntime
from datetime import time, datetime
import pytest

from utils.schedule import Scheduler, Job, set_sun_lat_lon

SUN = suntime.Sun(50, 20)
set_sun_lat_lon(50, 20)


@pytest.mark.parametrize("time_str,expectation",
        [("07", time(hour=7)),
         ("07:30", time(hour=7, minute=30)),
         ("07:30:01", time(hour=7, minute=30, second=1)),
         ("sunset", SUN.get_local_sunset_time().time()),
         ("sunrise", SUN.get_local_sunrise_time().time()),
])
def test_job_parse_time(time_str, expectation):
    job = Job(name='bob', runtime=time_str, job=lambda i: i)
    assert job.runtime == expectation


def test_find_schedule_index():
    scheduler = Scheduler()
    ind = scheduler.find_schedule_index(time(7, 0))
    assert ind == 0

    scheduler._jobs = [Job(runtime="07:00", job=lambda i: i, name='bob')]
    ind = scheduler.find_schedule_index(time(8,0))
    assert ind == 1
    ind = scheduler.find_schedule_index(time(7,0))
    assert ind == 1
    ind = scheduler.find_schedule_index(time(6,0))
    assert ind == 0

    scheduler._jobs = [Job(runtime="07:00", job=lambda i: i, name='bob1'),
                            Job(runtime="7:30", job=lambda i: i, name='bob2'),
                            Job(runtime="07:30", job=lambda i: i, name='bob3'),
                            Job(runtime="08:00", job=lambda i: i, name='bob4'),
    ]
    ind = scheduler.find_schedule_index(time(6,0))
    assert ind == 0
    ind = scheduler.find_schedule_index(time(7,10))
    assert ind == 1
    ind = scheduler.find_schedule_index(time(7,30))
    assert ind == 1
    ind = scheduler.find_schedule_index(time(7,31))
    assert ind == 3
    ind = scheduler.find_schedule_index(time(8,31))
    assert ind == 4


def test_add_job():
    func = lambda i: i
    scheduler = Scheduler()
    scheduler.add_job(Job(runtime="7", job=func, name='bob'))
    assert len(scheduler._jobs) == 1
    assert scheduler._jobs[0].name == 'bob'

    scheduler.add_job(Job(runtime="8", job=func, name='bob1'))
    assert len(scheduler._jobs) == 2
    assert scheduler._jobs[0].name == 'bob'
    assert scheduler._jobs[1].name == 'bob1'

    scheduler.add_job(Job(runtime="7:30", job=func, name='bob2'))
    assert len(scheduler._jobs) == 3
    assert scheduler._jobs[0].name == 'bob'
    assert scheduler._jobs[1].name == 'bob2'
    assert scheduler._jobs[2].name == 'bob1'

    scheduler.add_job(Job(runtime="7:30", job=func, name='bob3'))
    scheduler.add_job(Job(runtime="06:30", job=func, name='bob4'))
    scheduler.add_job(Job(runtime="8:30", job=func, name='bob5'))
    for i, name in enumerate(('bob4', 'bob', 'bob3', 'bob2', 'bob1', 'bob5')):
        assert scheduler._jobs[i].name == name


def test_get_job():
    func = lambda i: i
    scheduler = Scheduler()
    job = scheduler._get_next_job()
    assert job is None, "Empty jobs don't work"

    scheduler.add_job(Job(runtime="7", job=func, name='bob1'))
    for test_time in (time(6, 30), time(7, 30)):
        job = scheduler._get_next_job(test_time)
        assert job.name == 'bob1'

    scheduler.add_job(Job(runtime="6", job=func, name='bob0'))
    scheduler.add_job(Job(runtime="7:30", job=func, name='bob2'))
    scheduler.add_job(Job(runtime="7:40", job=func, name='bob3'))

    for test_time, name in ((time(5, 30), 'bob0'),
                            (time(6, 30), 'bob1'),
                            (time(7, 20), 'bob2'),
                            (time(7, 30), 'bob3'),
                            (time(7, 31), 'bob3'),
                            (time(7, 51), 'bob0'),):
        job = scheduler._get_next_job(test_time)
        assert job.name == name, "Incorrect job retrieved"


@pytest.mark.parametrize("test_time, num_seconds", [
        ('17:30', 30*60),
        ('18:00:01', 60*60 + 1),
        ('16:30', 24*3600 - 30*60),
        ('09:17:04', 9*3600 + 17*60 + 4 + 7*3600),
])
def test_get_sleep_time_to(test_time, num_seconds):
    func = lambda i: i
    scheduler = Scheduler()

    sleep_time = scheduler._get_sleep_time_to(
                    Job(runtime=test_time,
                        name='bob',
                        job=func),
                    m_time=time(17, 0)
    )
    assert sleep_time == num_seconds


def test_skip_dates():
    func = lambda i: i
    scheduler = Scheduler()

    scheduler.add_skip_dates({'2023-01-01'})

    test_time = '07:00'
    sleep_time = scheduler._get_sleep_time_to(
            Job(runtime=test_time,
                name='bob',
                job=func),
            m_time=time(17,0),
            m_date=date(2022,12,31),
    )

    assert sleep_time == ((14 + 24) * 3600)


def test_refresh_schedule():
    job = Job(runtime='7')
    job2 = Job(runtime='8')
    job3 = Job(runtime='9')

    scheduler = Scheduler()
    scheduler._jobs = [job2, job3, job]
    assert scheduler._jobs[0].runtime < scheduler._jobs[1].runtime
    assert scheduler._jobs[1].runtime > scheduler._jobs[2].runtime

    scheduler.refresh_order()

    assert scheduler._jobs[0].runtime < scheduler._jobs[1].runtime
    assert scheduler._jobs[1].runtime < scheduler._jobs[2].runtime
