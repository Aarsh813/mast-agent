import argparse
import uvicorn
import subprocess
import sys
import os

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
        print(f"Diagnosing run {args.run_id}...")
        # Implementation would call MASTClassifier
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
