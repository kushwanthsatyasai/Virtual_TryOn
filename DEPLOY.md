# Deploy to Render

## Backend (API)

1. **Connect repo**  
   In [Render Dashboard](https://dashboard.render.com), click **New** → **Web Service**. Connect your Git repo and select the **backend** directory as root (or set **Root Directory** to `backend`).

2. **Build & start**  
   Render will use `backend/render.yaml` if you use **Blueprint**; or set manually:
   - **Build Command:** `pip install --upgrade pip && pip install -r requirements.txt`
   - **Start Command:** `uvicorn complete_api:app --host 0.0.0.0 --port $PORT --workers 1`
   - **Environment:** Python 3.11

3. **Environment variables**  
   In the service’s **Environment** tab, set:
   - `SECRET_KEY` (required; use a long random string, or let Render generate)
   - `DATABASE_URL` (optional; default in render.yaml is SQLite; for production you can use Neon/Postgres from Render env)
   - `HF_TOKEN` (optional; for Hugging Face try-on spaces)
   - `GEMINI_API_KEY` (optional; for AI chat)
   - **`CLOUDINARY_URL`** (recommended for try-on on mobile): Render’s filesystem is ephemeral, so try-on result images saved to disk disappear after a restart. To make **Recent Looks** and try-on results visible on your mobile app, set `CLOUDINARY_URL` so results are uploaded to Cloudinary and served via persistent URLs.
     - Sign up at [cloudinary.com](https://cloudinary.com) (free tier).
     - In Dashboard → **Settings** → **API Keys**, copy your **Cloud name**, **API Key**, and **API Secret**.
     - Set `CLOUDINARY_URL` to: `cloudinary://API_KEY:API_SECRET@CLOUD_NAME` (replace with your values).

4. **Service URL**  
   After deploy, the API URL will be like:  
   `https://virtue-try-on.onrender.com`  
   The Flutter app is already configured to use this as the default API base URL.

---

## Frontend (Flutter Web)

The app defaults to the Render backend: `https://virtue-try-on.onrender.com`. For **local dev**, run with:

```bash
cd frontend
flutter run -d chrome --dart-define=API_BASE_URL=http://localhost:8000
```

To **deploy the Flutter web app** on Render as a Static Site:

1. **Build** (from repo root or `frontend`):
   ```bash
   cd frontend
   flutter build web
   ```
   Output is in `frontend/build/web/`.

2. **Render Static Site**  
   In Render: **New** → **Static Site**. Connect the same repo.
   - **Root Directory:** `frontend`
   - **Build Command:** `flutter pub get && flutter build web`
   - **Publish Directory:** `build/web`

3. **Custom domain (optional)**  
   In the Static Site’s **Settings**, add a custom domain or use the default `*.onrender.com` URL.

---

## Summary

| Component   | Render type   | URL (example)                          |
|------------|---------------|----------------------------------------|
| Backend API| Web Service   | `https://virtue-try-on.onrender.com`|
| Frontend   | Static Site   | `https://your-static-site.onrender.com`|

After both are deployed, open the Static Site URL; the app will call the API on Render by default.
