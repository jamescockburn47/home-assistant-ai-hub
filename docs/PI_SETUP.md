# Pi Setup & Environment

This guide outlines the basic hardware and environment configuration used for the project.

## Hardware
- **Raspberry Pi 5** (8GB RAM) with **500GB SSD** storage
- Raspberry Pi OS Lite

## Home Assistant
- Home Assistant **Core** installed via Docker
- Container name: `homeassistant`
- Data and configuration stored in `/srv/homeassistant/`

## Project Directory
- Clone this repository to `/media/pi/data/assistant`
- Create a Python **3.11** virtual environment:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  ```
- Copy `.env.example` to `.env` and add your `OPENAI_API_KEY` (and optional `HA_TOKEN`).

## Automation
- Schedule `daily_brain_boost_complete.py` via `cron` for automatic updates.
- Generated images and text are written to Home Assistant directories for the dashboard.
- Logs are written to `/media/pi/data/assistant/brain_boost.log` for troubleshooting.
