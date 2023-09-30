"""Router for /stream API routes"""

from fastapi import APIRouter, WebSocket
from app.schemas.errors import EntityNotFound

router = APIRouter(prefix="/stream", tags=["Streaming"])

not_found_response = {"model": EntityNotFound, "description": "Stream Not Found"}


@router.websocket("/ochl")
async def ochl_websocket(websocket: WebSocket):
    """Stream OCHL data via websocket."""
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")


@router.websocket("/tick")
async def tick_websocket(websocket: WebSocket):
    """Stream tick data via websocket."""
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")
