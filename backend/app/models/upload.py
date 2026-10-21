from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, Integer, String

from app.core.database import Base


def _utcnow():
    return datetime.now(UTC)


class Upload(Base):
    __tablename__ = "uploads"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    created_at = Column(DateTime, default=_utcnow)
