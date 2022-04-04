import asyncio
import logging
import os
import time
import websockets

from os.path import join, dirname
from dotenv import load_dotenv


# loading .env file
dotenv_path = join(dirname(__file__), 'server.env')
load_dotenv(dotenv_path)

# constants and global variables
UPTIME_FREQUENCY = int(os.getenv("UPTIME_FREQUENCY"))
HOST = os.getenv("HOST")
PORT = os.getenv("PORT")
TIME = time.time()
USERS = set()
INCREMENT = []

# Dict of server responces
RESPONCES = {"PING\r": "PONG",
             "FOO\r": "BAR",
             "REQUEST\r": "RESPONCE"
             }

# Create logging
mylogs = logging.getLogger(__name__)
mylogs.setLevel(logging.INFO)

# logging to a file
file = logging.FileHandler("server.log")
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


async def broadcast():
    """Function that periodically send to all clients server status.
    The frequency of sending loads from UPTIME_FREQUENCY variable.

    """

    while True:
        for user in USERS:
            server_status_message = encode(
                f"STATUS UPTIME {round(time.time() - TIME)}"
                )
            await user.send(server_status_message)
        await asyncio.sleep(UPTIME_FREQUENCY)


async def increment():
    """Function that creates incrementing list of values.
    Values apends to variable "INCREMENT" every 5 seconds.

    """

    while True:
        INCREMENT.append(1)
        await asyncio.sleep(5)


async def ansver_to_client(websocket, path):
    """Function that add new clients in one pool.
    After that server listens messages from clients and
    sends them answers from "RESPONCES" dictionary.
    Requests and responces goes into log "server.log"

    """
    USERS.add(websocket)
    mylogs.info('New client added')
    try:
        async for msg in websocket:
            if decode(msg) in RESPONCES.keys():
                mylogs.info(f"Client send to server: {decode(msg)}")
                for user in USERS:
                    if user == websocket:
                        send_message = f"{RESPONCES[decode(msg)]} {len(INCREMENT)}"
                        await user.send(encode(send_message))
                        mylogs.info(f"Server send to client: {send_message}")
            else:
                mylogs.error(f"Client send unknown command {decode(msg)}")
                for user in USERS:
                    if user == websocket:
                        error_message = encode(
                            f"Server don't know command {decode(msg)}"
                            )
                        await user.send(error_message)

    except websockets.exceptions.ConnectionClosedError:
         mylogs.info("Conection with client lost")

    finally:
        USERS.remove(websocket)

if __name__ == "__main__":
    try:
        # Server starting
        mylogs.info(f"Stared server and listening port {PORT}")
        start_server = websockets.serve(ansver_to_client, HOST, PORT)

        # Event loop managing
        loop = asyncio.get_event_loop()
        loop.create_task(broadcast())
        loop.create_task(increment())
        loop.run_until_complete(start_server)
        loop.run_forever()

    except KeyboardInterrupt:
        mylogs.info("Server is shutting down")
