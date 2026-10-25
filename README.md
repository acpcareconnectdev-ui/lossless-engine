# Lossless Engine

Lossless Engine is the API contract layer between MemoPop-quality investment
narrative and DidiDecks-quality deck redesign. It is not a copy of either
runtime and does not render decks or conduct research itself.

```text
MemoPop / LangGraph -> NarrativePacket -> Lossless Engine -> DesignPacket -> Deck runtime
```

## Responsibilities

- validate and version NarrativePacket and DesignPacket handoffs;
- preserve packet hashes, operation identity, and packet lineage;
- reject a DesignPacket whose referenced NarrativePacket is unknown or changed;
- provide a narrow API for a MemoPop adapter and a Deck adapter;
- keep private diligence references internal to packet metadata.

## Non-responsibilities

- no copied MemoPop LangGraph runtime;
- no copied DidiDecks UI or Astro routes;
- no deck rendering, publication, export, provider credentials, or browser-side
  OpenAI calls;
- no customer source material, raw research corpus, or firm-private data.

## Local development

```bash
python -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
DATABASE_URL=sqlite:///./lossless-engine.db .venv/bin/uvicorn lossless_engine.api:app --reload
```

Run tests:

```bash
.venv/bin/python -m pytest
```

## Railway deployment

Deploy this repository as one service with a Railway Postgres service. Set:

```text
DATABASE_URL=${{Postgres.DATABASE_URL}}
MEMOPOP_API_URL=<private MemoPop service URL, when deployed>
DECK_API_URL=<private Deck service URL, when deployed>
```

MemoPop and Deck remain separate Railway services. The engine stores only typed
packet projections and references; it does not proxy raw customer data between
services by default. See `docs/railway-architecture.md`.

See `docs/repository-deployment-plan.md` for the repository inventory and the
safe staged rollout into the existing Deck Railway project.
