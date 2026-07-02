import time
import uuid
from typing import Any, Dict, List, Optional
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult

from mast_agent.sdk.tracer import MastTracer, tracer

class MastLangGraphHandler(BaseCallbackHandler):
    """
    Drop-in callback handler for auto-instrumenting LangGraph and LangChain.
    Captures chains, LLM calls, and outputs.
    """
    def __init__(self, run_id: Optional[str] = None, task_description: str = "LangGraph Task"):
        self.run_id = run_id or str(uuid.uuid4())
        self.task_description = task_description
        self.run_span_context = None
        self.current_agent_role = "system"

    def on_chain_start(
        self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any
    ) -> None:
        """Run when chain starts."""
        name = (serialized or {}).get("name", "unknown_chain")
        
        # Determine if this is a node in LangGraph (agent role)
        if "node" in name.lower() or name in ["planner", "coder", "reviewer"]:
            self.current_agent_role = name
            
        attributes = {
            "mast.run.id": self.run_id,
            "mast.span_type": "chain_execution",
            "mast.chain.name": name,
            "mast.agent.role": self.current_agent_role,
        }
        
        span = tracer.start_span(f"chain_{name}", attributes=attributes)
        kwargs["span"] = span

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        """Run when chain ends."""
        span = kwargs.get("span")
        if span:
            span.set_attribute("mast.output_content", str(outputs))
            span.end()

    def on_chain_error(self, error: Exception, **kwargs: Any) -> None:
        """Run when chain errors."""
        span = kwargs.get("span")
        if span:
            span.record_exception(error)
            span.set_attribute("mast.error", str(error))
            span.end()

    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        """Run when LLM starts running."""
        model = kwargs.get("invocation_params", {}).get("model", "unknown")
        # Store start info in kwargs or instance to use in on_llm_end
        kwargs["llm_start_time"] = time.time()
        kwargs["model_name"] = model
        kwargs["prompts"] = prompts

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Run when LLM ends running."""
        llm_start_time = kwargs.get("llm_start_time", time.time())
        latency_ms = (time.time() - llm_start_time) * 1000
        model = kwargs.get("model_name", "unknown")
        prompts = kwargs.get("prompts", [""])[0]
        
        llm_output = response.llm_output or {}
        token_usage = llm_output.get("token_usage", {})
        
        tokens_in = token_usage.get("prompt_tokens", 0)
        tokens_out = token_usage.get("completion_tokens", 0)
        
        generation_text = ""
        if response.generations and response.generations[0]:
            generation_text = response.generations[0][0].text
            
        MastTracer.record_llm_call(
            run_id=self.run_id,
            agent_id=f"{self.current_agent_role}_{uuid.uuid4().hex[:6]}",
            agent_role=self.current_agent_role,
            model=model,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            latency_ms=latency_ms,
            prompt=str(prompts),
            response=generation_text
        )

    def on_llm_error(self, error: Exception, **kwargs: Any) -> None:
        """Run when LLM errors."""
        pass # In a full implementation, we'd record an error span
