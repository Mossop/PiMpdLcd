from adafruit.Adafruit_CharLCDPlate import Adafruit_CharLCDPlate

class OutputDevice(object):
    def __init__(self):
        self.lcd = None

    def on(self):
        self.lcd = Adafruit_CharLCDPlate()
        self.lcd.begin(16, 2)
        self.lcd.clear()
        self.lcd.backlight(self.lcd.RED)

    def off(self):
        self.lcd.stop()
        self.lcd = None

    def display(self, line1 = None, line2 = None):
        if not self.lcd:
            self.on()

        if line1 is not None:
            while len(line1) < 16:
                line1 = line1 + " "
            self.lcd.setCursor(0, 0)
            self.lcd.message(line1)
        if line2 is not None:
            while len(line2) < 16:
                line2 = line2 + " "
            self.lcd.setCursor(0, 1)
            self.lcd.message(line2)
