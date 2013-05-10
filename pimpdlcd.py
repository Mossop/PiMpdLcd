import pprint

from select import select
from mpd import MPDClient

try:
    from lcddevice import Output
except:
    from consoledevice import Output

HOST = 'officepi'
PORT = '6600'
PASSWORD = False

output = Output()

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
    ## MPD object instance
    client = MPDClient()
    client.connect(host = HOST, port = PORT)

    try:
        # Auth if password is set non False
        if PASSWORD:
            client.password(PASSWORD)

        while True:
            update_status(client)
            client.send_idle()
            select([client], [] ,[])
            client.fetch_idle()
    finally:
        client.disconnect()

# Script starts here
if __name__ == "__main__":
    main()
