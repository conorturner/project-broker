import asyncio
import unittest

from app.modules.pub_sub import Publisher, subscribe


class MyTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_multiple_subscribers(self):
        async def pause_subscribe(topics, listen_count=2):
            await asyncio.sleep(0.1)
            msgs = []
            counter = 0
            async for m in subscribe(topics=topics):
                msgs.append(m)
                counter += 1
                if counter == listen_count:
                    break  # Breaking from the loop causes disconnection
            return msgs

        pub = Publisher()

        async def pause_broadcast():
            await asyncio.sleep(0.2)
            await pub.broadcast('123', 'hello all')
            await pub.broadcast('123', 'hello again')
            await pub.broadcast('456', 'hello others')

        async def deferred_close():
            await asyncio.sleep(0.3)
            await pub.close()

        results = await asyncio.gather(
            pub.listen(),
            pause_broadcast(),
            deferred_close(),
            pause_subscribe(['123', '456'], listen_count=3),
            pause_subscribe(['456'], listen_count=1),
        )
        self.assertEqual(results[-2], ['hello all', 'hello again', 'hello others'])
        self.assertEqual(results[-1], ['hello others'])


if __name__ == '__main__':
    unittest.main()
