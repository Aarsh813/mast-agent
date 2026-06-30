import os
from sqlmodel import create_engine, SQLModel, Session

# Use SQLite for development
DATABASE_URL = os.getenv("MAST_DATABASE_URL", "sqlite:///./mast.db")

engine = create_engine(DATABASE_URL, echo=False)

def init_db():
    from mast_agent.server.models import Run, Span, Diagnosis, Cluster
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
