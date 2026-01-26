"""
Virtual Try-On Service using HuggingFace Spaces (Gradio API)
Uses: frogleo/AI-Clothes-Changer
"""
import os
import shutil
from pathlib import Path
from PIL import Image
from gradio_client import Client, handle_file
from ..core.config import settings

class GradioVTONService:
    """Virtual Try-On using frogleo/AI-Clothes-Changer Space"""
    
    def __init__(self):
        """Initialize the Gradio client"""
        self.space_name = settings.GRADIO_SPACE_NAME
        self.client = None
        self.connection_attempted = False
    
    def _connect(self):
        """Connect to the HuggingFace Space (lazy loading)"""
        if self.client or self.connection_attempted:
            return
        
        self.connection_attempted = True
        try:
            # Set HF token if available
            if settings.HF_TOKEN:
                # Clean the token (remove any null characters or whitespace)
                clean_token = str(settings.HF_TOKEN).strip().replace('\x00', '')
                if clean_token:
                    os.environ["HF_TOKEN"] = clean_token
                    os.environ["HUGGING_FACE_HUB_TOKEN"] = clean_token
            
            print(f"Connecting to {self.space_name}...")
            self.client = Client(self.space_name)
            print(f"Connected successfully!")
        except Exception as e:
            print(f"Warning: Failed to connect to Space: {e}")
            print("The server will start, but virtual try-on will not work until connection is established.")
    
    def generate_tryon(
        self,
        person_image_path: str,
        cloth_image_path: str,
        output_path: str,
        denoise_steps: int = 30,
        seed: int = 42
    ) -> str:
        """
        Generate virtual try-on result
        
        Args:
            person_image_path: Path to person image
            cloth_image_path: Path to cloth/garment image
            output_path: Where to save the result
            denoise_steps: Number of denoising steps (higher = better quality, slower)
            seed: Random seed for reproducibility
        
        Returns:
            Path to the generated image
        """
        # Try to connect if not already connected
        if not self.client:
            self._connect()
        
        if not self.client:
            raise RuntimeError("Gradio client not connected. Please check your internet connection.")
        
        # Ensure paths are absolute
        person_image_path = os.path.abspath(person_image_path)
        cloth_image_path = os.path.abspath(cloth_image_path)
        
        print(f"\nCalling {self.space_name} API...")
        print(f"  Person: {person_image_path}")
        print(f"  Garment: {cloth_image_path}")
        print(f"  Steps: {denoise_steps}, Seed: {seed}")
        
        try:
            # Call the Space API
            result_path = self.client.predict(
                person=handle_file(person_image_path),
                garment=handle_file(cloth_image_path),
                denoise_steps=denoise_steps,
                seed=seed,
                api_name="/infer"
            )
            
            # Copy result to output path
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            shutil.copy(result_path, output_path)
            
            print(f"  Generated image saved to: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Error calling Space API: {e}")
            raise
    
    def health_check(self) -> bool:
        """Check if the Space is accessible"""
        try:
            if not self.client:
                return False
            # Try to view API (doesn't make actual API call)
            self.client.view_api()
            return True
        except:
            return False
