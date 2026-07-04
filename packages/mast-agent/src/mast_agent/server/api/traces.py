from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from mast_agent.server.database import get_session
from mast_agent.server.models import Span, Run

router = APIRouter()

@router.get("/runs")
async def get_runs(db: Session = Depends(get_session), limit: int = 50):
    runs = db.exec(select(Run).order_by(Run.started_at.desc()).limit(limit)).all()
    return runs

@router.get("/traces/{run_id}")
async def get_trace(run_id: str, db: Session = Depends(get_session)):
    """Reassemble all spans for a run into an ordered timeline."""
    run = db.get(Run, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
        
    spans = db.exec(
        select(Span).where(Span.run_id == run_id).order_by(Span.started_at)
    ).all()
    
    # Calculate per-agent summary
    agent_summary = {}
    for span in spans:
        role = span.agent_role or "system"
        if role not in agent_summary:
            agent_summary[role] = {"tokens": 0, "calls": 0, "latency_ms": 0.0}
        
        agent_summary[role]["calls"] += 1
        agent_summary[role]["tokens"] += (span.tokens_in + span.tokens_out)
        agent_summary[role]["latency_ms"] += span.latency_ms

    from mast_agent.server.models import Diagnosis
    diagnosis = db.exec(
        select(Diagnosis).where(Diagnosis.run_id == run_id).order_by(Diagnosis.diagnosed_at.desc())
    ).first()

    return {
        "run": run,
        "timeline": spans,
        "agent_summary": agent_summary,
        "diagnosis": diagnosis,
    }
