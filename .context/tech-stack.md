# Tech Stack: Stilo

## Monorepo Structure
- `/frontend`: React + Vite (Port 3000).
- `/backend`: Python + FastAPI (Port 8000).
- `/shared`: (Planned) Shared schemas.
- `n8n`: Automation and workflow orchestration (Port 5678).

## Frontend
- **Framework**: React 19.
- **Styling**: Vanilla CSS.
- **API Client**: `frontend/services/geminiService.ts` (points to `VITE_API_BASE_URL`).

## Backend
- **Framework**: FastAPI.
- **Main Logic**: `backend/main.py`.
- **Key Services**:
  - `WhatsAppService`: `backend/services/whatsapp_service.py`.
  - `ReplicateService` (VTON): `backend/services/replicate_service.py`.
- **CORS**: Configured to allow `*` (development).

## External APIs
- **Google Gemini**: 1.5 Flash (for scale) and Pro (for logic).
- **Meta (WhatsApp)**: Cloud API via Webhooks.
- **Replicate**: `yisol/idm-vton` model.

## Environment Variables (.env)
- `GEMINI_API_KEY`: Google AI credentials.
- `WHATSAPP_TOKEN` / `WHATSAPP_PHONE_ID`: Meta credentials.
- `REPLICATE_API_TOKEN`: VTON credentials.
