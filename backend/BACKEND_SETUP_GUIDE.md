# Backend Setup Guide: Local vs Render

## Quick Fix: Database Reset

Your database schema is out of sync. Run:

```bash
cd backend
python reset_database.py
```

This will:
- Drop all tables (PostgreSQL) or clear SQLite
- Recreate tables with latest schema (including `age`, `gender`, `chest_cm`, etc.)

**⚠️ Warning:** This **deletes all data**. Only run on development DBs.

---

## Local vs Render: Which to Use?

### **Render (Online) - RECOMMENDED for Production**

**Pros:**
- ✅ Always accessible (no need to run server locally)
- ✅ Works from any device/network
- ✅ No port conflicts
- ✅ HTTPS by default
- ✅ Better for testing mobile apps (can't hit localhost from phone)

**Cons:**
- ⚠️ **Cold start delay** (~30-60 seconds first request after inactivity)
- ⚠️ Free tier has resource limits
- ⚠️ Slower than localhost for rapid iteration

**When to use:**
- Testing with mobile devices
- Sharing with others
- Production deployment
- When you want "always on" backend

**Setup:**
- Default in `api_client.dart` is already `https://virtue-try-on.onrender.com`
- Just run: `flutter run -d chrome` (no flags needed)

---

### **Localhost - RECOMMENDED for Development**

**Pros:**
- ✅ **Instant responses** (no network latency)
- ✅ **Fast iteration** (restart server quickly)
- ✅ **Full control** (logs, debugging, breakpoints)
- ✅ **No cold starts**
- ✅ **Free** (no resource limits)

**Cons:**
- ❌ Only accessible on your machine
- ❌ Can't test from mobile device easily
- ❌ Need to keep server running
- ❌ Port conflicts possible

**When to use:**
- Rapid development/debugging
- Testing API changes quickly
- When you need detailed logs
- Local database testing

**Setup:**
```bash
# Terminal 1: Backend
cd backend
python reset_database.py  # First time only
uvicorn complete_api:app --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd frontend
flutter run -d chrome --dart-define=API_BASE_URL=http://localhost:8000
```

---

## Current Configuration

**Default:** Render (`https://virtue-try-on.onrender.com`)

**To switch to localhost:**
```bash
flutter run -d chrome --dart-define=API_BASE_URL=http://localhost:8000
```

**To switch back to Render:**
```bash
flutter run -d chrome  # Uses default
```

---

## Troubleshooting

### "column users.age does not exist"
**Fix:** Run `python reset_database.py` to sync schema.

### "Request timeout" on Render
**Cause:** Cold start (first request after inactivity)
**Fix:** Wait 30-60 seconds, then retry. Subsequent requests are fast.

### "Connection refused" on localhost
**Fix:** Make sure backend is running:
```bash
cd backend
uvicorn complete_api:app --host 0.0.0.0 --port 8000
```

### Flutter can't reach localhost
**For Chrome:** Use `http://localhost:8000`
**For Android Emulator:** Use `http://10.0.2.2:8000`
**For iOS Simulator:** Use `http://localhost:8000`
**For Physical Device:** Use your PC's IP (e.g., `http://192.168.1.100:8000`)

---

## Recommendation

**For now (development):**
1. Use **localhost** for fast iteration
2. Run `python reset_database.py` to fix schema
3. Test registration/login locally
4. Once working, switch to Render for mobile testing

**For production:**
- Use **Render** (already configured as default)
- Ensure Render DB schema is also updated (may need to run migrations there too)
