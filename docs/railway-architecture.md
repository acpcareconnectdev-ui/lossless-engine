# Railway Architecture

Deploy three independent services in one Railway project:

```text
memopop-api       LangGraph narrative service
lossless-engine   packet validation and lineage gateway
deck-api          design, render, proof, publication, and export service
postgres          shared or independently owned persistence, by explicit schema boundary
redis             optional durable-job broker for the services that already require it
```

## Private API flow

1. MemoPop completes its existing narrative stages and POSTs a NarrativePacket to
   `lossless-engine.railway.internal`.
2. The engine persists the validated packet and returns its content hash.
3. The Deck service receives that hash, resolves the packet through the engine,
   creates a DesignPacket through its existing design handoff, and POSTs it back.
4. The Deck service renders and publishes only the candidate bound to that
   DesignPacket hash.

## Required variables

```text
lossless-engine
  DATABASE_URL=${{Postgres.DATABASE_URL}}
  MEMOPOP_API_URL=http://memopop-api.railway.internal
  DECK_API_URL=http://deck-api.railway.internal

memopop-api
  LOSSLESS_ENGINE_URL=http://lossless-engine.railway.internal

deck-api
  LOSSLESS_ENGINE_URL=http://lossless-engine.railway.internal
```

Use service-to-service authentication before accepting packets from another
service. Never pass user OpenAI keys, raw customer uploads, full research
corpora, or private firm content through this gateway.
