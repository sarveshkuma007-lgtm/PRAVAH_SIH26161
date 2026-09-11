# PRAVAH – SIH26161

A complete dam-break flood simulation prototype with separate frontend and backend.

## Run Backend
```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

## Run Frontend
Open a second terminal:
```bash
cd frontend
npm install
npm run dev
```

Open the URL shown by Vite, usually http://localhost:5173.

The frontend also includes fallback demo data, so the dashboard remains usable if the backend is not running.
