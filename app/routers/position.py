"""Router for /position API routes"""

from typing import List
from fastapi import APIRouter
from app.schemas.poisitions import PositionType, PositionOpenType
from app.schemas.errors import EntityNotFound

router = APIRouter(prefix="/position", tags=["Positions"])

not_found_response = {"model": EntityNotFound, "description": "Position Not Found"}


@router.get("/", response_model=List[PositionType])
def get_positions():
    """Return a list of positions."""
    return [{

    }]


@router.get("/{position_id}", response_model=PositionType, responses={404: not_found_response})
def get_position(position_id: str):
    """Return a single position by position_id."""
    print(position_id)
    return {"Hello": "World"}


@router.post("/", response_model=PositionType)
def open_position(body: PositionOpenType):
    """Create a new position."""
    print(body)
    return {"Hello": "World"}
