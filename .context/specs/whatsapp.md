# Spec: Mission 4 - WhatsApp Webhook & Channel

## Goal
Enable Stilo to receive and send messages through the WhatsApp Cloud API (Meta), allowing users to interact with the "Image Consultant" directly via WhatsApp.

## Requirements
- **Webhook Verification**: Implement the `GET /webhook` endpoint to handle Meta's verification challenge.
- **Event Handling**: Support `POST /webhook` to receive incoming text and image messages.
- **Media Storage**: Automatically download images from WhatsApp and store them in Cloud Storage (simulated locally for now).
- **Outbound Messages**: Implement a service to send text and image responses back to the user via the WhatsApp API.
- **Session Management**: Link WhatsApp `sender_id` to chat history in the backend.

## Technical Details
- **API**: WhatsApp Business Platform (Cloud API).
- **Security**: Verify `X-Hub-Signature-256` for incoming webhooks.
- **Environment Variables**:
  - `WHATSAPP_TOKEN`: Permanent access token.
  - `WHATSAPP_VERIFY_TOKEN`: Random string for webhook verification.
  - `WHATSAPP_PHONE_ID`: Unique ID for the sender phone number.

## Definition of Done (DoD)
- [ ] Backend responds correctly to Meta's verification request.
- [ ] Inbound messages are logged and forwarded to the Gemini Brain.
- [ ] Assistant responses are successfully sent back to the recipient on WhatsApp.
- [ ] Images sent via WhatsApp are correctly parsed by the Gemini Brain.
