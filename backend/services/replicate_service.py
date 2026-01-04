
import asyncio
import os
import replicate
from typing import Optional

class ReplicateService:
    def __init__(self):
        # The replicate library will automatically look for REPLICATE_API_TOKEN in env
        self.api_token = os.getenv("REPLICATE_API_TOKEN")

    async def run_vton(
        self, 
        human_image_url: str, 
        garment_image_url: str, 
        description: str = "A formal garment",
        category: str = "upper_body"
    ) -> Optional[str]:
        """
        Runs the IDM-VTON model on Replicate.
        """
        if not self.api_token:
            print("REPLICATE_API_TOKEN not found.")
            return None

        try:
            # Using yisol/idm-vton or cuuupid/idm-vton
            # We'll try the yisol version first as it's the original
            output = await asyncio.to_thread(
                replicate.run,
                "yisol/idm-vton:c871bb9b0f45610ec1f2747e4b52b21cf56b4eed8871bd5b5c92badc60814bb6",
                input={
                    "human_img": human_image_url,
                    "garm_img": garment_image_url,
                    "garment_des": description,
                    "category": category,
                    "crop": True,
                    "num_inference_steps": 30
                }
            )
            # Replicate output is usually a list of strings (URLs)
            if isinstance(output, list) and len(output) > 0:
                return output[0]
            return output
        except Exception as e:
            print(f"Error running Replicate VTON: {e}")
            return None
