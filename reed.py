# Python 3.9.10 embedded in Ren'Py

try:
    renpy = __import__("renpy").exports
except ImportError:
    renpy = None

import ast
import asyncio

from typing import Final, TypedDict, Optional
from websockets.exceptions import ConnectionClosedError
from websockets.server import serve, WebSocketServerProtocol

class ExecutedResult(TypedDict):
    result: bool
    exception: Optional[Exception]

def notify(message: str):
    if renpy:
        renpy.notify(message)
    else:
        print(message)

def execute(command: str) -> ExecutedResult:
    tree = ast.parse(command)
    if renpy:
        try:
            renpy.invoke_in_main_thread(exec, compile(tree, filename="<string>", mode="exec"), globals(), locals())
            return {
                "result": True,
                "exception": None
            }
        except Exception as err:
            # Return None
            return {
                "result": False,
                "exception": err
            }
    else:
        try:
            exec(compile(tree, filename="<string>", mode="exec"), globals(), locals())
            return {
                "result": True,
                "exception": None
            }
        except Exception as err:
            # Return None
            return {
                "result": False,
                "exception": err
            }

async def callback_websocket(websocket: WebSocketServerProtocol):
    notify(f"[reed] New connection from {websocket.remote_address[0]}")
    try:
        async for message in websocket:
            print(f"<<< {message}")
            # execute
            try:
                result = execute(str(message))
                if result["result"]:
                    await websocket.send("OK")
                else:
                    await websocket.send(f"ERR>>> {result['exception']}")
            except Exception as e:
                print(f"Error: {e}")
                await websocket.send(f"ERR>>> {e}")
    except ConnectionClosedError:
        notify(f"[reed] Connection from {websocket.remote_address[0]} closed ({websocket.close_code})")

async def serve_websocket(port: int = 35124):
    async with serve(callback_websocket, "0.0.0.0", port):
        await asyncio.Future()

def run(port: int):
    if renpy:
        try:
            notify("[reed] Reed debugger is running.")
        except Exception:
            pass
        renpy.invoke_in_thread(asyncio.run, serve_websocket(port=port))
    else:
        asyncio.run(serve_websocket(port=port))
