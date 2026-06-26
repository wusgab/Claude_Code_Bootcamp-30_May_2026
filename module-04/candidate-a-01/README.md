# Notes API (Track A — FastAPI + sqlite3)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload    # serves on http://127.0.0.1:8000
```

Endpoints: `POST /notes` (201) · `GET /notes?q=` (200) · `GET /notes/{id}` (200/404) · `PUT /notes/{id}` (200/404) · `DELETE /notes/{id}` (204/404). State persists to `notes.db`; invalid bodies return 422.
