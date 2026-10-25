from __future__ import annotations

from hashlib import sha256
import json

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Thesis(StrictModel):
    statement: str = Field(min_length=1)
    evidence_ids: list[str] = Field(min_length=1)
    qualifications: list[str] = Field(default_factory=list)


class InvestmentCase(StrictModel):
    company: str = Field(min_length=1)
    buyer_problem: str = Field(min_length=1)
    product_wedge: str = Field(min_length=1)
    commercial_logic: str = Field(min_length=1)
    strongest_reason_to_invest: str = Field(min_length=1)
    strongest_reason_not_to_invest: str = Field(min_length=1)
    decision_changing_proof: str = Field(min_length=1)


class SlideJob(StrictModel):
    id: str = Field(min_length=1)
    investor_belief: str = Field(min_length=1)
    job: str = Field(min_length=1)
    evidence_ids: list[str] = Field(default_factory=list)
    citation_ids: list[str] = Field(default_factory=list)
    required_qualifications: list[str] = Field(default_factory=list)
    missing_proof: list[str] = Field(default_factory=list)


class NarrativePacket(StrictModel):
    schema_version: str = "deck-narrative-packet.v1"
    operation_id: str = Field(min_length=1)
    source_evidence_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    research_corpus_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    primary_thesis: Thesis
    investment_case: InvestmentCase
    slide_jobs: list[SlideJob] = Field(min_length=1)
    private_diligence: list[str] = Field(default_factory=list)
    omissions: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def unique_slide_jobs(self) -> "NarrativePacket":
        if len({job.id for job in self.slide_jobs}) != len(self.slide_jobs):
            raise ValueError("slide_jobs must have unique IDs")
        return self


class StyleSelection(StrictModel):
    style_id: str = Field(min_length=1)
    style_revision_id: str = Field(min_length=1)
    appearance: str = Field(min_length=1)


class DeckVisualSystem(StrictModel):
    type_strategy: str = Field(min_length=1)
    surface_strategy: str = Field(min_length=1)
    colour_roles: str = Field(min_length=1)
    image_and_diagram_language: str = Field(min_length=1)
    rhythm: list[str] = Field(min_length=1)


class SlideDesign(StrictModel):
    slide_job_id: str = Field(min_length=1)
    dominant_composition: str = Field(min_length=1)
    focal_element: str = Field(min_length=1)
    visual_primitive: str = Field(min_length=1)
    background_treatment: str = Field(min_length=1)
    asset_ids: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    required_qualifications: list[str] = Field(default_factory=list)


class DesignPacket(StrictModel):
    schema_version: str = "deck-design-packet.v1"
    narrative_packet_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    style_selection: StyleSelection
    direction_seed: str = Field(min_length=1)
    deck_visual_system: DeckVisualSystem
    slides: list[SlideDesign] = Field(min_length=1)

    @model_validator(mode="after")
    def unique_slide_designs(self) -> "DesignPacket":
        if len({slide.slide_job_id for slide in self.slides}) != len(self.slides):
            raise ValueError("slides must have unique slide_job_id values")
        return self


def packet_hash(packet: StrictModel) -> str:
    payload = packet.model_dump(mode="json", by_alias=True, exclude_none=True)
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return sha256(encoded).hexdigest()
