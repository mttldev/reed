try:
    renpy = __import__("renpy").exports
except ImportError:
    renpy = None

import ast
import asyncio

import typing
from websockets.exceptions import ConnectionClosedError
from websockets.server import serve, WebSocketServerProtocol

class ExecutedResult:
    _failed: typing.Optional[bool] = None
    _exception: typing.Optional[Exception] = None

    def __init__(self, command: str) -> None:
        self.command = command

    @property
    def failed(self) -> bool:
        if self._failed is None:
            raise AttributeError("ExecutedResult object has not been executed yet.")
        return self._failed

    @failed.setter
    def failed(self, value: typing.Optional[bool]) -> None:
        raise AttributeError("Cannot set failed property of ExecutedResult object. Use failed() method instead.")

    @property
    def exception(self) -> Exception:
        if self._exception is None:
            raise AttributeError("ExecutedResult object has not been executed yet.")
        return self._exception

    @exception.setter
    def exception(self, value: typing.Optional[Exception]) -> None:
        raise AttributeError("Cannot set exception property of ExecutedResult object. Use exception() method instead.")

    def execute(self) -> None:
        try:
            tree = ast.parse(self.command)
            exec(compile(tree, filename="<string>", mode="exec"), globals(), locals())
            self._failed = False
        except Exception as e:
            self._exception = e
            self._failed = True

def notify(message: str):
    if renpy:
        renpy.notify(message)
    else:
        print(message)

async def callback_websocket(websocket: WebSocketServerProtocol):
    notify(f"[reed] New connection from {websocket.remote_address[0]}")
    try:
        async for message in websocket:
            print(f"<<< {message}")
            # execute
            try:
                command = str(message)
                result = ExecutedResult(command)
                result.execute()
                if result.failed:
                    await websocket.send(f"ERR>>> {result.exception}")
                else:
                    await websocket.send("OK>>>")
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
        renpy.invoke_in_main_thread(asyncio.create_task, serve_websocket(port=port))
    else:
        asyncio.run(serve_websocket(port=port))

run(35124)
