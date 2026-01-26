# Virtue Try-On Backend

AI-powered virtual try-on system using **frogleo/AI-Clothes-Changer** HuggingFace Space.

## Features

✅ **Realistic Cloth Fitting** - Uses AI to realistically fit clothes onto person images  
✅ **Cloud-Based Processing** - No need to download large models locally  
✅ **Fast Setup** - Just add your HuggingFace token and run  
✅ **Flutter Integration Ready** - Backend API designed for mobile integration  

## Quick Start

### 1. Prerequisites

- Python 3.11 (recommended)
- HuggingFace Account & Token ([Get one here](https://huggingface.co/settings/tokens))

### 2. Setup

```powershell
# Navigate to backend folder
cd backend

# Create virtual environment
python -m venv venv_py311

# Activate it
.\venv_py311\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

Create a `.env` file in the `backend` folder:

```env
HF_TOKEN=your_huggingface_token_here
USE_GRADIO_SPACE=True
```

### 4. Test Virtual Try-On

```powershell
python run_with_real_images.py
```

This will:
- Load test images from `test_images/`
- Call the frogleo/AI-Clothes-Changer Space
- Generate a virtual try-on result
- Save it to `static/generated_outputs/real_tryon.png`

### 5. View Results

Open the generated image:
```powershell
start static/generated_outputs/real_tryon.png
```

## How It Works

### Architecture

```
User Image + Cloth Image
         ↓
    AI Service (Backend)
         ↓
frogleo/AI-Clothes-Changer (HuggingFace Space via API)
         ↓
  Generated Try-On Result
```

### Key Components

1. **`app/services/gradio_vton_service.py`** - Gradio Space client
2. **`app/services/ai_service.py`** - Main AI service router
3. **`app/core/config.py`** - Configuration management
4. **`run_with_real_images.py`** - Test script
5. **`run_gradio_vton.py`** - Direct Gradio Space test

## Configuration Options

In `.env` file:

```env
# Required
HF_TOKEN=your_token_here

# Space Configuration
USE_GRADIO_SPACE=True  # Set to False to use local models
GRADIO_SPACE_NAME=frogleo/AI-Clothes-Changer

# Generation Parameters
VTON_DENOISE_STEPS=30  # Higher = better quality, slower (10-50)
VTON_SEED=42  # For reproducible results
```

## API Usage

### Python

```python
from app.services.ai_service import AIService
import asyncio

async def try_on():
    service = AIService()
    
    success = await service.generate_tryon(
        user_image_path="path/to/person.png",
        cloth_image_path="path/to/cloth.png",
        output_path="output/result.png"
    )
    
    if success:
        print("✅ Try-on successful!")
    
asyncio.run(try_on())
```

### Direct Gradio Space

```python
from app.services.gradio_vton_service import GradioVTONService

service = GradioVTONService()

result = service.generate_tryon(
    person_image_path="person.png",
    cloth_image_path="cloth.png",
    output_path="result.png",
    denoise_steps=30,
    seed=42
)
```

## Flutter Integration

See [FLUTTER_INTEGRATION.md](FLUTTER_INTEGRATION.md) for detailed integration guide.

**Key Points:**
- No need for lightweight models on the client
- All AI processing happens on the backend
- Flutter app just sends images and receives results
- Use REST API or direct HTTP calls

## Troubleshooting

### "Invalid user token" error

- Check that `HF_TOKEN` is correctly set in `.env`
- Verify your token at https://huggingface.co/settings/tokens
- Ensure the token has READ access

### "Space is not accessible"

- Check your internet connection
- Verify the Space is online: https://huggingface.co/spaces/frogleo/AI-Clothes-Changer
- Wait a few minutes if the Space is starting up

### Slow generation

- The Space API can take 30-60 seconds
- Consider reducing `VTON_DENOISE_STEPS` (e.g., 20 instead of 30)
- This is normal for cloud-based AI processing

## Project Structure

```
backend/
├── app/
│   ├── services/
│   │   ├── ai_service.py          # Main AI service router
│   │   └── gradio_vton_service.py # Gradio Space client
│   └── core/
│       └── config.py               # Configuration
├── test_images/                    # Test images
├── static/
│   ├── generated_outputs/          # Final results
│   └── intermediate_outputs/       # Processing stages
├── requirements.txt                # Dependencies
├── .env                            # Configuration (create this)
├── run_with_real_images.py        # Test script
└── run_gradio_vton.py             # Direct Gradio test

```

## Dependencies

Core dependencies:
- `fastapi` - Web framework
- `gradio_client` - HuggingFace Space API client
- `pillow` - Image processing
- `python-dotenv` - Environment variables

See `requirements.txt` for full list.

## Model Information

**Space:** [frogleo/AI-Clothes-Changer](https://huggingface.co/spaces/frogleo/AI-Clothes-Changer)

- Uses state-of-the-art diffusion models for virtual try-on
- Preserves cloth patterns and textures
- Handles various clothing types
- No local model download required

## License

This project uses HuggingFace Spaces which have their own licenses. Check the Space page for details.

## Support

For issues or questions:
1. Check the HuggingFace Space: https://huggingface.co/spaces/frogleo/AI-Clothes-Changer
2. Verify your `.env` configuration
3. Check the terminal output for error messages
