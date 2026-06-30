# MAST Reviewer Agent

Diagnose why your multi-agent LLM system failed — using the MAST taxonomy, backed by UC Berkeley research.

**"Agrees with expert human annotation >70% of the time."**

## What is this?
Building multi-agent systems is hard. They loop, they hallucinate, they fail to communicate. MAST (Multi-Agent Systems Failure Taxonomy) is a framework identifying 14 specific failure modes. 

`mast-agent` provides:
1. **SDK**: One-line OpenTelemetry auto-instrumentation for LangGraph.
2. **Diagnosis Engine**: Automatically classifies failed runs into one of the 14 MAST categories using an LLM.
3. **Dashboard**: Local visualization of traces, agent communication timelines, and failure clusters.

## Quickstart

```bash
pip install mast-agent
```

Wrap your LangGraph application:
```python
from mast_agent import MastLangGraphHandler

# 1. Initialize handler
mast_handler = MastLangGraphHandler()

# 2. Pass to your graph invoke
result = graph.invoke(
    {"task": "Build a data pipeline"},
    config={"callbacks": [mast_handler]}
)
```

Launch the dashboard:
```bash
mast serve
```
Open `http://localhost:3000` to view your execution traces and diagnoses.
