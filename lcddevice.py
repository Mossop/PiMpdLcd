from adafruit.Adafruit_CharLCDPlate import Adafruit_CharLCDPlate

from shared import *

class OutputDevice(object):
    def __init__(self):
        self.lcd = None
        self._color = RED

    def color(self, color):
        if self.lcd:
            self.lcd.backlight(color)
        self._color = color

    def on(self):
        self.lcd = Adafruit_CharLCDPlate()
        self.lcd.begin(WIDTH, 2)
        self.lcd.clear()
        self.lcd.backlight(self._color)

    def off(self):
        if self.lcd:
            self.lcd.clear()
            self.lcd.stop()
            self.lcd = None

    def display(self, line1 = None, line2 = None):
        if not self.lcd:
            self.on()

        if line1 is not None:
            line1 = str(line1).ljust(WIDTH)
            self.lcd.setCursor(0, 0)
            self.lcd.message(line1)
        if line2 is not None:
            line2 = str(line2).ljust(WIDTH)
            self.lcd.setCursor(0, 1)
            self.lcd.message(line2)
