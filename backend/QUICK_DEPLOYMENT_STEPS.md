# Quick Deployment Steps (5 Minutes)

## 🚀 Deploy to Render in 5 Steps

### Step 1: Create GitHub Repository (2 min)

```bash
cd C:\Users\kushw\virtue_try_on
git init
git add .
git commit -m "Ready for deployment"
```

Go to GitHub.com → Create new repository → Copy the URL

```bash
git remote add origin https://github.com/YOUR_USERNAME/virtue-tryon.git
git branch -M main
git push -u origin main
```

### Step 2: Sign up on Render (1 min)

1. Go to https://render.com
2. Click "Get Started for Free"
3. Sign up with GitHub

### Step 3: Deploy (1 min)

1. Click "New +" → "Web Service"
2. Click "Connect" next to your repository
3. Fill in:
   - **Name**: `virtue-tryon-api`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn complete_api:app --host 0.0.0.0 --port $PORT`
4. Click "Create Web Service"

### Step 4: Add Environment Variables (1 min)

In Render dashboard → Environment:

Add these:
- `SECRET_KEY`: (click "Generate" button)
- `HF_TOKEN`: (your Hugging Face token from .env file)

Click "Save Changes"

### Step 5: Get Your URL

After deployment completes (5-10 min), you'll see:

```
Your service is live at https://virtue-tryon-api.onrender.com
```

**That's your backend URL!** Copy it.

---

## 📱 Connect Flutter App

### Option A: Quick Test (No code change needed)

Update just one line in your Flutter code:

```dart
final baseUrl = 'https://virtue-tryon-api.onrender.com';
```

### Option B: Production Setup (Recommended)

1. Create `lib/config/api_config.dart`:

```dart
class ApiConfig {
  static const String baseUrl = 'https://YOUR-APP-NAME.onrender.com';
}
```

2. Use it everywhere:

```dart
import 'package:your_app/config/api_config.dart';

final url = '${ApiConfig.baseUrl}/api/v1/auth/login';
```

---

## ✅ Test Your Deployment

### Test 1: Open in Browser

Visit: `https://your-app-name.onrender.com/docs`

You should see the API documentation!

### Test 2: Test Registration

Use Postman or this curl command:

```bash
curl -X POST https://your-app-name.onrender.com/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "Test123!",
    "full_name": "Test User"
  }'
```

### Test 3: Test from Flutter

Run your Flutter app and try to:
1. Register a new account
2. Login
3. Upload images for try-on

---

## 🎯 Important Notes

### Free Tier Limitations:
- ⚠️ App "sleeps" after 15 min of inactivity
- ⚠️ Takes ~30 seconds to "wake up" on first request
- ✅ Perfect for development/testing/demo
- ✅ Upgrade to paid ($7/month) for always-on

### First Request After Sleep:
Your Flutter app should show a loading indicator saying "Starting up server..." for the first request.

### File Storage:
- Images are stored temporarily
- Use cloud storage (AWS S3, Cloudinary) for production

---

## 🔧 Troubleshooting

### Problem: "Build Failed"
**Solution**: Check build logs. Usually missing dependency in `requirements.txt`

### Problem: "Application Error"
**Solution**: Check logs in Render dashboard. Usually missing environment variable.

### Problem: "Connection Timeout"
**Solution**: First request after sleep takes time. Wait 30 seconds and retry.

### Problem: "CORS Error"
**Solution**: Already fixed in code. If still happening, check browser console for exact error.

---

## 📊 Monitor Your App

### View Logs:
Render Dashboard → Your Service → Logs tab

### Check Status:
```
GET https://your-app-name.onrender.com/health
```

Should return: `{"status": "healthy"}`

---

## 💡 Pro Tips

1. **Keep App Awake**: Use a service like UptimeRobot to ping your app every 5 minutes
2. **Faster Deploys**: Enable "Auto-Deploy" in Render for automatic updates when you push to GitHub
3. **Custom Domain**: In Render, go to Settings → Add custom domain
4. **Database**: For production, use PostgreSQL instead of SQLite

---

## 🎉 You're Done!

Your app is now live and accessible from anywhere in the world!

**API Base URL**: `https://your-app-name.onrender.com`

Next steps:
1. Update Flutter app with this URL
2. Test all features
3. Build release APK/IPA
4. Share with users!

---

**Need help?** Check the full guide: `DEPLOYMENT_GUIDE.md`
