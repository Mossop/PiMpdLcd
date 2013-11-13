import threading

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
        self._lock = threading.Lock()

    def get_buttons(self):
        pressed = []
        self._lock.acquire()
        try:
            if not self.lcd:
                return []
            buttons = self.lcd.buttons()
        finally:
            self._lock.release()
        for button in BUTTONS:
            power = 1 << button
            if (buttons & power) == 0:
                if (self._lastbuttons & power) != 0:
                    pressed.append(button)

        self._lastbuttons = buttons
        return pressed

    def color(self, color):
        if self.lcd:
            self._lock.acquire()
            self.lcd.backlight(color)
            self._lock.release()
        self._color = color

    def on(self):
        self._lock.acquire()
        self.lcd = Adafruit_CharLCDPlate()
        self.lcd.begin(WIDTH, 2)
        self.lcd.clear()
        self.lcd.backlight(self._color)
        self._lock.release()

    def off(self):
        if self.lcd:
            self._lock.acquire()
            self.lcd.clear()
            self.lcd.stop()
            self.lcd = None
            self._lock.release()

    def display(self, line1 = None, line2 = None):
        if not self.lcd:
            self.on()

        self._lock.acquire()
        if line1 is not None:
            line1 = str(line1).ljust(WIDTH)
            self.lcd.setCursor(0, 0)
            self.lcd.message(line1)
        if line2 is not None:
            line2 = str(line2).ljust(WIDTH)
            self.lcd.setCursor(0, 1)
            self.lcd.message(line2)
        self._lock.release()
