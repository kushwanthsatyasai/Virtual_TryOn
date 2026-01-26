# 🔐 Authentication Guide - How to Authorize

## Quick Start

Your server uses **JWT (JSON Web Token)** authentication. Here's how to use it:

---

## Method 1: Using Swagger UI (API Docs) - Easiest! 👍

### Step 1: Open API Docs

Visit: http://localhost:8000/docs

### Step 2: Register a New User

1. Find `POST /auth/register` endpoint
2. Click **"Try it out"**
3. Fill in the request body:

```json
{
  "email": "test@example.com",
  "username": "testuser",
  "password": "securepassword123",
  "full_name": "Test User"
}
```

4. Click **"Execute"**
5. You'll get a response with a **token**:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "test@example.com",
    "username": "testuser",
    "full_name": "Test User",
    "is_premium": false
  }
}
```

### Step 3: Authorize in Swagger

1. **Copy the `access_token`** from the response
2. Scroll to the top of the page
3. Click the **🔓 Authorize** button (green lock icon)
4. In the popup, paste your token in the "Value" field:
   ```
   Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```
   *(Note: Type "Bearer " followed by your token)*
5. Click **"Authorize"**
6. Click **"Close"**

### Step 4: Test Protected Endpoints

Now you can call any protected endpoint! Try:
- `GET /auth/me` - Get your profile
- `POST /api/v1/chat/send` - Send a chat message
- `GET /api/v1/recommendations` - Get recommendations

All authenticated endpoints will now work! ✅

---

## Method 2: Using cURL (Command Line)

### Step 1: Register a User

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "securepassword123",
    "full_name": "Test User"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {...}
}
```

### Step 2: Save the Token

Copy the `access_token` value.

### Step 3: Use Token in Requests

```bash
# Store token in variable (PowerShell)
$token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Make authenticated request
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer $token"
```

---

## Method 3: Using Postman

### Step 1: Register User

1. Create new request: `POST http://localhost:8000/auth/register`
2. Set Headers: `Content-Type: application/json`
3. Body (raw JSON):
```json
{
  "email": "test@example.com",
  "username": "testuser",
  "password": "securepassword123",
  "full_name": "Test User"
}
```
4. Click **Send**
5. **Copy the `access_token`** from response

### Step 2: Set Authorization

For all future requests:
1. Go to **Authorization** tab
2. Type: Select **"Bearer Token"**
3. Token: Paste your `access_token`
4. Save

Now all requests will include the token! ✅

---

## Method 4: Using Python

### Register and Get Token

```python
import requests

BASE_URL = "http://localhost:8000"

# Register
response = requests.post(
    f"{BASE_URL}/auth/register",
    json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "securepassword123",
        "full_name": "Test User"
    }
)

data = response.json()
token = data['access_token']
print(f"Token: {token}")

# Use token for authenticated requests
headers = {"Authorization": f"Bearer {token}"}

# Get user profile
profile = requests.get(f"{BASE_URL}/auth/me", headers=headers)
print(profile.json())

# Send chat message
chat_response = requests.post(
    f"{BASE_URL}/api/v1/chat/send",
    headers=headers,
    json={"message": "What should I wear to a wedding?"}
)
print(chat_response.json())
```

---

## Method 5: Login (If Already Registered)

If you already have an account, use login instead:

### API Docs:
1. Find `POST /auth/login`
2. Click "Try it out"
3. Fill in **form data** (not JSON!):
   - username: `testuser`
   - password: `securepassword123`
4. Execute
5. Copy token and authorize as before

### cURL:
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=securepassword123"
```

### Python:
```python
response = requests.post(
    f"{BASE_URL}/auth/login",
    data={  # Note: data, not json
        "username": "testuser",
        "password": "securepassword123"
    }
)
token = response.json()['access_token']
```

---

## 📱 Flutter Integration

### Authentication Service

```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

class AuthService {
  final String baseUrl = 'http://your-api-url';
  String? _token;

  // Register
  Future<Map<String, dynamic>> register({
    required String email,
    required String username,
    required String password,
    String? fullName,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/register'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({
        'email': email,
        'username': username,
        'password': password,
        'full_name': fullName,
      }),
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      _token = data['access_token'];
      // Save token to secure storage
      await _saveToken(_token!);
      return data;
    }
    throw Exception('Registration failed');
  }

  // Login
  Future<Map<String, dynamic>> login({
    required String username,
    required String password,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/login'),
      headers: {'Content-Type': 'application/x-www-form-urlencoded'},
      body: {
        'username': username,
        'password': password,
      },
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      _token = data['access_token'];
      await _saveToken(_token!);
      return data;
    }
    throw Exception('Login failed');
  }

  // Get headers with token
  Map<String, String> getHeaders() {
    return {
      'Authorization': 'Bearer $_token',
      'Content-Type': 'application/json',
    };
  }

  // Make authenticated request
  Future<http.Response> get(String endpoint) async {
    return await http.get(
      Uri.parse('$baseUrl$endpoint'),
      headers: getHeaders(),
    );
  }

  Future<http.Response> post(String endpoint, Map<String, dynamic> body) async {
    return await http.post(
      Uri.parse('$baseUrl$endpoint'),
      headers: getHeaders(),
      body: json.encode(body),
    );
  }

  // Save token to secure storage
  Future<void> _saveToken(String token) async {
    // Use flutter_secure_storage
    final storage = FlutterSecureStorage();
    await storage.write(key: 'auth_token', value: token);
  }

  // Load token from secure storage
  Future<void> loadToken() async {
    final storage = FlutterSecureStorage();
    _token = await storage.read(key: 'auth_token');
  }

  // Check if logged in
  bool isLoggedIn() => _token != null;

  // Logout
  Future<void> logout() async {
    _token = null;
    final storage = FlutterSecureStorage();
    await storage.delete(key: 'auth_token');
  }
}
```

### Usage in Flutter

```dart
final authService = AuthService();

