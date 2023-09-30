"""
Module containing the functions and classes used to pass
live prices from broker streams to subscribers.
"""

import asyncio
from typing import Dict, List
from fastapi import WebSocket


class MessageBus:
    """The MessageBus class is a stateful service for asynchronous messaging (many-to-many)"""
    topics: Dict[str, List[WebSocket]]

    def __init__(self):
        """Initialise message bus with empty topics dictionary."""
        self.topics = {}

    def subscribe(self, topic: str, listener: WebSocket):
        """Subscribes a websocket to a given topic name."""
        if topic not in self.topics:
            self.topics[topic] = []
        self.topics[topic].append(listener)

    def unsubscribe(self, topic: str, listener: WebSocket):
        """Unsubscribes a websocket to a given topic name."""
        # TODO: delete websocket from dictionary
        raise NotImplementedError()

    async def broadcast(self, topic: str, message):
        """Broadcasts a message to all subscribers of a topic."""
        if topic not in self.topics:
            return
        # Run them all in parallel
        await asyncio.gather(*[listener.send_text(message) for listener in self.topics[topic]])


bus = MessageBus()
