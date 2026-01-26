# Flutter Integration Guide

This guide shows how to integrate the Virtual Try-On backend with your Flutter app.

## Overview

**No client-side models needed!** All AI processing happens on the backend. Your Flutter app simply:
1. Captures/selects person and cloth images
2. Sends them to the backend API
3. Receives the generated try-on result

## Backend API Setup

### Option 1: Direct Gradio Space (Recommended for Testing)

Your Flutter app can directly call the HuggingFace Space API:

```dart
import 'package:http/http.dart' as http;
import 'dart:io';
import 'dart:convert';

Future<File> generateVirtualTryOn({
  required File personImage,
  required File clothImage,
  int denoiseSteps = 30,
  int seed = 42,
}) async {
  const String spaceUrl = 'https://frogleo-ai-clothes-changer.hf.space';
  
  // Create multipart request
  var request = http.MultipartRequest(
    'POST',
    Uri.parse('$spaceUrl/run/infer'),
  );
  
  // Add images
  request.files.add(
    await http.MultipartFile.fromPath('person', personImage.path),
  );
  request.files.add(
    await http.MultipartFile.fromPath('garment', clothImage.path),
  );
  
  // Add parameters
  request.fields['denoise_steps'] = denoiseSteps.toString();
  request.fields['seed'] = seed.toString();
  
  // Send request
  var response = await request.send();
  
  if (response.statusCode == 200) {
    // Save response to file
    final bytes = await response.stream.toBytes();
    final tempDir = await getTemporaryDirectory();
    final file = File('${tempDir.path}/tryon_result.png');
    await file.writeAsBytes(bytes);
    return file;
  } else {
    throw Exception('Virtual try-on failed');
  }
}
```

### Option 2: Your Own Backend (Recommended for Production)

For production, you'll want your own backend server:

#### 1. Create FastAPI Endpoint

Add this to your backend (e.g., `main.py`):

```python
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from app.services.ai_service import AIService
import uuid
import os

app = FastAPI()
ai_service = None

@app.on_event("startup")
async def startup():
    global ai_service
    ai_service = AIService()

@app.post("/api/v1/try-on")
async def virtual_try_on(
    person: UploadFile = File(...),
    cloth: UploadFile = File(...),
    denoise_steps: int = 30,
    seed: int = 42
):
    # Generate unique session ID
    session_id = str(uuid.uuid4())
    
    # Save uploaded files
    person_path = f"temp/{session_id}_person.png"
    cloth_path = f"temp/{session_id}_cloth.png"
    output_path = f"temp/{session_id}_result.png"
    
    os.makedirs("temp", exist_ok=True)
    
    with open(person_path, "wb") as f:
        f.write(await person.read())
    
    with open(cloth_path, "wb") as f:
        f.write(await cloth.read())
    
    # Generate try-on
    success = await ai_service.generate_tryon(
        user_image_path=person_path,
        cloth_image_path=cloth_path,
        output_path=output_path,
        session_id=session_id
    )
    
    if success and os.path.exists(output_path):
        return FileResponse(
            output_path,
            media_type="image/png",
            filename="tryon_result.png"
        )
    else:
        return {"error": "Try-on generation failed"}, 500

@app.get("/health")
async def health_check():
    return {"status": "ok"}
```

#### 2. Run the Backend

```powershell
# In backend folder
uvicorn main:app --host 0.0.0.0 --port 8000
```

#### 3. Flutter Integration

```dart
import 'package:http/http.dart' as http;
import 'dart:io';

class VirtualTryOnService {
  static const String baseUrl = 'http://YOUR_SERVER_IP:8000/api/v1';
  
  Future<File> generateTryOn({
    required File personImage,
    required File clothImage,
  }) async {
    var request = http.MultipartRequest(
      'POST',
      Uri.parse('$baseUrl/try-on'),
    );
    
    // Add images
    request.files.add(
      await http.MultipartFile.fromPath('person', personImage.path),
    );
    request.files.add(
      await http.MultipartFile.fromPath('cloth', clothImage.path),
    );
    
    // Optional parameters
    request.fields['denoise_steps'] = '30';
    request.fields['seed'] = '42';
    
    // Send request
    var response = await request.send();
    
    if (response.statusCode == 200) {
      // Save result
      final bytes = await response.stream.toBytes();
      final tempDir = await getTemporaryDirectory();
      final file = File('${tempDir.path}/tryon_${DateTime.now().millisecondsSinceEpoch}.png');
      await file.writeAsBytes(bytes);
      return file;
    } else {
      throw Exception('Try-on failed: ${response.statusCode}');
    }
  }
  
  Future<bool> checkHealth() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/../health'));
      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }
}
```

## Flutter UI Example

