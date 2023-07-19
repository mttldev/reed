# Python 3.9.10 embedded in Ren'Py

try:
    renpy = __import__("renpy").exports
except ImportError:
    renpy = None

import asyncio
import enum

from typing import Final
from websockets.exceptions import ConnectionClosedError
from websockets.server import serve, WebSocketServerProtocol


ExecResult: Final[int] = 0
ExecEnv: Final[int] = 1
ExecMode: Final[int] = 2


class ExecuteEnvironment(enum.Enum):
    RENPY = 1
    PYTHON = 2

class ExecuteMode(enum.Enum):
    EVAL = 1
    EXEC = 2

def notify(message: str):
    if renpy:
        renpy.notify(message)
    else:
        print(message)

def execute(command: str):
    if renpy:
        # Execute in Ren'Py
        try:
            # Return the result of the expression.
            return [renpy.python.py_eval(command), ExecuteEnvironment.RENPY, ExecuteMode.EVAL]
        except SyntaxError:
            # Return None
            return [renpy.python.py_exec(command), ExecuteEnvironment.RENPY, ExecuteMode.EXEC]
    else:
        # Execute in Python
        try:
            # Return the result of the expression.
            return [eval(command), ExecuteEnvironment.PYTHON, ExecuteMode.EVAL]
        except SyntaxError:
            # Return None
            return [exec(command), ExecuteEnvironment.PYTHON, ExecuteMode.EXEC]

async def callback_websocket(websocket: WebSocketServerProtocol):
    notify(f"reed: New connection from {websocket.remote_address[0]}")
    try:
        async for message in websocket:
            print(f"<<< {message}")
            # execute
            try:
                result = execute(str(message))
                if result[ExecMode] == ExecuteMode.EVAL:
                    await websocket.send(f"OK[{'RENPY' if result[ExecEnv] == ExecuteEnvironment.RENPY else 'PYTHON'}]>>> {result[ExecResult]}")
                elif result[ExecMode] == ExecuteMode.EXEC:
                    await websocket.send(f"OK[{'RENPY' if result[ExecEnv] == ExecuteEnvironment.RENPY else 'PYTHON'}].")
            except Exception as e:
                print(f"Error: {e}")
                await websocket.send(f"ERR>>> {e}")
    except ConnectionClosedError:
        notify(f"reed: Connection from {websocket.remote_address[0]} closed ({websocket.close_code})")

async def serve_websocket():
    async with serve(callback_websocket, "0.0.0.0", 35124):
        await asyncio.Future()

def run():
    if renpy:
        renpy.invoke_in_thread(asyncio.run, serve_websocket())
    else:
        asyncio.run(serve_websocket())
