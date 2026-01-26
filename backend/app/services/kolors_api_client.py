"""
Kolors Virtual Try-On API Client
================================
Based on the official Kolors app.py implementation

This service connects to a Kolors API server that runs the actual model.
The API uses a submit/query pattern for async processing.
"""

import os
import cv2
import numpy as np
import base64
import requests
import json
import time
import logging
from typing import Optional, Tuple
from PIL import Image

logger = logging.getLogger(__name__)


class KolorsAPIClient:
    """
    Kolors API Client - Matches the official app.py implementation
    
    Architecture:
    - Submit endpoint: Sends images and gets task ID
    - Query endpoint: Polls for results using task ID
    
    Models used by Kolors (server-side):
    - Stable Diffusion XL (via diffusers)
    - Custom VTO pipeline
    - Invisible watermarking
    - xformers for optimization
    """
    
    def __init__(
        self,
        api_url: str,
        token: Optional[str] = None,
        cookie: Optional[str] = None,
        referer: Optional[str] = None,
        timeout: int = 50
    ):
        """
        Initialize Kolors API client
        
        Args:
            api_url: Base URL of Kolors API (e.g., "api.example.com")
            token: Authentication token
            cookie: Cookie for authentication
            referer: Referer header
            timeout: Request timeout in seconds
        """
        self.api_url = api_url.rstrip('/')
        self.token = token
        self.cookie = cookie
        self.referer = referer
        self.timeout = timeout
        
        # Build headers
        self.headers = {
            'Content-Type': 'application/json',
        }
        if token:
            self.headers['token'] = token
        if cookie:
            self.headers['Cookie'] = cookie
        if referer:
            self.headers['referer'] = referer
        
        logger.info(f"🔗 Kolors API Client initialized: {self.api_url}")
    
    def _encode_image(self, image: np.ndarray) -> str:
        """
        Encode image to base64 (matches Kolors app.py)
        
        Args:
            image: RGB numpy array
            
        Returns:
            Base64 encoded JPEG string
        """
        # Convert RGB to BGR for OpenCV
        bgr_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        # Encode as JPEG
        _, encoded = cv2.imencode('.jpg', bgr_image)
        encoded_bytes = encoded.tobytes()
        
        # Base64 encode
        encoded_str = base64.b64encode(encoded_bytes).decode('utf-8')
        
        return encoded_str
    
    def _decode_image(self, base64_str: str) -> np.ndarray:
        """
        Decode base64 image to numpy array
        
        Args:
            base64_str: Base64 encoded image
            
        Returns:
            RGB numpy array
        """
        # Decode base64
        image_bytes = base64.b64decode(base64_str)
        
        # Decode JPEG
        image_np = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(image_np, cv2.IMREAD_UNCHANGED)
        
        # Convert BGR to RGB
        if len(image.shape) == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        return image
    
    def submit_task(
        self,
        person_image: np.ndarray,
        garment_image: np.ndarray,
        seed: int = 0
    ) -> Optional[str]:
        """
        Submit a try-on task to Kolors API
        
        Args:
            person_image: Person image as RGB numpy array
            garment_image: Garment image as RGB numpy array
            seed: Random seed for reproducibility
            
        Returns:
            Task UUID if successful, None otherwise
        """
        try:
            # Encode images
            encoded_person = self._encode_image(person_image)
            encoded_garment = self._encode_image(garment_image)
            
            # Prepare data
            data = {
                "clothImage": encoded_garment,
                "humanImage": encoded_person,
                "seed": seed
            }
            
            # Submit
            url = f"http://{self.api_url}/Submit"
            logger.info(f"📤 Submitting task to {url}")
            
            response = requests.post(
                url,
                headers=self.headers,
                data=json.dumps(data),
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json().get('result', {})
                status = result.get('status')
                
                if status == "success":
                    task_uuid = result.get('result')  # Task ID
                    logger.info(f"✅ Task submitted: {task_uuid}")
                    return task_uuid
                else:
                    logger.error(f"❌ Submit failed: {status}")
                    return None
            else:
                logger.error(f"❌ HTTP {response.status_code}: {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error("⏱️  Request timeout")
            return None
        except Exception as e:
            logger.error(f"❌ Submit error: {e}")
            return None
    
    def query_result(
        self,
        task_uuid: str,
        max_retries: int = 12,
        retry_delay: int = 1,
        initial_delay: int = 9
    ) -> Tuple[Optional[np.ndarray], str]:
        """
        Query for try-on result
        
        Args:
            task_uuid: Task ID from submit_task
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries (seconds)
            initial_delay: Initial delay before first query (seconds)
            
        Returns:
            Tuple of (result_image, status_info)
        """
        # Wait initial delay
        if initial_delay > 0:
            time.sleep(initial_delay)
        
        url = f"http://{self.api_url}/Query?taskId={task_uuid}"
        result_image = None
        info = ""
        err_log = ""
        
        for i in range(max_retries):
            try:
                logger.info(f"🔍 Querying result (attempt {i+1}/{max_retries})...")
                
                response = requests.get(
                    url,
                    headers=self.headers,
                    timeout=20
                )
                
                if response.status_code == 200:
                    result = response.json().get('result', {})
                    status = result.get('status')
                    
                    if status == "success":
                        # Decode result image
                        result_base64 = result.get('result')
                        if result_base64:
                            result_image = self._decode_image(result_base64)
                            info = "Success"
                            logger.info("✅ Result received!")
                            break
                    elif status == "error":
                        err_log = "Status is Error"
                        info = "Error"
                        logger.error("❌ Server returned error status")
                        break
                else:
                    err_log = f"HTTP {response.status_code}"
                    info = f"URL error (HTTP {response.status_code})"
                    logger.error(f"❌ HTTP {response.status_code}: {response.text}")
                    break
                    
            except requests.exceptions.ReadTimeout:
                err_log = "Http Timeout"
                info = "Http Timeout, please try again later"
                logger.warning(f"⏱️  Timeout on attempt {i+1}")
                
            except Exception as e:
                err_log = f"Exception: {e}"
                logger.warning(f"⚠️  Query error on attempt {i+1}: {e}")
            
            # Wait before next retry
            if i < max_retries - 1:
                time.sleep(retry_delay)
        
        if info == "":
            err_log = f"No image after {max_retries} retries"
            info = "Too many users, please try again later"
            logger.error(f"❌ {err_log}")
        
        if info != "Success" and err_log:
            logger.error(f"Error Log: {err_log}")
        
        return result_image, info
    
    def tryon(
        self,
        person_image: np.ndarray,
        garment_image: np.ndarray,
        seed: int = 0,
        max_retries: int = 12,
        retry_delay: int = 1,
        initial_delay: int = 9
    ) -> Tuple[Optional[np.ndarray], int, str]:
        """
        Complete try-on workflow: submit + query
        
        Args:
            person_image: Person image as RGB numpy array
            garment_image: Garment image as RGB numpy array
            seed: Random seed
            max_retries: Max query retries
            retry_delay: Delay between retries
            initial_delay: Initial delay before querying
            
        Returns:
            Tuple of (result_image, seed_used, status_info)
        """
        start_time = time.time()
        
        # Submit task
        task_uuid = self.submit_task(person_image, garment_image, seed)
        
        if task_uuid is None:
            return None, seed, "Failed to submit task"
        
        # Query result
        result_image, info = self.query_result(
            task_uuid,
            max_retries=max_retries,
            retry_delay=retry_delay,
            initial_delay=initial_delay
        )
        
        elapsed = time.time() - start_time
        logger.info(f"⏱️  Total time: {elapsed:.2f}s")
        
        return result_image, seed, info


# Convenience function for PIL Images
def tryon_from_pil(
    person_image: Image.Image,
    garment_image: Image.Image,
    api_url: str,
    token: Optional[str] = None,
    cookie: Optional[str] = None,
    referer: Optional[str] = None,
    seed: int = 0
) -> Tuple[Optional[Image.Image], int, str]:
    """
    Try-on using PIL Images
    
    Args:
        person_image: PIL Image
        garment_image: PIL Image
        api_url: Kolors API URL
        token: API token
        cookie: Cookie
        referer: Referer
        seed: Random seed
        
    Returns:
        Tuple of (result_image, seed_used, status_info)
    """
    # Convert PIL to numpy
    person_np = np.array(person_image.convert('RGB'))
    garment_np = np.array(garment_image.convert('RGB'))
    
    # Create client and run
    client = KolorsAPIClient(api_url, token, cookie, referer)
    result_np, seed_used, info = client.tryon(person_np, garment_np, seed)
    
    # Convert back to PIL
    if result_np is not None:
        result_image = Image.fromarray(result_np)
    else:
        result_image = None
    
    return result_image, seed_used, info

