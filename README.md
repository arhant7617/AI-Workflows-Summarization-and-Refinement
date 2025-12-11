**AI Workflow Engine — Minimal Graph-Based Workflow System (FastAPI):**

A lightweight workflow/graph engine built using Python and FastAPI, supporting nodes, edges, branching, looping, and simple tool execution. This project demonstrates how an “agent-like” workflow system can be structured using clean Python modules.



**Features**

1. Minimal Workflow / Graph Engine:


		Nodes = Python functions that read/modify shared state
		Edges = Define execution order
		Conditional branching
		Looping until a condition is met      
		Clean execution log + run state tracking


<ins>2.Simple Tool Registry</ins>


Register any Python function as a tool

Nodes can call tools using the registry


3. FastAPI Endpoints


    **Endpoint**                              **Description**
POST /graph/create	                  Create a new workflow graph
POST /graph/run	                      Run the graph with an initial state
GET /graph/state/{run_id}	            Fetch current workflow state


**PROJECT STRUCTURE**
'''
   app/
   │── engine.py         # Core workflow engine (nodes, edges, branching, loops)
   │── tools.py          # Tool registry + example tools
   │── models.py         # Pydantic models for state + API schemas
   │── workflows.py      # Example workflow definition
   │── main.py           # FastAPI API routes
   │── __init__.py                      
'''

**Installation & Running the Project**

1️. Clone the Repository
git clone https://github.com/<your-username>/AiWorkflowAssignment.git
cd AiWorkflowAssignment

2️. Create & Activate Virtual Environment
python -m venv .venv
.venv\Scripts\activate

3️. Install Requirements
pip install -r requirements.txt

4️. Run FastAPI Server
uvicorn app.main:app --reload

5️. Open API Docs
Go to:
http://127.0.0.1:8000/docs


**Example Workflow**


The repository includes an example workflow where:


Nodes perform simple state updates
1. A tool analyzes data
2. The workflow branches based on conditions
3. A loop continues until a state value meets a threshold


Example JSON for running:


{
  "graph_id": "example_graph",
  "initial_state": {
    "value": 0
  }
}


**What This Engine Supports:**


Core Supported Features
Sequential node execution
Directed node-edge mapping
Conditional branching
Looping logic
Tool registry for extending functionality
Run logging + state tracking


**What Could Improve With More Time**


Visual UI for designing workflows
Parallel node execution
Database-backed state storage
Hot-reloadable workflows
More robust error handling
Support for asynchronous nodes
Built-in monitoring dashboard
