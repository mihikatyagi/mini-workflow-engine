import uuid
from typing import Dict, Any
from threading import Lock

# In-memory storage (simple for assignment)
graphs: Dict[str, Dict[str, Any]] = {}
runs: Dict[str, Dict[str, Any]] = {}
run_subscribers: Dict[str, list] = {}

# Thread lock (ensures safe access when multiple requests happen)
_lock = Lock()


# ---------------------------------------------------------
# ID Generators
# ---------------------------------------------------------
def new_graph_id() -> str:
    return "g_" + uuid.uuid4().hex[:8]

def new_run_id() -> str:
    return "r_" + uuid.uuid4().hex[:8]


# ---------------------------------------------------------
# Graph Storage
# ---------------------------------------------------------
def save_graph(graph_id: str, graph_data: Dict[str, Any]):
    with _lock:
        graphs[graph_id] = graph_data

def get_graph(graph_id: str):
    return graphs.get(graph_id)


# ---------------------------------------------------------
# Run Storage
# ---------------------------------------------------------
def save_run(run_id: str, run_data: Dict[str, Any]):
    with _lock:
        runs[run_id] = run_data

def get_run(run_id: str):
    return runs.get(run_id)


# ---------------------------------------------------------
# WebSocket Subscribers
# ---------------------------------------------------------
def subscribe_run(run_id: str, websocket):
    with _lock:
        run_subscribers.setdefault(run_id, []).append(websocket)

def unsubscribe_run(run_id: str, websocket):
    with _lock:
        if run_id in run_subscribers:
            run_subscribers[run_id] = [
                ws for ws in run_subscribers[run_id] if ws != websocket
            ]
            if not run_subscribers[run_id]:
                run_subscribers.pop(run_id, None)

def get_subscribers(run_id: str):
    return list(run_subscribers.get(run_id, []))
