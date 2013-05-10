from select import select
from mpd import MPDClient
from threading import Timer

try:
    from lcddevice import OutputDevice
except:
    from consoledevice import OutputDevice

HOST = 'officepi'
PORT = '6600'
PASSWORD = False

WIDTH = 16
SCROLL_TIME = 1
SCROLL_SHORT = False

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

class Display(OutputDevice):
    def __init__(self):
        self._status = "stop"
        self._song = {}
        self._timer = None
        self._line1 = Line("")
        self._line2 = Line("")

        OutputDevice.__init__(self)

    def on(self):
        OutputDevice.on(self)
        if not self._timer:
            self._timer = Timer(SCROLL_TIME, self._update_display)
            self._timer.start()

    def off(self):
        self._status = "stop"
        if self._timer:
            self._timer.cancel()
            self._timer = None
        OutputDevice.off(self)

    def _update_display(self):
        self._timer = None
        self._line1.update()
        self._line2.update()

        self._timer = Timer(SCROLL_TIME, self._update_display)
        self._timer.start()

        self.display(str(self._line1), str(self._line2))

    def _update(self):
        line1 = self._song["title"]
        line2 = self._song["artist"]

        if line1 != self._line1.raw:
            self._line1 = Line(line1)

        if line2 != self._line2.raw:
            self._line2 = Line(line2)

        if self._status == "pause":
            self._line2.override("PAUSED")
        else:
            self._line2.override(None)

        if self._timer:
            self._timer.cancel()
        self._update_display()

    def set_status(self, value):
        if value == "stop":
            self.off()
            return

        self._status = value
        self._update()

    def set_song(self, value):
        self._song = value
        self._update()

output = Display()
client = MPDClient()

def main():
    global client

    client = MPDClient()
    client.connect(host = HOST, port = PORT)
    # Auth if password is set non False
    if PASSWORD:
        client.password(PASSWORD)

    while True:
        status = client.status()
        if status["state"] != "stop":
            output.set_song(client.currentsong())
        output.set_status(status["state"])

        client.send_idle()
        select([client], [] ,[])
        client.fetch_idle()

# Script starts here
if __name__ == "__main__":
    while True:
        try:
            main()
        except:
            output.off()
