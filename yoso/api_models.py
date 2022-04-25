from pydantic import BaseModel
from typing import Dict


class CounterResponse(BaseModel):
    items: Dict[str, int]
