from typing import Dict, Any
import os
import json
from datetime import datetime

import pika 

from domain.events import DocumentCreatedEvent, DocumentSharedEvent, FiridaEventType


Event = DocumentCreatedEvent | DocumentSharedEvent
EventData = Dict[str, Any]


def publish_event(event: Event): 
    conn = pika.BlockingConnection(pika.URLParameters(os.environ["AMQP_URL"]))
    channel = conn.channel() 
    channel.exchange_declare(exchange=os.environ["EXCHANGE_NAME"], exchange_type="fanout") # type: ignore

    event_data: EventData = {}
    if isinstance(event, DocumentCreatedEvent):
        event_data = {
            "event_type": FiridaEventType.DOCUMENT_CREATED.value, 
            "created_at": str(datetime.now()),
            "data": {
                "creator_id": event.creator_id, 
                "document_id": event.document_id, 
            }
        }
    elif isinstance(event, DocumentSharedEvent): # type: ignore
        ...
    else:
        raise ValueError("INCORRECT EVENT TYPE")

    channel.basic_publish(exchange=os.environ["EXCHANGE_NAME"], routing_key="", body=json.dumps(event_data))
    conn.close()
