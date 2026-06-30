# Multi-Agent Systems Failure Taxonomy (MAST)

Based on the research paper "Why Do Multi-Agent LLM Systems Fail?" (Cemri et al.), the MAST framework categorizes multi-agent system (MAS) failures into 14 distinct modes across 3 core categories.

## Category 1: Specification and System Design Issues (~41.8% of failures)
These failures stem from architectural flaws, where the system design fails to provide clear guidance or constraints to the agents.

1. **Unclear Role Definition (SD-01):** An agent is given a vague role and misinterprets its boundaries or responsibilities.
2. **Unauthorized Decision-Making (SD-02):** Subordinate agents make executive choices they are not authorized or equipped to make.
3. **Inadequate Planning (SD-03):** The system or a planner agent fails to create a logical, step-by-step plan, resulting in missing or poorly ordered steps.
4. **Step Repetition (SD-04):** The system enters an infinite loop, repeating completed steps and wasting resources without making progress.
5. **Context/History Loss (SD-05):** Agents "forget" previous context or experience unexpected "conversation resets," leading to a loss of progress and forced restarts.

## Category 2: Inter-Agent Misalignment (~36.9% of failures)
These failures occur during interactions between agents, often resulting from a lack of structured communication protocols.

6. **Communication Breakdown (IA-01):** Agents fail to ask for necessary information or clarification, proceeding instead based on faulty assumptions.
7. **Information Withholding (IA-02):** An agent finds critical data (e.g., an API credential or key fact) but fails to communicate it to the rest of the team, causing downstream tasks to fail.
8. **Reasoning Mismatch (IA-03):** An agent’s final action does not logically follow from its internal reasoning, resulting in inconsistent or unpredictable behavior.
9. **Unintended Autonomy (IA-04):** An agent goes rogue, pursuing its own inferred goals rather than the system's assigned task.
10. **Conflicting Actions (IA-05):** Two or more agents work at cross-purposes, overriding or sabotaging each other's work due to poor coordination.

## Category 3: Task Verification and Termination (~21.3% of failures)
These failures are related to how the system validates results or recognizes when a task is completed.

11. **Superficial Verification (TV-01):** Verifier agents perform low-level, inadequate checks (e.g., only checking if code compiles or looks plausible) rather than evaluating whether the output meets high-level requirements.
12. **Premature Termination (TV-02):** The system declares the task done before all requirements are actually fulfilled.
13. **Termination Unawareness (TV-03):** The system fails to recognize that the goal has been achieved, leading to unnecessary continuation or "over-engineering."
14. **Cascading Errors (TV-04):** One agent's mistake propagates unchecked through the rest of the agent chain, amplifying the failure.
