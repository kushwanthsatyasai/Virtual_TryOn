"""
Virtual Try-On Service using HuggingFace Spaces (Gradio API)
Supports: Kwai-Kolors/Kolors-Virtual-Try-On, yisol/IDM-VTON (api tryon), frogleo/AI-Clothes-Changer (api /infer)
"""
import os
import shutil
from pathlib import Path
from PIL import Image
from gradio_client import Client, handle_file
from ..core.config import settings

# yisol/IDM-VTON expects 768x1024; keep images within this to avoid Space errors
VTON_HEIGHT = 1024
VTON_WIDTH = 768
MAX_IMAGE_DIMENSION = 768


def _preprocess_image(path: str, target_size: tuple = None) -> str:
    """Resize and normalize image for Gradio Space (RGB, optional target size)."""
    path = os.path.abspath(path)
    if not os.path.isfile(path):
        return path
    try:
        with Image.open(path) as im:
            im = im.convert("RGB")
            w, h = im.size
            if target_size:
                new_w, new_h = target_size
                im = im.resize((new_w, new_h), Image.Resampling.LANCZOS)
            elif w > MAX_IMAGE_DIMENSION or h > MAX_IMAGE_DIMENSION:
                if w > h:
                    new_w = MAX_IMAGE_DIMENSION
                    new_h = int(h * MAX_IMAGE_DIMENSION / w)
                else:
                    new_h = MAX_IMAGE_DIMENSION
                    new_w = int(w * MAX_IMAGE_DIMENSION / h)
                im = im.resize((new_w, new_h), Image.Resampling.LANCZOS)
            base = os.path.splitext(os.path.basename(path))[0]
            out_dir = os.path.dirname(path)
            out_path = os.path.join(out_dir, f"{base}_preprocessed.png")
            im.save(out_path, "PNG", optimize=True)
            return out_path
    except Exception as e:
        print(f"Preprocess warning ({path}): {e}, using original")
        return path


def _is_yisol_space(space_name: str) -> bool:
    return "yisol" in space_name.lower() and "IDM-VTON" in space_name


def _is_kolors_space(space_name: str) -> bool:
    return "kolors" in space_name.lower() or "Kwai-Kolors" in space_name


def _is_frogleo_space(space_name: str) -> bool:
    return "frogleo" in space_name.lower() and "AI-Clothes-Changer" in space_name


# Fallback when frogleo fails (Kolors exposes no API; yisol has named /tryon)
FALLBACK_SPACE = "yisol/IDM-VTON"


