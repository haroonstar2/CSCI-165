from pydantic import BaseModel

class Point(BaseModel):
    x: int
    y: int

class GAConfig(BaseModel):
    population_size: int = 100
    dna_length: int = 150
    mutation_rate: float = 0.02
    elite_count: int = 10
    max_generations: int = 60

class StartSimulationRequest(BaseModel):
    algorithm: str
    start: Point
    target: Point
    grid: list[list[int]]
    camps: list[dict]
    ga_config: GAConfig | None = None

class SpeedRequest(BaseModel):
    speed: int
