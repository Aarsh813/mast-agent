import os
from typing import Any, Dict, Optional
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor

def get_tracer():
    # Setup OpenTelemetry Tracer
    resource = Resource.create({"service.name": "mast-reviewer"})
    provider = TracerProvider(resource=resource)
    
    # Configure the OTLP exporter to send to our FastAPI collector
    # Defaults to localhost:8000/v1/traces
    endpoint = os.getenv("MAST_COLLECTOR_URL", "http://localhost:8000/v1/traces")
    otlp_exporter = OTLPSpanExporter(endpoint=endpoint)
    
    processor = BatchSpanProcessor(otlp_exporter)
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    
    return trace.get_tracer("mast-agent")

tracer = get_tracer()

class MastTracer:
    """Thin wrapper over OTel that enforces MAST-specific span attributes."""
    
    @staticmethod
    def start_run(task: str, run_id: str, metadata: Optional[Dict[str, Any]] = None):
        """Begin a new traced run."""
        attributes = {
            "mast.run.id": run_id,
            "mast.run.task": task,
            "mast.span_type": "mast_run",
        }
        if metadata:
            for k, v in metadata.items():
                attributes[f"mast.run.metadata.{k}"] = str(v)
        return tracer.start_span("mast_run", attributes=attributes)
        
    @staticmethod
    def record_llm_call(
        run_id: str,
        agent_id: str,
        agent_role: str,
        model: str,
        tokens_in: int,
        tokens_out: int,
        latency_ms: float,
        prompt: str = "",
        response: str = ""
    ):
        """Record a single LLM invocation as an OTel span."""
        attributes = {
            "mast.run.id": run_id,
            "mast.agent.id": agent_id,
            "mast.agent.role": agent_role,
            "mast.span_type": "llm_call",
            "gen_ai.request.model": model,
            "gen_ai.usage.input_tokens": tokens_in,
            "gen_ai.usage.output_tokens": tokens_out,
            "mast.latency_ms": latency_ms,
            "mast.input_content": prompt,
            "mast.output_content": response
        }
        with tracer.start_as_current_span("llm_call", attributes=attributes):
            pass

    @staticmethod
    def record_agent_message(
        run_id: str,
        from_agent: str,
        to_agent: str,
        content: str,
        message_type: str = "handoff"
    ):
        """Record inter-agent communication."""
        attributes = {
            "mast.run.id": run_id,
            "mast.span_type": "agent_message",
            "mast.message.from": from_agent,
            "mast.message.to": to_agent,
            "mast.message.type": message_type,
            "mast.input_content": content,
        }
        with tracer.start_as_current_span("agent_message", attributes=attributes):
            pass
