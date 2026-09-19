"""Session factory. Owner: Person A."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.config import settings


database_url = settings().database_url.replace(
    "postgresql://", "postgresql+psycopg://", 1
)
engine = create_engine(database_url, connect_args={"options": "-c timezone=UTC"})
SessionLocal = sessionmaker(bind=engine)
