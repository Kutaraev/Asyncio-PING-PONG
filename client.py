import asyncio
import logging
import os
import websockets

from os.path import join, dirname
from dotenv import load_dotenv

# loading .env file
dotenv_path = join(dirname(__file__), 'client.env')
load_dotenv(dotenv_path)

# constants and global variables
FREQUENCY = int(os.getenv("CLIENT_COMMAND_FREQUENCY"))
HOST = os.getenv("HOST")
PORT = os.getenv("PORT")

# Dict of client requests
REQUESTS = {"PING": "PING\r",
            "FOO": "FOO\r",
            "REQUEST": "REQUEST\r"
            }

# Create logging
mylogs = logging.getLogger(__name__)
mylogs.setLevel(logging.INFO)

# logging to a file
file = logging.FileHandler("client.log")
fileformat = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
file.setLevel(logging.INFO)
file.setFormatter(fileformat)

# logging to console
stream = logging.StreamHandler()
streamformat = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
stream.setLevel(logging.DEBUG)
stream.setFormatter(streamformat)

# adding logging handlers
mylogs.addHandler(file)
mylogs.addHandler(stream)


def encode(message):
    """Function that encodes message in "str" to message in "UTF-8" format.

    Args:
        param1: message in "str" format.

    Returns:
        Encoded mesage to "UTF-8" format.

    """

    return message.encode('utf-8')


def decode(message):
    """Function that decodes message in "UTF-8" to message in "str" format.

    Args:
        param1: message in "UTF-8" format.

    Returns:
        Decoded message to "str" format.

    """

    return message.decode('utf-8')


async def send_message():
    message = REQUESTS['PING']
    await asyncio.sleep(FREQUENCY)
    return message


async def listen_server():
    """Function connects to server, sends and recieves messages.
    Requests takes from "REQUESTS" dictionary and sends with frequency in
    "FREQUENCY" variable. Requests and responces goes unto log "client.log"

    """
    server_url = f"ws://{HOST}:{PORT}"

    async with websockets.connect(server_url) as websocket:
        while True:
            # Sending messages
            push_message = await send_message()
            await websocket.send(encode(push_message))
            mylogs.info(f"Client send to server: {push_message}")
            # Recieving messages
            message_from_server = await websocket.recv()
            mylogs.info(f" Server send to client: {decode(message_from_server)}")


if __name__ == "__main__":
    try:
        # Event loop managing
        asyncio.get_event_loop().run_until_complete(listen_server())

    except websockets.exceptions.ConnectionClosedError:
        mylogs.error("Connection with server lost")

    except KeyboardInterrupt:
        mylogs.info("Connection is closed")
