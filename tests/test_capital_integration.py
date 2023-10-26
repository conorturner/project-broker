import os
import unittest

from app.modules.broker_integrations.base_integration import NewPositionDetails
from app.modules.broker_integrations.capital_integration import CapitalIntegration

CAPITAL_API_KEY = os.environ.get('CAPITAL_API_KEY')
CAPITAL_USER = os.environ.get('CAPITAL_USER')
CAPITAL_PASS = os.environ.get('CAPITAL_PASS')


class CapitalTestCase(unittest.IsolatedAsyncioTestCase):

    async def test_stream(self):
        client = CapitalIntegration(CAPITAL_USER, CAPITAL_API_KEY, CAPITAL_PASS, demo=True)
        async for msg in client.stream(['OIL_CRUDE']):
            print(msg)
        # print(account)

    async def test_all_accounts(self):
        self.skipTest('needs mocks')
        # TODO: write a mock for this test
        client = CapitalIntegration(CAPITAL_USER, CAPITAL_API_KEY, CAPITAL_PASS, demo=True)
        account = await client.all_accounts()
        print(account)
        # print(account)

    async def test_search_instruments(self):
        # TODO: write a mock for this test
        self.skipTest('needs mocks')

        client = CapitalIntegration(CAPITAL_USER, CAPITAL_API_KEY, CAPITAL_PASS, demo=True)
        account = await client.search_instruments('crude')
        print(account)
        # print(account)

    async def test_open_close_success(self):
        # TODO: write a mock for this test
        # TODO: make the test pass
        # TODO: use assertions in equivalent test for IG to write assertions here
        self.skipTest('needs mocks')

        client = CapitalIntegration(CAPITAL_USER, CAPITAL_API_KEY, CAPITAL_PASS, demo=True)

        account = (await client.all_accounts())["accounts"]
        print(account)

        # client.change_active_account(account[0]["accountId"])

        deal_id = await client.open_position("TSLA", NewPositionDetails('BUY', 1))

        # positions = client.all_positions()
        # print(positions)
        result = await client.close_position(deal_id=deal_id['affectedDeals'][0]['dealId'])
        print(result)
        # client.update_position(deal_id=deal_id["affectedDeals"][0]["dealId"])

        print(
            f"I´ve made {result['profit']}$ of profit!"
        )

    # TODO: write a test case for when the market is closed, assert the correct exception is raised.


if __name__ == '__main__':
    unittest.main()
