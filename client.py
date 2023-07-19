import asyncio
import websockets

from websockets.client import connect
from websockets.exceptions import ConnectionClosedError

async def ws_client():
    uri = input("Enter the URI of the server: ")
    async with connect(uri) as websocket:
        print("Connected to server.")
        while True:
            try:
                send_data = input(">>> ")
                await websocket.send(send_data)
                recv_data = await websocket.recv()
                print(f"<<< {recv_data}")
            except ConnectionClosedError:
                print("Connection closed.")
                return


if __name__ == "__main__":
    asyncio.run(ws_client())
