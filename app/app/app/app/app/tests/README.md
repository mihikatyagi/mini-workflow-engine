# Mini Workflow Engine (SDN Assignment)

This project implements a simple **Workflow Engine** using **FastAPI**, as required in the assignment.

The engine supports:
- Nodes (each node calls a function/tool)
- Edges (define how nodes connect)
- Conditional branching
- Looping using `loop_condition`
- Shared state dictionary
- Asynchronous execution in background tasks
- WebSocket for real-time logs
- Example Code-Review Mini-Agent workflow using tools

---

## 🚀 How to Run the Project

### 1. Create a virtual environment

python3 -m venv .venv
source .venv/bin/activate  # Mac/Linux
# .venv\Scripts\activate   # Windows 

### 2. Install Requirements
pip install -r requirements.txt

### 3. Start FastAPI server
uvicorn app.main:app --reload --port 8000

### server will run at:
http://127.0.0.1:8000



### API Endpoints
POST /graph/create

Create a workflow graph.

POST /graph/run

Start execution of the graph.

GET /graph/state/{run_id}

Check the current state & logs of a run.

WS /ws/logs/{run_id}

(Stream logs live over WebSocket)


### Example Workflow (Code Review Mini-Agent)
{
  "nodes": [
    {"name": "extract", "func": "extract_functions"},
    {"name": "complexity", "func": "check_complexity"},
    {"name": "detect", "func": "detect_issues"},
    {"name": "suggest", "func": "suggest_improvements",
     "loop_condition": {"key": "quality_score", "op": "lt", "value": 80}
    },
    {"name": "end", "func": "noop"}
  ],
  "edges": {
    "extract": "complexity",
    "complexity": "detect",
    "detect": "suggest",
    "suggest": {
      "if": {"key": "quality_score", "op": "gte", "value": 80},
      "then": "end",
      "else": "suggest"
    },
    "end": null
  }
}


### Improvements If I Had More Time

1. Add database persistence (SQLite/Postgres)

2. Add a UI dashboard to visualize node execution

3. Add retries and timeout handling for nodes

4. Add more unit tests

5. Add metrics and performance logging



### Product Structure

app/
    main.py
    engine.py
    tools.py
    storage.py
    schemas.py
tests/
    test_engine.py
requirements.txt
README.md
.gitignore
