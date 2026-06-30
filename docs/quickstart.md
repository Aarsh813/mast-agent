# Quickstart Guide

This guide will help you set up and run the MAST Reviewer Agent demo.

## 1. Environment Setup

Copy `.env.example` to `.env` and fill in your API keys:
```bash
cp .env.example .env
```
Provide an API key for your preferred LLM. For testing, a Groq API key is recommended since it is fast and free.

## 2. Install Dependencies

We recommend setting up a virtual environment:
```bash
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate
```

Install the project dependencies (editable mode):
```bash
pip install -e packages/mast-agent
pip install langchain-groq langchain-openai httpx
```

## 3. Run the Demo Agents

The demo simulates a 3-agent system (Planner, Coder, Reviewer) and is designed to deliberately trigger failures.

```bash
python demo/runner.py
```
This will generate execution traces and save them in `demo/saved_runs/`.

## 4. Run the Dashboard

```bash
mast serve
```
The FastAPI backend will start on `http://localhost:8000` and you can run the Next.js frontend in the `dashboard` directory:

```bash
cd dashboard
npm run dev
```

Navigate to `http://localhost:3000` to explore the dashboard.
