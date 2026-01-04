import asyncio
import base64
import os
from typing import Optional, Tuple

# Use the new google-genai SDK for image generation
from google import genai
from google.genai import types

class GeminiImageService:
    """Service for generating images using Gemini's image generation models."""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.client = None
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        # Use Gemini image generation model
        self.model_name = "gemini-2.0-flash-exp-image-generation"
    
    async def generate_outfit_suggestion(
        self,
        user_image_base64: Optional[str],
        garment_description: str,
        style_context: str = ""
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Generates an image of the suggested outfit.
        
        Returns:
            Tuple of (image_base64, error_message)
        """
        if not self.client:
            return None, "GEMINI_API_KEY not configured"
        
        try:
            # Build the prompt for image generation
            prompt = f"""Generate a high-quality fashion product photo of: {garment_description}

Style: Professional fashion photography, clean white background, high resolution, detailed fabric texture, premium quality garment.
Generate ONLY the garment image, no model wearing it."""

            # Generate the image with response_modalities
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE", "TEXT"]
                )
            )
            
            # Extract image from response
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        image_data = part.inline_data.data
                        if isinstance(image_data, bytes):
                            return base64.b64encode(image_data).decode('utf-8'), None
                        return image_data, None
            
            return None, "No image generated in response"
            
        except Exception as e:
            print(f"Error generating image with Gemini: {e}")
            import traceback
            traceback.print_exc()
            return None, str(e)
    
    async def generate_virtual_tryon(
        self,
        user_image_base64: str,
        garment_description: str
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Generates a virtual try-on image combining user photo with suggested garment.
        
        Returns:
            Tuple of (image_base64, error_message)
        """
        if not self.client:
            return None, "GEMINI_API_KEY not configured"
        
        try:
            # Decode user image
            user_image_bytes = base64.b64decode(user_image_base64)
            
            prompt = f"""Look at this person's photo and create a new image showing them wearing: {garment_description}

Keep the person's face, body, and pose exactly the same. Replace only the upper body clothing with the described garment.
Make it look natural and professionally photographed. High quality output."""

            # Create image part
            image_part = types.Part.from_bytes(
                data=user_image_bytes,
                mime_type="image/jpeg"
            )
            
            # Generate with image input
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_name,
                contents=[prompt, image_part],
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE", "TEXT"]
                )
            )
            
            # Extract image from response
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        image_data = part.inline_data.data
                        if isinstance(image_data, bytes):
                            return base64.b64encode(image_data).decode('utf-8'), None
                        return image_data, None
            
            return None, "No image generated in response"
            
        except Exception as e:
            print(f"Error in virtual try-on: {e}")
            import traceback
            traceback.print_exc()
            return None, str(e)
