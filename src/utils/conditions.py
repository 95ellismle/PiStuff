import asyncio
import logging
import python_weather

from typing import Callable

log = logging.getLogger(__name__)


def get_condition_func(conditions: dict | None) -> Callable | None:
    """Return a function that will determine whether to do an action (return True or False)
    based on some logic"""
    if conditions is None:
        return None

    def condition_func(conditions):
        for condition in conditions:
            if condition['type'] == 'weather':
                if weather_condition(condition) is False:
                    log.info(f"Weather condition is False")
                    return False

        log.info(f"All conditions are True. Conditions: {conditions}")
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
    log.info("Checking weather condition")
    for key, value in condition.items():
        if key == 'type':
            continue
        elif key == 'kind':
            log.info("Evaluating weather kind condition")
            requested_kind = getattr(python_weather.Kind, value.upper(), None)
            log.info(f"Requested kind of weather: {requested_kind}. Kind of weather: {weather.kind}")
            if requested_kind != weather.kind:
                log.info(f"Condition is False as requested_kind != weather.kind ({requested_kind} != {weather.kind})")
                return False
            log.info(f"Condition is True as requested_kind == weather.kind ({requested_kind} == {weather.kind})")

        elif key == 'temperature':
            log.info("Evaluating weather temperature condition")
            operation = value['operation']
            comparator = value['value']
            temp = weather.temperature
            log.info(f"Weather temperature = {temp}, operation: {value['top']}, threshold: {comparator}")
            if eval(f"{temp} {operation} {comparator}") is False:
                log.info(f"Condition is False  as temperature not {operation} threshold ({temp} !{operation} {comparator})")
                return False
            log.info(f"Condition is True  as temperature {operation} threshold ({temp} {operation} {comparator})")
    return True
