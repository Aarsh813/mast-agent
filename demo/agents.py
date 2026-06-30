import os
from typing import TypedDict, Literal
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field

# We use ChatGroq for fast/free dev testing, but you can swap to ChatOpenAI
# Make sure to `pip install langchain-groq` or `langchain-openai`
try:
    from langchain_groq import ChatGroq
except ImportError:
    ChatGroq = None

class AgentState(TypedDict):
    task: str
    plan: list[str]
    current_step: int
    code_attempts: dict[int, list[str]]  # step_index -> list of code strings
    reviews: dict[int, str]              # step_index -> reviewer feedback
    final_code: str
    status: Literal["planning", "coding", "reviewing", "done", "failed"]
    messages: list[BaseMessage]

# --- Output Parsers ---

class PlanOutput(BaseModel):
    steps: list[str] = Field(description="List of steps to accomplish the task")

class CodeOutput(BaseModel):
    code: str = Field(description="The python code implementation")

class ReviewOutput(BaseModel):
    approved: bool = Field(description="Whether the code is approved")
    feedback: str = Field(description="Feedback on the code")

# --- Agents ---

def get_llm(temperature=0.7):
    from mast_agent.diagnosis.llm_factory import LLMFactory
    provider = os.getenv("MAST_LLM_PROVIDER", "groq")
    model = os.getenv("MAST_LLM_MODEL", "llama-3.1-70b-versatile")
    return LLMFactory.create(provider, model, temperature=temperature)

def planner_node(state: AgentState) -> dict:
    llm = get_llm(temperature=0.7)
    sys_msg = SystemMessage(content="You are a planner. Break down the user's task into 1-3 high-level steps. Return ONLY valid JSON matching the schema.")
    human_msg = HumanMessage(content=f"Task: {state['task']}")
    
    # In a real app we'd use .with_structured_output(), doing it simply here:
    llm_with_struct = llm.with_structured_output(PlanOutput)
    response = llm_with_struct.invoke([sys_msg, human_msg])
    
    plan_steps = response.steps
    return {
        "plan": plan_steps,
        "current_step": 0,
        "status": "coding",
        "messages": [AIMessage(content=f"Plan created: {plan_steps}")]
    }

def coder_node(state: AgentState) -> dict:
    llm = get_llm(temperature=0.5)
    step_idx = state.get("current_step", 0)
    plan = state.get("plan", [])
    if step_idx >= len(plan):
        return {"status": "done"}
    
    current_step_desc = plan[step_idx]
    sys_msg = SystemMessage(content="You are a python coder. Write code for the given step. Keep it concise. Return ONLY valid JSON.")
    
    # Provide context of previous feedback if any
    feedback = state.get("reviews", {}).get(step_idx, "")
    feedback_text = f"\nPrevious feedback: {feedback}" if feedback else ""
    
    human_msg = HumanMessage(content=f"Overall Task: {state['task']}\nCurrent Step: {current_step_desc}{feedback_text}")
    
    llm_with_struct = llm.with_structured_output(CodeOutput)
    response = llm_with_struct.invoke([sys_msg, human_msg])
    
    code = response.code
    
    # Update attempts
    attempts = state.get("code_attempts", {})
    if step_idx not in attempts:
        attempts[step_idx] = []
    attempts[step_idx].append(code)
    
    return {
        "code_attempts": attempts,
        "status": "reviewing",
        "messages": [AIMessage(content=f"Code for step {step_idx}: {code}")]
    }

def reviewer_node(state: AgentState) -> dict:
    llm = get_llm(temperature=0.2)
    step_idx = state.get("current_step", 0)
    attempts = state.get("code_attempts", {}).get(step_idx, [])
    if not attempts:
        return {"status": "failed"} # Should not happen
        
    latest_code = attempts[-1]
    
    sys_msg = SystemMessage(content="You are a code reviewer. Review the code. If it loosely solves the step, approve it. If there are major issues, reject and provide feedback. Return ONLY valid JSON.")
    human_msg = HumanMessage(content=f"Task: {state['task']}\nStep: {state['plan'][step_idx]}\nCode:\n{latest_code}")
    
    llm_with_struct = llm.with_structured_output(ReviewOutput)
    response = llm_with_struct.invoke([sys_msg, human_msg])
    
    reviews = state.get("reviews", {})
    reviews[step_idx] = response.feedback
    
    if response.approved:
        # Move to next step
        next_step = step_idx + 1
        is_done = next_step >= len(state.get("plan", []))
        return {
            "reviews": reviews,
            "current_step": next_step,
            "status": "done" if is_done else "coding",
            "messages": [AIMessage(content=f"Review for step {step_idx}: Approved.")],
            "final_code": latest_code if is_done else state.get("final_code", "")
        }
    else:
        # Check for infinite loops (MAST SD-04: Step Repetition)
        if len(attempts) >= 3:
            return {
                "reviews": reviews,
                "status": "failed",
                "messages": [AIMessage(content=f"Review for step {step_idx}: Rejected 3 times. Failing.")]
            }
        return {
            "reviews": reviews,
            "status": "coding", # Go back to coder
            "messages": [AIMessage(content=f"Review for step {step_idx}: Rejected. Feedback: {response.feedback}")]
        }

# --- Graph Definition ---

def route_next(state: AgentState) -> str:
    return state["status"]

graph = StateGraph(AgentState)
graph.add_node("planner", planner_node)
graph.add_node("coder", coder_node)
graph.add_node("reviewer", reviewer_node)

graph.set_entry_point("planner")
graph.add_edge("planner", "coder")
graph.add_edge("coder", "reviewer")

graph.add_conditional_edges(
    "reviewer",
    route_next,
    {
        "coding": "coder",
        "done": END,
        "failed": END
    }
)

app = graph.compile()
