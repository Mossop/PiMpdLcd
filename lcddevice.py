from adafruit.Adafruit_CharLCDPlate import Adafruit_CharLCDPlate

from shared import *

BUTTONS = [
    SELECT,
    UP,
    DOWN,
    LEFT,
    RIGHT
]

class Device(threading.Thread):
    def __init__(self):
        self.lock = threading.Lock()
        threading.Thread.__init__(self)
        self.daemon = True

        self.lcd = None
        self._color = RED
        self._buttons = []

        self.start()

    def run(self):
        lastbuttons = 0
        while True:
            buttons = self.lcd.buttons()

            for button in BUTTONS:
                button = 1 << button
                if (lastbuttons & button) and not (buttons & button):
                    self.lock.acquire()
                    self._buttons.append(button)
                    self.lock.release()

            lastbuttons = buttons

    def get_buttons(self):
        self.lock.acquire()
        buttons = self._buttons
        self._buttons = []
        self.lock.release()
        return buttons

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
