from pydantic import BaseModel
from typing import List, Optional


class WorkflowState(BaseModel):
    input_text: str
    max_length: int = 200

    chunks: List[str] = []
    chunk_summaries: List[str] = []
    merged_summary: str = ""
    refined_summary: str = ""

    done: bool = False
    log: List[str] = []


class CreateGraphRequest(BaseModel):
    type: str


class CreateGraphResponse(BaseModel):
    graph_id: str


class RunGraphRequest(BaseModel):
    graph_id: str
    input_text: str
    max_length: int = 200


class RunGraphResponse(BaseModel):
    run_id: str
    final_state: WorkflowState
    log: List[str]
