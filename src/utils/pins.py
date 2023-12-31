from raspi_gpio import GPIO
from time import sleep
import logging

logger = logging.getLogger(__name__)


class PinOut:
   num: int    = None
   _name: str  = None
   _state: int = None
   _schedules: list["Job"] = None
   _init_done_: bool = False

   def __init__(self, pin_num: int, name: str = None):
      self.num = pin_num
      self._name = pin_num if name is None else name

      if self._init_done_ is False:
          GPIO.setmode(GPIO.BOARD)
          self._init_done_ = True

      GPIO.setup(pin_num, GPIO.OUT)
      self.off()
      self._schedules = []

   def add_schedule(self, daily_schedule: "Job"):
      self._schedules.append(daily_schedule)
      logger.info("Adding schedule {t} to pin {n}".format(t=daily_schedule._time_to_run.strftime('%H:%m'),
                                                          n=self._name))

   def run_schedule(self):
      for schedule in self._schedules:
         schedule.run()

   def on(self):
      logger.info("Turning on PIN {name}".format(name=self._name))
      if self._state == GPIO.HIGH:
         return

      GPIO.output(self.num, GPIO.HIGH)
      self._state = GPIO.HIGH

   def off(self):
      logger.info("Turning off PIN {name}".format(name=self._name))
      if self._state == GPIO.LOW:
         return

      GPIO.output(self.num, GPIO.LOW)
      self._state = GPIO.LOW

   def set_for_time(self, sleep_time=0.5, set_to=GPIO.HIGH):
      """turn on a pin for a set amount of time and then turn it off"""
      if set_to == GPIO.HIGH:
         self.on()
         sleep(sleep_time)
         self.off()
      else:
         self.off()
         sleep(sleep_time)
         self.on()
