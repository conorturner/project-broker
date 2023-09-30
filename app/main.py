"""Module docstring"""

import asyncio

from fastapi import FastAPI, Depends

from app.middleware.auth import get_token_header

from app.routers import position, history, stream


async def test():
    """This is just an example async function that can run in the background."""
    while True:
        await asyncio.sleep(1)
        # print('working')


tags_metadata = [
    {
        "name": "Positions",
        "description": "Create and manage positions."
        # "\n## Subheading example",
    }
]

# with open('./docs/1-Getting-Started.md') as f:
#     desc = f.read()

app = FastAPI(
    title="MarketAPI",
    description='Description',
    version="0.1.0",
    openapi_tags=tags_metadata,
    contact={
        "name": "Conor Turner",
        "url": "https://xxx.yyy",
        "email": "conor@xxx.yyy",
    },
)


@app.on_event('startup')
async def start():
    """Async tasks must be started here when using uvicorn"""
    asyncio.create_task(test())


app.include_router(position.router, dependencies=[Depends(get_token_header)])
app.include_router(history.router, dependencies=[Depends(get_token_header)])
app.include_router(stream.router, dependencies=[Depends(get_token_header)])
