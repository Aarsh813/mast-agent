import functools
from mast_agent.sdk.tracer import tracer
import uuid

def trace_agent(role: str = "agent"):
    """Decorator to manually trace an agent's execution."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Try to extract run_id from kwargs, or generate one
            run_id = kwargs.get("run_id", str(uuid.uuid4()))
            attributes = {
                "mast.run.id": run_id,
                "mast.agent.role": role,
                "mast.span_type": "agent_execution",
                "mast.agent.name": func.__name__,
            }
            with tracer.start_as_current_span(f"agent_{func.__name__}", attributes=attributes) as span:
                try:
                    result = func(*args, **kwargs)
                    span.set_attribute("mast.output_content", str(result))
                    return result
                except Exception as e:
                    span.record_exception(e)
                    span.set_attribute("mast.error", str(e))
                    raise
        return wrapper
    return decorator

def trace_tool(name: str):
    """Decorator to manually trace a tool execution."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            run_id = kwargs.get("run_id", "unknown")
            attributes = {
                "mast.run.id": run_id,
                "mast.span_type": "tool_call",
                "mast.tool.name": name,
                "mast.input_content": str(args) + str(kwargs),
            }
            with tracer.start_as_current_span(f"tool_{name}", attributes=attributes) as span:
                try:
                    result = func(*args, **kwargs)
                    span.set_attribute("mast.output_content", str(result))
                    return result
                except Exception as e:
                    span.record_exception(e)
                    span.set_attribute("mast.error", str(e))
                    raise
        return wrapper
    return decorator
