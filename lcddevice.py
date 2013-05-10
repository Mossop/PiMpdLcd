from adafruit.Adafruit_CharLCDPlate import Adafruit_CharLCDPlate

class Output(object):
    def __init__(self):
        self.lcd = Adafruit_CharLCDPlate()
        self.lcd.clear()
        self.lcd.backlight(self.lcd.RED)

    def display(self, line1 = "", line2 = ""):
        self.lcd.message(line1[:16] + "\n" + line2[:16])
