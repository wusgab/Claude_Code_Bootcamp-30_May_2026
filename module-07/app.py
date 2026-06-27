"""Dashboard single-page app (Track A: Flask + Jinja).

Run:
    python app.py
Then open http://127.0.0.1:5000/ and size the viewport to 1280x720.
"""

from flask import Flask, render_template

app = Flask(__name__)

VERSION = "v1.0.0"

# --- Static, hardcoded sample data (no database, no auth) -------------------

NAV_ITEMS = [
    {"label": "Overview", "active": True},
    {"label": "Notes", "active": False},
    {"label": "Tasks", "active": False},
    {"label": "Reports", "active": False},
    {"label": "Settings", "active": False},
]

KPIS = [
    {"label": "KPI 1", "value": "128"},
    {"label": "KPI 2", "value": "42"},
    {"label": "KPI 3", "value": "7d"},
]

RECENT_ITEMS = [
    {"name": "Row 1", "value": "value"},
    {"name": "Row 2", "value": "value"},
    {"name": "Row 3", "value": "value"},
    {"name": "Row 4", "value": "value"},
    {"name": "Row 5", "value": "value"},
]


@app.route("/")
def index():
    return render_template(
        "index.html",
        nav_items=NAV_ITEMS,
        kpis=KPIS,
        recent_items=RECENT_ITEMS,
        version=VERSION,
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
