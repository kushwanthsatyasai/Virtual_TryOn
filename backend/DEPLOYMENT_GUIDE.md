# Complete Deployment Guide: Backend + Flutter Integration

## Overview

This guide will help you:
1. Deploy your FastAPI backend to the cloud
2. Connect your Flutter app to the deployed backend
3. Use your app from anywhere with internet

---

## 🌐 **Deployment Options**

### **Option 1: Render (Recommended - FREE)**
- ✅ Free tier available
- ✅ Easy deployment
- ✅ Automatic HTTPS
- ✅ Good for prototypes/MVPs
- ⚠️ Free tier sleeps after inactivity (30 sec wake-up time)

### **Option 2: Railway**
- ✅ $5 free credit
- ✅ Very easy deployment
- ✅ Fast performance
- ⚠️ No free tier after trial

### **Option 3: Google Cloud Platform (GCP)**
- ✅ $300 free credit (90 days)
- ✅ Professional grade
- ✅ Scalable
- ⚠️ More complex setup

### **Option 4: AWS EC2**
- ✅ Free tier (12 months)
- ✅ Full control
- ⚠️ Complex setup
- ⚠️ Requires DevOps knowledge

### **Option 5: Heroku**
- ⚠️ No longer has free tier
- ⚠️ $5-7/month minimum

---

## 🚀 **RECOMMENDED: Deploy to Render (FREE)**

### **Step 1: Prepare Your Backend**

1. **Create `render.yaml` in your backend folder:**

```yaml
services:
  - type: web
    name: virtue-tryon-api
    env: python
    region: oregon
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn complete_api:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: SECRET_KEY
        generateValue: true
      - key: DATABASE_URL
        value: sqlite:///./virtue_tryon.db
      - key: HF_TOKEN
        sync: false
```

2. **Update `requirements.txt` - Make sure it includes:**

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
sqlalchemy==2.0.23
pydantic==2.5.0
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
bcrypt==4.1.1
pillow==10.1.0
opencv-python-headless==4.8.1.78
numpy==1.26.2
torch==2.1.1
torchvision==0.16.1
mediapipe==0.10.8
gradio_client==0.7.1
requests==2.31.0
faiss-cpu==1.7.4
scikit-image==0.22.0
```

3. **Create `.gitignore` if you don't have one:**

```
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
venv/
venv_py311/
*.db
*.db-journal
.env
test_images/
static/generated_outputs/
temp/
intermediate_outputs_*/
*.log
```

4. **Update `complete_api.py` - Add CORS for Flutter:**

Find the CORS middleware section and update it:

```python
# Enable CORS for Flutter app
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:*",
        "https://*.render.com",
        "*"  # Allow all origins (restrict in production)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

5. **Make sure your app uses environment variable for PORT:**

```python
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
```

### **Step 2: Deploy to Render**

1. **Create a GitHub Repository:**
   ```bash
   cd C:\Users\kushw\virtue_try_on
   git init
   git add .
   git commit -m "Initial commit for deployment"
   ```

2. **Push to GitHub:**
   - Create a new repository on GitHub.com
   - Follow their instructions to push your code:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/virtue-tryon.git
   git branch -M main
   git push -u origin main
   ```

3. **Deploy on Render:**
   - Go to https://render.com
   - Sign up/Login
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Select the `virtue_try_on` repository
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn complete_api:app --host 0.0.0.0 --port $PORT`
   - Click "Create Web Service"

4. **Get Your API URL:**
   - After deployment, you'll get a URL like: `https://virtue-tryon-api.onrender.com`
   - This is your backend URL!

---

## 📱 **Connect Flutter App to Backend**

### **Step 1: Create API Configuration File**

Create `lib/config/api_config.dart`:

```dart
class ApiConfig {
  // Change this to your deployed backend URL
  static const String baseUrl = 'https://virtue-tryon-api.onrender.com';
  
  // For local testing, use:
  // static const String baseUrl = 'http://localhost:8000';
  
  // API Endpoints
  static const String register = '$baseUrl/api/v1/auth/register';
  static const String login = '$baseUrl/api/v1/auth/login';
  static const String virtualTryOn = '$baseUrl/api/v1/virtual-tryon/generate';
  static const String getTryOnHistory = '$baseUrl/api/v1/tryon-history';
  static const String recommendations = '$baseUrl/api/v1/recommendations/smart';
  static const String wardrobe = '$baseUrl/api/v1/wardrobe/items';
  static const String favorites = '$baseUrl/api/v1/favorites';
  static const String chat = '$baseUrl/api/v1/chat/send';
  
  // Timeout duration
  static const Duration timeout = Duration(seconds: 60);
}
```

