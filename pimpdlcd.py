from select import select
from mpd import MPDClient

try:
    from lcddevice import OutputDevice
except:
    from consoledevice import OutputDevice

HOST = 'officepi'
PORT = '6600'
PASSWORD = False

output = OutputDevice()
client = MPDClient()

def update_status(client):
    status = client.status()
    if status["state"] == "stop":
        output.display("STOPPED")
        return
    song = client.currentsong()
    if status["state"] == "pause":
        output.display(song["title"], "PAUSED")
    else:
        output.display(song["title"], song["artist"])

def main():
    global client

    client = MPDClient()
    client.connect(host = HOST, port = PORT)
    # Auth if password is set non False
    if PASSWORD:
        client.password(PASSWORD)

    while True:
        update_status(client)
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
            pass
