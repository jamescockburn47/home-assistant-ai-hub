# Home Assistant AI Hub: Daily Brain Boost & Modular Smart Assistant

> An extensible, privacy-first automation and AI assistant ecosystem for Home Assistant—featuring daily engaging content, persistent memory, local LLMs, voice control, and a comprehensive roadmap for offline-first home intelligence.

---

## 🌟 Overview

This project transforms Home Assistant into a full AI-powered hub that combines:
- **Daily Brain Boost**: Automated daily content generation with unique AI artwork
- **Local Voice Assistant**: Privacy-first voice control using local LLMs
- **Knowledge Base**: Offline Wikipedia/Wiktionary for verified facts
- **Smart Home Intelligence**: Agentic control, automation, and monitoring
- **Extensible Framework**: Modular design for budgeting, 3D printing, OCR, and more

Everything is designed for persistent memory, offline-first operation, and continuous expansion.

---

## 🎯 Features

### ✅ Daily Brain Boost (Fully Operational)
- **8 Daily Content Cards**: Science facts, UK history, word of the day, jokes, riddles, poems, quotes, and "on this day" events
- **AI-Generated Artwork**: Each piece gets unique artwork in the style of dynamically-chosen famous artists
- **Anti-Repetition System**: 14-day rolling memory prevents duplicate content
- **British/UK Focus**: Prioritizes British history, discoveries, and cultural content
- **Automatic Updates**: Full automation via cron with cache management

### 🔧 Partially Implemented/Planned
- **Voice Assistant & Local LLMs**: Mistral 7B/DeepSeek running locally via llama.cpp, whisper.cpp for STT, Piper for TTS (in progress)
- **Knowledge & RAG System**: Kiwix local server for offline Wikipedia/Wiktionary; RAG pipeline under development
- **Calendar Integration**: iCloud/Google sync works; voice control for event add planned
- **Budget Agent**: Designed, not implemented
- **3D Print Automation**: Infrastructure in progress
- **Document OCR**: Scripts and pipeline designed
- **Recipe Suggestions Page**: GPT-based recipe ideas and selection

---

## 📁 Project Structure

/media/pi/data/assistant/
├── daily_brain_boost_complete.py    # Main script
├── .env.example                     # API key template (never commit real keys)
├── README.md                        # This file
├── requirements.txt                 # Python dependencies
├── brain_boost_history.json         # Rolling memory (ignored by git)
├── dashboard.yaml                   # Dashboard UI config
├── docs/                            # Docs & setup guides
│   └── PI_SETUP.md
├── voice/                           # Voice assistant scripts
├── llm/                             # Local LLM configs
├── calendar/                        # Calendar integration
├── recipes/                         # Recipe finder module
├── ai/                              # (Text output, ignored by git)
├── venv/                            # Python virtualenv, not tracked
└── ... (other modules)


---

## 🚀 Quick Start

1.  **Clone this repo to your Pi:**
    ```bash
    git clone [https://github.com/jamescockburn47/home-assistant-ai-hub.git](https://github.com/jamescockburn47/home-assistant-ai-hub.git) /media/pi/data/assistant
    cd /media/pi/data/assistant
    ```

2.  **Set up Python environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Create your .env file:**
    ```bash
    cp .env.example .env
    # Edit .env and add your OpenAI API key
    # Optional: add HA_TOKEN for Home Assistant scripts
    ```

    The `add_event.sh` helper script will read `HA_TOKEN` from this file
    or your environment when adding calendar entries.

4.  **Run the script:**
    ```bash
    python daily_brain_boost_complete.py
    ```

5.  **Add to cron for daily automation:**
    ```cron
    5 2 * * * /media/pi/data/assistant/venv/bin/python /media/pi/data/assistant/daily_brain_boost_complete.py
    ```

6.  **Configure Home Assistant:**
    * Place generated images in `/srv/homeassistant/www/daily_images/`
    * Place generated text in `/srv/homeassistant/ai/`
    * Reference these in your `dashboard.yaml` (e.g., `image: "/local/daily_images/fact.png?v=..."`)
    * Create a file sensor so dashboards refresh when `current_timestamp.txt` changes. Example:

      ```yaml
      # examples/brain_boost_timestamp_sensor.yaml
      sensor:
        - platform: file
          name: Brain Boost Timestamp
          file_path: /srv/homeassistant/www/daily_images/current_timestamp.txt
          value_template: "{{ value }}"
      ```

      Then use `cachebust={{ states('sensor.brain_boost_timestamp') }}` in `dashboard.yaml`.

---

## 🏗️ Architecture

* **Home Assistant Core** in Docker (on Pi 5, 500GB SSD)
* **Project files**: `/media/pi/data/assistant/`
* **Virtualenv** for Python packages (local to project directory)
* **Images/text**: Written to HA config folders for direct dashboard integration
* **Memory**: Rolling 14-day anti-repeat system per card (JSON)
* **Voice/Llama/Offline/RAG modules**: Scripts and configs present for future growth

---

## 📊 Status Table

