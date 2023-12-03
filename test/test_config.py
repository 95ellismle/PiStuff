import tempfile
import pytest

from utils.schedule import Scheduler, set_sun_lat_lon, get_sun
from config.config import get_config



@pytest.fixture()
def scheduler():
    return Scheduler()


@pytest.fixture()
def sun():
    set_sun_lat_lon(50, 0)
    sun = get_sun()
    return sun


def test_get_config_sunset_sunrise(scheduler, sun):
    config_str = b"""
settings:
    latitude: 50
    longitude: 0

schedule:
    - name: bob
      runtime: sunset
      job: null

    - name: bob1
      runtime: sunrise
      job: null
    """
    with tempfile.NamedTemporaryFile() as fp:
        fp.write(config_str)
        fp.flush()

        config = get_config(fp.name, scheduler)
        assert 'refresh' in scheduler._jobs[0].name.lower()
        assert scheduler._jobs[1].runtime == sun.get_local_sunrise_time().time()
        assert scheduler._jobs[2].runtime == sun.get_local_sunset_time().time()
