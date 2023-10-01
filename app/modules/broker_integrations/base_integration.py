"""Contains generic classes for broker API integration."""

from abc import abstractmethod
from dataclasses import dataclass


@dataclass
class NewPositionDetails:
    """Contains fields for creating a new position."""
    direction: str
    size: float
    limit: float = None
    stop: float = None
    currency: str = 'GBP'
    expiry: str = '-'


class BaseIntegration:
    """Abstract parent class for broker API integration."""
    @abstractmethod
    async def open_position(self, epic: str, details: NewPositionDetails):
        """Method stub for opening a new position."""
        raise NotImplementedError()

    @abstractmethod
    async def close_position(self, deal_id: str, size, direction):
        """Method stub for closing a position."""
        raise NotImplementedError()

    @abstractmethod
    async def get_position(self, deal_id: str):
        """Method stub for getting a position."""
        raise NotImplementedError()

    @abstractmethod
    async def get_positions(self):
        """Method stub for getting all positions."""
        raise NotImplementedError()

    @abstractmethod
    async def search_instruments(self, search_term):
        """Method stub for searching for instruments."""
        raise NotImplementedError()
