from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from app.schemas import GraphDef, CreateGraphResponse, RunRequest, RunResponse, RunState
from app.storage import new_graph_id, save_graph, get_graph, get_run, subscribe_run, unsubscribe_run
from app.engine import GraphEngine

app = FastAPI(title="Mini Workflow Engine")
engine = GraphEngine()

@app.post("/graph/create", response_model=CreateGraphResponse)
async def create_graph(graph: GraphDef):
    graph_id = new_graph_id()
    data = graph.dict()
    if not data.get("start_node") and data["nodes"]:
        data["start_node"] = data["nodes"][0]["name"]
    save_graph(graph_id, data)
    return {"graph_id": graph_id}

@app.post("/graph/run", response_model=RunResponse)
async def run_graph(req: RunRequest):
    g = get_graph(req.graph_id)
    if not g:
        raise HTTPException(status_code=404, detail="Graph not found")
    run_id = await engine.run_graph(req.graph_id, req.initial_state)
    return {"run_id": run_id}

@app.get("/graph/state/{run_id}", response_model=RunState)
async def graph_state(run_id: str):
    r = get_run(run_id)
    if not r:
        raise HTTPException(status_code=404, detail="Run not found")
    return r

@app.websocket("/ws/logs/{run_id}")
async def websocket_logs(websocket: WebSocket, run_id: str):
    await websocket.accept()
    subscribe_run(run_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        unsubscribe_run(run_id, websocket)