class GradioVTONService:
    """Virtual Try-On using HuggingFace Gradio Space (Kolors, yisol/IDM-VTON, or frogleo/AI-Clothes-Changer)"""
    
    def __init__(self):
        """Initialize the Gradio client"""
        self.space_name = settings.GRADIO_SPACE_NAME
        self.client = None
        self.connection_attempted = False
        self._use_yisol_api = _is_yisol_space(self.space_name)
        self._use_kolors_api = _is_kolors_space(self.space_name)
        self._use_frogleo_api = _is_frogleo_space(self.space_name)
    
    def _connect(self):
        """Connect to the HuggingFace Space (lazy loading)"""
        if self.client or self.connection_attempted:
            return
        
        self.connection_attempted = True
        try:
            if settings.HF_TOKEN:
                clean_token = str(settings.HF_TOKEN).strip().replace('\x00', '')
                if clean_token:
                    os.environ["HF_TOKEN"] = clean_token
                    os.environ["HUGGING_FACE_HUB_TOKEN"] = clean_token
            
            print(f"Connecting to {self.space_name}...")
            self.client = Client(self.space_name)
            api_desc = "Kolors tryon" if self._use_kolors_api else ("tryon" if self._use_yisol_api else ("/infer (frogleo)" if self._use_frogleo_api else "default"))
            print(f"Connected successfully! (API: {api_desc})")
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
        """
        if not self.client:
            self._connect()
        
        if not self.client:
            raise RuntimeError("Gradio client not connected. Please check your internet connection.")
        
        person_image_path = os.path.abspath(person_image_path)
        cloth_image_path = os.path.abspath(cloth_image_path)
        
        # yisol/IDM-VTON expects 768x1024; Kolors accepts any size (we preprocess to reasonable size)
        if self._use_yisol_api:
            person_prep = _preprocess_image(person_image_path, (VTON_WIDTH, VTON_HEIGHT))
            cloth_prep = _preprocess_image(cloth_image_path, (VTON_WIDTH, VTON_HEIGHT))
        else:
            person_prep = _preprocess_image(person_image_path)
            cloth_prep = _preprocess_image(cloth_image_path)
        
        print(f"\nCalling {self.space_name} API...")
        print(f"  Person: {person_prep}")
        print(f"  Garment: {cloth_prep}")
        print(f"  Steps: {denoise_steps}, Seed: {seed}")
        
        try:
            if self._use_kolors_api:
                # Kwai-Kolors/Kolors-Virtual-Try-On: tryon(person_img, garment_img, seed, randomize_seed)
                # Space has api_name=False (multiple endpoints); use fn_index=0 for first endpoint
                result = self.client.predict(
                    handle_file(person_prep),
                    handle_file(cloth_prep),
                    seed,
                    False,  # randomize_seed = False for reproducibility
                    fn_index=0,
                )
                # Returns (image_out, seed_used, result_info) - take first (image); handle empty/None
                if isinstance(result, (list, tuple)) and len(result) > 0:
                    result_path = result[0]
                elif isinstance(result, (list, tuple)):
                    result_path = None
                else:
                    result_path = result
            elif self._use_yisol_api:
                # yisol/IDM-VTON: official API /tryon (HF Space docs)
                # dict(background, layers, composite), garm_img, garment_des, is_checked, is_checked_crop, denoise_steps, seed
                # Returns tuple: (output_image, masked_image) – use [0]
                imgs_value = {
                    "background": handle_file(person_prep),
                    "layers": [],
                    "composite": None,
                }
                result = self.client.predict(
                    imgs_value,
                    garm_img=handle_file(cloth_prep),
                    garment_des="garment",
                    is_checked=True,
                    is_checked_crop=False,
                    denoise_steps=denoise_steps,
                    seed=seed,
                    api_name="/tryon",
                )
                result_path = result[0] if isinstance(result, (list, tuple)) and len(result) > 0 else result
            else:
                # frogleo/AI-Clothes-Changer: official API /infer (person, garment, denoise_steps, seed)
                # https://huggingface.co/spaces/frogleo/AI-Clothes-Changer – use gradio_client same as run_frogleo_api.py
                try:
                    result_path = self.client.predict(
                        person=handle_file(person_prep),
                        garment=handle_file(cloth_prep),
                        denoise_steps=denoise_steps,
                        seed=seed,
                        api_name="/infer",
                    )
                except Exception as frogleo_err:
                    if not self._use_frogleo_api:
                        raise frogleo_err
                    # Fallback to Kwai-Kolors/Kolors-Virtual-Try-On
                    err_msg = str(frogleo_err)
                    print(f"frogleo Space failed ({err_msg[:80]}...), falling back to {FALLBACK_SPACE}")
                    try:
                        person_prep_fb = _preprocess_image(person_image_path, (VTON_WIDTH, VTON_HEIGHT))
                        cloth_prep_fb = _preprocess_image(cloth_image_path, (VTON_WIDTH, VTON_HEIGHT))
                        fallback_client = Client(FALLBACK_SPACE)
                        imgs_value = {
                            "background": handle_file(person_prep_fb),
                            "layers": [],
                            "composite": None,
                        }
                        result = fallback_client.predict(
                            imgs_value,
                            garm_img=handle_file(cloth_prep_fb),
                            garment_des="garment",
                            is_checked=True,
                            is_checked_crop=False,
                            denoise_steps=denoise_steps,
                            seed=seed,
                            api_name="/tryon",
                        )
                        result_path = result[0] if isinstance(result, (list, tuple)) and len(result) > 0 else result
                    except Exception as fallback_err:
                        print(f"Fallback ({FALLBACK_SPACE}) also failed: {fallback_err}")
                        raise RuntimeError(
                            "Try-on service is temporarily unavailable (frogleo and fallback failed). "
                            "Please try again in a few minutes."
                        ) from frogleo_err
            
            if not result_path or not os.path.isfile(result_path):
                raise RuntimeError("Space returned no output image.")
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            shutil.copy(result_path, output_path)
            
            print(f"  Generated image saved to: {output_path}")
            return output_path
            
        except Exception as e:
            err_msg = str(e)
            print(f"Error calling Space API: {err_msg}")
            if "upstream Gradio app" in err_msg or "AppError" in type(e).__name__:
                raise RuntimeError(
                    "Try-on service is temporarily unavailable (upstream error). "
                    "Please try again in a few minutes or use different images."
                ) from e
            if "ZeroGPU" in err_msg or "quota" in err_msg.lower():
                raise RuntimeError(
                    "Try-on Space has run out of daily GPU quota. Please try again later."
                ) from e
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
