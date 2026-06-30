from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from mast_agent.server.database import init_db
from mast_agent.server.collector import router as collector_router
from mast_agent.server.api.traces import router as traces_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    yield
    # Shutdown

app = FastAPI(title="MAST Reviewer Agent API", lifespan=lifespan)

# Allow dashboard to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(collector_router, tags=["collector"])
app.include_router(traces_router, prefix="/api/v1", tags=["traces"])

@app.get("/health")
async def health_check():
    return {"status": "ok"}
