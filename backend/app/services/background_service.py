"""
Background Removal and Replacement Service
==========================================
Remove or replace backgrounds from try-on results
"""

from PIL import Image
import numpy as np
from typing import Optional

try:
    from rembg import remove
    REMBG_AVAILABLE = True
except ImportError:
    REMBG_AVAILABLE = False
    print("⚠️  rembg not installed. Background removal disabled.")


class BackgroundService:
    """Handle background removal and replacement"""
    
    def __init__(self):
        self.available = REMBG_AVAILABLE
    
    def remove_background(
        self,
        image_path: str,
        output_path: str,
        alpha_matting: bool = True
    ) -> str:
        """
        Remove background from image
        
        Args:
            image_path: Path to input image
            output_path: Path to save result (PNG with transparency)
            alpha_matting: Use alpha matting for better edges
        
        Returns:
            Path to output image
        """
        if not self.available:
            raise RuntimeError("rembg not installed")
        
        # Load image
        with open(image_path, 'rb') as f:
            input_data = f.read()
        
        # Remove background
        output_data = remove(
            input_data,
            alpha_matting=alpha_matting,
            alpha_matting_foreground_threshold=240,
            alpha_matting_background_threshold=10,
            alpha_matting_erode_size=10
        )
        
        # Save result
        with open(output_path, 'wb') as f:
            f.write(output_data)
        
        return output_path
    
    def replace_background(
        self,
        image_path: str,
        background_path: str,
        output_path: str
    ) -> str:
        """
        Replace background with a new one
        
        Args:
            image_path: Path to image (with or without background)
            background_path: Path to new background image
            output_path: Path to save result
        
        Returns:
            Path to output image
        """
        # First remove existing background
        temp_no_bg = output_path.replace('.png', '_temp_nobg.png')
        self.remove_background(image_path, temp_no_bg)
        
        # Load images
        foreground = Image.open(temp_no_bg).convert('RGBA')
        background = Image.open(background_path).convert('RGB')
        
        # Resize background to match foreground
        background = background.resize(foreground.size, Image.Resampling.LANCZOS)
        
        # Convert to RGBA for compositing
        background = background.convert('RGBA')
        
        # Composite
        result = Image.alpha_composite(background, foreground)
        
        # Save
        result = result.convert('RGB')
        result.save(output_path, 'PNG')
        
        # Clean up temp file
        import os
        if os.path.exists(temp_no_bg):
            os.remove(temp_no_bg)
        
        return output_path
    
    def apply_solid_color_background(
        self,
        image_path: str,
        output_path: str,
        color: tuple = (255, 255, 255)
    ) -> str:
        """
        Apply solid color background
        
        Args:
            image_path: Path to input image
            output_path: Path to save result
            color: RGB color tuple (default: white)
        
        Returns:
            Path to output image
        """
        # Remove background
        temp_no_bg = output_path.replace('.png', '_temp_nobg.png')
        self.remove_background(image_path, temp_no_bg)
        
        # Load foreground
        foreground = Image.open(temp_no_bg).convert('RGBA')
        
        # Create solid color background
        background = Image.new('RGBA', foreground.size, color + (255,))
        
        # Composite
        result = Image.alpha_composite(background, foreground)
        
        # Save
        result = result.convert('RGB')
        result.save(output_path, 'PNG')
        
        # Clean up
        import os
        if os.path.exists(temp_no_bg):
            os.remove(temp_no_bg)
        
        return output_path
    
    def create_background_variants(
        self,
        image_path: str,
        output_dir: str,
        colors: list = None
    ) -> list:
        """
        Create multiple background color variants
        
        Args:
            image_path: Path to input image
            output_dir: Directory to save variants
            colors: List of RGB tuples (default: white, black, gray, blue)
        
        Returns:
            List of output paths
        """
        if colors is None:
            colors = [
                (255, 255, 255),  # White
                (0, 0, 0),        # Black
                (240, 240, 240),  # Light gray
                (135, 206, 235),  # Sky blue
                (255, 182, 193),  # Light pink
            ]
        
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        results = []
        color_names = ['white', 'black', 'gray', 'blue', 'pink']
        
        for i, color in enumerate(colors):
            color_name = color_names[i] if i < len(color_names) else f'color{i}'
            output_path = os.path.join(output_dir, f'bg_{color_name}.png')
            
            self.apply_solid_color_background(image_path, output_path, color)
            results.append(output_path)
        
        return results
