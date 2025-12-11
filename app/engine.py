from typing import Callable, Dict, Optional, Awaitable
from .models import WorkflowState
import uuid
import inspect

# Node function type
NodeFn = Callable[[WorkflowState], WorkflowState | Awaitable[WorkflowState]]

# Callback used for WebSocket live updates
StepCallback = Callable[[str, WorkflowState], Awaitable[None]]

# In-memory storage
GRAPHS: Dict[str, "Graph"] = {}
RUNS: Dict[str, WorkflowState] = {}
RUN_LOGS: Dict[str, list[str]] = {}


class Graph:
    def __init__(self, nodes: Dict[str, NodeFn], edges: Dict[str, Optional[str]], start_node: str):
        """
        nodes: mapping of node_name -> function
        edges: mapping of node_name -> next_node_name (or None)
        """
        self.nodes = nodes
        self.edges = edges
        self.start_node = start_node


async def _execute_node(node_fn: NodeFn, state: WorkflowState) -> WorkflowState:
    """Run a node (supports both sync and async functions)."""
    if inspect.iscoroutinefunction(node_fn):
        # async node
        return await node_fn(state)
    else:
        # sync node
        return node_fn(state)


async def run_graph_async(
    graph_id: str,
    initial_state: WorkflowState,
    on_step: Optional[StepCallback] = None,
):
    """
    Runs a graph node-by-node.
    Calls on_step(node_name, state) after each node if provided (for WebSockets).
    """

    graph = GRAPHS[graph_id]
    state = initial_state
    run_id = str(uuid.uuid4())

    RUNS[run_id] = state
    RUN_LOGS[run_id] = []

    current = graph.start_node

    while current is not None and not state.done:
        node_fn = graph.nodes[current]

        # Log
        msg = f"Running node: {current}"
        state.log.append(msg)
        RUN_LOGS[run_id].append(msg)

        # WebSocket live update
        if on_step:
            await on_step(current, state)

        # Execute node
        state = await _execute_node(node_fn, state)

        # Save state snapshot
        RUNS[run_id] = state

        # Get next node
        current = graph.edges.get(current)

    # Final callback if WebSocket is connected
    if on_step:
        await on_step("END", state)

    return state, run_id
