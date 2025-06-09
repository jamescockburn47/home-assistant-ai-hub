"""Minimal Flask UI for Standalone AI Hub.

This script serves the latest generated content via a simple web
interface. The Raspberry Pi can access it over the network.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any

from flask import Flask, render_template_string, send_from_directory

DATA_DIR = Path("data")
IMAGES_DIR = DATA_DIR / "images"

app = Flask(__name__)

HTML_TEMPLATE = """
<!doctype html>
<title>Daily Content</title>
<h1>Daily Content</h1>
{% if data %}
  <ul>
  {% for key, value in data.items() %}
    <li><strong>{{ key }}:</strong> {{ value }}</li>
  {% endfor %}
  </ul>
  {% if image_name %}
    <img src="/images/{{ image_name }}" alt="Daily image" />
  {% endif %}
{% else %}
  <p>No content available. Run daily_content.py first.</p>
{% endif %}
"""


def _latest_data_folder() -> Path | None:
    """Return the most recent data directory or ``None`` if none exist."""
    if not DATA_DIR.exists():
        return None
    dirs = [d for d in DATA_DIR.iterdir() if d.is_dir() and d.name.isdigit()]
    return max(dirs, default=None)


def load_latest_data() -> Dict[str, Any]:
    """Load the most recent ``content.json`` file if present."""
    folder = _latest_data_folder()
    if not folder:
        return {}
    json_file = folder / "content.json"
    if not json_file.exists():
        return {}
    try:
        return json.loads(json_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


@app.route("/")
def index() -> str:
    """Render the latest text content and image."""
    folder = _latest_data_folder()
    data = load_latest_data()

    image_name = None
    if folder:
        candidate = IMAGES_DIR / f"joke_{folder.name}.png"
        if candidate.exists():
            image_name = candidate.name

    return render_template_string(
        HTML_TEMPLATE,
        data=data,
        image_name=image_name,
    )


@app.route("/images/<path:filename>")
def images(filename: str):
    """Serve generated images."""
    return send_from_directory(IMAGES_DIR, filename)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

