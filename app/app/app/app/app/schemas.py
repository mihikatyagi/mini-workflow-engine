from typing import Any, Dict, List, Optional
from pydantic import BaseModel


# ---------------------------------------------------------
# Node Definition
# Represents a single node in the workflow graph
# ---------------------------------------------------------
class NodeDef(BaseModel):
    name: str                     # name of the node
    func: str                     # tool/function name
    loop_condition: Optional[Dict[str, Any]] = None  # optional looping rule


# ---------------------------------------------------------
# Graph Definition
# Nodes + edges + optional start node
# ---------------------------------------------------------
class GraphDef(BaseModel):
    nodes: List[NodeDef]
    edges: Dict[str, Any]
    start_node: Optional[str] = None


# ---------------------------------------------------------
# API Models
# ---------------------------------------------------------
class CreateGraphResponse(BaseModel):
    graph_id: str

class RunRequest(BaseModel):
    graph_id: str
    initial_state: Dict[str, Any]

class RunResponse(BaseModel):
    run_id: str

class RunState(BaseModel):
    run_id: str
    graph_id: str
    state: Dict[str, Any]
    status: str
    log: List[str]
