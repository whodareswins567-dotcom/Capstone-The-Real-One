# Inventory Management System

## Summary

This project is an inventory management system using FastAPI, SQLite3, and plain HTML/CSS/JavaScript. It supports basic inventory item management.

## Current Scope

- Add inventory items.
- View inventory items.
- Search inventory by SKU, name, or category.
- Filter low-stock inventory.
- Edit item details.
- Delete inventory items.

## Technical Stack

- Frontend: HTML, CSS, JavaScript.
- Backend: FastAPI.
- Database: SQLite3.
- API style: REST.

## Architecture

```text
Browser UI -> FastAPI REST API -> SQLite Database
```

FastAPI serves both the REST API and the static frontend. SQLite is used as a lightweight local database for the initial phase.

## Important Files

- `backend/main.py`: API routes and frontend serving.
- `backend/database.py`: database setup and seed data.
- `backend/models.py`: request and response models.
- `frontend/index.html`: UI page.
- `frontend/styles.css`: UI styling.
- `frontend/app.js`: frontend behavior and API calls.
- `doc/`: documentation.
- `plan/`: build notes and verification plan.
