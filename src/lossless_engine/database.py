from __future__ import annotations

import os

from sqlalchemy import JSON, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./lossless-engine.db")
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


class PacketRecord(Base):
    __tablename__ = "packet_records"

    packet_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    packet_type: Mapped[str] = mapped_column(String(32), nullable=False)
    operation_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    parent_hash: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)


def initialize_database() -> None:
    Base.metadata.create_all(bind=engine)
