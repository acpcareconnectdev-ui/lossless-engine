from fastapi.testclient import TestClient

from lossless_engine.api import app


def narrative_payload() -> dict:
    return {
        "operation_id": "operation-1",
        "source_evidence_hash": "a" * 64,
        "research_corpus_hash": "b" * 64,
        "primary_thesis": {"statement": "The company wins a costly workflow.", "evidence_ids": ["fact-1"]},
        "investment_case": {
            "company": "Example Co", "buyer_problem": "Manual work", "product_wedge": "Automation",
            "commercial_logic": "Subscription", "strongest_reason_to_invest": "Evidence-backed value",
            "strongest_reason_not_to_invest": "Limited proof", "decision_changing_proof": "Retention",
        },
        "slide_jobs": [{"id": "thesis", "investor_belief": "The workflow matters", "job": "Establish thesis", "evidence_ids": ["fact-1"]}],
    }


def design_payload(narrative_packet_hash: str) -> dict:
    return {
        "narrative_packet_hash": narrative_packet_hash,
        "style_selection": {"style_id": "editorial-bold", "style_revision_id": "style-1", "appearance": "light"},
        "direction_seed": "Editorial evidence-led investor deck.",
        "deck_visual_system": {
            "type_strategy": "Display thesis with readable body", "surface_strategy": "Tonal fields",
            "colour_roles": "One primary accent", "image_and_diagram_language": "Evidence diagrams",
            "rhythm": ["thesis", "proof", "close"],
        },
        "slides": [{"slide_job_id": "thesis", "dominant_composition": "typographic thesis", "focal_element": "claim", "visual_primitive": "statement", "background_treatment": "tonal", "evidence_ids": ["fact-1"]}],
    }


def test_packet_lineage_round_trip():
    with TestClient(app) as client:
        narrative = client.post("/v1/narrative-packets", json=narrative_payload())
        assert narrative.status_code == 201
        narrative_hash = narrative.json()["packetHash"]
        design = client.post("/v1/design-packets", json=design_payload(narrative_hash))
        assert design.status_code == 201
        assert design.json()["narrativePacketHash"] == narrative_hash


def test_design_packet_rejects_unknown_narrative():
    with TestClient(app) as client:
        response = client.post("/v1/design-packets", json=design_payload("c" * 64))
        assert response.status_code == 422
