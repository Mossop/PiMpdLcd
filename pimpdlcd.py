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

def center(str):
    while len(str) < (WIDTH - 1):
        str = " " + str + " "
    if len(str) < WIDTH:
        str = str + " "
    return str

def build_line(str, pos):
    if len(str) == WIDTH:
        return str

    if len(str) < WIDTH:
        line = "".ljust(pos) + str
        return line.ljust(WIDTH)

    return str[pos:pos + WIDTH]

def next_dir(str, pos, dir):
    if len(str) == WIDTH:
        return 0

    if dir == 0:
        return 1

    if len(str) < WIDTH:
        if dir > 0 and (len(str) + pos) == WIDTH:
            dir = -1
        elif dir < 0 and pos == 0:
            dir = 1
    else:
        if dir > 0 and len(str) - pos == WIDTH:
            dir = -1
        elif dir < 0 and pos == 0:
            dir = 1

    return dir

class Display(OutputDevice):
    def __init__(self):
        self._status = "stop"
        self._song = {}
        self._timer = None
        self._line1 = ""
        self._line2 = ""

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

        if len(self._line1) <= WIDTH:
            line1 = center(self._line1)
        else:
            self._line1pos = self._line1pos + self._line1dir
            self._line1dir = next_dir(self._line1, self._line1pos, self._line1dir)
            line1 = build_line(self._line1, self._line1pos)

        if len(self._line2) <= WIDTH:
            line2 = center(self._line2)
        else:
            self._line2pos = self._line2pos + self._line2dir
            self._line2dir = next_dir(self._line2, self._line2pos, self._line2dir)
            line2 = build_line(self._line2, self._line2pos)

        self._timer = Timer(SCROLL_TIME, self._update_display)
        self._timer.start()

        self.display(line1, line2)

    def _update(self):
        line1 = self._song["title"]
        if self._status == "pause":
            line2 = "PAUSED"
        else:
            line2 = self._song["artist"]

        if line1 != self._line1:
            self._line1 = line1
            self._line1pos = 0
            self._line1dir = 0

        if line2 != self._line2:
            self._line2 = line2
            self._line2pos = 0
            self._line2dir = 0

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
