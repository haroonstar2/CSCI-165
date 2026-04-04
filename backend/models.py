from pydantic import BaseModel
from typing import Optional

class Point(BaseModel):
    x: int
    y: int

class StartSimulationRequest(BaseModel):
    algorithm: str
    start: Optional[Point] = None
    target: Optional[Point] = None
    grid: list[list[int]]
    camps: list[dict]
    side: Optional[str] = None

class SpeedRequest(BaseModel):
    speed: int
