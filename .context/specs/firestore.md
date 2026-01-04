# Spec: Mission 10 - Persistent Chat (Firestore)

## Goal
Implement persistent chat history and user preferences using Google Firestore. This ensures that the Stilo consultant remembers the user's biotype, style preferences, and past conversations across different sessions and channels (Web and WhatsApp).

## Requirements
- **Database**: Use Google Cloud Firestore in Native mode.
- **Session Management**: 
  - Web: Use a unique `session_id` (stored in localStorage).
  - WhatsApp: Use the user's phone number as the unique identifier.
- **Data Model**:
  - `sessions/{sessionId}/messages`: Collection of chat messages.
  - `users/{userId}/profile`: User biotype, preferred styles, etc.
- **Service Layer**: Create `firestore_service.py` to handle all DB operations.

## Technical Details
- **Dependency**: `google-cloud-firestore`.
- **Authentication**: Use Application Default Credentials (ADC) or a Service Account JSON key.
- **Integration**:
  - The `/api/chat` and `/webhook` endpoints should load history from Firestore instead of relying solely on the request payload.

## Definition of Done (DoD)
- [ ] Backend can successfully read/write to Firestore.
- [ ] Chat history persists after page reload on the web.
- [ ] WhatsApp conversations maintain context across multiple messages.
- [ ] User profile (biotype) is updated based on Gemini's analysis.
