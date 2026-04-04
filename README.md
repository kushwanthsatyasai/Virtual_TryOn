# Virtue Try-On

**Virtue Try-On** is a full-stack virtual fashion try-on product: a **Flutter** client talks to a **FastAPI** backend that runs AI garment fitting, optional size guidance from body photos, personalized recommendations, and an AI fashion chat. The system is designed for **web and mobile**, with deployment targets including **Render** (API + static web) and local development.

---

## Repository layout

| Area | Role |
|------|------|
| [`frontend/`](frontend/) | Flutter app (Android, iOS, web, desktop targets). REST client via **Dio**, local persistence for favorites/cart. |
| [`backend/`](backend/) | Python 3.11 **FastAPI** app, SQLAlchemy ORM, JWT auth, AI services, static uploads. |
| [`backend/U-2-Net/`](backend/U-2-Net/) | U²-Net research/training code (submodule-style tree); used in advanced segmentation / fine-tuning workflows documented under backend services. |
| [`DEPLOY.md`](DEPLOY.md) | Step-by-step **Render** deployment (API web service + Flutter web static site). |
| [`backend/README.md`](backend/README.md) | Deeper notes on Hugging Face Gradio Spaces, local vs cloud try-on, and test scripts. |

**Production API entrypoint:** `uvicorn complete_api:app` — the monolithic app in [`backend/complete_api.py`](backend/complete_api.py) is what Render runs (see [`backend/render.yaml`](backend/render.yaml)).

**Alternate / modular app:** [`backend/app/main.py`](backend/app/main.py) mounts versioned routers under `/api/v1` (auth, users, products, virtual-try-on). That layout is useful for incremental development; the Flutter app in this repo is wired to the **`complete_api`** surface (paths below).

---

## High-level architecture

```mermaid
flowchart LR
  subgraph client [Flutter client]
    UI[Screens]
    Dio[Dio HTTP client]
    UI --> Dio
  end

  subgraph api [FastAPI complete_api]
    Auth[JWT auth]
    DB[(SQLAlchemy DB)]
    TryOn[Try-on pipeline]
    Size[Size recommendation]
    Rec[Recommendations]
    Chat[AI chat]
    Auth --> DB
    TryOn --> DB
    Chat --> DB
    Rec --> DB
  end

  subgraph external [External services]
    HF[Hugging Face Gradio Space]
    Gemini[Google Gemini API]
    Cloud[Cloudinary optional]
  end

  Dio --> Auth
  Dio --> TryOn
  Dio --> Size
  Dio --> Rec
  Dio --> Chat
  TryOn --> HF
  TryOn --> Cloud
  Chat --> Gemini
```

1. **Client** sends JSON and multipart requests with optional `Authorization: Bearer <token>`.
2. **Backend** validates JWTs, reads/writes **SQLite** (default) or **PostgreSQL** (e.g. Neon on Render via `DATABASE_URL`).
3. **Virtual try-on** prefers **remote** inference through a **Gradio Client** to a Hugging Face Space (default `frogleo/AI-Clothes-Changer`), with fallback Space logic in code; optional **local** Kolors/diffusers path when `USE_GRADIO_SPACE=False`.
4. **Media:** result and avatar files are stored under `uploads/` and `temp/` and exposed via static mounts; **`CLOUDINARY_URL`** uploads give **persistent HTTPS URLs** on ephemeral hosts (recommended for Render + mobile).

---

## Technology stack

### Frontend

- **Flutter** (Dart SDK `>=3.0.0 <4.0.0`)
- **Dio** for REST, long timeouts for slow try-on jobs
- **shared_preferences**, local stores for favorites/cart
- **image_picker**, **flutter_image_compress**, **mobile_scanner**, **google_sign_in**, **permission_handler**, **flutter_svg**

Default API base URL is defined in [`frontend/lib/services/api_client.dart`](frontend/lib/services/api_client.dart) (overridable with `--dart-define=API_BASE_URL=...`).

### Backend

