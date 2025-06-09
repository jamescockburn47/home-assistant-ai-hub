#!/usr/bin/env python3
"""Recipe Finder for Home Assistant.

Uses GPT to suggest recipe ideas based on a comma-separated list of
ingredients. Presents up to three options and saves the chosen
recipe title for display on a dashboard.

Usage:
    python recipe_finder.py "chicken, rice, tomato"

Environment variables:
    OPENAI_API_KEY - API key for the OpenAI client
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import List

from openai import OpenAI

TEXT_MODEL = "gpt-4o"
OUTPUT_DIR = Path("/srv/homeassistant/ai")
OPTIONS_FILE = OUTPUT_DIR / "recipe_options.txt"
SELECTED_FILE = OUTPUT_DIR / "selected_recipe.txt"


def fetch_recipes(ingredients: str, limit: int = 3) -> List[str]:
    """Return recipe titles suggested by GPT for the given ingredients."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY must be set")

    client = OpenAI(api_key=api_key)
    prompt = (
        f"Suggest {limit} recipes using these ingredients: {ingredients}. "
        "Reply with a simple numbered list of titles only."
    )
    try:
        response = client.chat.completions.create(
            model=TEXT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.7,
        )
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"GPT request failed: {exc}") from exc

    lines = response.choices[0].message.content.strip().splitlines()
    cleaned = [line.lstrip("0123456789.- ").strip() for line in lines if line.strip()]
    return cleaned[:limit]


def choose_recipe(options: List[str]) -> str:
    """Prompt the user to select one recipe option."""
    if not options:
        raise ValueError("No recipe options available")

    print("Recipe options:")
    for idx, name in enumerate(options, start=1):
        print(f"{idx}. {name}")

    while True:
        choice = input(f"Select [1-{len(options)}]: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return options[int(choice) - 1]
        print("Invalid selection, try again.")


def save_selection(selected: str, options: List[str]) -> None:
    """Write the chosen recipe and list of options to files for Home Assistant."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OPTIONS_FILE.write_text("\n".join(options), encoding="utf-8")
    SELECTED_FILE.write_text(selected, encoding="utf-8")


def main(argv: List[str] | None = None) -> None:
    """Entry point: fetch recipes and prompt for selection."""
    argv = argv or sys.argv[1:]
    if not argv:
        print("Usage: recipe_finder.py \"ingredient1, ingredient2\"")
        raise SystemExit(1)

    ingredients = argv[0]
    try:
        options = fetch_recipes(ingredients)
    except Exception as exc:  # noqa: BLE001
        sys.exit(f"Failed to fetch recipes: {exc}")

    try:
        selected = choose_recipe(options)
    except Exception as exc:  # noqa: BLE001
        sys.exit(f"Selection error: {exc}")

    save_selection(selected, options)
    print(f"Chosen recipe saved to {SELECTED_FILE}")


if __name__ == "__main__":
    main()
