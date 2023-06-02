from web_app import create_app
from engineio.payload import Payload

Payload.max_decode_packets = 50
app = create_app()

if __name__ == "__main__":
    app.run()
