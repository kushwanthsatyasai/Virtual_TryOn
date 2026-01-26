"""
Image processing utilities for virtual try-on
"""
import cv2
import numpy as np
from PIL import Image, ImageEnhance
from typing import Tuple, Optional, List
import base64
import io
import logging
from app.core.exceptions import ImageProcessingException

logger = logging.getLogger(__name__)


class ImageProcessor:
    """Image processing utilities"""
    
    @staticmethod
    def base64_to_image(base64_string: str) -> Image.Image:
        """Convert base64 string to PIL Image"""
        try:
            # Remove data URL prefix if present
            if ',' in base64_string:
                base64_string = base64_string.split(',')[1]
            
            # Decode base64
            image_data = base64.b64decode(base64_string)
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            return image
        except Exception as e:
            logger.error(f"Failed to decode base64 image: {e}")
            raise ImageProcessingException(f"Failed to decode base64 image: {e}")
    
    @staticmethod
    def image_to_base64(image: Image.Image, format: str = "JPEG") -> str:
        """Convert PIL Image to base64 string"""
        try:
            buffer = io.BytesIO()
            image.save(buffer, format=format)
            image_data = buffer.getvalue()
            base64_string = base64.b64encode(image_data).decode('utf-8')
            return f"data:image/{format.lower()};base64,{base64_string}"
        except Exception as e:
            logger.error(f"Failed to encode image to base64: {e}")
            raise ImageProcessingException(f"Failed to encode image to base64: {e}")
    
    @staticmethod
    def resize_image(image: Image.Image, max_size: int = 1024) -> Image.Image:
        """Resize image while maintaining aspect ratio"""
        try:
            width, height = image.size
            
            # Calculate new dimensions
            if width > height:
                new_width = min(max_size, width)
                new_height = int((height * new_width) / width)
            else:
                new_height = min(max_size, height)
                new_width = int((width * new_height) / height)
            
            return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        except Exception as e:
            logger.error(f"Failed to resize image: {e}")
            raise ImageProcessingException(f"Failed to resize image: {e}")
    
    @staticmethod
    def enhance_image(image: Image.Image) -> Image.Image:
        """Enhance image quality for better virtual try-on results"""
        try:
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.1)
            
            # Enhance sharpness
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.05)
            
            # Enhance color
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(1.02)
            
            return image
        except Exception as e:
            logger.error(f"Failed to enhance image: {e}")
            raise ImageProcessingException(f"Failed to enhance image: {e}")
    
    @staticmethod
    def detect_person_in_image(image: Image.Image) -> Tuple[bool, Optional[Tuple[int, int, int, int]]]:
        """Detect if there's a person in the image and return bounding box"""
        try:
            # Convert PIL to OpenCV format
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Load pre-trained person detection model
            # In practice, you'd use a more sophisticated model like YOLO or MediaPipe
            hog = cv2.HOGDescriptor()
            hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
            
            # Detect people
            boxes, weights = hog.detectMultiScale(cv_image, winStride=(8, 8), padding=(32, 32), scale=1.05)
            
            if len(boxes) > 0:
                # Return the largest detection
                largest_box = max(boxes, key=lambda x: x[2] * x[3])
                x, y, w, h = largest_box
                return True, (x, y, x + w, y + h)
            
            return False, None
            
        except Exception as e:
            logger.error(f"Person detection failed: {e}")
            return False, None
    
    @staticmethod
    def crop_person_from_image(image: Image.Image, bbox: Optional[Tuple[int, int, int, int]] = None) -> Image.Image:
        """Crop person from image using bounding box"""
        try:
            if bbox is None:
                # If no bbox provided, try to detect person
                has_person, bbox = ImageProcessor.detect_person_in_image(image)
                if not has_person:
                    return image
            
            if bbox:
                x1, y1, x2, y2 = bbox
                # Add some padding
                padding = 20
                x1 = max(0, x1 - padding)
                y1 = max(0, y1 - padding)
                x2 = min(image.width, x2 + padding)
                y2 = min(image.height, y2 + padding)
                
                return image.crop((x1, y1, x2, y2))
            
            return image
            
        except Exception as e:
            logger.error(f"Person cropping failed: {e}")
            return image
    
    @staticmethod
    def validate_image_for_vton(image: Image.Image) -> Tuple[bool, str]:
        """Validate if image is suitable for virtual try-on"""
        try:
            # Check image size
            width, height = image.size
            if width < 256 or height < 256:
                return False, "Image too small. Minimum size is 256x256 pixels."
            
            # Check aspect ratio
            aspect_ratio = width / height
            if aspect_ratio < 0.5 or aspect_ratio > 2.0:
                return False, "Image aspect ratio not suitable for virtual try-on."
            
            # Check if image contains a person
            has_person, _ = ImageProcessor.detect_person_in_image(image)
            if not has_person:
                return False, "No person detected in image. Please ensure the image contains a person."
            
            return True, "Image is suitable for virtual try-on."
            
        except Exception as e:
            logger.error(f"Image validation failed: {e}")
            return False, f"Image validation failed: {e}"
    
    @staticmethod
    def preprocess_for_vton(person_image: Image.Image, clothing_image: Image.Image) -> Tuple[Image.Image, Image.Image]:
        """Preprocess images for virtual try-on"""
        try:
            # Validate person image
            is_valid, message = ImageProcessor.validate_image_for_vton(person_image)
            if not is_valid:
                raise ImageProcessingException(message)
            
            # Resize images
            person_image = ImageProcessor.resize_image(person_image, max_size=512)
            clothing_image = ImageProcessor.resize_image(clothing_image, max_size=512)
            
            # Enhance images
            person_image = ImageProcessor.enhance_image(person_image)
            clothing_image = ImageProcessor.enhance_image(clothing_image)
            
            return person_image, clothing_image
            
        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            raise ImageProcessingException(f"Image preprocessing failed: {e}")


# Global image processor instance
image_processor = ImageProcessor()
