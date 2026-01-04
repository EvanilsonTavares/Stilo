# Active Context: Jan 3, 2026

## Ongoing Work
- **Mission 4 Verification**: Webhooks are implemented but need to be tested with real WhatsApp payloads. Use `ngrok` to expose port 8000.
- **Mission 8 Verification**: VTON integration is implemented. It requires a valid `REPLICATE_API_TOKEN` and a public URL for user images (currently simulated with data URIs, which Replicate may not always support - might need S3/GCS upload).

## Process Update
- Added CDD modes (Light/Full) and templates under `.context/specs/_templates`.
- Default to Full if changes touch contracts, integrations, security, deploy/infra, data storage, or scope > 1 day / > 3 files.

## Next Recommended Tasks
1. Firestore Integration: Persist conversation history and user biotype across sessions.
2. Image Upload Service: Real implementation of image uploading to Cloud Storage to provide clean URLs for Replicate/WhatsApp.
3. UI Polish: Ensure the "t" timestamp issue in Vite logs (or source mapping) is clarified to the user (it's normal Vite behavior).

## Environment Check
- User has Docker Desktop installed.
- Backend is running via Uvicorn.
- Frontend is running via Vite.
