from abc import abstractmethod


class BaseIntegration:
    @abstractmethod
    async def open_position(self):
        pass

    @abstractmethod
    async def close_position(self):
        pass

    @abstractmethod
    async def get_position(self):
        pass

    @abstractmethod
    async def get_positions(self):
        pass

    @abstractmethod
    async def search_instruments(self):
        pass
