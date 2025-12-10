import asyncio
from typing import Dict, Any
from app.storage import get_graph, get_run, save_run, get_subscribers
from app.storage import new_run_id
from app.tools import TOOL_REGISTRY

class GraphEngine:
    def __init__(self):
        self._tasks = {}

    async def run_graph(self, graph_id: str, initial_state: Dict[str, Any]) -> str:
        graph = get_graph(graph_id)
        if not graph:
            raise ValueError("Graph not found")

        run_id = new_run_id()
        run_data = {
            "run_id": run_id,
            "graph_id": graph_id,
            "state": dict(initial_state),
            "status": "running",
            "log": []
        }

        save_run(run_id, run_data)

        task = asyncio.create_task(self._execute_run(run_id, graph))
        self._tasks[run_id] = task

        return run_id

    async def _broadcast(self, run_id: str, message: str):
        subscribers = get_subscribers(run_id)
        for ws in subscribers:
            try:
                await ws.send_text(message)
            except:
                pass

    async def _execute_run(self, run_id: str, graph: Dict[str, Any]):
        run = get_run(run_id)
        state = run["state"]
        log = run["log"]

        nodes = {n["name"]: n for n in graph["nodes"]}
        edges = graph["edges"]
        current = graph.get("start_node", graph["nodes"][0]["name"])

        while current:
            node_def = nodes.get(current)
            if not node_def:
                msg = f"Node '{current}' not found."
                log.append(msg)
                await self._broadcast(run_id, msg)
                break

            func_name = node_def["func"]
            tool = TOOL_REGISTRY.get(func_name)

            msg = f"Running node '{current}' → {func_name}"
            log.append(msg)
            await self._broadcast(run_id, msg)

            if not tool:
                log.append(f"Tool '{func_name}' missing.")
                break

            # Many tools accept 'state', some accept (code, state)
            try:
                result = tool(state)
            except TypeError:
                result = tool(state.get("code", ""), state)

            if isinstance(result, dict):
                state.update(result)

            result_msg = f"Node '{current}' output: {result}"
            log.append(result_msg)
            await self._broadcast(run_id, result_msg)

            # Check loop condition
            loop = node_def.get("loop_condition")
            if loop:
                key = loop["key"]
                op = loop["op"]
                value = loop["value"]
                lhs = state.get(key)

                condition = False
                if op == "lt": condition = lhs < value
                elif op == "gt": condition = lhs > value
                elif op == "lte": condition = lhs <= value
                elif op == "gte": condition = lhs >= value
                elif op == "eq": condition = lhs == value

                if condition:
                    await asyncio.sleep(0.1)
                    continue

            # Find next node
            e = edges.get(current)
            if e is None:
                break

            if isinstance(e, dict):
                cond = e.get("if")
                if cond:
                    key = cond["key"]
                    op = cond["op"]
                    val = cond["value"]
                    lhs = state.get(key)
                    valid = False
                    if op == "gte": valid = lhs >= val
                    elif op == "lte": valid = lhs <= val
                    elif op == "gt": valid = lhs > val
                    elif op == "lt": valid = lhs < val
                    elif op == "eq": valid = lhs == val

                    current = e["then"] if valid else e["else"]
                else:
                    current = e.get("next")
            else:
                current = e

            await asyncio.sleep(0)

        run["status"] = "finished"
        save_run(run_id, run)
        await self._broadcast(run_id, "Run finished.")

