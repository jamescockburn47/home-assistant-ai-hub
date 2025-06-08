#!/usr/bin/env python3
"""
Daily Brain Boost - Complete Version with Auto HA Restart
---------------------------------------------------------
• Unique image filenames with timestamps (guaranteed cache bust)
• Writes timestamp file for dashboard
• Artistic images with LLM-chosen artists
• UK-focused content with REAL facts
• Joke images based on actual joke content
• Auto-restarts Home Assistant to clear cache
"""

import os, sys, json, random, shutil, logging, requests, time, subprocess
from datetime import datetime, timedelta
from pathlib import Path

try:
    from dotenv import load_dotenv
    import openai
except ImportError:
    print("Run: pip install openai python-dotenv requests pillow")
    sys.exit(1)

# --- CONFIGURATION ---
TEXT_MODEL = "gpt-4o"
IMAGE_MODEL = "dall-e-3"
OUTDIR = Path("/srv/homeassistant/ai")
WWW_DIR = Path("/srv/homeassistant/www/daily_images")
LOGFILE = Path("/media/pi/data/assistant/brain_boost.log")
HISTORY_FILE = Path("/media/pi/data/assistant/brain_boost_history.json")
HISTORY_DAYS_TO_KEEP = 14
WORD_RETRY_LIMIT = 3
ENABLE_IMAGES = True
TODAY_STR = datetime.now().strftime("%Y%m%d")
TIMESTAMP = str(int(time.time()))  # Unique timestamp for this run

# --- LOGGING ---
LOGFILE.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler(LOGFILE), logging.StreamHandler(sys.stdout)]
)
log = logging.getLogger(__name__)

# --- LOAD ENVIRONMENT ---
SCRIPT_DIR = Path(__file__).resolve().parent
ENV_FILE = SCRIPT_DIR / ".env"
if ENV_FILE.exists():
    load_dotenv(ENV_FILE)
else:
    # Try common locations
    for env_path in [Path("/home/pi/.env"), Path("/home/pi/Desktop/.env")]:
        if env_path.exists():
            load_dotenv(env_path)
            break

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    log.critical("OPENAI_API_KEY not found in environment")
    sys.exit(1)

openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)

# --- CREATE DIRECTORIES ---
OUTDIR.mkdir(parents=True, exist_ok=True)
WWW_DIR.mkdir(parents=True, exist_ok=True)
(OUTDIR / "images").mkdir(exist_ok=True)

# --- CLEANUP OLD IMAGES ---
def cleanup_old_images():
    """Remove old timestamped images, keeping only the most recent set"""
    try:
        # Find all timestamped images
        for pattern in ['fact_*.png', 'on_this_day_*.png', 'quote_*.png', 
                       'poem_*.png', 'history_*.png', 'word_*.png', 
                       'riddle_*.png', 'joke_*.png']:
            files = sorted(WWW_DIR.glob(pattern))
            # Keep only the 3 most recent of each type
            for old_file in files[:-3]:
                old_file.unlink()
                log.info(f"Cleaned up old image: {old_file.name}")
    except Exception as e:
        log.warning(f"Cleanup error: {e}")

# --- HISTORY FUNCTIONS ---
def load_history():
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_history(history):
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=4)

def get_recent_examples(history, filename, days):
    recent = []
    if filename in history:
        for entry in history[filename]:
            try:
                entry_date = datetime.fromisoformat(entry['date'])
                if datetime.now() - entry_date < timedelta(days=days):
                    recent.append(entry['content'])
            except:
                continue
    return recent[-5:] if recent else []

# --- PROMPTS ---
def get_prompts(history):
    current_date = datetime.now().strftime("%B %d")
    current_year = datetime.now().year
    
    def avoid_recent(filename):
        examples = get_recent_examples(history, filename, HISTORY_DAYS_TO_KEEP)
        if examples:
            avoid_list = "\n".join([f"- {ex[:80]}..." for ex in examples])
            return f"\n\nDo NOT repeat these recent examples:\n{avoid_list}"
        return ""
    
    return {
        "fact.txt": (
            "Tell me a REAL, verifiable science fact. Focus on UK/British discoveries or research. "
            "Must be factually accurate and specific. "
            "MUST be under 250 characters, single paragraph." + avoid_recent('fact.txt')
        ),
        "on_this_day.txt": (
            f"What ACTUALLY happened on {current_date} in British history? "
            f"Give me a REAL historical event that occurred on this exact date (any year before {current_year}). "
            "Must be historically accurate - do not make up events. "
            "Under 250 characters." + avoid_recent('on_this_day.txt')
        ),
        "quote.txt": (
            "Share a REAL, verifiable quote from a British historical figure, writer, or scientist. "
            "Must be an actual quote they said or wrote, not made up. "
            "Include who said it. Under 250 characters." + avoid_recent('quote.txt')
        ),
        "poem.txt": (
            "Share a REAL short poem (4-6 lines) by an actual British poet. "
            "Must be a real published poem, not made up. "
            "Format: '[poem text] — [Author]' on ONE line. Under 250 chars." + avoid_recent('poem.txt')
        ),
        "history.txt": (
            "Share a REAL, verifiable historical fact about the United Kingdom. "
            "Must be factually accurate and specific, not generic. "
            "Single paragraph under 250 characters." + avoid_recent('history.txt')
        ),
        "word.txt": (
            "Share a REAL unusual English word (preferably British origin) from the dictionary. "
            "Must be an actual word with its correct definition. "
            "Format: 'Word: [word] - [accurate definition under 15 words]'. Max 120 chars." + avoid_recent('word.txt')
        ),
        "riddle.txt": (
            "Share a clever traditional riddle. Can be a classic riddle or create a new one. "
            "Format: 'Riddle: [question] Answer: [answer]' "
            "on ONE line. Under 250 characters." + avoid_recent('riddle.txt')
        ),
    }