- **FastAPI**, **Uvicorn**, **Pydantic v2**, **python-multipart**
- **SQLAlchemy 2**, **Alembic** (migrations available in tree); **psycopg2** for Postgres
- **JWT** (`python-jose`), **passlib/bcrypt**
- **AI / CV:** `gradio_client`, **PyTorch**, **diffusers** / **transformers** (local path), **rembg** (ONNX), **MediaPipe** + **OpenCV** (pose for sizing), **FAISS** (visual similarity for recommendations)
- **LLM chat:** `google-genai` (Gemini default), optional OpenAI / Anthropic in dependencies
- **Cloudinary** Python SDK for uploads

---

## Methodologies and design choices

- **REST over HTTP/JSON** for most operations; **multipart/form-data** for image uploads (try-on, profile photo, size image).
- **OAuth2-style password flow** for Swagger compatibility (`POST /auth/login` with form fields) plus a **JSON login** alias (`POST /auth/login-simple`).
- **JWT bearer authentication** for protected routes (`Authorization: Bearer ...`).
- **Lazy service initialization** in `complete_api.py` so cold starts do not load heavy AI stacks until first use.
- **Render-safe startup:** no full `create_all` on deploy; directories created in lifespan; optional DB column ensure for `tryon_history.metadata`.
- **CORS:** permissive (`allow_origins=["*"]`) in `complete_api` for cross-origin Flutter web and mobile tooling.
- **Separation of concerns:** `app/services/*` encapsulate try-on, auth, sizing, chat, recommendations; `app/models/*` define ORM entities.

---

## User workflows (product)

1. **Onboarding / auth:** Register or log in (email/username + password); optional **Google** handoff — see security note below.
2. **Profile:** `GET/PATCH /api/v1/users/me`; upload **full-body photo** for avatar-driven features.
3. **Try-on:** User selects person + garment images; client calls `POST /api/v1/try-on`; backend calls HF Space, saves history, returns `result_url` (path or Cloudinary URL).
4. **Recent looks:** `GET /api/v1/try-on/history` drives home/history UI.
5. **Size help:** `POST` or `GET /api/v1/size/recommend` using uploaded image or stored profile photo + optional height.
6. **Recommendations:** `GET /api/v1/recommendations` blends history, favorites, wardrobe signals, collaborative signals, trending, and **ResNet + FAISS** visual similarity when enabled.
7. **AI stylist chat:** `POST /api/v1/chat/send` with conversation threading stored in DB; backend calls configured LLM (default Gemini).

---

## HTTP API reference (`complete_api`)

Base URL examples:

- **Local:** `http://localhost:8000`
- **Deployed (default in app):** `https://virtue-try-on.onrender.com`

Unless noted, protected routes require header: `Authorization: Bearer <access_token>`.

### Health

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/` | No | Liveness: `{ "status": "alive", ... }` |
| GET | `/health` | No | Health check |

### Authentication & account

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/auth/register` | No | Create user; returns `access_token` + `user` |
| POST | `/auth/login` | No | OAuth2 password form (`username`, `password`) |
| POST | `/auth/login-simple` | No | JSON `{ "username", "password" }` |
| POST | `/auth/google-login` | No | JSON `{ "email", "full_name?", "google_id?", "id_token?" }` — returns token or `needs_signup` |
| POST | `/auth/password-reset` | No | Demo-style reset by email + new password |
| POST | `/auth/password-reset/request-otp` | No | OTP flow start (SMTP if configured) |
| POST | `/auth/password-reset/confirm` | No | OTP + new password |

**Swagger / OpenAPI:** served by FastAPI at `/docs` and `/openapi.json` when the server is running.

### Profile

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/v1/users/me` | Yes | Full profile incl. measurements, `avatar_url` |
| GET | `/api/v1/profile/me` | Yes | Alias of above |
| PATCH | `/api/v1/users/me` | Yes | Partial profile update |
| POST | `/api/v1/profile/full-body-photo` | Yes | Multipart `photo` → updates `avatar_url` (Cloudinary if set) |

### Virtual try-on & history

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/try-on` | Yes | Multipart `person`, `cloth`; optional form fields `product_id`, `product_name`, `product_image_url` |
| GET | `/api/v1/try-on/history` | Yes | Query `skip`, `limit` — list of results with `metadata` |

Static files: `/uploads/*`, `/temp/*` (local dev); production should prefer **Cloudinary** URLs in history.

