from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

from .contracts import DesignPacket, NarrativePacket, packet_hash
from .database import PacketRecord, SessionLocal, initialize_database


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    yield


app = FastAPI(title="Lossless Engine", version="0.1.0", lifespan=lifespan)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/healthz")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/narrative-packets", status_code=status.HTTP_201_CREATED)
def create_narrative_packet(packet: NarrativePacket, db: Session = Depends(get_db)) -> dict[str, str]:
    value_hash = packet_hash(packet)
    existing = db.get(PacketRecord, value_hash)
    if existing is None:
        db.add(PacketRecord(
            packet_hash=value_hash,
            packet_type="narrative",
            operation_id=packet.operation_id,
            parent_hash=None,
            payload=packet.model_dump(mode="json"),
        ))
        db.commit()
    return {"packetHash": value_hash, "operationId": packet.operation_id}


@app.get("/v1/narrative-packets/{value_hash}")
def get_narrative_packet(value_hash: str, db: Session = Depends(get_db)) -> dict:
    record = db.get(PacketRecord, value_hash)
    if record is None or record.packet_type != "narrative":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NarrativePacket not found")
    return {"packetHash": record.packet_hash, "packet": record.payload}


@app.post("/v1/design-packets", status_code=status.HTTP_201_CREATED)
def create_design_packet(packet: DesignPacket, db: Session = Depends(get_db)) -> dict[str, str]:
    parent = db.get(PacketRecord, packet.narrative_packet_hash)
    if parent is None or parent.packet_type != "narrative":
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="NarrativePacket is unknown")
    narrative = NarrativePacket.model_validate(parent.payload)
    known_jobs = {job.id for job in narrative.slide_jobs}
    unknown_jobs = {slide.slide_job_id for slide in packet.slides} - known_jobs
    if unknown_jobs:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="DesignPacket references unknown slide jobs")
    value_hash = packet_hash(packet)
    if db.get(PacketRecord, value_hash) is None:
        db.add(PacketRecord(
            packet_hash=value_hash,
            packet_type="design",
            operation_id=narrative.operation_id,
            parent_hash=packet.narrative_packet_hash,
            payload=packet.model_dump(mode="json"),
        ))
        db.commit()
    return {"packetHash": value_hash, "narrativePacketHash": packet.narrative_packet_hash}


@app.get("/v1/design-packets/{value_hash}")
def get_design_packet(value_hash: str, db: Session = Depends(get_db)) -> dict:
    record = db.get(PacketRecord, value_hash)
    if record is None or record.packet_type != "design":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="DesignPacket not found")
    return {"packetHash": record.packet_hash, "narrativePacketHash": record.parent_hash, "packet": record.payload}
