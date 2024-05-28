import os
import logging
from logging import Logger
from collections import defaultdict
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)
logging.basicConfig(filename="example.log", encoding="utf-8", level=logging.INFO)

from typing import DefaultDict, List, Annotated
import asyncio


from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query

from infrastructure.firebase import FIREBASE_APP
from firebase_admin.auth import verify_id_token

from application.observer import INotifier, create_app_observer
from infrastructure.rabbitmq.async_consumer import PikaConsumer


class WebSocketManger:

    def __init__(self, logger: Logger):
        self._logger = logger
        self._ids_to_socks: DefaultDict[str, List[WebSocket]] = defaultdict(list)

    async def add_websocket(self, id: str, websocket: WebSocket):
        await websocket.accept()
        self._ids_to_socks[id].append(websocket)
        self._logger.info(f"[now we are working with {len(self._ids_to_socks[id])}]")

    def remove_connection(self, id: str): ...

    async def unicast_json(self, id: str, msg: dict): # type: ignore
        if id not in self._ids_to_socks.keys():
            raise BaseException(f"[connection with id: {id} not found]")
        for websock in self._ids_to_socks[id]:
            await websock.send_json(msg)

    async def try_unicast_json(self, id: str, msg: dict): # type: ignore
        """Tries to unicast the message through all the websockets 
        being closed then the websocket is removed from the list
        assigned to that id, if a websocket fails to be updated due to it 
        """
        websocks_to_remove = []
        for websock in self._ids_to_socks[id]:
            try:
                await websock.send_json(msg)
            except WebSocketDisconnect as inst:
                websocks_to_remove.append(inst)
            except BaseException as inst:
                self._logger.error(f"[Error while trying to unicast {str(inst)}] through a specific websocket")
        for websock in websocks_to_remove:
            self._ids_to_socks[id].remove(websock)

    async def multicast_json(self, ids: List[str], msg: dict): # type: ignore
        for id in ids:
            await self.unicast_json(id, msg) # type: ignore

    async def try_multicast(self, ids: List[str], msg: dict): # type: ignore
        for id in ids:
            await self.try_unicast_json(id, msg)# type: ignore

    async def broadcast_json(self, msg: dict): # type: ignore
        raise NotImplementedError()

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
    id = verify_id_token(auth_token)["uid"] #type: ignore
    logger.info(str(id))
    try: 
        await websocket_manager.add_websocket(id, websocket) # type: ignore
    
        # prevents the socket from closing
        while True:
            await asyncio.sleep(10)
    except BaseException as inst:
        logger.info(f"Unable to stablish connection with auth_token={id}")