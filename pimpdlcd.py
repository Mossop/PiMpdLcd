from select import select
from mpd import MPDClient
from threading import Timer

from shared import *

try:
    from lcddevice import Device
except:
    from consoledevice import Device

HOST = 'officepi'
PORT = '6600'
PASSWORD = False

SCROLL_TIME = 1
SCROLL_SHORT = False

POLL_STATUS_TIME = 1
POLL_BUTTON_TIME = 0.1

class Line(object):
    def __init__(self, str):
        self._str = str
        self._pos = 0
        self._dir = 0
        self._override = None
        self._overridden = False

    def override(self, str):
        self._override = str
        self._overridden = False

    def update(self):
        if self._override:
            self._overridden = not self._overridden
            if self._overridden:
                return

        self._pos = self._pos + self._dir

        if len(self._str) == WIDTH:
            self._dir = 0
        elif self._dir == 0:
            self._dir = 1
        elif len(self._str) < WIDTH:
            if self._dir > 0 and (len(self._str) + self._pos) == WIDTH:
                self._dir = -1
            elif self._dir < 0 and self._pos == 0:
                self._dir = 1
        else:
            if self._dir > 0 and len(self._str) - self._pos == WIDTH:
                self._dir = -1
            elif self._dir < 0 and self._pos == 0:
                self._dir = 1

    @property
    def raw(self):
        return self._str

    def __str__(self):
        if self._overridden:
            return self._override.center(WIDTH)

        if len(self._str) == WIDTH:
            return self._str

        if len(self._str) < WIDTH:
            if not SCROLL_SHORT:
                return self._str.center(WIDTH)
            line = "".ljust(self._pos) + self._str
            return line.ljust(WIDTH)

        return self._str[self._pos:self._pos + WIDTH]

class Display(Device):
    def __init__(self):
        self._status = "stop"
        self._song = {}
        self._timer = None
        self._line1 = Line("")
        self._line2 = Line("")

        Device.__init__(self)

    def on(self):
        Device.on(self)
        if not self._timer:
            self._timer = Timer(SCROLL_TIME, self._update_display)
            self._timer.start()

    def off(self):
        self._status = "stop"
        if self._timer:
            self._timer.cancel()
            self._timer = None
        Device.off(self)

    def _update_display(self):
        self._timer = None
        self._line1.update()
        self._line2.update()

        self._timer = Timer(SCROLL_TIME, self._update_display)
        self._timer.start()

        self.display(self._line1, self._line2)

    def _update(self, forceupdate = False):
        line1 = self._song["title"]
        line2 = self._song["artist"]

        if not forceupdate and self._line1.raw == line1 and self._line2.raw == line2:
            return

        if line1 != self._line1.raw:
            self._line1 = Line(line1)

        if line2 != self._line2.raw:
            self._line2 = Line(line2)

        if self._timer:
            self._timer.cancel()
        self._update_display()

    def set_status(self, value):
        if value == self._status:
            return

        if value == "stop":
            self.off()
            return

        if self._status == "stop":
            self._update(True)

        if value == "pause":
            self._line2.override("PAUSED")
        else:
            self._line2.override(None)

        self._status = value

    def set_song(self, value):
        if value == self._song:
            return

        self._song = value
        if self._status != "stop":
            self._update()

output = Display()

class Monitor(object):
    def __init__(self):
        self.color = RED
        output.color(self.color)

        self.client = MPDClient()
        self.client.connect(host = HOST, port = PORT)
        if PASSWORD:
            self.client.password(PASSWORD)

        self.poll_buttons()
        self.update_status()

    def poll_buttons(self):
        try:
            buttons = output.get_buttons()
            for button in buttons:
                if button == SELECT:
                    self.color = self.color + 1
                    if self.color > WHITE:
                        self.color = RED
                    output.color(self.color)
                elif button == UP:
                    status = self.client.status()["state"]
                    if status == "play":
                        self.client.pause()
                    else:
                        self.client.play()
                elif button == DOWN:
                    self.client.stop()
                elif button == LEFT:
                    self.client.previous()
                elif button == RIGHT:
                    self.client.next()
        except:
            pass

        self.polltimer = Timer(POLL_BUTTON_TIME, self.poll_buttons)
        self.polltimer.start()

    def update_status(self):
        try:
            status = self.client.status()
            if status["state"] != "stop":
                output.set_song(self.client.currentsong())
            output.set_status(status["state"])

            self.statustimer = Timer(POLL_STATUS_TIME, self.update_status)
            self.statustimer.start()
        except:
            self.polltimer.cancel()
            init_monitor()

def init_monitor():
    try:
        Monitor()
    except:
        init_monitor()

# Script starts here
if __name__ == "__main__":
    init_monitor()
