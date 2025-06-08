# Pi, OS and Container Setup

This guide covers the hardware and basic environment configuration used by the Home Assistant AI Hub project. It reflects the setup referenced in the main `README.md`.

## Hardware
- **Raspberry Pi 5** with **8GB RAM**
- **500GB SSD** for storage (configured for root filesystem)

## Operating System
- **Raspberry Pi OS 64‑bit (Bookworm)** or another Debian-based distro
- Update packages after installation:
  ```bash
  sudo apt update && sudo apt upgrade
  ```

## Docker & Home Assistant
1. Install Docker and Docker Compose:
   ```bash
   curl -fsSL https://get.docker.com | sh
   sudo apt install docker-compose -y
   sudo usermod -aG docker $USER
   ```
   Log out and back in so group changes take effect.
2. Pull and run Home Assistant Core:
   ```bash
   docker run -d --name homeassistant \
     --restart unless-stopped \
     -v /srv/homeassistant:/config \
     -p 8123:8123 \
     ghcr.io/home-assistant/home-assistant:stable
   ```

## Project Directory Layout
- Clone this repository to `/media/pi/data/assistant/`:
  ```bash
  git clone https://github.com/jamescockburn47/home-assistant-ai-hub.git /media/pi/data/assistant
  cd /media/pi/data/assistant
  ```
- Create a Python virtual environment (Python **3.11.2** tested):
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  ```
- Output directories used by the scripts:
  - `/srv/homeassistant/www/daily_images/` for generated images
  - `/srv/homeassistant/ai/` for generated text

Ensure these directories are writable by the user running the scripts and by the Home Assistant container.

## Cron Automation
Add the Daily Brain Boost script to cron for automatic execution:
```cron
5 2 * * * /media/pi/data/assistant/venv/bin/python /media/pi/data/assistant/daily_brain_boost_complete.py
```

## Permissions
The user running the scripts (typically `pi`) needs write access to `/srv/homeassistant/` and `/media/pi/data/assistant/`. Adjust permissions or use the `docker` group as required.

---
This setup provides a reproducible environment for running the project on a Raspberry Pi with Home Assistant in Docker.
