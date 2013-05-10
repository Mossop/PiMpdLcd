from select import select
from mpd import MPDClient

try:
    from lcddevice import OutputDevice
except:
    from consoledevice import OutputDevice

HOST = 'officepi'
PORT = '6600'
PASSWORD = False

def center(str):
    while len(str) < 15:
        str = " " + str + " "
    if len(str) < 16:
        str = str + " "
    return str

class Display(OutputDevice):
    def __init__(self):
        OutputDevice.__init__(self)

        self._status = "stop"
        self._song = {}

    def off(self):
        self._status = "stop"
        OutputDevice.off(self)

    def _update(self):
        self._line1 = center(self._song["title"])
        if self._status == "pause":
            self._line2 = center("PAUSED")
        else:
            self._line2 = center(self._song["artist"])
        self._line1pos = 0
        self._line2pos = 0
        self.display(self._line1, self._line2)

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
