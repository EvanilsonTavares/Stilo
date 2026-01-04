
import os
import httpx
from typing import Optional, List

class WhatsAppService:
    def __init__(self):
        self.access_token = os.getenv("WHATSAPP_TOKEN") or os.getenv("WHATSAPP_ACCESS_TOKEN")
        self.phone_number_id = os.getenv("WHATSAPP_PHONE_ID")
        self.api_version = "v21.0"
        self.base_url = f"https://graph.facebook.com/{self.api_version}/{self.phone_number_id}"
        self.timeout = httpx.Timeout(10.0, connect=5.0)

    async def send_text_message(self, to: str, text: str):
        url = f"{self.base_url}/messages"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {"body": text},
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()

    async def send_image_message(self, to: str, image_url: str, caption: Optional[str] = None):
        url = f"{self.base_url}/messages"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "image",
            "image": {
                "link": image_url,
            },
        }
        if caption:
            payload["image"]["caption"] = caption
            
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()

    async def get_media_url(self, media_id: str):
        url = f"https://graph.facebook.com/{self.api_version}/{media_id}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json().get("url")

    async def download_media(self, media_url: str):
        headers = {
            "Authorization": f"Bearer {self.access_token}",
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(media_url, headers=headers)
            response.raise_for_status()
            return response.content
