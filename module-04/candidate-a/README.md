# Notes API (Track A — FastAPI + sqlite3)

```sh
python3 -m venv .venv && . .venv/bin/activate   # 1. create/activate venv
pip install -r requirements.txt                 # 2. install deps
python3 app.py                                  # 3. serve at http://127.0.0.1:8000
```

Schema auto-initialises in `notes.db` on startup. Endpoints: `POST /notes`, `GET /notes[?q=]`, `GET /notes/{id}`, `PUT /notes/{id}`, `DELETE /notes/{id}`.