### **Step 2: Create API Service**

Create `lib/services/api_service.dart`:

```dart
import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../config/api_config.dart';

class ApiService {
  static String? _token;
  
  // Initialize token from storage
  static Future<void> init() async {
    final prefs = await SharedPreferences.getInstance();
    _token = prefs.getString('auth_token');
  }
  
  // Save token
  static Future<void> saveToken(String token) async {
    _token = token;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('auth_token', token);
  }
  
  // Clear token (logout)
  static Future<void> clearToken() async {
    _token = null;
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('auth_token');
  }
  
  // Get headers with authentication
  static Map<String, String> _getHeaders({bool includeAuth = true}) {
    final headers = <String, String>{
      'Content-Type': 'application/json',
    };
    
    if (includeAuth && _token != null) {
      headers['Authorization'] = 'Bearer $_token';
    }
    
    return headers;
  }
  
  // Register user
  static Future<Map<String, dynamic>> register({
    required String email,
    required String password,
    required String fullName,
  }) async {
    try {
      final response = await http.post(
        Uri.parse(ApiConfig.register),
        headers: _getHeaders(includeAuth: false),
        body: jsonEncode({
          'email': email,
          'password': password,
          'full_name': fullName,
        }),
      ).timeout(ApiConfig.timeout);
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        await saveToken(data['access_token']);
        return {'success': true, 'data': data};
      } else {
        return {
          'success': false,
          'error': jsonDecode(response.body)['detail'] ?? 'Registration failed'
        };
      }
    } catch (e) {
      return {'success': false, 'error': 'Network error: $e'};
    }
  }
  
  // Login user
  static Future<Map<String, dynamic>> login({
    required String email,
    required String password,
  }) async {
    try {
      final response = await http.post(
        Uri.parse(ApiConfig.login),
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: {
          'username': email,
          'password': password,
        },
      ).timeout(ApiConfig.timeout);
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        await saveToken(data['access_token']);
        return {'success': true, 'data': data};
      } else {
        return {
          'success': false,
          'error': jsonDecode(response.body)['detail'] ?? 'Login failed'
        };
      }
    } catch (e) {
      return {'success': false, 'error': 'Network error: $e'};
    }
  }
  
  // Virtual Try-On
  static Future<Map<String, dynamic>> virtualTryOn({
    required File personImage,
    required File clothImage,
  }) async {
    try {
      var request = http.MultipartRequest(
        'POST',
        Uri.parse(ApiConfig.virtualTryOn),
      );
      
      // Add auth header
      if (_token != null) {
        request.headers['Authorization'] = 'Bearer $_token';
      }
      
      // Add files
      request.files.add(
        await http.MultipartFile.fromPath('person_image', personImage.path),
      );
      request.files.add(
        await http.MultipartFile.fromPath('cloth_image', clothImage.path),
      );
      
      final streamedResponse = await request.send().timeout(
        Duration(seconds: 120), // Longer timeout for image processing
      );
      
      final response = await http.Response.fromStream(streamedResponse);
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return {'success': true, 'data': data};
      } else {
        return {
          'success': false,
          'error': jsonDecode(response.body)['detail'] ?? 'Try-on failed'
        };
      }
    } catch (e) {
      return {'success': false, 'error': 'Network error: $e'};
    }
  }
  
  // Get Try-On History
  static Future<Map<String, dynamic>> getTryOnHistory({
    int skip = 0,
    int limit = 10,
  }) async {
    try {
      final response = await http.get(
        Uri.parse('${ApiConfig.getTryOnHistory}?skip=$skip&limit=$limit'),
        headers: _getHeaders(),
      ).timeout(ApiConfig.timeout);
      
      if (response.statusCode == 200) {
        return {'success': true, 'data': jsonDecode(response.body)};
      } else {
        return {'success': false, 'error': 'Failed to fetch history'};
      }
    } catch (e) {
      return {'success': false, 'error': 'Network error: $e'};
    }
  }
  
  // Get Recommendations
  static Future<Map<String, dynamic>> getRecommendations({
    int limit = 10,
  }) async {
    try {
      final response = await http.get(
        Uri.parse('${ApiConfig.recommendations}?limit=$limit'),
        headers: _getHeaders(),
      ).timeout(ApiConfig.timeout);
      
      if (response.statusCode == 200) {
        return {'success': true, 'data': jsonDecode(response.body)};
      } else {
        return {'success': false, 'error': 'Failed to fetch recommendations'};
      }
    } catch (e) {
      return {'success': false, 'error': 'Network error: $e'};
    }
  }
  
  // Send Chat Message
  static Future<Map<String, dynamic>> sendChatMessage({
    required String message,
    int? conversationId,
  }) async {
    try {
      final response = await http.post(
        Uri.parse(ApiConfig.chat),
        headers: _getHeaders(),
        body: jsonEncode({
          'message': message,
          'conversation_id': conversationId,
        }),
      ).timeout(ApiConfig.timeout);
      
      if (response.statusCode == 200) {
        return {'success': true, 'data': jsonDecode(response.body)};
      } else {
        return {'success': false, 'error': 'Failed to send message'};
      }
    } catch (e) {
      return {'success': false, 'error': 'Network error: $e'};
    }
  }
}
```

