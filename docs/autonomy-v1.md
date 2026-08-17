# OED Autonomous Mode v1

## Objective

Continuously maximize useful public coverage of the Dominican State with the least possible human intervention. The operating priority is:

1. Poder Ejecutivo
2. Poder Legislativo
3. Poder Judicial

The system publishes useful basic coverage as soon as a traceable source exists, then improves depth and accuracy iteratively.

## Permanent mission

> Maximizar continuamente la cobertura publica verificable del Estado dominicano, priorizando Poder Ejecutivo, Poder Legislativo y Poder Judicial. Publicar cobertura basica util tan pronto exista una fuente trazable y mejorarla iterativamente.

## Operating loop

`inspect state -> measure coverage -> choose branch -> research -> structure -> write -> publish -> audit -> repeat`

The Director must not stop because one backlog is finished. It re-evaluates coverage and creates the next batch of work.

## Roles

### Director
- Reads the current OED state.
- Uses `python -m app.modules.autonomy` or the public coverage endpoint to measure progress.
- Prioritizes the next State branch.
- Creates the next work batch and continues after completion.

### Researcher
- Finds official and reputable public sources.
- Extracts institutions, authorities, legal bases, structures, payroll, budget, procurement and other available public facts.
- Always preserves source URL and retrieval context.

### Builder / Data Engineer
- Normalizes and writes data into the existing OED domain model.
- Uses actor type `autonomy` while autonomous mode is enabled.
- Creates or improves parsers and connectors when needed.
- Publishes partial but useful coverage instead of waiting for perfect completeness.

### Auditor
- Runs after publication rather than blocking normal progress.
- Detects stale authorities, duplicates, weak sources, classification errors and contradictions.
- Improves or versions records; it does not silently erase history.

## Minimal non-blocking controls

Autonomy v1 deliberately keeps controls small. These remain mandatory because they do not materially slow coverage:

- Preserve a source/evidence link for published facts.
- Preserve historical changes instead of silently deleting or overwriting history.
- Keep a project/model spending cap outside the data model.
- Do not automatically publish accusations of corruption, fraud, crimes, guilt or intent.
- Use Git history for code changes so a bad autonomous code change can be reverted.

## Enabling autonomy

Set:

```env
AUTONOMY_MODE_ENABLED=true
AUTONOMY_TARGET_BASIC_COVERAGE=0.80
```

Autonomous writers use `actor_type=autonomy`. `app.modules.autonomy.runtime.activate_autonomy_session()` sets the PostgreSQL transaction actor accordingly.

## Coverage endpoints

The public API adds:

- `GET /api/v1/public/state/coverage`
- `GET /api/v1/public/state/institutions?branch=executive`
- `GET /api/v1/public/state/institutions?branch=legislative`
- `GET /api/v1/public/state/institutions?branch=judicial`

The frontend exposes the three powers from the home page. Legislative and Judicial directories can show records immediately as the autonomous system adds them.

## Deployment boundary

This repository contains the OED-side autonomy contract. The external AI Company supervisor on the VPS remains responsible for LLM execution, task queues, budgets, retries and tool orchestration. It should call this OED layer using the `autonomy` actor and use the coverage result to decide what to do next.
