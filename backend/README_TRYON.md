# Virtual Try-On (Gradio Spaces)

## Test without FastAPI

Run the standalone script (no API server) to verify Spaces:

```bash
cd backend
.\venv_py311\Scripts\python.exe test_gradio_direct.py
# Or with your own images:
.\venv_py311\Scripts\python.exe test_gradio_direct.py path/to/person.png path/to/cloth.png
```

- **If the script fails**, the same call will fail via FastAPI. The issue is the Space (quota, upstream error) or the Space’s API (e.g. Kolors exposes no endpoints).
- **If the script works**, FastAPI uses the same `gradio_client` calls; Try On via the app should work when the Space is healthy.

## Spaces used

| Space | API | Notes |
|-------|-----|--------|
| **yisol/IDM-VTON** | `api_name="/tryon"` | Default. Named API; can hit ZeroGPU quota or upstream errors. |
| **frogleo/AI-Clothes-Changer** | `api_name="/infer"` | Often "upstream error" or "ZeroGPU quota". Fallback tries yisol. |
| **Kwai-Kolors/Kolors-Virtual-Try-On** | — | Not callable via `gradio_client` (no exposed endpoints). |

## Common errors

- **"upstream Gradio app has raised an exception"** – Space-side error (e.g. quota, crash). Retry later or try another Space.
- **"ZeroGPU quotas"** – Hugging Face ZeroGPU limit for that Space. Retry later or use HF Pro.
- **"list index out of range"** (Kolors) – Space does not expose a compatible API; don’t use Kolors via this client.

## Config

Set in `.env` or environment:

- `GRADIO_SPACE_NAME=yisol/IDM-VTON` (default)
- `GRADIO_SPACE_NAME=frogleo/AI-Clothes-Changer` (then fallback to yisol on failure)
