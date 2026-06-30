import os
import asyncio
import json
from dotenv import load_dotenv

load_dotenv()

from mast_agent.diagnosis.classifier import MASTClassifier

# This script would download the MAST huggingface dataset (mcemri/MAD) and run the classifier against it.
# For demonstration purposes, we will mock the dataset structure.

async def validate_classifier():
    provider = os.getenv("MAST_LLM_PROVIDER", "groq")
    model = os.getenv("MAST_LLM_MODEL", "llama-3.3-70b-versatile")
    classifier = MASTClassifier(provider=provider, model=model)
    
    # Read a real generated trace from demo/saved_runs
    runs_dir = os.path.join(os.path.dirname(__file__), "..", "demo", "saved_runs")
    failed_runs = []
    if os.path.exists(runs_dir):
        for fname in os.listdir(runs_dir):
            if fname.endswith(".json"):
                with open(os.path.join(runs_dir, fname), "r") as f:
                    data = json.load(f)
                    if data.get("outcome") == "fail":
                        failed_runs.append(data)
                        
    if not failed_runs:
        print("No failed runs found. Run demo/runner.py first.")
        return
        
    trace = failed_runs[0]
    print(f"Diagnosing a real failed run: {trace['run_id']}")
    print(f"Task: {trace['task_description']}")
    
    # Mocking the Span objects from the final_state messages
    spans = []
    for i, msg in enumerate(trace["final_state"]["messages"]):
        spans.append(type("SpanMock", (), {
            "id": str(i),
            "agent_role": "agent",
            "span_type": "llm_call",
            "output_content": msg,
            "input_content": ""
        }))
        
    prediction = await classifier.diagnose(
        trace["run_id"], 
        spans, 
        trace["task_description"], 
        trace["outcome"]
    )
    
    print("\n--- MAST DIAGNOSIS ---")
    print(f"Failure Category: {prediction['failure_category']}")
    print(f"Failure Mode:     {prediction['failure_mode']}")
    print(f"Confidence:       {prediction['confidence']}")
    print(f"Root Cause:       {prediction['root_cause']}")
    print(f"Suggested Fix:    {prediction['suggested_fix']}")
    print("----------------------")

if __name__ == "__main__":
    asyncio.run(validate_classifier())
