import asyncio

from fastapi import WebSocket
from typing import Dict, List


class MessageBus:
    topics: Dict[str, List[WebSocket]]

    def __init__(self):
        self.topics = {}

    def subscribe(self, topic: str, listener: WebSocket):
        if topic not in self.topics:
            self.topics[topic] = []
        self.topics[topic].append(listener)

    def unsubscribe(self, topic: str, listener: WebSocket):
        pass  # TODO: delete websocket from dictionary

    async def broadcast(self, topic: str, message):
        if topic not in self.topics:
            return
        # Run them all in parallel
        await asyncio.gather(*[listener.send_text(message) for listener in self.topics[topic]])


bus = MessageBus()
