from dataclasses import dataclass
from typing import Dict

@dataclass
class FailureMode:
    id: str
    name: str
    category: str
    description: str

MAST_TAXONOMY: Dict[str, FailureMode] = {
    # Category 1: Specification and System Design Issues
    "SD-01": FailureMode(
        "SD-01", "Unclear Role Definition", "Specification",
        "Agent is given a vague role and misinterprets its boundaries or responsibilities."
    ),
    "SD-02": FailureMode(
        "SD-02", "Unauthorized Decision-Making", "Specification",
        "Subordinate agents make executive choices they are not authorized or equipped to make."
    ),
    "SD-03": FailureMode(
        "SD-03", "Inadequate Planning", "Specification",
        "The system or planner agent fails to create a logical, step-by-step plan, resulting in missing or poorly ordered steps."
    ),
    "SD-04": FailureMode(
        "SD-04", "Step Repetition", "Specification",
        "The system enters an infinite loop, repeating completed steps and wasting resources without making progress."
    ),
    "SD-05": FailureMode(
        "SD-05", "Context/History Loss", "Specification",
        "Agents 'forget' previous context or experience unexpected conversation resets, leading to a loss of progress."
    ),
    # Category 2: Inter-Agent Misalignment
    "IA-01": FailureMode(
        "IA-01", "Communication Breakdown", "Inter-Agent Misalignment",
        "Agents fail to ask for necessary information or clarification, proceeding instead based on faulty assumptions."
    ),
    "IA-02": FailureMode(
        "IA-02", "Information Withholding", "Inter-Agent Misalignment",
        "An agent finds critical data but fails to communicate it to the rest of the team, causing downstream tasks to fail."
    ),
    "IA-03": FailureMode(
        "IA-03", "Reasoning Mismatch", "Inter-Agent Misalignment",
        "An agent's final action does not logically follow from its internal reasoning, resulting in inconsistent behavior."
    ),
    "IA-04": FailureMode(
        "IA-04", "Unintended Autonomy", "Inter-Agent Misalignment",
        "An agent goes rogue, pursuing its own inferred goals rather than the system's assigned task."
    ),
    "IA-05": FailureMode(
        "IA-05", "Conflicting Actions", "Inter-Agent Misalignment",
        "Two or more agents work at cross-purposes, overriding or sabotaging each other's work due to poor coordination."
    ),
    # Category 3: Task Verification and Termination
    "TV-01": FailureMode(
        "TV-01", "Superficial Verification", "Task Verification",
        "Verifier agents perform low-level, inadequate checks rather than evaluating whether output meets high-level requirements."
    ),
    "TV-02": FailureMode(
        "TV-02", "Premature Termination", "Task Verification",
        "The system declares the task done before all requirements are actually fulfilled."
    ),
    "TV-03": FailureMode(
        "TV-03", "Termination Unawareness", "Task Verification",
        "The system fails to recognize that the goal has been achieved, leading to unnecessary continuation."
    ),
    "TV-04": FailureMode(
        "TV-04", "Cascading Errors", "Task Verification",
        "One agent's mistake propagates unchecked through the rest of the agent chain, amplifying the failure."
    ),
}
