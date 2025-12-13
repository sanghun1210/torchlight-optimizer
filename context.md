# Project Context & Transition Plan

## 1. Project Overview
**Name:** Torchlight Optimizer
**Current Status:** Functional Data Ingestion & Basic Web UI
**Goal:** Transition from a hard-coded rule-based recommendation engine to an **AI-driven recommendation system** powered by the OpenAI API.

## 2. Architecture Transition

### Existing Architecture (To be Deprecated/Refactored)
- **Backend:** FastAPI, SQLAlchemy, SQLite/Postgres.
- **Crawler:** Robust scripts (`/backend/crawler/`) that scrape `tlidb.com` and populate the DB. **(KEEP)**
- **Recommendation:** `engine_v2.py`, `game_mechanics.py`, `talent_mechanics.py`. These use hard-coded scoring logic. **(DEPRECATE/REPLACE)**

### New Architecture (AI-Driven)
The new flow will be:
1.  **User Input:** User selects a Hero/Trait or asks for a specific style (e.g., "Fire explosion build") via Frontend.
2.  **Context Builder (Backend):** 
    - Query the local Database to fetch relevant raw data (Hero traits, Skills matching tags, Legendary items).
    - Format this structured data into a concise text prompt.
3.  **AI Inference (OpenAI API):**
    - Send the prompt + System Instructions to OpenAI.
    - AI analyzes the synergies and generates a build recommendation JSON.
4.  **Presentation:** Frontend renders the AI-generated JSON.

## 3. Technology Stack Changes
- **Core:** Python 3.12, FastAPI.
- **AI Integration:** `openai` python library.
- **Data:** Existing SQLAlchemy models serve as the knowledge base for the AI.

## 4. Immediate Tasks
1.  **Environment Setup:** Add `openai` to `requirements.txt` and set up API keys.
2.  **Context Service:** Create a service that can intelligently query the DB to build a prompt context (to avoid token limits, we cannot send the whole DB).
    - Example: If user selects "Rehan" (Hero), fetch only Rehan's traits and "Melee/Fire" related skills/items.
3.  **Prompt Engineering:** Design system prompts that instruct the AI to act as a "Torchlight Infinite Theorycrafter".
4.  **API Integration:** Replace the logic in `backend/api/routes/recommendations.py` to call the new AI service instead of `engine_v2`.

## 5. File Structure Reference
- `backend/database/models.py`: The schema for Heroes, Skills, Items (Source of Truth).
- `backend/crawler/`: Scripts that keep the DB fresh.
- `backend/recommendation/`: currently contains `engine_v2.py`. This will likely house the new `ai_service.py`.

## 6. Philosophy
- **Data-Driven AI:** The AI should not hallucinate stats. It must strictly use the provided context from our Database for item names and skill values.
- **Flexibility:** The system should handle vague user inputs and turn them into concrete builds.
