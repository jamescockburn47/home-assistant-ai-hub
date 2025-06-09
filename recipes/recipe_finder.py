#!/usr/bin/env python3
"""Recipe Finder for Home Assistant.

Uses GPT to suggest recipe ideas based on a comma-separated list of
ingredients. Presents up to three options with detailed information
and saves the chosen recipe for display on a dashboard.

Usage:
    python recipe_finder.py "chicken, rice, tomato" --dietary vegetarian --preferences quick

Environment variables:
    OPENAI_API_KEY - API key for the OpenAI client
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from openai import OpenAI

TEXT_MODEL = "gpt-4"
OUTPUT_DIR = Path("/srv/homeassistant/ai")
RECIPES_DIR = OUTPUT_DIR / "recipes"
OPTIONS_FILE = OUTPUT_DIR / "recipe_options.txt"
SELECTED_FILE = OUTPUT_DIR / "selected_recipe.txt"
HISTORY_FILE = RECIPES_DIR / "recipe_history.json"

DIETARY_OPTIONS = [
    "vegetarian",
    "vegan",
    "gluten-free",
    "dairy-free",
    "keto",
    "paleo",
    "none",
]

@dataclass
class Recipe:
    """Represents a complete recipe with all its details."""
    title: str
    ingredients: List[str]
    instructions: List[str]
    cooking_time: str
    difficulty: str
    category: str
    dietary_info: List[str]
    rating: Optional[float] = None
    date_added: Optional[str] = None

def setup_directories() -> None:
    """Create necessary directories if they don't exist."""
    RECIPES_DIR.mkdir(parents=True, exist_ok=True)
    if not HISTORY_FILE.exists():
        HISTORY_FILE.write_text("[]", encoding="utf-8")

def fetch_recipes(
    ingredients: str,
    dietary: str = "none",
    preferences: Optional[str] = None,
    limit: int = 3
) -> List[Recipe]:
    """Return detailed recipe suggestions from GPT for the given ingredients."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY must be set")

    client = OpenAI(api_key=api_key)
    
    # Build a more detailed prompt
    prompt = (
        f"Suggest {limit} detailed recipes using these ingredients: {ingredients}.\n"
        f"Dietary restrictions: {dietary}\n"
        f"Additional preferences: {preferences or 'none'}\n\n"
        "For each recipe, provide a JSON array of objects with these fields:\n"
        "{\n"
        '  "title": "Recipe Name",\n'
        '  "ingredients": ["ingredient1", "ingredient2"],\n'
        '  "instructions": ["step1", "step2"],\n'
        '  "cooking_time": "30 minutes",\n'
        '  "difficulty": "Easy/Medium/Hard",\n'
        '  "category": "Main Course/Dessert/etc",\n'
        '  "dietary_info": ["vegetarian", "gluten-free"]\n'
        "}\n\n"
        "Return ONLY the JSON array, no other text."
    )

    try:
        response = client.chat.completions.create(
            model=TEXT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.7,
        )
    except Exception as exc:
        raise RuntimeError(f"GPT request failed: {exc}") from exc

    try:
        # Clean the response to ensure it's valid JSON
        content = response.choices[0].message.content.strip()
        # Remove any markdown code block markers
        content = content.replace("```json", "").replace("```", "").strip()
        recipes_data = json.loads(content)
        
        if not isinstance(recipes_data, list):
            recipes_data = [recipes_data]
            
        return [Recipe(**recipe) for recipe in recipes_data[:limit]]
    except json.JSONDecodeError as exc:
        print("Debug: Raw GPT response:", content)
        raise RuntimeError(f"Failed to parse recipe data: {exc}") from exc
    except Exception as exc:
        print("Debug: Raw GPT response:", content)
        raise RuntimeError(f"Failed to process recipe data: {exc}") from exc

def choose_recipe(recipes: List[Recipe]) -> Recipe:
    """Display recipe options and prompt for selection."""
    if not recipes:
        raise ValueError("No recipe options available")

    print("\nRecipe options:")
    for idx, recipe in enumerate(recipes, start=1):
        print(f"\n{idx}. {recipe.title}")
        print(f"   Cooking time: {recipe.cooking_time}")
        print(f"   Difficulty: {recipe.difficulty}")
        print(f"   Category: {recipe.category}")
        if recipe.dietary_info:
            print(f"   Dietary: {', '.join(recipe.dietary_info)}")

    while True:
        choice = input(f"\nSelect [1-{len(recipes)}]: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(recipes):
            return recipes[int(choice) - 1]
        print("Invalid selection, try again.")

def save_selection(selected: Recipe, options: List[Recipe]) -> None:
    """Save the chosen recipe and update history."""
    setup_directories()
    
    # Save options list
    options_text = "\n".join(f"{idx+1}. {recipe.title}" for idx, recipe in enumerate(options))
    OPTIONS_FILE.write_text(options_text, encoding="utf-8")
    
    # Save selected recipe details
    selected.date_added = datetime.now().isoformat()
    recipe_data = {
        "title": selected.title,
        "ingredients": selected.ingredients,
        "instructions": selected.instructions,
        "cooking_time": selected.cooking_time,
        "difficulty": selected.difficulty,
        "category": selected.category,
        "dietary_info": selected.dietary_info,
        "date_added": selected.date_added
    }
    SELECTED_FILE.write_text(json.dumps(recipe_data, indent=2), encoding="utf-8")
    
    # Update history
    history = []
    if HISTORY_FILE.exists():
        history = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    history.append(recipe_data)
    HISTORY_FILE.write_text(json.dumps(history[-10:], indent=2), encoding="utf-8")

def rate_recipe(recipe: Recipe) -> None:
    """Allow user to rate the selected recipe."""
    while True:
        try:
            rating = float(input("\nRate this recipe (1-5 stars): ").strip())
            if 1 <= rating <= 5:
                recipe.rating = rating
                break
            print("Please enter a number between 1 and 5")
        except ValueError:
            print("Please enter a valid number")

def main(argv: List[str] | None = None) -> None:
    """Entry point: fetch recipes and prompt for selection."""
    parser = argparse.ArgumentParser(description="Find recipes based on ingredients")
    parser.add_argument("ingredients", help="Comma-separated list of ingredients")
    parser.add_argument(
        "--dietary",
        choices=DIETARY_OPTIONS,
        default="none",
        help="Dietary restrictions"
    )
    parser.add_argument(
        "--preferences",
        help="Additional preferences (e.g., 'quick', 'healthy')"
    )
    
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])
    
    try:
        recipes = fetch_recipes(
            args.ingredients,
            dietary=args.dietary,
            preferences=args.preferences
        )
    except Exception as exc:
        sys.exit(f"Failed to fetch recipes: {exc}")

    try:
        selected = choose_recipe(recipes)
        rate_recipe(selected)
        save_selection(selected, recipes)
        print(f"\nRecipe saved to {SELECTED_FILE}")
        print(f"History updated in {HISTORY_FILE}")
    except Exception as exc:
        sys.exit(f"Selection error: {exc}")

if __name__ == "__main__":
    main()
