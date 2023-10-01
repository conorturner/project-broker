import os
import unittest
from app.modules.broker_integrations.capital_api import CapitalClient

CAPITAL_API_KEY = os.environ.get('CAPITAL_API_KEY')
CAPITAL_USER = os.environ.get('CAPITAL_USER')
CAPITAL_PASS = os.environ.get('CAPITAL_PASS')


class CapitalTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_all_accounts(self):
        client = CapitalClient(CAPITAL_USER, CAPITAL_API_KEY, CAPITAL_PASS, demo=True)
        account = await client.all_accounts()
        print(account)
        # print(account)

    async def test_search_instruments(self):
        client = CapitalClient(CAPITAL_USER, CAPITAL_API_KEY, CAPITAL_PASS, demo=True)
        account = await client.search_instruments('crude')
        print(account)
        # print(account)

    # def test_open_close_success(self):
    #     self.skipTest('doesnt work on weekends')
    #     client = CapitalClient(CAPITAL_USER, CAPITAL_API_KEY, CAPITAL_PASS, demo=True)
    #
    #     account = client.all_accounts()["accounts"]
    #     print(account)
    #
    #     # client.change_active_account(account[0]["accountId"])
    #
    #     deal_id = client.open_position("TSLA", "BUY", 1)
    #
    #     # positions = client.all_positions()
    #     # print(positions)
    #     result = client.close_position(deal_id=deal_id['affectedDeals'][0]['dealId'])
    #     print(result)
    #     # client.update_position(deal_id=deal_id["affectedDeals"][0]["dealId"])
    #
    #     print(
    #         f"I´ve made {result['profit']}$ of profit!"
    #     )


if __name__ == '__main__':
    unittest.main()