```dart
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'dart:io';

class VirtualTryOnScreen extends StatefulWidget {
  @override
  _VirtualTryOnScreenState createState() => _VirtualTryOnScreenState();
}

class _VirtualTryOnScreenState extends State<VirtualTryOnScreen> {
  final ImagePicker _picker = ImagePicker();
  final VirtualTryOnService _service = VirtualTryOnService();
  
  File? _personImage;
  File? _clothImage;
  File? _resultImage;
  bool _isProcessing = false;
  
  Future<void> _pickImage(ImageSource source, bool isPerson) async {
    final XFile? image = await _picker.pickImage(source: source);
    if (image != null) {
      setState(() {
        if (isPerson) {
          _personImage = File(image.path);
        } else {
          _clothImage = File(image.path);
        }
      });
    }
  }
  
  Future<void> _generateTryOn() async {
    if (_personImage == null || _clothImage == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Please select both images')),
      );
      return;
    }
    
    setState(() {
      _isProcessing = true;
      _resultImage = null;
    });
    
    try {
      final result = await _service.generateTryOn(
        personImage: _personImage!,
        clothImage: _clothImage!,
      );
      
      setState(() {
        _resultImage = result;
        _isProcessing = false;
      });
    } catch (e) {
      setState(() {
        _isProcessing = false;
      });
      
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $e')),
      );
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Virtual Try-On')),
      body: SingleChildScrollView(
        padding: EdgeInsets.all(16),
        child: Column(
          children: [
            // Person Image
            _buildImageSection(
              title: 'Person',
              image: _personImage,
              onTap: () => _pickImage(ImageSource.gallery, true),
            ),
            
            SizedBox(height: 16),
            
            // Cloth Image
            _buildImageSection(
              title: 'Cloth',
              image: _clothImage,
              onTap: () => _pickImage(ImageSource.gallery, false),
            ),
            
            SizedBox(height: 24),
            
            // Generate Button
            ElevatedButton(
              onPressed: _isProcessing ? null : _generateTryOn,
              child: _isProcessing
                  ? Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        ),
                        SizedBox(width: 12),
                        Text('Generating...'),
                      ],
                    )
                  : Text('Generate Try-On'),
              style: ElevatedButton.styleFrom(
                padding: EdgeInsets.symmetric(horizontal: 32, vertical: 16),
              ),
            ),
            
            SizedBox(height: 24),
            
            // Result
            if (_resultImage != null)
              Card(
                child: Column(
                  children: [
                    Padding(
                      padding: EdgeInsets.all(8),
                      child: Text(
                        'Result',
                        style: Theme.of(context).textTheme.headline6,
                      ),
                    ),
                    Image.file(_resultImage!),
                  ],
                ),
              ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildImageSection({
    required String title,
    required File? image,
    required VoidCallback onTap,
  }) {
    return Card(
      child: InkWell(
        onTap: onTap,
        child: Container(
          height: 200,
          width: double.infinity,
          child: image != null
              ? Image.file(image, fit: BoxFit.cover)
              : Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(Icons.add_photo_alternate, size: 48),
                    SizedBox(height: 8),
                    Text('Select $title Image'),
                  ],
                ),
        ),
      ),
    );
  }
}
```

## Required Flutter Dependencies

Add to your `pubspec.yaml`:

```yaml
dependencies:
  flutter:
    sdk: flutter
  http: ^1.1.0
  image_picker: ^1.0.4
  path_provider: ^2.1.1
```

## Deployment Considerations

### Backend Hosting

For production, deploy your backend to:
- **AWS EC2** - Full control, good for scaling
- **Google Cloud Run** - Serverless, auto-scaling
- **Heroku** - Easy deployment, managed
- **DigitalOcean App Platform** - Simple, cost-effective

### Performance Tips

1. **Image Compression**: Compress images before upload to reduce transfer time
2. **Caching**: Cache results for previously tried combinations
3. **Progress Indicators**: Show loading states (30-60 seconds is normal)
4. **Error Handling**: Implement retry logic for network failures
5. **Quality Settings**: Allow users to choose quality (lower steps = faster)

### Security

1. Add API authentication (JWT tokens)
2. Rate limiting to prevent abuse
3. Image size validation
4. HTTPS for all requests
5. Store user tokens securely

## Example .env Configuration

```env
# HuggingFace Token (required)
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxx

# Space Configuration
USE_GRADIO_SPACE=True
GRADIO_SPACE_NAME=frogleo/AI-Clothes-Changer

# Generation Settings
VTON_DENOISE_STEPS=30  # 10-50, higher = better quality
VTON_SEED=42

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=False  # Set to False in production
```

## Testing

1. **Backend Health Check**:
   ```
   http://YOUR_SERVER_IP:8000/health
   ```

2. **Test with cURL**:
   ```bash
   curl -X POST http://YOUR_SERVER_IP:8000/api/v1/try-on \
     -F "person=@person.jpg" \
     -F "cloth=@cloth.jpg" \
     --output result.png
   ```

3. **Flutter Test**:
   - Use test images from `backend/test_images/`
   - Verify response times
   - Test error scenarios

## Troubleshooting

### "Connection refused"
- Ensure backend is running
- Check firewall settings
- Verify correct IP/port

### "Invalid user token"
- Check HF_TOKEN in backend `.env`
- Verify token at https://huggingface.co/settings/tokens

### Slow responses
- Normal: 30-60 seconds for generation
- Reduce `denoise_steps` for faster results
- Consider caching frequent requests

## Next Steps

1. Set up your backend server
2. Implement Flutter UI
3. Test with sample images
4. Add error handling
5. Implement caching
6. Deploy to production

For questions or issues, check the main README.md or HuggingFace Space documentation.
