import unittest
from app.modules.message_bus import MessageBus


class MockWebsocket:
    def __init__(self):
        self.sent = []

    async def send_text(self, msg):
        self.sent.append(msg)


class MessageBusTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_message_bus(self):
        ws1 = MockWebsocket()
        ws2 = MockWebsocket()
        ws3 = MockWebsocket()
        mb = MessageBus()

        mb.subscribe('EURUSD', ws1)
        mb.subscribe('EURUSD', ws2)
        mb.subscribe('TSLA', ws3)

        await mb.broadcast('EURUSD', '123')
        await mb.broadcast('EURUSD', '456')
        await mb.broadcast('TSLA', '456')

        self.assertEqual(ws1.sent, ['123', '456'])
        self.assertEqual(ws2.sent, ['123', '456'])
        self.assertEqual(ws3.sent, ['456'])


if __name__ == '__main__':
    unittest.main()
