# PocketSmart AI

A responsive budget-planning web app based on the supplied PocketSmart AI documentation. It includes three planners: Home Interior, Party Planning, and Jewelry Recommendations, with optional outfit-image input for the Jewelry planner.

## Implementation notes

- **Backend:** FastAPI with modular planner routes and a Gemini service.
- **Frontend:** HTML, CSS, JavaScript, served by FastAPI/Jinja2.
- **AI:** Google Gen AI SDK. Default model is configurable with `GEMINI_MODEL` (currently set to `gemini-2.5-flash`). The documentation mentions “Gemini 1.5 Flash Pro”; model availability can change, so use a model available to your Google AI Studio project.
- **Product/vendor integrations:** The documentation permits mock API calls or simulated sourcing. This version does **not** scrape stores or verify live listings. It returns AI-generated planning suggestions and clearly labels fallback/demo recommendations.
- **Fallback:** The app still works without a Gemini key using deterministic demo allocations.
- **Security:** API keys belong in `.env`, never in frontend JavaScript or source control. Image upload accepts JPG/PNG/WEBP up to 5 MB.

## 1. Install prerequisites

Install Python 3.11 or newer from https://www.python.org/downloads/ and tick **Add Python to PATH** in the installer. Install Visual Studio Code.

Open this folder in VS Code, then choose **Terminal → New Terminal**.

## 2. Create and activate a virtual environment (Windows PowerShell)

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If `py` is not recognized, try:
```powershell
python --version
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation for this terminal only:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

If you use Command Prompt instead:
```bat
python -m venv .venv
.venv\Scripts\activate.bat
```

## 3. Install packages

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 4. Configure Gemini (optional but recommended)

1. Visit https://aistudio.google.com/ and create an API key for your project.
2. In VS Code, copy `.env.example` to a new file named `.env`.
3. Paste the key after `GEMINI_API_KEY=`. Leave `GEMINI_MODEL=gemini-2.5-flash` unless your account uses another supported model.
4. Save `.env` and restart the server after changing it.

Without a key, the site uses demo fallback allocations. A configured key can still fail if the model is unavailable, the key lacks access, quota is exhausted, or the network is offline; in that case the app falls back to demo mode.

## 5. Run the application

From the project root, with the virtual environment active:

```powershell
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000 in your browser. API docs are at http://127.0.0.1:8000/docs and health check is http://127.0.0.1:8000/health. Keep the terminal open while using the app; press Ctrl+C to stop.

## 6. Test all planners

- **Home:** budget `25000`; room `Living room`; items `2 fans, 4 lights, sofa`; preferences `simple modern style`.
- **Party:** budget `30000`; event `Birthday`; guests `25`; venue `home`.
- **Jewelry:** budget `5000`; occasion `Wedding`; style `Traditional`; material `Gold-tone`. Optionally upload a JPG/PNG/WEBP outfit image.

Expected: a summary, allocation bars, practical recommendations, and tips. With no API key or if Gemini fails, the result badge says **Demo plan**. With a successful Gemini response it says **Gemini AI plan**.

## 7. API endpoints

- `GET /health`
- `POST /api/generate-home`
- `POST /api/generate-party`
- `POST /api/generate-jewelry`

The three planner POST routes accept `multipart/form-data`: `budget` (required), `currency`, `location`, `preferences`, `details` (JSON object encoded as text), and optional `image` for the jewelry planner.

## Troubleshooting

- **`py` not recognized:** install Python with PATH enabled, then restart VS Code. Try `python --version`.
- **Activation script not recognized:** check that `.venv` exists in the project root. Recreate it if necessary with `python -m venv .venv`.
- **`ModuleNotFoundError`:** activate `.venv`, then run `pip install -r requirements.txt`.
- **Gemini error:** check `.env`, model availability, API key permissions, quota, internet, and terminal output. The app deliberately shows demo results if Gemini is unavailable.
- **Port in use:** run `uvicorn app.main:app --reload --port 8001` and open http://127.0.0.1:8001.

## Scope / honest limitations

This is a complete runnable project scaffold for the documentation's main workflow, not a live shopping aggregator. Amazon/Flipkart/IKEA/Swiggy/Zomato/OYO product/service data are not fetched automatically. To add verified listings, integrate authorized partner APIs or approved affiliate/product feeds and display timestamps/source links. Do not rely on AI-generated prices as current market prices.
