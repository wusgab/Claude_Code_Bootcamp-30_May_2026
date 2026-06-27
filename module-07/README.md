# Module 07 — Dashboard SPA

A single-page dashboard web app built from the wireframe in
`wireframe-sketch.png` / `wireframe.png`.

## Track choice: **Track A — Flask + Jinja**

Flask was chosen over Streamlit because the wireframe demands precise layout
control — a fixed header bar, a left nav sidebar, a 3-up KPI grid, and a
dotted-leader "Recent items" list inside a 1280×720 frame. Plain CSS over a
Jinja template reproduces that layout faithfully; Streamlit's auto-layout
makes that pixel fidelity hard.

## Stack

- Python 3.11+ (developed on 3.12)
- Flask + Jinja templates
- Plain CSS (`static/style.css`) — no Tailwind, no component libraries
- Static, hardcoded sample data in `app.py` — no database, no auth

## Run

```bash
# one-time setup (PEP 668 externally-managed environments need a venv)
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# single command to run
.venv/bin/python app.py
```

Then open <http://127.0.0.1:5000/> and size the browser viewport to **1280×720**
to match the wireframe.

> If Flask is already on your system Python, `python app.py` works directly.

## Layout map (wireframe → app)

| Wireframe element            | App element                          |
| ---------------------------- | ------------------------------------ |
| "Dashboard" title + button   | `.header` / `.btn-new`               |
| Left nav (Overview…Settings) | `.sidebar`                           |
| KPI 1 / KPI 2 / KPI 3 cards  | `.kpis .kpi-card`                    |
| "Recent items" + Row 1…5     | `.panel` / `.rows`                   |
| v1.0.0                       | `.footer`                            |

## Files

```
app.py               Flask app + hardcoded data
templates/index.html Jinja template
static/style.css     plain CSS
requirements.txt     flask
```
