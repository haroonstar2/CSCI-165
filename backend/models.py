from pydantic import BaseModel

class Point(BaseModel):
    x: int
    y: int

class StartSimulationRequest(BaseModel):
    algorithm: str
    start: Point
    target: Point
    grid: list[list[int]]
    camps: list[dict]

class SpeedRequest(BaseModel):
    speed: int
