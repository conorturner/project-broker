from enum import Enum
from pydantic import BaseModel, Field


class BrokerEnum(str, Enum):
    ig = 'IG'
    capital = 'CAPITAL'


class DirectionEnum(str, Enum):
    long = 'LONG'
    short = 'SHORT'


class PositionType(BaseModel):
    position_id: str = Field(description='The ID of the position.', example='12345jgjv')
    epic: str = Field(description='EPIC of traded instrument.', example='EURUSD')
    broker: BrokerEnum = Field(description='Broker the position is help with.')
    direction: DirectionEnum = Field(description='Direction of position.')
    size: float = Field(description='Size of position..', example=1.5)
    margin: float = Field(description='Current margin requirement for the position.', example=11.23)
    entry_price: float = Field(description='Price the position was opened at.', example=112.34)
    current_price: float = Field(description='Current price of instrument.', example=134.34)
    stop_loss: float = Field(description='Value of stop loss.', example=154.34)
    take_profit: float = Field(description='Value of take profit.', example=111.34)


class PositionOpenType(BaseModel):
    epic: str = Field(description='EPIC of traded instrument.', example='EURUSD')
    broker: BrokerEnum = Field(description='Broker the position is help with.')
    direction: DirectionEnum = Field(description='Direction of position.')
    size: float = Field(description='Size of position..', example=1.5)
    stop_loss: float = Field(description='Value of stop loss.', example=154.34)
    take_profit: float = Field(description='Value of take profit.', example=111.34)
