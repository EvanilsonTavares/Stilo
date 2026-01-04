# Spec (Full)

## Problem / Objective
- Harden WhatsApp webhook handling so it is production-safe, resilient, and aligned with Meta requirements without changing Stilo behavior.

## Scope
- In:
  - Validate webhook signatures for POST requests.
  - Robust payload parsing across entries, changes, and messages.
  - Handle text and image messages; ignore unsupported types.
  - Idempotency guard for duplicate message IDs.
  - Safe logging and explicit error handling.
  - Align and document environment variables for WhatsApp auth.
- Out:
  - New persistent storage or chat history (Firestore).
  - Media upload service (public URLs) or CDN.
  - Prompt changes or JSON contract changes.
  - Frontend changes.

## Requirements
### Functional
- Verify `X-Hub-Signature-256` using the WhatsApp app secret; reject invalid or missing signatures with 403.
- Support multiple `entry` and `changes` blocks in a single payload.
- Process `text` and `image` message types; return 200 and ignore unsupported types.
- Enforce timeouts for outbound HTTP calls (Graph API, Gemini, Replicate).
- Return 200 quickly after validation and processing start; no blocking on long operations.
- Apply idempotency for duplicate `message.id` within a short window.
- Keep GET `/webhook` verification compatible with Meta.

### Non-functional
- Do not log secrets, tokens, or full payloads with sensitive data.
- Log a stable request ID for traceability.
- Deterministic error responses (no stack traces to clients).
- Minimal latency overhead added by verification.

## Contracts / Interfaces
- API endpoints:
  - `GET /webhook` for verification challenge.
  - `POST /webhook` for event delivery.
- Input examples:
  - Meta Cloud API webhook payload with `entry -> changes -> value -> messages`.
- Output:
  - 200 with `{ "status": "ok" | "no_messages" | "ignored" }` after validation.
  - 403 for invalid signatures.

## Integrations / Dependencies
- External services:
  - Meta Graph API (media fetch).
  - Gemini API (content generation).
  - Replicate API (VTON, only when triggered).
- Env vars / secrets:
  - `WHATSAPP_VERIFY_TOKEN`
  - `WHATSAPP_PHONE_ID`
  - `WHATSAPP_ACCESS_TOKEN` (or align to `WHATSAPP_TOKEN`; decide one)
  - `WHATSAPP_APP_SECRET` (for signature validation)
  - `GEMINI_API_KEY`
  - `REPLICATE_API_TOKEN`

## Security / Privacy
- Validate signatures on every POST request.
- Do not persist message content or media beyond request flow (unless specified later).
- Reject malformed payloads without leaking internal details.

## Definition of Done
- Signature validation implemented with invalid/missing signature tests.
- Payload parsing handles multiple entries/messages without crashing.
- Unsupported types return 200 with `ignored`.
- Idempotency guard prevents duplicate processing within window.
- Env var names documented and consistent in code.
- Manual test with ngrok + Meta webhook verification succeeds.