# --- CONTENT GENERATION ---
def gpt_text(prompt, max_tokens=80):
    try:
        response = openai_client.chat.completions.create(
            model=TEXT_MODEL,
            messages=[
                {"role": "system", "content": "You are a factual assistant. Only provide real, verifiable information. Never make up facts, events, quotes, or historical information. If you're not certain something is true, don't include it."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        log.error(f"GPT text error: {e}")
        return None

def gpt_image(prompt, filename):
    """Generate artistic image with unique filename"""
    # Let GPT choose an artist based on the content
    artist_prompt = (
        f"Based on this content: '{prompt[:100]}...', "
        f"choose ONE famous artist (painter, illustrator, or visual artist from any era or culture) "
        f"whose style would best suit illustrating this concept. "
        f"Consider artists from all movements: Renaissance, Impressionism, Surrealism, Pop Art, "
        f"Japanese Ukiyo-e, Abstract Expressionism, Art Nouveau, Bauhaus, Street Art, Digital Art, etc. "
        f"Reply with ONLY the artist's name, nothing else."
    )
    
    try:
        # Get artist recommendation
        artist_response = openai_client.chat.completions.create(
            model=TEXT_MODEL,
            messages=[
                {"role": "system", "content": "You are an art expert. Reply with only an artist name."},
                {"role": "user", "content": artist_prompt}
            ],
            max_tokens=20,
            temperature=0.9  # Higher temperature for more variety
        )
        
        artist = artist_response.choices[0].message.content.strip()
        
        # Fallback if response is too long or weird
        if len(artist) > 40 or not artist:
            artists_fallback = [
                "Monet", "Van Gogh", "Hokusai", "Picasso", "Dalí", "Warhol",
                "Banksy", "Kahlo", "Basquiat", "Hockney", "Klimt", "Munch"
            ]
            artist = random.choice(artists_fallback)
        
        log.info(f"Creating image in style of {artist}")
        
        # Create artistic prompt
        image_prompt = (
            f"Create an artistic illustration in the distinctive style of {artist}. "
            f"Subject: '{prompt}'. "
            f"The image should clearly reflect {artist}'s unique artistic style, techniques, and color palette. "
            f"If {artist} is known for specific techniques (pointillism, cubism, etc), use them. "
            f"No text or words in the image. Family-friendly content."
        )
        
        response = openai_client.images.generate(
            model=IMAGE_MODEL,
            prompt=image_prompt,
            size="1024x1024",
            n=1,
            quality="standard",
            style="vivid"  # Use vivid for more artistic interpretation
        )
        
        image_url = response.data[0].url
        response_get = requests.get(image_url, timeout=30)
        if response_get.status_code != 200:
            log.error(
                f"Image download failed for {filename} with status {response_get.status_code}"
            )
            return False
        image_data = response_get.content
        
        # Save with timestamp in filename
        base_name = filename.replace('.png', '')
        timestamped_filename = f"{base_name}_{TIMESTAMP}.png"
        
        # Save dated archive copy
        dated_filename = f"{base_name}_{TODAY_STR}.png"
        dated_path = OUTDIR / "images" / dated_filename
        with open(dated_path, 'wb') as f:
            f.write(image_data)
        
        # Save timestamped version
        timestamped_path = WWW_DIR / timestamped_filename
        with open(timestamped_path, 'wb') as f:
            f.write(image_data)
        
        # Update symlink
        symlink_path = WWW_DIR / filename
        if symlink_path.exists() or symlink_path.is_symlink():
            symlink_path.unlink()
        
        # Create relative symlink
        try:
            symlink_path.symlink_to(timestamped_filename)
        except:
            # If symlink fails, just copy the file
            shutil.copy(timestamped_path, symlink_path)
        
        log.info(f"✓ Image saved: {filename} -> {timestamped_filename} (style: {artist})")
        return True
        
    except Exception as e:
        log.exception(
            "Image generation failed for %s. Prompt: %s", filename, prompt
        )
        return False

def fetch_joke():
    """Get joke from API or generate one"""
    try:
        r = requests.get("https://icanhazdadjoke.com/", 
                        headers={"Accept": "application/json"}, 
                        timeout=5)
        if r.status_code == 200:
            return r.json().get("joke", "Why don't scientists trust atoms? Because they make up everything!")
    except:
        pass
    
    # Fallback to GPT
    prompt = "Tell me a clever, family-friendly joke. Preferably with British humor. Keep it short."
    joke = gpt_text(prompt, max_tokens=60)
    return joke or "What do you call a bear with no teeth? A gummy bear!"

def generate_word_with_retry(prompt):
    """Try to generate a word that will pass image generation"""
    for attempt in range(WORD_RETRY_LIMIT + 1):
        text = gpt_text(prompt, max_tokens=40)
        if not text:
            continue
            
        # Extract just the word
        try:
            word = text.split()[1]  # Get word after "Word:"
        except:
            word = "Serendipity"
            
        if gpt_image(word, "word.png"):
            return text
            
        log.warning(f"Word '{word}' image failed, attempt {attempt + 1}")
    
    # If all attempts failed, use a safe fallback
    fallback_text = "Word: Serendipity - A happy accident or pleasant surprise"
    gpt_image("Abstract concept of serendipity", "word.png")
    return fallback_text

# --- MAIN ---
def main():
    log.info("=== Daily Brain Boost Generator Starting ===")
    log.info(f"Timestamp for this run: {TIMESTAMP}")
    
    # Clean up old images first
    cleanup_old_images()
    
    history = load_history()
    prompts = get_prompts(history)
    
    generated_content = {}
    
    # Generate text content
    for filename, prompt in prompts.items():
        if filename == "word.txt":
            continue  # Handle separately
            
        log.info(f"Generating {filename}")
        
        # Adjust tokens for different content
        if filename == "poem.txt":
            max_tokens = 100
        elif filename in ["fact.txt", "history.txt", "on_this_day.txt"]:
            max_tokens = 70
        else:
            max_tokens = 80
            
        content = gpt_text(prompt, max_tokens)
        
        if content:
            generated_content[filename] = content
            filepath = OUTDIR / filename
            filepath.write_text(content + "\n", encoding='utf-8')
            log.info(f"✓ Generated {filename}")
        else:
            log.error(f"✗ Failed to generate {filename}")
    
    # Handle joke separately
    log.info("Generating joke.txt")
    joke = fetch_joke()
    generated_content["joke.txt"] = joke
    (OUTDIR / "joke.txt").write_text(joke + "\n", encoding='utf-8')
    
    # Handle word with retry logic
    log.info("Generating word.txt")
    word_text = generate_word_with_retry(prompts["word.txt"])
    generated_content["word.txt"] = word_text
    (OUTDIR / "word.txt").write_text(word_text + "\n", encoding='utf-8')
    
    # Generate images
    if ENABLE_IMAGES:
        log.info("Generating artistic images...")
        
        # Generate images for text content
        for filename, content in generated_content.items():
            if content and "[GENERATION FAILED]" not in content:
                image_name = filename.replace('.txt', '.png')
                if filename != "word.txt":  # Word already handled
                    success = gpt_image(content, image_name)
                    if success is False:
                        log.warning(
                            f"Image generation failed for {image_name}" 
                        )
    
    # Update history
    for filename, content in generated_content.items():
        if content:
            if filename not in history:
                history[filename] = []
            history[filename].append({
                'date': datetime.now().isoformat(),
                'content': content
            })
    
    save_history(history)
    
    # Write timestamp file for dashboard to read
    timestamp_file = WWW_DIR / "current_timestamp.txt"
    timestamp_file.write_text(TIMESTAMP)
    log.info(f"Timestamp file written: {TIMESTAMP}")
    
    log.info("=== Generation Complete ===")
    log.info(f"Images saved with timestamp: {TIMESTAMP}")
    
    # Restart Home Assistant to clear cache
    log.info("Restarting Home Assistant to clear cache...")
    try:
        result = subprocess.run(['docker', 'restart', 'homeassistant'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            log.info("Home Assistant restart initiated successfully")
            log.info("Wait 30-60 seconds for Home Assistant to fully restart")
        else:
            log.error(f"Failed to restart Home Assistant: {result.stderr}")
    except Exception as e:
        log.error(f"Error restarting Home Assistant: {e}")
    
    log.info("=== Brain Boost Complete ===")

if __name__ == "__main__":
    main()
