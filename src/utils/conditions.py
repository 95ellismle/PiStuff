import asyncio
import python_weather

from typing import Callable


def get_condition_func(conditions: dict | None) -> Callable:
    """Return a function that will determine whether to do an action (return True or False)
    based on some logic"""
    def condition_func(conditions):
        for condition in conditions:
            if condition['type'] == 'weather':
                if weather_condition(condition) is False:
                    return False
        return True
    return lambda : condition_func(conditions)


async def get_weather():
    async with python_weather.Client(unit=python_weather.METRIC) as client:
        # fetch a weather forecast from a city
        weather = await client.get('London')
        return weather


def weather_condition(condition):
    """Check the weather forecast,
    if it fulfills the conditions given in the yaml then return True else False"""
    weather = asyncio.run(get_weather())
    for key, value in condition.items():
        if key == 'type':
            continue
        elif key == 'kind':
            requested_kind = getattr(python_weather.Kind, value.upper(), None)
            if requested_kind != weather.kind:
                return False

        elif key == 'temperature':
            operation = value['op']
            comparator = value['val']
            temp = weather.temperature
            if eval(f"{temp} {operation} {comparator}") is False:
                return False
    return True
