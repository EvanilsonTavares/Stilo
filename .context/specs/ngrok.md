# Spec: Mission 9 - Real-time Testing with ngrok

## Goal
Expose the local FastAPI backend (port 8000) to the public internet using `ngrok` so the WhatsApp Cloud API can send webhook events to the local environment for real-time testing.

## Requirements
- **Tunneling**: Start an HTTP tunnel to `localhost:8000`.
- **Static Domain (Optional)**: If available, use a static ngrok domain to avoid updating Meta Dashboard every session.
- **Webhook Endpoint**: Use the `https://[ngrok-id].ngrok-free.app/webhook` URL in the Meta Developer Portal.
- **Verification Token**: Use `STILO_VERIFY_TOKEN` (defined in `.env`).

## Setup Steps
1. **Installation**: If not present, install `ngrok` via winget.
2. **Authentication**: User must run `ngrok config add-authtoken <token>`.
3. **Execution**: Run `ngrok http 8000`.
4. **Configuration**: 
   - Copy the "Forwarding" HTTPS URL.
   - Go to [Meta for Developers](https://developers.facebook.com/).
   - Update the Webhook Callback URL.

## Definition of Done (DoD)
- [ ] ngrok is running and forwarding to port 8000.
- [ ] Meta "Verify and Save" succeeds for the `/webhook` endpoint.
- [ ] Incoming messages from WhatsApp are visible in the backend terminal logs.
