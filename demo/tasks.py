"""
Ambiguous tasks deliberately designed to trigger MAST failure modes:
- SD-01 (Unclear Role Definition)
- SD-03 (Inadequate Planning)
- IA-01 (Communication Breakdown)
- TV-01 (Superficial Verification)
- TV-02 (Premature Termination)
"""

TASKS = [
    {
        "id": "task_1",
        "description": "Build a function that validates user input.",
        # Ambiguity: What constitutes "valid"? What input format?
        # Expected failures: Premature Termination (TV-02), Unclear Role Definition (SD-01)
    },
    {
        "id": "task_2",
        "description": "Create a data pipeline that handles errors gracefully.",
        # Ambiguity: What data? Where is it coming from? What errors?
        # Expected failures: Inadequate Planning (SD-03), Reasoning Mismatch (IA-03)
    },
    {
        "id": "task_3",
        "description": "Write a caching system with an eviction policy.",
        # Ambiguity: Which eviction policy? LRU? LFU? Time-based? In-memory or Redis?
        # Expected failures: Conflicting Actions (IA-05), Superficial Verification (TV-01)
    },
    {
        "id": "task_4",
        "description": "Write a script to clean up messy data logs.",
        # Ambiguity: What format are the logs? What is considered messy?
        # Expected failures: Communication Breakdown (IA-01), Cascading Errors (TV-04)
    }
]
