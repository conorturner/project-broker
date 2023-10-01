from abc import abstractmethod


class BaseIntegration:
    @abstractmethod
    async def open_position(self, epic: str, direction: str, size: int, expiry='-', limit=None, stop=None,
                            currency='GBP'):
        raise NotImplemented()

    @abstractmethod
    async def close_position(self, deal_id: str):
        raise NotImplemented()

    @abstractmethod
    async def get_position(self, deal_id: str):
        raise NotImplemented()

    @abstractmethod
    async def get_positions(self):
        raise NotImplemented()

    @abstractmethod
    async def search_instruments(self, search_term):
        raise NotImplemented()
