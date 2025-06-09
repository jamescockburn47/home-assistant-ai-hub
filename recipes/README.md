# Recipe Finder Module

This module uses GPT to generate recipe ideas from a list of ingredients
and saves the chosen recipe for display on a dedicated Home Assistant dashboard.

## Usage

1. Set `OPENAI_API_KEY` in your environment or `.env` file.
2. Run the script with a comma-separated list of ingredients:

```bash
python recipes/recipe_finder.py "tomato, cheese"
```

The script lists up to three recipe options and prompts you to choose one.
The selected title is written to `/srv/homeassistant/ai/selected_recipe.txt`.
You can display this file via a file sensor or markdown card in Home Assistant.
