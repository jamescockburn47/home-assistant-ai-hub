# Standalone AI Hub

A cross-platform Python project providing daily AI-generated content without relying on Home Assistant.
Designed to run on Raspberry Pi and Windows desktops.

## Features
- Generate daily science facts, quotes, jokes, poems, riddles, history notes, UK events, and word of the day
- Optionally generate accompanying images using DALL·E
- Stores generated content in a timestamped folder under `data/`

## Requirements
- Python 3.9+
- [OpenAI API key](https://platform.openai.com/)

Install dependencies (ideally in a virtual environment):
```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root containing your OpenAI API key:
```bash
OPENAI_API_KEY=your_key_here
```

## Usage
Run the script from a terminal:
```bash
python daily_content.py
```
By default, text is saved to `data/YYYYMMDD` and images to `data/images`.

After running `daily_content.py`, start the web server to view the results:
```bash
python web_app.py
```

## Windows Notes
Use `python` from the Command Prompt or PowerShell. Ensure paths do not contain spaces or wrap them in quotes.

## Raspberry Pi Notes
On Raspberry Pi OS, Python 3 is usually installed by default. If not, install it with:
```bash
sudo apt-get update && sudo apt-get install python3 python3-pip
```

## Web UI
View the generated content in your browser by starting the Flask server (after running the generator):
```bash
python web_app.py
```
Open `http://<host-ip>:8000` from any device on the same network (including a Raspberry Pi).
