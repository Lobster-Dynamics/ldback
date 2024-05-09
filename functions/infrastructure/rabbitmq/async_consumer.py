"""
NOTE: type warnings here can be ignored
"""

import uuid
import asyncio 

import pika
from pika.channel import Channel
from pika.adapters.asyncio_connection import AsyncioConnection
from pika.exchange_type import ExchangeType


from application.observer import Observer


class PikaConsumer(object):

    def __init__(self, app_observer: Observer, amqp_url: str, exchange_name: str):
        self._queue_name = str(uuid.uuid1())
        self._connection: AsyncioConnection
        self._channel: Channel
        self._app_observer = app_observer
        self._amqp_url = amqp_url
        self._exchange_name = exchange_name

    
    def acknowledge_message(self, delivery_tag): # type: ignore
        self._channel.basic_ack(delivery_tag)

    def on_message(self, _unused_channel, basic_deliver, properties, body):
        loop = asyncio.get_event_loop()
        asyncio.run_coroutine_threadsafe(
            self._app_observer.notify_raw_event(body), loop
        )
        self.acknowledge_message(basic_deliver.delivery_tag)

    def on_basic_qos_ok(self, _unused_frame):
        self._consumer_tag = self._channel.basic_consume(
            self._queue_name, self.on_message
        )

    def on_queue_bind(self, _unused_frame):
        self._channel.basic_qos(prefetch_count=1, callback=self.on_basic_qos_ok)  # type: ignore

    def on_queue_declare(self, _unused_frame):
        self._channel.queue_bind(
            exchange=self._exchange_name,
            queue=self._queue_name,
            callback=self.on_queue_bind,  # type: ignore
        )

    def on_exchange_declare(self, _unused_frame):
        self._channel.queue_declare(
            queue=self._queue_name, callback=self.on_queue_declare  # type: ignore
        )

    def on_open_channel_callback(self, channel: Channel):
        self._channel = channel
        self._channel.exchange_declare(
            exchange=self._exchange_name,
            exchange_type=ExchangeType.fanout,
            callback=self.on_exchange_declare,  # type: ignore
        )

    def on_open_connection_callback(self, _unused_connection):
        self._connection.channel(on_open_callback=self.on_open_channel_callback)

    def run(self, loop):
        self._connection = AsyncioConnection(
            parameters=pika.URLParameters(self._amqp_url),
            on_open_callback=self.on_open_connection_callback,
            custom_ioloop=loop,
        )
