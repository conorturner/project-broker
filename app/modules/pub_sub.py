"""
Module containing the functions and classes used to pass live prices from broker streams to subscribers.
"""

import asyncio
import aiohttp.web
from typing import Dict, Set

from aiohttp.web_ws import WebSocketResponse


async def subscribe(topics):
    url = f'ws://localhost:9000/subscribe?topics={",".join(topics)}'
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(url) as ws:
            async for msg in ws:
                if msg.type in (aiohttp.WSMsgType.CLOSED,
                                aiohttp.WSMsgType.ERROR):
                    break

                print('Message received from server:', msg.data)
                yield msg.data


class Publisher:
    topics: Dict[str, Set[WebSocketResponse]] = {}
    runner: aiohttp.web.AppRunner
    isListening = True

    async def broadcast(self, topic, message):
        if topic not in self.topics:
            return

        return asyncio.gather(*[ws.send_str(message) for ws in self.topics[topic]])

    def add_subscriber(self, topics, ws: WebSocketResponse):
        for topic in topics:
            if topic not in self.topics:
                # Topics are created by subscribers (bit of an anti-pattern tbh)
                self.topics[topic] = set()

            self.topics[topic].add(ws)

    def remove_subscriber(self, topics, ws: WebSocketResponse):
        for topic in topics:
            self.topics[topic].remove(ws)
            if len(self.topics[topic]) == 0:  # Remove topics with no subscribers.
                del self.topics[topic]

    async def websocket_handler(self, request):
        ws = aiohttp.web.WebSocketResponse()
        await ws.prepare(request)
        print('Websocket connection ready')

        epics = request.query['topics'].split(',')
        self.add_subscriber(epics, ws)

        async for msg in ws:
            pass

        print('Websocket connection closed')
        self.remove_subscriber(epics, ws)
        return ws

    async def listen(self):
        app = aiohttp.web.Application()
        app.router.add_route('GET', '/subscribe', self.websocket_handler)

        self.runner = aiohttp.web.AppRunner(app)
        await self.runner.setup()

        site = aiohttp.web.TCPSite(self.runner, 'localhost', 9000)
        await site.start()

        while self.isListening:
            await asyncio.sleep(.2)

    async def close(self):
        self.isListening = False
        await self.runner.cleanup()
