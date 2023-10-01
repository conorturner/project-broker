"""Contains functions and types for authenticating API requests via token secret.."""

from fastapi import HTTPException, Header

AccessTokenType = Header(..., description='Access token generated using master password.')


async def get_token_header(access_token: str = AccessTokenType):
    """Middleware function checking for access_token in request headers."""
    if access_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")
