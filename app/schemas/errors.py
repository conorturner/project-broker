from typing import List
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime


class EntityNotFound(BaseModel):
    message: str


class DuplicateEntity(BaseModel):
    message: str
