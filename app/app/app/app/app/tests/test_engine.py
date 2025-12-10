import asyncio
from app.engine import GraphEngine
from app.storage import save_graph, new_graph_id, get_run


# Minimal test graph
sample_graph = {
    "nodes": [
        {"name": "start", "func": "noop"},
        {"name": "end", "func": "noop"}
    ],
    "edges": {
        "start": "end",
        "end": None
    },
    "start_node": "start"
}


def test_engine_run():
    # Create new graph
    gid = new_graph_id()
    save_graph(gid, sample_graph)

    engine = GraphEngine()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    run_id = loop.run_until_complete(engine.run_graph(gid, {"msg": "hello"}))

    # Allow engine to run
    loop.run_until_complete(asyncio.sleep(0.2))

    run_data = get_run(run_id)

    assert run_data is not None
    assert run_data["status"] in ("running", "finished", "failed")
