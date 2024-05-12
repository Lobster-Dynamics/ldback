import os
import logging
from logging import Logger
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)
logging.basicConfig(filename="example.log", encoding="utf-8", level=logging.INFO)

from typing import Dict, List, Annotated
import asyncio

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query

from application.observer import INotifier, create_app_observer
from infrastructure.rabbitmq.async_consumer import PikaConsumer


class WebSocketManger:

    def __init__(self, logger: Logger):
        self._logger = logger
        self._ids_to_socks: Dict[str, WebSocket] = {}

    async def add_websocket(self, id: str, websocket: WebSocket):
        await websocket.accept()
        self._ids_to_socks[id] = websocket

    def remove_connection(self, id: str): ...

    async def unicast_json(self, id: str, msg: dict): # type: ignore
        if id not in self._ids_to_socks.keys():
            raise BaseException(f"[connection with id: {id} not found]")
        await self._ids_to_socks[id].send_json(msg)

    async def try_unicast_json(self, id: str, msg: dict): # type: ignore
        try:
            await self.unicast_json(id, msg) # type: ignore
        except WebSocketDisconnect as inst:
            del self._ids_to_socks[id]
        except BaseException as inst:
            self._logger.error(f"[Error while trying to unicast {str(inst)}]")

    async def multicast_json(self, ids: List[str], msg: dict): # type: ignore
        for id in ids:
            await self.unicast_json(id, msg) # type: ignore

    async def try_multicast(self, ids: List[str], msg: dict): # type: ignore
        for id in ids:
            await self.try_unicast_json(id, msg)# type: ignore

    async def broadcast_json(self, msg: dict): # type: ignore
        to_delete_ids = []
        for id in self._ids_to_socks.keys():
            try:
                await self.unicast_json(id=id, msg=msg) # type: ignore
            except WebSocketDisconnect as inst: # type: ignore
                to_delete_ids.append(id) # type: ignore
        for id in to_delete_ids: # type: ignore
            del self._ids_to_socks[id]

# define concrete notifier
class WebSocketNotifier(INotifier):
    def __init__(self, websocket_manager: WebSocketManger):
        self._websocket_manager = websocket_manager

    async def notify_user(self, user_id: str, msg: dict): # type: ignore
        await self._websocket_manager.try_unicast_json(user_id, msg) # type: ignore


websocket_manager = WebSocketManger(logger=logger)
observer = create_app_observer(concrete_notifier=WebSocketNotifier(websocket_manager=websocket_manager))
consumer = PikaConsumer(app_observer=observer, amqp_url=os.environ["AMQP_URL"], exchange_name=os.environ["EXCHANGE_NAME"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    consumer.run(asyncio.get_running_loop()) # type: ignore
    yield

 
app = FastAPI(lifespan=lifespan)


@app.websocket("/notifications")
async def websocket_endpoint(auth_token: Annotated[str, Query()], websocket: WebSocket):
    id = auth_token
    await websocket_manager.add_websocket(id, websocket)
    
    # prevents the socket from closing
    while True:
        await asyncio.sleep(10)