### Size recommendation

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/size/recommend` | Yes | Multipart `image`; query `user_height_cm`, `garment_type` |
| GET | `/api/v1/size/recommend` | Yes | Uses profile `avatar_url` + query `garment_type` |

### AI chat

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/chat/send` | Yes | JSON `{ "message", "conversation_id?" }` → assistant reply, persisted messages |

### Recommendations

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/v1/recommendations` | Yes | Query `limit`, `category`, `exclude_tried` |

---

## External APIs and integrations

| Integration | Purpose | Configuration |
|-------------|---------|----------------|
| **Hugging Face Gradio** | Virtual try-on inference via Space API | `HF_TOKEN`, `GRADIO_SPACE_NAME`, `USE_GRADIO_SPACE`, `VTON_DENOISE_STEPS`, `VTON_SEED` ([`app/core/config.py`](backend/app/core/config.py)) |
| **Google Gemini** | Default fashion chat LLM | `GEMINI_API_KEY`, optional `GEMINI_MODEL`, `AI_CHAT_PROVIDER=gemini` |
| **OpenAI / Anthropic** | Optional chat providers | `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `AI_CHAT_PROVIDER` |
| **Cloudinary** | Durable image URLs for avatars and try-on results | `CLOUDINARY_URL` (`cloudinary://KEY:SECRET@CLOUD_NAME`) |
| **SMTP** | Password-reset OTP emails | `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM_EMAIL` |

---

## Environment variables (summary)

| Variable | Required | Notes |
|----------|----------|--------|
| `SECRET_KEY` | Yes (production) | JWT signing; Render can generate |
| `DATABASE_URL` | Optional | Defaults to SQLite file; use Postgres URL on Render for durability |
| `HF_TOKEN` | For HF Spaces | Read token from [Hugging Face settings](https://huggingface.co/settings/tokens) |
| `USE_GRADIO_SPACE` | Optional | Default true — cloud try-on |
| `GRADIO_SPACE_NAME` | Optional | Default `frogleo/AI-Clothes-Changer` |
| `CLOUDINARY_URL` | Strongly recommended on Render | Persistent media URLs |
| `GEMINI_API_KEY` | For chat | Without it, chat returns configuration errors |
| `AI_CHAT_PROVIDER` | Optional | Default `gemini` |
| `DEBUG` | Optional | `true` may return `dev_otp` in OTP flow when SMTP missing |
| `PORT` | Set by host | e.g. Render injects `$PORT` |
| SMTP vars | Optional | Real email delivery for OTP |

---

## Local development

### Backend

```powershell
cd backend
python -m venv venv_py311
.\venv_py311\Scripts\activate
pip install -r requirements.txt
# Create backend/.env with at least HF_TOKEN (and optional keys above)
uvicorn complete_api:app --reload --host 0.0.0.0 --port 8000
```

Database helpers (if you use the modular app or init scripts): see [`backend/scripts/`](backend/scripts/).

### Frontend

```bash
cd frontend
flutter pub get
flutter run -d chrome --dart-define=API_BASE_URL=http://localhost:8000
```

---

## Deployment

See **[DEPLOY.md](DEPLOY.md)** for Render blueprint / manual setup: Python web service for `complete_api`, environment variables, and Flutter `build/web` as a static site.

---

## Security and privacy notes

- **Passwords** are hashed with bcrypt via the auth service.
- **Google login** in `complete_api` is a **lightweight flow**: the server does **not** verify `id_token` with Google in the current implementation; treat it as suitable for demos unless you add server-side token verification.
- **JWT** expiry and `SECRET_KEY` strength matter for production.
- **CORS** is wide open on `complete_api`; tighten `allow_origins` if you deploy a fixed web origin.

---

## Further reading

- [`DEPLOY.md`](DEPLOY.md) — hosting
- [`backend/README.md`](backend/README.md) — Gradio Space testing and local model toggles
- [`backend/app/services/fine_tuning/README.md`](backend/app/services/fine_tuning/README.md) — fine-tuning / dataset-oriented workflows

---

## License and third-party models

Virtual try-on behavior depends on **Hugging Face Spaces** and model licenses defined by those projects. U²-Net and other bundled research code retain their original licenses. Check each Space and model card before commercial use.
