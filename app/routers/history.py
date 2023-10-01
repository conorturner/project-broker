"""Router for /history API routes"""

from fastapi import APIRouter
from app.schemas.poisitions import PositionType
from app.schemas.errors import EntityNotFound

router = APIRouter(prefix="/history", tags=["History"])

not_found_response = {"model": EntityNotFound, "description": "Position Not Found"}


@router.get("/{epic}", response_model=PositionType, responses={404: not_found_response})
def get_position(epic: str):
    """API route for getting a position."""
    print(epic)
    return {"Hello": "World"}
