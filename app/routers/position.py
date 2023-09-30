from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.schemas.poisitions import PositionType, PositionOpenType
from app.schemas.errors import EntityNotFound

router = APIRouter(prefix="/position", tags=["Positions"])

not_found_response = {"model": EntityNotFound, "description": "Position Not Found"}


@router.get("/", response_model=List[PositionType])
def get_positions():
    return [{

    }]


@router.get("/{position_id}", response_model=PositionType, responses={404: not_found_response})
def get_position(position_id: str):
    return {"Hello": "World"}


@router.post("/", response_model=PositionType)
def open_position(body: PositionOpenType):
    return {"Hello": "World"}
