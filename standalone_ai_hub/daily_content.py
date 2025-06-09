#!/usr/bin/env python3
"""Standalone Daily Content Generator.

Generates daily facts, jokes, quotes, and more using OpenAI.
Results are stored under the ``data/`` directory with a timestamped subfolder.
Designed for cross-platform compatibility (Raspberry Pi and Windows).
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict

import requests

try:
    from dotenv import load_dotenv
    import openai
except ImportError:  # pragma: no cover - dependency check
    print("Run: pip install -r requirements.txt")
    sys.exit(1)


TEXT_MODEL = "gpt-4o"
IMAGE_MODEL = "dall-e-3"
DATA_DIR = Path("data")
IMAGES_DIR = DATA_DIR / "images"

PROMPTS = {
    "fact": "Provide a short, interesting science fact.",
    "history": "Give a notable UK historical event for today in history.",
    "word": "Share an uncommon English word of the day and its meaning.",
    "joke": "Tell a family-friendly joke.",
    "riddle": "Provide a short riddle.",
    "poem": "Write a two-line inspirational poem.",
    "quote": "Provide a motivational quote.",
    "on_this_day": "List a world event that occurred on this day.",
}


def init_client() -> openai.OpenAI:
    """Create an OpenAI client using the environment API key."""
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set in environment")
    return openai.OpenAI(api_key=api_key)


def generate_text(client: openai.OpenAI, prompt: str) -> str:
    """Generate text using the chat completion endpoint."""
    response = client.chat.completions.create(
        model=TEXT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=60,
    )
    return response.choices[0].message.content.strip()


def generate_image(client: openai.OpenAI, prompt: str, filename: Path) -> bool:
    """Generate an image for ``prompt`` and save it to ``filename``.

    Returns ``True`` if the image was successfully downloaded.
    """

    try:
        img = client.images.generate(model=IMAGE_MODEL, prompt=prompt, n=1)
        url = img.data[0].url
    except Exception as exc:  # pragma: no cover - network failure
        print(f"Image request failed: {exc}")
        return False

    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            filename.write_bytes(response.content)
            return True
    except Exception as exc:  # pragma: no cover - network failure
        print(f"Image download failed: {exc}")
    return False


def save_text(data: Dict[str, str], folder: Path) -> None:
    """Save generated text to JSON in the given folder."""
    folder.mkdir(parents=True, exist_ok=True)
    outfile = folder / "content.json"
    with outfile.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def main() -> None:
    """Generate daily content and optionally images."""
    client = init_client()
    today = datetime.now().strftime("%Y%m%d")
    out_folder = DATA_DIR / today
    out_folder.mkdir(parents=True, exist_ok=True)
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    results: Dict[str, str] = {}
    for key, prompt in PROMPTS.items():
        results[key] = generate_text(client, prompt)

    save_text(results, out_folder)

    # Example image: generate based on the joke
    img_file = IMAGES_DIR / f"joke_{today}.png"
    generate_image(client, results.get("joke", ""), img_file)
    print(f"Content saved to {out_folder}")


if __name__ == "__main__":
    main()
