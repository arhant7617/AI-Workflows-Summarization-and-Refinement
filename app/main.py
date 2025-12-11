from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from .models import (
    CreateGraphRequest,
    CreateGraphResponse,
    RunGraphRequest,
    RunGraphResponse,
    WorkflowState,
)
from .engine import GRAPHS, RUNS, RUN_LOGS, run_graph_async
from .workflows import create_option_b_graph
import uuid

app = FastAPI(title="Workflow Engine - Summarizer (Option B)")

# Allow CORS for testing from browser tools (optional)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# simple root for a quick health check
@app.get("/")
async def root():
    return {"message": "Server is running!"}


# -------------------------
# Create graph
# -------------------------
@app.post("/graph/create", response_model=CreateGraphResponse)
async def create_graph(req: CreateGraphRequest):
    # only option_b implemented in this project
    if req.type != "option_b":
        raise HTTPException(status_code=400, detail="Only 'option_b' supported in this demo")

    graph = create_option_b_graph()
    graph_id = str(uuid.uuid4())
    GRAPHS[graph_id] = graph
    return CreateGraphResponse(graph_id=graph_id)


# -------------------------
# Run graph (blocking - returns final state when finished)
# -------------------------
@app.post("/graph/run", response_model=RunGraphResponse)
async def run_graph_endpoint(req: RunGraphRequest):
    if req.graph_id not in GRAPHS:
        raise HTTPException(status_code=404, detail="Graph not found")

    # prepare initial state
    state = WorkflowState(input_text=req.input_text, max_length=req.max_length)
    final_state, run_id = await run_graph_async(req.graph_id, state)
    log = RUN_LOGS.get(run_id, [])
    return RunGraphResponse(run_id=run_id, final_state=final_state, log=log)


# -------------------------
# Get latest state for a run
# -------------------------
@app.get("/graph/state/{run_id}", response_model=WorkflowState)
async def get_state(run_id: str):
    if run_id not in RUNS:
        raise HTTPException(status_code=404, detail="Run not found")
    return RUNS[run_id]


# -------------------------
# WebSocket endpoint: run graph and stream step-by-step logs
# -------------------------
@app.websocket("/ws/run")
async def run_graph_ws(websocket: WebSocket):
    """
    Protocol:
    - Client connects and sends a JSON message with keys:
      { "graph_id": "...", "input_text": "...", "max_length": 200 }
    - Server streams JSON messages of the form:
      { "event": "step", "node": "<node_name>", "state": { "done": bool, "log": [...] } }
    - Finally server sends { "event": "finished", "run_id": "...", "final_state": {...} }
    """
    await websocket.accept()
    try:
        init_msg = await websocket.receive_json()
        graph_id = init_msg.get("graph_id")
        input_text = init_msg.get("input_text", "")
        max_length = init_msg.get("max_length", 200)

        if not graph_id or graph_id not in GRAPHS:
            await websocket.send_json({"event": "error", "message": "Graph not found or graph_id missing"})
            await websocket.close()
            return

        state = WorkflowState(input_text=input_text, max_length=max_length)

        async def on_step(node_name: str, current_state: WorkflowState):
            # send a concise state to avoid huge messages
            await websocket.send_json({
                "event": "step",
                "node": node_name,
                "state": {
                    "done": current_state.done,
                    "log": current_state.log[-10:],  # last 10 log lines
                    "refined_summary_preview": (current_state.refined_summary[:300] + "...") if current_state.refined_summary else ""
                }
            })

        final_state, run_id = await run_graph_async(graph_id, state, on_step=on_step)

        await websocket.send_json({
            "event": "finished",
            "run_id": run_id,
            "final_state": final_state.dict(),
        })
        await websocket.close()

    except WebSocketDisconnect:
        # client disconnected; run is still recorded in RUNS
        return
    except Exception as e:
        await websocket.send_json({"event": "error", "message": str(e)})
        await websocket.close()