### **Step 3: Update pubspec.yaml**

Add required packages:

```yaml
dependencies:
  flutter:
    sdk: flutter
  http: ^1.1.0
  shared_preferences: ^2.2.2
  image_picker: ^1.0.4
  path_provider: ^2.1.1
```

Then run:
```bash
flutter pub get
```

### **Step 4: Example Login Screen**

Create `lib/screens/login_screen.dart`:

```dart
import 'package:flutter/material.dart';
import '../services/api_service.dart';

class LoginScreen extends StatefulWidget {
  @override
  _LoginScreenState createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _isLoading = false;
  
  Future<void> _login() async {
    setState(() => _isLoading = true);
    
    final result = await ApiService.login(
      email: _emailController.text,
      password: _passwordController.text,
    );
    
    setState(() => _isLoading = false);
    
    if (result['success']) {
      Navigator.pushReplacementNamed(context, '/home');
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(result['error'])),
      );
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Login')),
      body: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            TextField(
              controller: _emailController,
              decoration: InputDecoration(labelText: 'Email'),
              keyboardType: TextInputType.emailAddress,
            ),
            SizedBox(height: 16),
            TextField(
              controller: _passwordController,
              decoration: InputDecoration(labelText: 'Password'),
              obscureText: true,
            ),
            SizedBox(height: 24),
            _isLoading
                ? CircularProgressIndicator()
                : ElevatedButton(
                    onPressed: _login,
                    child: Text('Login'),
                  ),
          ],
        ),
      ),
    );
  }
}
```

### **Step 5: Example Try-On Screen**

Create `lib/screens/tryon_screen.dart`:

```dart
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../services/api_service.dart';

class TryOnScreen extends StatefulWidget {
  @override
  _TryOnScreenState createState() => _TryOnScreenState();
}

class _TryOnScreenState extends State<TryOnScreen> {
  File? _personImage;
  File? _clothImage;
  String? _resultImageUrl;
  bool _isLoading = false;
  final _picker = ImagePicker();
  
  Future<void> _pickPersonImage() async {
    final pickedFile = await _picker.pickImage(source: ImageSource.gallery);
    if (pickedFile != null) {
      setState(() => _personImage = File(pickedFile.path));
    }
  }
  
  Future<void> _pickClothImage() async {
    final pickedFile = await _picker.pickImage(source: ImageSource.gallery);
    if (pickedFile != null) {
      setState(() => _clothImage = File(pickedFile.path));
    }
  }
  
  Future<void> _generateTryOn() async {
    if (_personImage == null || _clothImage == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Please select both images')),
      );
      return;
    }
    
    setState(() => _isLoading = true);
    
    final result = await ApiService.virtualTryOn(
      personImage: _personImage!,
      clothImage: _clothImage!,
    );
    
    setState(() => _isLoading = false);
    
    if (result['success']) {
      setState(() {
        _resultImageUrl = result['data']['result_url'];
      });
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(result['error'])),
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
            GestureDetector(
              onTap: _pickPersonImage,
              child: Container(
                height: 200,
                decoration: BoxDecoration(
                  border: Border.all(color: Colors.grey),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: _personImage == null
                    ? Center(child: Text('Tap to select person image'))
                    : Image.file(_personImage!, fit: BoxFit.cover),
              ),
            ),
            SizedBox(height: 16),
            
            // Cloth Image
            GestureDetector(
              onTap: _pickClothImage,
              child: Container(
                height: 200,
                decoration: BoxDecoration(
                  border: Border.all(color: Colors.grey),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: _clothImage == null
                    ? Center(child: Text('Tap to select cloth image'))
                    : Image.file(_clothImage!, fit: BoxFit.cover),
              ),
            ),
            SizedBox(height: 24),
            
            // Generate Button
            _isLoading
                ? CircularProgressIndicator()
                : ElevatedButton(
                    onPressed: _generateTryOn,
                    child: Text('Generate Try-On'),
                  ),
            
            SizedBox(height: 24),
            
            // Result Image
            if (_resultImageUrl != null)
              Image.network(_resultImageUrl!),
          ],
        ),
      ),
    );
  }
}
```

