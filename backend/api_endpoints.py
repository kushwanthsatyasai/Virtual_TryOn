"""
REST API Endpoints for Flutter Integration
===========================================
Full-featured API for virtual try-on mobile app
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uuid
import os
import shutil
from datetime import datetime
from app.services.ai_service import AIService
from app.core.config import settings

app = FastAPI(title="Virtue Try-On API", version="1.0.0")

# CORS - Allow Flutter app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your Flutter app domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI Service
ai_service = None

@app.on_event("startup")
async def startup():
    global ai_service
    ai_service = AIService()
    os.makedirs("temp/uploads", exist_ok=True)
    os.makedirs("temp/results", exist_ok=True)

# Models
class TryOnRequest(BaseModel):
    quality: str = "balanced"  # fast, balanced, high
    save_history: bool = True

class TryOnResponse(BaseModel):
    success: bool
    result_id: str
    result_url: str
    processing_time: float
    message: Optional[str] = None

class HistoryItem(BaseModel):
    id: str
    person_image_url: str
    cloth_image_url: str
    result_url: str
    quality: str
    created_at: str
    favorite: bool

# Endpoints

@app.get("/")
async def root():
    return {
        "name": "Virtue Try-On API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Virtual Try-On",
        "gradio_space": settings.GRADIO_SPACE_NAME,
        "using_gradio": settings.USE_GRADIO_SPACE
    }

@app.post("/api/v1/try-on", response_model=TryOnResponse)
async def virtual_try_on(
    person: UploadFile = File(..., description="Person/model image"),
    cloth: UploadFile = File(..., description="Clothing item image"),
    quality: str = "balanced"
):
    """
    Generate virtual try-on result
    
    **Quality Options:**
    - `fast`: 15 steps (~15-20 seconds)
    - `balanced`: 30 steps (~30-40 seconds) [DEFAULT]
    - `high`: 50 steps (~50-60 seconds)
    """
    start_time = datetime.now()
    
    # Validate quality
    quality_map = {
        "fast": 15,
        "balanced": 30,
        "high": 50
    }
    denoise_steps = quality_map.get(quality, 30)
    
    # Generate unique ID
    result_id = str(uuid.uuid4())
    
    # Save uploaded files
    person_path = f"temp/uploads/{result_id}_person.png"
    cloth_path = f"temp/uploads/{result_id}_cloth.png"
    result_path = f"temp/results/{result_id}_result.png"
    
    try:
        # Save uploads
        with open(person_path, "wb") as f:
            f.write(await person.read())
        
        with open(cloth_path, "wb") as f:
            f.write(await cloth.read())
        
        # Generate try-on
        success = await ai_service.generate_tryon(
            user_image_path=person_path,
            cloth_image_path=cloth_path,
            output_path=result_path,
            session_id=result_id
        )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        if success and os.path.exists(result_path):
            return TryOnResponse(
                success=True,
                result_id=result_id,
                result_url=f"/api/v1/results/{result_id}",
                processing_time=processing_time,
                message="Virtual try-on generated successfully"
            )
        else:
            raise HTTPException(status_code=500, detail="Try-on generation failed")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/results/{result_id}")
async def get_result(result_id: str):
    """Download generated try-on result"""
    result_path = f"temp/results/{result_id}_result.png"
    
    if not os.path.exists(result_path):
        raise HTTPException(status_code=404, detail="Result not found")
    
    return FileResponse(
        result_path,
        media_type="image/png",
        filename=f"tryon_{result_id}.png"
    )

@app.post("/api/v1/batch-try-on")
async def batch_try_on(
    person: UploadFile = File(...),
    clothes: List[UploadFile] = File(...),
    quality: str = "balanced",
    background_tasks: BackgroundTasks = None
):
    """
    Try multiple clothes on the same person
    Returns immediately with job ID, results available via /api/v1/batch-results/{job_id}
    """
    job_id = str(uuid.uuid4())
    
    # Save person image
    person_path = f"temp/uploads/{job_id}_person.png"
    with open(person_path, "wb") as f:
        f.write(await person.read())
    
    # Save all cloth images
    cloth_paths = []
    for i, cloth in enumerate(clothes):
        cloth_path = f"temp/uploads/{job_id}_cloth_{i}.png"
        with open(cloth_path, "wb") as f:
            f.write(await cloth.read())
        cloth_paths.append(cloth_path)
    
    # Process in background
    # (In production, use Celery or similar for this)
    
    return {
        "job_id": job_id,
        "status": "processing",
        "total_items": len(cloth_paths),
        "status_url": f"/api/v1/batch-status/{job_id}"
    }

@app.post("/api/v1/comparison")
async def create_comparison(
    person: UploadFile = File(...),
    cloth: UploadFile = File(...),
    quality: str = "balanced"
):
    """Generate try-on with side-by-side comparison"""
    result_id = str(uuid.uuid4())
    
    person_path = f"temp/uploads/{result_id}_person.png"
    cloth_path = f"temp/uploads/{result_id}_cloth.png"
    result_path = f"temp/results/{result_id}_result.png"
    comparison_path = f"temp/results/{result_id}_comparison.png"
    
    # Save uploads
    with open(person_path, "wb") as f:
        f.write(await person.read())
    
    with open(cloth_path, "wb") as f:
        f.write(await cloth.read())
    
    # Generate try-on
    success = await ai_service.generate_tryon(
        user_image_path=person_path,
        cloth_image_path=cloth_path,
        output_path=result_path,
        session_id=result_id
    )
    
    if success:
        # Create comparison image
        from PIL import Image
        
        person_img = Image.open(person_path)
        cloth_img = Image.open(cloth_path)
        result_img = Image.open(result_path)
        
        # Resize to same height
        height = 800
        person_img = person_img.resize((int(person_img.width * height / person_img.height), height))
        cloth_img = cloth_img.resize((int(cloth_img.width * height / cloth_img.height), height))
        result_img = result_img.resize((int(result_img.width * height / result_img.height), height))
        
        # Create side-by-side
        total_width = person_img.width + cloth_img.width + result_img.width + 40
        comparison = Image.new('RGB', (total_width, height), (255, 255, 255))
        
        comparison.paste(person_img, (0, 0))
        comparison.paste(cloth_img, (person_img.width + 20, 0))
        comparison.paste(result_img, (person_img.width + cloth_img.width + 40, 0))
        
        comparison.save(comparison_path)
        
        return {
            "success": True,
            "result_id": result_id,
            "result_url": f"/api/v1/results/{result_id}",
            "comparison_url": f"/api/v1/comparison/{result_id}"
        }
    else:
        raise HTTPException(status_code=500, detail="Try-on generation failed")

@app.get("/api/v1/comparison/{result_id}")
async def get_comparison(result_id: str):
    """Download comparison image"""
    comparison_path = f"temp/results/{result_id}_comparison.png"
    
    if not os.path.exists(comparison_path):
        raise HTTPException(status_code=404, detail="Comparison not found")
    
    return FileResponse(
        comparison_path,
        media_type="image/png",
        filename=f"comparison_{result_id}.png"
    )

@app.delete("/api/v1/results/{result_id}")
async def delete_result(result_id: str):
    """Delete a result and its associated files"""
    files_to_delete = [
        f"temp/uploads/{result_id}_person.png",
        f"temp/uploads/{result_id}_cloth.png",
        f"temp/results/{result_id}_result.png",
        f"temp/results/{result_id}_comparison.png"
    ]
    
    deleted = 0
    for file_path in files_to_delete:
        if os.path.exists(file_path):
            os.remove(file_path)
            deleted += 1
    
    return {
        "success": True,
        "deleted_files": deleted,
        "message": f"Deleted {deleted} files for result {result_id}"
    }

@app.get("/api/v1/quality-presets")
async def get_quality_presets():
    """Get available quality presets"""
    return {
        "presets": {
            "fast": {
                "denoise_steps": 15,
                "estimated_time": "15-20 seconds",
                "quality": "Good"
            },
            "balanced": {
                "denoise_steps": 30,
                "estimated_time": "30-40 seconds",
                "quality": "Better (Recommended)"
            },
            "high": {
                "denoise_steps": 50,
                "estimated_time": "50-60 seconds",
                "quality": "Best"
            }
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
