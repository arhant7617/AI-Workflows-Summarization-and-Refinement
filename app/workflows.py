from .models import WorkflowState
from .tools import TOOL_REGISTRY
from .engine import Graph


# ---------------------------------------------------------
# NODE 1 — Split text into chunks
# ---------------------------------------------------------
def node_split_text(state: WorkflowState) -> WorkflowState:
    state.log.append("Splitting text into chunks...")

    # Step 1: compute max_length automatically (target = original_length/3)
    total_words = len(state.input_text.split())
    state.max_length = max(total_words // 3, 20)   # minimum 20 words

    # Step 2: split text
    splitter = TOOL_REGISTRY["split_text"]
    state.chunks = splitter(state.input_text, chunk_size=200)

    return state


# ---------------------------------------------------------
# NODE 2 — Summaries for each chunk
# ---------------------------------------------------------
def node_generate_summaries(state: WorkflowState) -> WorkflowState:
    state.log.append("Generating summaries for each chunk...")
    summarizer = TOOL_REGISTRY["summarize_chunk"]

    state.chunk_summaries = [
        summarizer(chunk, max_words=50)
        for chunk in state.chunks
    ]
    return state


# ---------------------------------------------------------
# NODE 3 — Merge summaries
# ---------------------------------------------------------
def node_merge_summaries(state: WorkflowState) -> WorkflowState:
    state.log.append("Merging chunk summaries...")

    merger = TOOL_REGISTRY["merge_summaries"]
    state.merged_summary = merger(state.chunk_summaries)

    # Initial refined summary = merged summary
    state.refined_summary = state.merged_summary
    return state


# ---------------------------------------------------------
# NODE 4 — Refine final summary
# ---------------------------------------------------------
def node_refine_summary(state: WorkflowState) -> WorkflowState:
    state.log.append("Refining summary...")

    refiner = TOOL_REGISTRY["refine_summary"]
    state.refined_summary = refiner(state.refined_summary, state.max_length)

    return state


# ---------------------------------------------------------
# NODE 5 — Check if summary length is short enough
# Loop control node
# ---------------------------------------------------------
def node_check_length(state: WorkflowState) -> WorkflowState:
    word_count = len(state.refined_summary.split())

    if word_count <= state.max_length:
        state.log.append(f"Summary within limit ({word_count} words). Finishing workflow.")
        state.done = True
    else:
        state.log.append(f"Summary too long ({word_count} words). Will refine again.")

    return state


# ---------------------------------------------------------
# Build the Graph for Option B
# ---------------------------------------------------------
def create_option_b_graph() -> Graph:
    nodes = {
        "split_text": node_split_text,
        "generate_summaries": node_generate_summaries,
        "merge_summaries": node_merge_summaries,
        "refine_summary": node_refine_summary,
        "check_length": node_check_length,
    }

    edges = {
        "split_text": "generate_summaries",
        "generate_summaries": "merge_summaries",
        "merge_summaries": "refine_summary",
        "refine_summary": "check_length",

        # Loop: check_length → refine_summary (unless done=True)
        "check_length": "refine_summary",
    }

    return Graph(nodes=nodes, edges=edges, start_node="split_text")