// Register
try {
  final result = await authService.register(
    email: 'user@example.com',
    username: 'username',
    password: 'password123',
    fullName: 'John Doe',
  );
  
  print('Registered: ${result['user']['username']}');
  
  // Now can make authenticated requests
  final profile = await authService.get('/auth/me');
  
} catch (e) {
  print('Error: $e');
}

// Login
try {
  await authService.login(
    username: 'username',
    password: 'password123',
  );
  
  // Make authenticated request
  final recommendations = await authService.get('/api/v1/recommendations');
  
} catch (e) {
  print('Error: $e');
}
```

---

## 🔑 Token Information

### Token Format
Your JWT token looks like:
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VybmFtZSIsImV4cCI6MTYxNjI1MjkwOH0.xxx
```

It contains:
- **Header**: Algorithm and token type
- **Payload**: User info (username, expiration)
- **Signature**: Verification

### Token Expiration
- **Default**: 30 minutes (configurable in `.env`)
- When expired: You'll get `401 Unauthorized`
- Solution: Login again to get a new token

### Update Expiration Time

Edit `backend/.env`:
```env
ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24 hours
```

---

## 🛡️ Security Best Practices

### ✅ DO:
- Store tokens securely (flutter_secure_storage, encrypted storage)
- Send tokens over HTTPS only (in production)
- Logout when done (clear token)
- Use strong passwords
- Handle token expiration gracefully

### ❌ DON'T:
- Store tokens in plain text
- Share tokens publicly
- Hardcode tokens in code
- Send tokens in URLs
- Use weak passwords

---

## 🧪 Quick Test Script

Save as `test_auth.py`:

```python
import requests
import json

BASE_URL = "http://localhost:8000"

def test_authentication():
    print("="*60)
    print("AUTHENTICATION TEST")
    print("="*60)
    
    # 1. Register
    print("\n1. Registering user...")
    register_response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": "demo@example.com",
            "username": "demouser",
            "password": "demo123456",
            "full_name": "Demo User"
        }
    )
    
    if register_response.status_code == 200:
        data = register_response.json()
        token = data['access_token']
        print(f"✅ Registered successfully!")
        print(f"   User: {data['user']['username']}")
        print(f"   Token: {token[:50]}...")
    else:
        print(f"❌ Registration failed: {register_response.text}")
        return
    
    # 2. Test authenticated endpoint
    print("\n2. Testing authenticated endpoint...")
    headers = {"Authorization": f"Bearer {token}"}
    
    profile_response = requests.get(
        f"{BASE_URL}/auth/me",
        headers=headers
    )
    
    if profile_response.status_code == 200:
        profile = profile_response.json()
        print(f"✅ Authentication working!")
        print(f"   Profile: {json.dumps(profile, indent=2)}")
    else:
        print(f"❌ Authentication failed: {profile_response.text}")
    
    # 3. Test chat (if OpenAI key is set)
    print("\n3. Testing AI chat...")
    chat_response = requests.post(
        f"{BASE_URL}/api/v1/chat/send",
        headers=headers,
        json={"message": "Hello! Can you help me?"}
    )
    
    if chat_response.status_code == 200:
        chat_data = chat_response.json()
        print(f"✅ Chat working!")
        print(f"   AI Response: {chat_data.get('message', 'N/A')[:100]}...")
    else:
        print(f"⚠️  Chat requires OpenAI API key: {chat_response.text[:100]}")
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)

if __name__ == "__main__":
    test_authentication()
```

Run it:
```bash
python test_auth.py
```

---

## 🆘 Troubleshooting

### "401 Unauthorized"
- **Cause**: Invalid or expired token
- **Fix**: Login again to get a new token

### "403 Forbidden"
- **Cause**: Token valid but insufficient permissions
- **Fix**: Check if endpoint requires specific user role

### "422 Validation Error"
- **Cause**: Missing or invalid fields
- **Fix**: Check request body matches API schema

### "User already exists"
- **Cause**: Email or username already registered
- **Fix**: Use `/auth/login` instead or choose different credentials

---

## ✅ Summary

### To Authorize:

1. **Register**: `POST /auth/register` → Get token
2. **Or Login**: `POST /auth/login` → Get token  
3. **Use Token**: Add `Authorization: Bearer <token>` header
4. **In Swagger**: Click 🔓 Authorize button → Paste token

### Token Lifespan:
- Default: 30 minutes
- Configurable in `.env`: `ACCESS_TOKEN_EXPIRE_MINUTES`

### Protected Endpoints:
All endpoints except:
- `POST /auth/register`
- `POST /auth/login`
- `GET /` (home)
- `GET /health`

**You're now ready to use all authenticated features!** 🎉

---

**Quick Start**: 
1. Open http://localhost:8000/docs
2. Try `POST /auth/register`
3. Copy token
4. Click 🔓 Authorize
5. Test any endpoint!
