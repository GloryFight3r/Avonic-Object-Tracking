from engineio.payload import Payload
from maat_web_app import create_app

Payload.max_decode_packets = 50
app = create_app()

if __name__ == "__main__":
    app.run()
