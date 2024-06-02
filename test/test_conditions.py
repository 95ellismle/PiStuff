import asyncio
from utils.conditions import get_condition_func, get_weather


def test_weather_condition_func():
    weather = asyncio.run(get_weather())
    conditions = [{'type': 'weather',
                   'kind': weather.description.lower(),
                   'temperature':
                     {'op': '>=',
                      'val': weather.temperature}}]
    condition_func = get_condition_func(conditions)
    cond = condition_func()
    assert cond == True, "Cond should be true..."
