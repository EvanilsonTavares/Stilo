# Spec: Mission 8 - Real VTON Integration (Virtual Try-On)

## Goal
Replace the placeholder image generation with a real Virtual Try-On service. This allows users to see how suggested clothes look on their own bodies, using the provided test image (`Imagem para teste.jpeg`) or photos sent via WhatsApp/Web.

## Requirements
- **VTON Engine**: Use Replicate API with the **IDM-VTON** model (or similar).
- **Image Processing**:
  - Handle user image (human) and reference garment image.
  - Support different garment categories (upper_body, lower_body, dresses).
- **Backend Service**: Create a dedicated `replicate_service.py` for API communication.
- **Frontend Feedback**: Show a loading state while the image is being processed by the AI.
- **WhatsApp Support**: Send the final VTON generated image back to the user on WhatsApp.

## Technical Details
- **API Provider**: [Replicate](https://replicate.com/yisol/idm-vton)
- **Environment Variables**:
  - `REPLICATE_API_TOKEN`: API key for Replicate.
- **Input logic**:
  - `human_image`: Current photo of the user.
  - `garment_image`: Image of the clothing item to try on.

## Definition of Done (DoD)
- [ ] Backend can successfully trigger a Replicate VTON prediction.
- [ ] The generated image is returned to the frontend/WhatsApp.
- [ ] Users receive a realistic simulation of the clothing on their body.
