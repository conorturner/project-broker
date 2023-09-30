import os
import unittest
from app.modules.broker_integrations.ig_api import IgAPI

IG_API_KEY = os.environ.get('IG_API_KEY')
IG_ACCOUNT = os.environ.get('IG_ACCOUNT')
IG_USER = os.environ.get('IG_USER')
IG_PASS = os.environ.get('IG_PASS')

class IGIntegrationTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_market_search(self):
        api = IgAPI(IG_API_KEY, IG_ACCOUNT, IG_USER, IG_PASS)
        result = await api.search_market('wall street cash')
        print(result)

    async def test_open_close_position(self):
        api = IgAPI(IG_API_KEY, IG_ACCOUNT, IG_USER, IG_PASS)

        epic = 'IX.D.DOW.IFD.IP'

        position = await api.open_position('BUY', 1, epic, currency='USD')
        print(position)
        position = await api.close_position(position['dealId'], 1, 'SELL')
        print(position)


if __name__ == '__main__':
    unittest.main()
