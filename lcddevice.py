from adafruit.Adafruit_CharLCDPlate import Adafruit_CharLCDPlate

from shared import *

BUTTONS = [
    SELECT,
    UP,
    DOWN,
    LEFT,
    RIGHT
]

class Device(object):
    def __init__(self):
        self.lcd = None
        self._color = RED
        self._lastbuttons = 0

    def get_buttons(self):
        if not self.lcd:
            return []

        pressed = []
        buttons = self.lcd.buttons()
        for button in BUTTONS:
            button = 1 << button
            if (self._lastbuttons & button) and not (buttons & button):
                pressed.append(button)

        self._lastbuttons = buttons
        return pressed

    def color(self, color):
        if self.lcd:
            self.lcd.backlight(color)
        self._color = color

    def on(self):
        self.lock.acquire()
        self.lcd = Adafruit_CharLCDPlate()
        self.lcd.begin(WIDTH, 2)
        self.lcd.clear()
        self.lcd.backlight(self._color)
        self.lock.release()

    def off(self):
        self.lock.acquire()
        if self.lcd:
            self.lcd.clear()
            self.lcd.stop()
            self.lcd = None
        self.lock.release()

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
