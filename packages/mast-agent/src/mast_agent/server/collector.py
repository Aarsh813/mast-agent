import json
from datetime import datetime
from fastapi import APIRouter, Depends, Request
from sqlmodel import Session
from mast_agent.server.database import get_session
from mast_agent.server.models import Span, Run

router = APIRouter()

@router.post("/v1/traces")
async def ingest_traces(request: Request, db: Session = Depends(get_session)):
    """
    Ingest OpenTelemetry traces exported via HTTP JSON (OTLP).
    Extracts custom MAST attributes and stores them.
    """
    content_type = request.headers.get("content-type", "")
    if "application/x-protobuf" in content_type:
        from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import ExportTraceServiceRequest
        from google.protobuf.json_format import MessageToDict
        raw_body = await request.body()
        req = ExportTraceServiceRequest.FromString(raw_body)
        body = MessageToDict(req)
    else:
        try:
            body = await request.json()
        except Exception:
            return {"error": "Invalid JSON"}

    resource_spans = body.get("resourceSpans", [])
    for rs in resource_spans:
        scope_spans = rs.get("scopeSpans", [])
        for ss in scope_spans:
            for otel_span in ss.get("spans", []):
                # Extract attributes
                attrs = {}
                for attr in otel_span.get("attributes", []):
                    key = attr.get("key")
                    # Handle different types of values (stringValue, intValue, etc)
                    val_dict = attr.get("value", {})
                    if "stringValue" in val_dict:
                        val = val_dict["stringValue"]
                    elif "intValue" in val_dict:
                        val = int(val_dict["intValue"])
                    elif "doubleValue" in val_dict:
                        val = float(val_dict["doubleValue"])
                    else:
                        val = str(val_dict)
                    attrs[key] = val

                run_id = attrs.get("mast.run.id", "unknown")
                span_id = otel_span.get("spanId", "unknown")
                
                # Check if Run exists, if not create a stub
                run = db.get(Run, run_id)
                if not run:
                    task = attrs.get("mast.run.task", "Unknown Task")
                    run = Run(id=run_id, task=task)
                    db.add(run)
                    db.commit()

                # Calculate latency
                start_time_unix_nano = int(otel_span.get("startTimeUnixNano", 0))
                end_time_unix_nano = int(otel_span.get("endTimeUnixNano", 0))
                
                start_dt = datetime.fromtimestamp(start_time_unix_nano / 1e9)
                end_dt = datetime.fromtimestamp(end_time_unix_nano / 1e9)
                latency_ms = (end_time_unix_nano - start_time_unix_nano) / 1e6
                
                span_type = attrs.get("mast.span_type", "unknown")
                
                span_record = Span(
                    id=span_id,
                    run_id=run_id,
                    parent_span_id=otel_span.get("parentSpanId"),
                    agent_id=attrs.get("mast.agent.id"),
                    agent_role=attrs.get("mast.agent.role"),
                    span_type=span_type,
                    model=attrs.get("gen_ai.request.model"),
                    input_content=attrs.get("mast.input_content"),
                    output_content=attrs.get("mast.output_content"),
                    tokens_in=attrs.get("gen_ai.usage.input_tokens", 0),
                    tokens_out=attrs.get("gen_ai.usage.output_tokens", 0),
                    latency_ms=latency_ms,
                    error=attrs.get("mast.error"),
                    started_at=start_dt,
                    ended_at=end_dt
                )
                
                # Update run stats
                if span_type == "llm_call":
                    run.total_tokens += span_record.tokens_in + span_record.tokens_out
                    run.total_latency_ms += latency_ms
                    # Simple cost estimate
                    cost_per_1k = 0.001 
                    run.total_cost_usd += (span_record.tokens_in + span_record.tokens_out) / 1000.0 * cost_per_1k
                
                db.add(span_record)
                db.commit()

    return {"status": "ok"}
