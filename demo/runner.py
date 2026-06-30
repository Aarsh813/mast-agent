import os
import json
import time
import uuid
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from demo.tasks import TASKS
from demo.agents import app as agent_graph

RUNS_DIR = os.path.join(os.path.dirname(__file__), "saved_runs")

def run_task(task_obj):
    run_id = str(uuid.uuid4())
    start_time = time.time()
    
    state = {
        "task": task_obj["description"],
        "plan": [],
        "current_step": 0,
        "code_attempts": {},
        "reviews": {},
        "final_code": "",
        "status": "planning",
        "messages": []
    }
    
    # We aren't using the MastLangGraphHandler yet, just saving the state dumps manually
    # for Phase 1 to have raw execution traces.
    
    try:
        final_state = agent_graph.invoke(state)
        error = None
    except Exception as e:
        final_state = state # partial state
        error = str(e)
    
    end_time = time.time()
    
    # Determine basic pass/fail heuristic
    outcome = "pass"
    if final_state.get("status") == "failed" or error:
        outcome = "fail"
    elif not final_state.get("final_code"):
        outcome = "fail"
        
    run_log = {
        "run_id": run_id,
        "task_id": task_obj["id"],
        "task_description": task_obj["description"],
        "started_at": datetime.fromtimestamp(start_time).isoformat(),
        "ended_at": datetime.fromtimestamp(end_time).isoformat(),
        "latency_ms": (end_time - start_time) * 1000,
        "outcome": outcome,
        "error": error,
        "final_state": {
            "plan": final_state.get("plan"),
            "current_step": final_state.get("current_step"),
            "status": final_state.get("status"),
            "final_code": final_state.get("final_code"),
            # Exclude full messages object to keep JSON clean, just stringify
            "messages": [msg.content for msg in final_state.get("messages", [])]
        }
    }
    
    file_path = os.path.join(RUNS_DIR, f"run_{run_id}.json")
    with open(file_path, "w") as f:
        json.dump(run_log, f, indent=2)
        
    print(f"[{outcome.upper()}] Task {task_obj['id']} completed in {run_log['latency_ms']:.0f}ms. Log: {file_path}")

def main():
    if not os.path.exists(RUNS_DIR):
        os.makedirs(RUNS_DIR)
        
    runs_per_task = 5 # In real test, 10-15
    print(f"Starting batch run: {len(TASKS)} tasks x {runs_per_task} iterations")
    
    for task in TASKS:
        for i in range(runs_per_task):
            print(f"Running {task['id']} (Iteration {i+1}/{runs_per_task})...")
            run_task(task)

if __name__ == "__main__":
    main()
