# Repository and Railway Deployment Plan

## Goal

Connect MemoPop-quality VC narrative to the existing Deck runtime through the
Lossless Engine packet API. This is a staged deployment plan. It does not
replace, merge, or redeploy any current working service until its replacement or
adapter is proven.

## Repository inventory

| Repository or local source | Product responsibility | Deploy to Railway? | Deployment role |
| --- | --- | --- | --- |
| `acpcareconnectdev-ui/lossless-engine` | Versioned NarrativePacket/DesignPacket validation and lineage gateway. | Yes | New `lossless-engine` API service. |
| `lossless-group/investment-memo-orchestrator` | MemoPop research, LangGraph analysis, VC narrative, source and citation discipline. | Yes | `memopop-narrative` API/worker service. |
| `acpcareconnectdev-ui/deck-v-4-` | Existing Deck API, workers, rendering, Chromium proof, publication, export, Smart Deck, Smart Edit, Due Diligence. | Already deployed | Keep as the existing Deck runtime. Do not duplicate it. |
| `dididecks-ai-development` | Whole-deck design direction, composition, clean-room variant, and browser-review contracts. | No | Checked-in source/reference contracts consumed by Deck prompts and tests. |
| `instant-deck-migration-kit` | Portable integration, narrative, design, surface, and intelligence contracts. | No | Checked-in source/reference contracts. |
| `deck-v4-pipeline-package (2)` | Static snapshot of pipeline handovers and prompt assembly. | No | Inspection/reference package only. |
| `apps/memopop-native` and `apps/memopop-site` | Desktop and marketing clients. | Not for this engine phase | Optional clients after narrative API and Deck integration are proven. |

## Current Railway state

| Railway project | Workspace | Region | Relevant services | Decision |
| --- | --- | --- | --- | --- |
| `deck-v2-personal-test` | Phoenix Capera's Projects | us-west2 | `deck-api`, Deck workers, renderer, Postgres, Redis, deck frontend | Use as the initial integration environment. Freeze its existing services. |
| `memopop` | The Lossless Group | us-east4-eqdc4 | `connector` from `lossless-group/investment-memo-orchestrator` | Existing MemoPop deployment is a reference. It is not on the same private network as the Deck project. |
| `deck-v5` | Phoenix Capera's Projects | us-west2 | separate deck service | Out of scope for the first integration. |

Railway private networking is scoped to the project environment. The current
MemoPop service cannot call `deck-api.railway.internal`, and Deck cannot call
`connector.railway.internal`, because they are in different projects and
workspaces. The first integration must deploy a compatible MemoPop narrative
service into the Deck project or use a deliberately authenticated public bridge.
The recommended first path is the same-project service.

## Target topology

```text
deck-v2-personal-test / production
  Postgres                  existing Deck database; do not alter schema ownership
  Redis                     existing Deck worker broker; do not alter queues
  deck-api + workers        existing runtime; frozen baseline
  lossless-engine           new packet gateway
  engine-postgres           new database owned only by lossless-engine
  memopop-narrative         new MemoPop API/worker deployment for packet generation

memopop-narrative -> lossless-engine -> deck-api
```

Use a separate `engine-postgres` database. Do not let the new gateway write into
the Deck database until a deliberate schema and ownership review says otherwise.

## Deployment phases

### Phase 0: Freeze and baseline

- Record the exact successful deployment IDs, source commits, variables names,
  service configuration, and health of the existing Deck services.
- Run the Deck source, generation, render-proof, publication, reload, and export
  checks that currently pass.
- Do not change graph stages, trigger conditions, worker commands, Redis queues,
  provider budgets, or the production Deck database.

### Phase 1: Deploy Lossless Engine only

- Push the local `lossless-engine` scaffold to
  `acpcareconnectdev-ui/lossless-engine`.
- Create `engine-postgres` and `lossless-engine` in `deck-v2-personal-test`.
- Set `DATABASE_URL` on the engine from `engine-postgres`.
- Generate a Railway private domain for the engine.
- Verify `/healthz`, NarrativePacket persistence, DesignPacket lineage rejection,
  and restart durability. No Deck calls occur in this phase.

### Phase 2: Deploy MemoPop narrative service beside Deck

- Attach `lossless-group/investment-memo-orchestrator` at its approved branch to
  a new `memopop-narrative` service in the same project/environment.
- Give it its own data volume or object storage only for explicitly approved
  test/owned data. Do not copy the existing `memopop-data` volume or private
  firm buckets into the Phoenix project.
- Add an engine URL and service-to-service authentication secret by reference.
- Expose only a narrow packet-generation endpoint. The adapter emits a
  NarrativePacket; it does not expose private corpus files or raw firm data.
- Test an owned/synthetic deck through MemoPop to Lossless Engine. Do not connect
  it to Deck generation yet.

### Phase 3: Add a Deck feature-gated adapter

- Add a new-operation-only, disabled-by-default integration flag in Deck.
- At an existing narrative handoff, Deck reads a NarrativePacket hash from the
  engine and writes the packet reference into its existing working document or
  checkpoint boundary.
- Deck emits a DesignPacket through the existing design handoff and binds its
  hash to the candidate/proof lineage.
- Keep existing Deck behavior as fallback when the flag is off or packet assembly
  fails. Never change historical operations.

### Phase 4: Prove one end-to-end owned deck

- MemoPop emits the NarrativePacket with evidence/citation bindings.
- Lossless Engine validates and persists it.
- Deck generates a DesignPacket, candidate, browser proof, and immutable
  DesignVersion using its existing workflow.
- Verify exact preview reload and exact-version export.
- Human-review narrative quality against MemoPop rules and design quality against
  DidiDecks rules. Technical success alone is not acceptance.

### Phase 5: Expand interactive surfaces

- Configure the workspace-owned OpenAI key flow.
- Test Smart Deck chat, Smart Edit candidate review, Due Diligence chat, warning
  ledger, research admission, and embedding evaluation per
  `instant-deck-migration-kit/14-INTERACTIVE-AI-SURFACE-CONTRACT.md` and
  `15-PRODUCT-INTELLIGENCE-CONTRACT.md`.
- Do not expose these flows to shared customer data before their durable-state,
  reload, authorization, and key-handling tests pass.

## Service variables

Use Railway service references rather than copying credentials into repositories:

```text
lossless-engine
  DATABASE_URL=${{engine-postgres.DATABASE_URL}}
  MEMOPOP_API_URL=http://memopop-narrative.railway.internal
  DECK_API_URL=http://deck-api.railway.internal
  SERVICE_AUTH_TOKEN=<Railway secret>

memopop-narrative
  LOSSLESS_ENGINE_URL=http://lossless-engine.railway.internal
  SERVICE_AUTH_TOKEN=<same or dedicated Railway secret>

deck-api
  LOSSLESS_ENGINE_URL=http://lossless-engine.railway.internal
  SERVICE_AUTH_TOKEN=<dedicated Railway secret>
  NARRATIVE_DESIGN_PACKET_INTEGRATION=false
```

Never commit token values, user OpenAI keys, private source files, customer
uploads, MemoPop firm directories, or bucket credentials.

## Before any Railway mutation

1. Confirm the exact MemoPop GitHub repository branch and its Railway start
   command/API entrypoint.
2. Push `lossless-engine` to GitHub.
3. Confirm that `deck-v2-personal-test` is the intended integration project,
   not a production customer environment.
4. Confirm that creating `engine-postgres` and `memopop-narrative` in that
   project is approved.
5. Review the staged Railway changes before deployment.