---

## 🔧 **Testing Your Deployment**

### **Test 1: Check if Backend is Running**

Visit in your browser:
```
https://your-app-name.onrender.com/docs
```

You should see the FastAPI Swagger documentation.

### **Test 2: Test Registration**

Using Postman or curl:
```bash
curl -X POST https://your-app-name.onrender.com/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!",
    "full_name": "Test User"
  }'
```

### **Test 3: Test from Flutter**

1. Update `ApiConfig.baseUrl` to your Render URL
2. Run your Flutter app
3. Try to register/login
4. Try virtual try-on

---

## 🔒 **Security Considerations**

### **1. Environment Variables**

Never commit sensitive data. On Render, add environment variables:
- `SECRET_KEY`: Your JWT secret
- `HF_TOKEN`: Your Hugging Face token
- `DATABASE_URL`: Database connection string

### **2. HTTPS Only**

Always use HTTPS in production. Render provides this automatically.

### **3. Rate Limiting**

Add rate limiting to your API (optional but recommended).

---

## 📊 **Monitoring Your Deployment**

### **Check Logs on Render:**
1. Go to your service dashboard
2. Click "Logs" tab
3. Monitor for errors

### **Check API Health:**
```
GET https://your-app-name.onrender.com/health
```

---

## 💰 **Cost Comparison**

| Platform | Free Tier | Paid |
|----------|-----------|------|
| Render | Yes (sleeps after 15min inactivity) | $7/month |
| Railway | $5 credit | $5/month+ |
| GCP | $300 credit (90 days) | Variable |
| AWS | 12 months free | Variable |
| Heroku | No | $7/month+ |

---

## 🚨 **Common Issues & Solutions**

### **Issue 1: "Connection refused"**
- **Solution**: Make sure backend is using `0.0.0.0` instead of `127.0.0.1`

### **Issue 2: "CORS error"**
- **Solution**: Check CORS middleware in `complete_api.py`

### **Issue 3: "Timeout"**
- **Solution**: Increase timeout in Flutter (virtual try-on takes time)

### **Issue 4: "Module not found"**
- **Solution**: Check all dependencies are in `requirements.txt`

### **Issue 5: "Database locked"**
- **Solution**: Use PostgreSQL instead of SQLite for production

---

## 🎯 **Production Checklist**

- [ ] Backend deployed and accessible
- [ ] HTTPS enabled
- [ ] Environment variables configured
- [ ] CORS properly configured
- [ ] Flutter app points to correct backend URL
- [ ] Authentication tested
- [ ] Virtual try-on tested
- [ ] Error handling implemented
- [ ] Logs monitoring set up
- [ ] Database backed up (if using PostgreSQL)

---

## 📞 **Next Steps**

1. **Deploy backend to Render** (follow Step 2 above)
2. **Get your API URL**
3. **Update Flutter app** with the URL
4. **Test all features**
5. **Build Flutter app for release**:
   ```bash
   flutter build apk --release  # For Android
   flutter build ios --release  # For iOS
   ```

---

**Generated:** 2026-01-26  
**For:** Virtue Try-On Deployment  

Your app will be accessible from anywhere with these configurations!
