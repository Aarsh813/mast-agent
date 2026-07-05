import logging
import time
import uuid
import os

log_dir = os.path.join(os.getcwd(), "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "sdk.log")

file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    logger.addHandler(file_handler)

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
        self.chain_spans = {}
        self.llm_runs = {}

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
        
        logger.debug(f"Starting chain span '{name}' with attributes: {attributes}")
        
        span = tracer.start_span(f"chain_{name}", attributes=attributes)
        run_id = kwargs.get("run_id")
        if run_id:
            self.chain_spans[run_id] = span

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        """Run when chain ends."""
        run_id = kwargs.get("run_id")
        span = self.chain_spans.pop(run_id, None)
        if span:
            span.set_attribute("mast.output_content", str(outputs))
            span.end()
            logger.debug(f"Ended chain span for run_id {run_id} with outputs: {outputs}")

    def on_chain_error(self, error: Exception, **kwargs: Any) -> None:
        """Run when chain errors."""
        run_id = kwargs.get("run_id")
        span = self.chain_spans.pop(run_id, None)
        if span:
            span.record_exception(error)
            span.set_attribute("mast.error", str(error))
            span.end()

    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        """Run when LLM starts running."""
        model = kwargs.get("invocation_params", {}).get("model", "unknown")
        if model == "unknown" and "invocation_params" in kwargs and "model_name" in kwargs["invocation_params"]:
            model = kwargs["invocation_params"]["model_name"]
            
        run_id = kwargs.get("run_id")
        self.llm_runs[run_id] = {
            "llm_start_time": time.time(),
            "model_name": model,
            "prompts": prompts
        }
        logger.info(f"Starting LLM call for model {model} (run_id: {run_id})")
        logger.debug(f"LLM Prompts: {prompts}")

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Run when LLM ends running."""
        run_id = kwargs.get("run_id")
        llm_run = self.llm_runs.pop(run_id, {})
        
        llm_start_time = llm_run.get("llm_start_time", time.time())
        latency_ms = (time.time() - llm_start_time) * 1000
        model = llm_run.get("model_name", "unknown")
        prompts = llm_run.get("prompts", [""])[0]
        
        llm_output = response.llm_output or {}
        token_usage = llm_output.get("token_usage", {})
        
        tokens_in = token_usage.get("prompt_tokens", 0)
        tokens_out = token_usage.get("completion_tokens", 0)
        
        generation_text = ""
        if response.generations and response.generations[0]:
            generation = response.generations[0][0]
            if hasattr(generation, "message") and hasattr(generation.message, "content"):
                if isinstance(generation.message.content, str):
                    generation_text = generation.message.content
                else:
                    generation_text = str(generation.message.content)
            else:
                generation_text = generation.text
            
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
        logger.info(f"Ended LLM call for model {model} (Latency: {latency_ms:.2f}ms, Tokens: {tokens_in} in / {tokens_out} out)")
        logger.debug(f"LLM Response: {generation_text}")

    def on_llm_error(self, error: Exception, **kwargs: Any) -> None:
        """Run when LLM errors."""
        run_id = kwargs.get("run_id")
        self.llm_runs.pop(run_id, None)
