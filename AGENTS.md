# AGENTS.md - Instructions for AI Assistants

Welcome, Agent. You are working on **Stilo**, a professional AI-driven male image consultant.

## 🎯 Your Mission
Maintain the high technical standard and "Premium" aesthetic of this project while following the established Context-Driven Development (CDD) methodology.

## 🧠 System Context
The core intelligence and rules are stored in the [`.context/`](file:///c:/Users/evani/Stilo/.context/) directory.
- **Vision & Rules**: [`.context/vision.md`](file:///c:/Users/evani/Stilo/.context/vision.md)
- **Tech Stack**: [`.context/tech-stack.md`](file:///c:/Users/evani/Stilo/.context/tech-stack.md)
- **Workflows**: [`.context/workflows.md`](file:///c:/Users/evani/Stilo/.context/workflows.md)

## 🛠️ Technical Guidelines
1.  **Monorepo**: Respect the separation between `/frontend` (React) and `/backend` (FastAPI).
2.  **API Security**: NEVER implement direct AI calls from the frontend. Always use the backend as a proxy.
3.  **JSON Contract**: The AI (model) must respond with text + a structured JSON for actions (VTON/Image Gen). Follow the schema defined in `backend/main.py` or `.context/vision.md`.
4.  **Environment**: Use `.env` files locally, but design for Google Secret Manager in production.

## 🎭 Persona: "Stilo"
When generating system prompts or AI responses, remember:
- **Tone**: Technical, direct, and professional.
- **Goal**: Always push for style improvements.
- **Constraint**: No conversational "fluff". Focus on biotype and colorimetry analysis.

## 📂 Key Entry Points
- Frontend Entry: `frontend/src/main.tsx`
- Backend Entry: `backend/main.py`
- Integration Services: `backend/services/`
