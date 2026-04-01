from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
import uuid
import json

app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

active_simulations = {}

# Endpoints

@app.post("/api/simulate/start")
async def start_simulation(req: StartSimulationRequest):
    # Generate a unique ID for this simulation run
    run_id = str(uuid.uuid4())
    
    # Store the initial state
    active_simulations[run_id] = {
        "request": req,
        "is_running": True,
    }
    
    return {"runId": run_id, "status": "initialized"}

@app.post("/api/simulate/{run_id}/reset")
async def reset_simulation(run_id: str):

    # Flip the flag to stop the generator loop
    if run_id in active_simulations:
        active_simulations[run_id]["is_running"] = False
    return {"status": "reset_successful"}

@app.post("/api/simulate/{run_id}/speed")
async def update_simulation_speed(run_id: str, req: SpeedRequest):
    if run_id in active_simulations:
        active_simulations[run_id]["speed"] = req.speed
        return {"status": "success", "new_speed": req.speed}
    return {"error": "Simulation not found"}


async def simulation_event_generator(run_id: str):
    sim = active_simulations.get(run_id)
    if not sim:
        yield f"data: {json.dumps({'error': 'Simulation not found'})}\n\n"
        return
    
    if "speed" not in sim:
        sim["speed"] = 50 # Default to 50

    # Extract start data
    curr_x = sim["request"].start.x
    curr_y = sim["request"].start.y
    algo = sim["request"].algorithm

    step = 0
    # Runs until it hits the target or the user hits Reset
    while sim["is_running"] and step < 50: 

        slider_val = sim["speed"]
        delay = max(0.02, 1.0 - (slider_val / 100.0))

        await asyncio.sleep(delay)
        
        # Dummy logic. Should replace this with the steps from the algorithm
        curr_x += 1
        curr_y += 1
        
        # Construct the payload
        payload = {
            "agentPos": {"x": curr_x, "y": curr_y},
            "visitedNode": {"x": curr_x, "y": curr_y},
            "log": f"[{algo.upper()}] Evaluated node ({curr_x}, {curr_y}) | Cost: {step}"
        }
        
        yield f"data: {json.dumps(payload)}\n\n"
        
        step += 1

    # Send a final message when finished
    if sim["is_running"]:
        yield f"data: {json.dumps({'status': 'finished', 'log': 'Target reached!'})}\n\n"

# StreamingResponse keeps the connection open and streams the yields from the generator
# Basically sends finished parts back to frontend while the rest is still being processed
# https://apidog.com/blog/fastapi-streaming-response/

# It also allowing multiple requests to be made at the same time (like play, pause, reset)

@app.get("/api/simulate/{run_id}/stream")
async def stream_simulation(run_id: str):

    return StreamingResponse(
        simulation_event_generator(run_id), 
        media_type="text/event-stream"
    )