| Module                 | Status  | Notes                                  |
| ---------------------- | ------- | -------------------------------------- |
| Daily Brain Boost      | ✅ Stable | Fully automated, cache-bust            |
| Voice Assistant LLM    | 🟡 Partial | Components tested                      |
| Local LLMs             | 🟡 Partial | Wrappers set up                        |
| Calendar Integration   | ✅ Working | Voice add planned                      |
| Knowledge Base (RAG)   | 🟡 Partial | Kiwix server running                   |
| Budget Agent           | 🟡 Designed | Not yet implemented                    |
| Recipe Suggestions     | 🆕 Experimental | GPT-based suggestions dashboard  |
| 3D Print Automation    | 🟡 Planned | Infrastructure set                     |
| OCR Pipeline           | 🟡 Designed | Scripts drafted                        |

---

## 📝 Pi & System Setup

See `docs/PI_SETUP.md` for full hardware, Docker, directory, and environment details.

---

## 🐛 Troubleshooting

* **Images not updating?**
    * Run the script, then restart Home Assistant (`docker restart homeassistant`)
    * Clear browser cache
* **Dashboard missing content?**
    * Ensure the correct `dashboard.yaml` is in git and loaded in Home Assistant
* **Packages missing?**
    * (Re)activate `venv`, re-run `pip install -r requirements.txt`
* **.env not found?**
    * Check permissions and location in `/media/pi/data/assistant/`
* **Image errors?**
    * Inspect `brain_boost.log` for `WARNING` lines about failed image generation
    * `grep 'Image generation failed' /media/pi/data/assistant/brain_boost.log`
* **Still stuck?**
    * See `docs/` or open an issue

---

## 🛡️ Security

* No API keys or secrets in git
* All personal data stays local to Pi/SSD
* All cloud features are opt-in
* Rolling history can be deleted at any time

---

## 📚 ANNEX: System Memory, Workstreams & Future Vision

This section documents all current, partial, and planned modules, per your memory protocol. Nothing is ever forgotten, overwritten, or lost—even if only designed or prototyped.

### 1. Voice Assistant & Local LLMs
* **Goal**: Full privacy-first, always-on home voice assistant.
* **STT**: `whisper.cpp` (tested locally)
* **TTS**: `piper` (en_GB-alba-medium)
* **LLMs**: Mistral 7B, DeepSeek via `llama.cpp` (tested; future: Codestral, RAG with Kiwix)
* **Intent/skill scripts**: Modular, persistent, session memory
* **Cloud escalation**: Only by explicit user choice
* **Home Assistant API**: Voice-to-automation mapping

### 2. Offline Knowledge Base & RAG
* **Kiwix Wikipedia, Wiktionary, Wikiquote**:
    * All `.zim` files hosted locally for fast RAG
    * Accessible via API/scripts, not for Brain Boost content (which is OpenAI-only)
* **Future**:
    * All "verified fact" queries, trivia, and Q&A to use local RAG for explainability and transparency

### 3. Budget Agent & Analytics (Planned)
* **Features**:
    * Manual upload or API pull of bank statements
    * Spending analysis, savings tips, agentic investment routines (Revolut API planned)
    * Home Assistant dashboard analytics

### 4. Calendar, Notifications & Summaries
* **Current**:
    * iCloud/Google sync, dashboard display, summary scripts
* **Planned**:
    * Voice-driven event add, LLM summarization, daily/weekly spoken briefings

### 5. 3D Printing/Workshop Integration
* **Printers**: AnkerMake M5C, Anycubic Kobra 3 (confirmed hardware)
* **Planned**:
    * STL generation (Rodin), slicing (OrcaSlicer), print job dispatch, monitoring, AI task planning, wall display integration

### 6. Document/OCR Pipeline
* **Goal**:
    * Use webcam/Pi camera, Tesseract OCR, LLM parsing for document management, reminders, post scanning
* **Status**:
    * Script prototypes exist, dashboard integration planned

### 7. Modular Memory & Audit Protocol
* All features and experiments are always preserved in `docs/` and `README`.
* No module, workstream, or protocol is ever deleted or "forgotten" per memory discipline.
* Every summary or project audit must include both live and planned functions.

---

## 💾 Pi/OS/Container Setup

See `docs/PI_SETUP.md` for hardware, OS, Docker container, and directory layout, including:

* Pi 5 (8GB RAM) + 500GB SSD
* Home Assistant Core in Docker
* Python 3.11.2 virtualenv
* Project at `/media/pi/data/assistant/`
* Data at `/srv/homeassistant/`
* Cron jobs and permissions

---

## 🤝 Contributing & Memory Protocol

* **No accidental omission**:
    * All planned/partial/abandoned experiments must be included in `README`/`docs/`commits
* **Pull requests**:
    * Must update documentation/memory with new workstreams or modules
* **Key files not tracked**:
    * No `.env`, images, or generated text content in repo
* **Memory is canonical**:
    * This README is the single source of truth

---

## 📜 License

Personal/family/educational use only.

Contact owner for commercial or multi-user licensing.

---
*Last updated: 2025-06-09*
*Maintainer: James Cockburn*

**Building the future of home intelligence, one module at a time.**
