import argparse
import uvicorn
import subprocess
import sys
import os
from dotenv import load_dotenv
load_dotenv()

def serve():
    print("Starting MAST Reviewer Agent Backend on http://localhost:8000")
    # In a real package, we would ensure the Next.js dashboard also starts, 
    # but for now we just start the FastAPI server.
    uvicorn.run("mast_agent.server.app:app", host="0.0.0.0", port=8000, reload=True)

def main():
    parser = argparse.ArgumentParser(description="MAST Reviewer Agent CLI")
    subparsers = parser.add_subparsers(dest="command")

    # serve command
    serve_parser = subparsers.add_parser("serve", help="Start the local backend server")

    # diagnose command
    diag_parser = subparsers.add_parser("diagnose", help="Diagnose a specific run")
    diag_parser.add_argument("--run-id", required=True, help="The ID of the run to diagnose")

    args = parser.parse_args()

    if args.command == "serve":
        serve()
    elif args.command == "diagnose":
        import asyncio
        from sqlmodel import Session, select
        from mast_agent.server.database import engine
        from mast_agent.server.models import Run, Span, Diagnosis
        from mast_agent.diagnosis.classifier import MASTClassifier
        
        async def run_diagnosis():
            print(f"Diagnosing run {args.run_id}...")
            with Session(engine) as session:
                run = session.get(Run, args.run_id)
                if not run:
                    print(f"Error: Run {args.run_id} not found.")
                    return
                
                spans = session.exec(select(Span).where(Span.run_id == args.run_id).order_by(Span.started_at)).all()
                if not spans:
                    print(f"Error: No spans found for run {args.run_id}.")
                    return
                
                classifier = MASTClassifier()
                try:
                    result = await classifier.diagnose(
                        run_id=run.id,
                        trace_spans=spans,
                        task=run.task,
                        outcome=run.outcome or run.status
                    )
                    
                    import json
                    print("\n--- Diagnosis Result ---")
                    print(json.dumps(result, indent=2))
                    
                    # Save to DB
                    import uuid
                    diagnosis_id = f"diag_{uuid.uuid4().hex[:8]}"
                    diag_record = Diagnosis(
                        id=diagnosis_id,
                        run_id=run.id,
                        failure_category=result.get("failure_category", "unknown"),
                        failure_mode=result.get("failure_mode", "unknown"),
                        confidence=result.get("confidence", 0.0),
                        root_cause=result.get("root_cause", ""),
                        suggested_fix=result.get("suggested_fix", ""),
                        evidence_span_ids=json.dumps(result.get("evidence_span_ids", []))
                    )
                    session.add(diag_record)
                    session.commit()
                    print("\nDiagnosis saved to database successfully.")
                except Exception as e:
                    print(f"\nError running diagnosis: {e}")
                    
        asyncio.run(run_diagnosis())
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
