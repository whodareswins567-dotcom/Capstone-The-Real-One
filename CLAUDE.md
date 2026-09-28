# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A small inventory management system: static HTML/CSS/JS frontend served by a FastAPI backend backed by SQLite3. Supports listing (with search/low-stock filter), creating, editing, and deleting inventory items. The FastAPI app description itself notes this is a "Partially implemented inventory API with intentional gaps" — treat missing validation/features as potentially deliberate, not necessarily bugs to silently fix.

## Commands

Install dependencies and run the dev server:

```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

App: http://127.0.0.1:8000
Interactive API docs (Swagger): http://127.0.0.1:8000/docs

There is no test suite, linter, or build step configured in this repo.

## Architecture

Three-part flow: `Browser UI -> FastAPI REST API -> SQLite Database`.

- `backend/main.py` — FastAPI app. Defines all routes, mounts `frontend/` as static files at `/static`, and serves `frontend/index.html` at `/`. Route handlers open a raw `sqlite3` connection per request via `get_connection()` and build SQL inline (parameterized) rather than using an ORM.
- `backend/database.py` — SQLite connection factory (`get_connection`), schema creation (`init_db`, creates `inventory_items` table + an `updated_at` trigger), and dev seed data (`seed_db`). Both run at app startup via the `lifespan` context manager in `main.py`. DB file lives at `backend/inventory.db` (created on first run, not meant to be hand-edited).
- `backend/models.py` — Pydantic schemas: `InventoryItemBase`/`InventoryItemCreate` (full payload for creation), `InventoryItemUpdate` (all-optional fields, used with `model_dump(exclude_unset=True)` for PATCH), and `InventoryItem` (response shape, adds `id`, `created_at`, `updated_at`, `low_stock`).
- `frontend/` — Static, framework-free UI (`index.html`, `app.js`, `styles.css`). `app.js` talks directly to `/api/items` via `fetch`, holds an in-memory `items` array, and does full table re-renders on any change. No bundler/build step.

Key implementation details worth knowing before modifying:
- `low_stock` is not a DB column — it's computed on read in `main.map_item()` as `quantity <= reorder_level`.
- `sku` has a `UNIQUE` DB constraint; violations surface as HTTP 409 in both create and update handlers.
- PATCH builds its `UPDATE ... SET` clause dynamically from whichever fields were provided (`exclude_unset=True`), so partial updates only touch the fields sent.
- `updated_at` is refreshed by a SQL trigger (`set_inventory_updated_at`) on any row update, not by application code.

## Documentation

`doc/` contains hand-written design docs that are useful context but not auto-generated — check them for intent before large changes, and keep them in sync if you change API shape or architecture:
- `doc/architecture.md` — component responsibilities and data flow.
- `doc/api-reference.md` — endpoint list with example requests/responses.
- `doc/high-level-design.md`, `doc/low-level-design.md` — design notes.
- `doc/achievements-so-far.md`, `doc/confluence-*.md` — status/progress writeups (Confluence-oriented copies).
