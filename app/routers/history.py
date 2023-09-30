from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.schemas.poisitions import PositionType, PositionOpenType
from app.schemas.errors import EntityNotFound

router = APIRouter(prefix="/history", tags=["History"])

not_found_response = {"model": EntityNotFound, "description": "Position Not Found"}


@router.get("/{epic}", response_model=PositionType, responses={404: not_found_response})
def get_position(epic: str):
    return {"Hello": "World"}
