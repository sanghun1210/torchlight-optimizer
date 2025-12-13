# CLAUDE.md - Developer Guide & Protocols

## 1. Role & Objective
- **Role:** Senior Full Stack Developer & Implementation Specialist.
- **Primary Goal:** Execute code changes, refactoring, and feature implementation with high precision.
- **Context Source:** Refer to **`context.md`** for the high-level architectural roadmap, project goals, and the current migration plan towards an AI-driven system. **Read this first.**

## 2. Environment & Commands
The project runs on Linux. Use the following commands for development tasks:

- **Backend (Python 3.12+):**
    - Virtual Env: `.venv/bin/activate` (Ensure this is active)
    - Install Deps: `pip install -r requirements.txt`
    - Run Server: `uvicorn backend.main:app --reload` (Port 8000)
    - Run Tests: `pytest` or `pytest tests/path_to_test.py`
    - Crawlers: Run via scripts, e.g., `python scripts/run_crawler.py`

- **Frontend (React/Vite):**
    - Directory: `cd frontend`
    - Install: `npm install`
    - Dev Server: `npm run dev` (Port 5173)
    - Build: `npm run build`

## 3. Coding Standards

### Python (Backend)
- **Type Hinting:** Mandatory for all function arguments and return values. Use `typing` module or standard types.
- **Style:** PEP 8. Use 4 spaces for indentation.
- **Async:** Prefer `async def` for API routes and DB operations.
- **Error Handling:** Use `try-except` blocks explicitly, especially for external API calls (OpenAI) and DB queries.
- **Docstrings:** Required for complex functions and classes.

### JavaScript/React (Frontend)
- **Components:** Functional components with Hooks only.
- **Structure:** Keep logic separated from UI where possible.
- **Styling:** Use CSS modules or existing CSS patterns. Avoid inline styles for layout.

## 4. Workflow Protocol
1.  **Context Check:** Always check `context.md` if the task involves architectural changes or the new AI migration.
2.  **Analysis:** Before editing, read the relevant files to understand imports and dependencies.
3.  **Atomic Changes:** Make small, verifiable changes. Don't refactor unrelated code unless requested.
4.  **Verification:**
    - For Backend changes: Run `pytest` or a specific reproduction script.
    - For Frontend changes: Ensure the build passes (`npm run build`).
5.  **No Hallucinations:** When implementing the AI recommender, ensure the prompt injection logic strictly uses data from our local Database (Source of Truth).

## 5. Key Directories
- `backend/crawler/`: Data scraping scripts (DO NOT Modify unless broken).
- `backend/database/`: ORM Models.
- `backend/recommendation/`: **Focus Area.** Transitioning from `engine_v2.py` to AI-based services.
- `scripts/`: Utility scripts for debugging and data verification.
