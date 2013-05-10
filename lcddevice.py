from adafruit.Adafruit_CharLCDPlate import Adafruit_CharLCDPlate

def center(str):
    while len(str) < 15:
        str = " " + str + " "
    return str

class Output(object):
    def __init__(self):
        self.lcd = Adafruit_CharLCDPlate()
        self.lcd.clear()
        self.lcd.backlight(self.lcd.RED)

    def display(self, line1 = "", line2 = ""):
        self.lcd.clear()
        self.lcd.message(center(line1[:16]) + "\n" + center(line2[:16]))
