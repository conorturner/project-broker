from fastapi import APIRouter, Depends, HTTPException, WebSocket
from typing import List
from app.schemas.poisitions import PositionType, PositionOpenType
from app.schemas.errors import EntityNotFound
from app.modules.message_bus import bus

router = APIRouter(prefix="/stream", tags=["Streaming"])

not_found_response = {"model": EntityNotFound, "description": "Stream Not Found"}


@router.websocket("/ochl")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")


@router.websocket("/tick")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")
