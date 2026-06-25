#!/usr/bin/env python3
"""
ClaimCoin Bot - Complete Automation Script
with Memory-Based Learning System & Parallel OCR
"""

import os
import sys
import time
import json
import re
import random
import requests
from bs4 import BeautifulSoup
from html import unescape
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed

# ============================================================
# PSYCHO UI - Premium UI Framework
# ============================================================
class PsychoUI:
    def __init__(self, typing_speed=0.002):
        self.speed = typing_speed
        self.success_history = []
        self.max_history = 999999
        self.show_success = True
        
        self.pri = "\033[38;5;147m"
        self.sec = "\033[38;5;123m"
        self.gray = "\033[38;5;243m"
        self.green = "\033[38;5;120m"
        self.red = "\033[38;5;204m"
        self.yellow = "\033[38;5;223m"
        self.gold = "\033[38;5;220m"
        self.pink = "\033[38;5;212m"
        self.orange = "\033[38;5;214m"
        self.purple = "\033[38;5;135m"
        self.reset = "\033[0m"
        
        self.brand = "PSYCHO BOT"
        self.author = "VENUJAN"
        self.web = "GIT"
        self.version = "12.0.0"

    def type_text(self, text, color="", delay=0.001):
        full_text = f"{color}{text}{self.reset}\n"
        for char in full_text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(delay)

    def show_banner(self, faucet_name="ClaimCoin"):
        os.system('cls' if os.name == 'nt' else 'clear')
        
        colors = ['\033[38;5;147m', '\033[38;5;123m', '\033[38;5;220m']
        banner_lines = [
            r"   ██████╗ ███████╗██╗   ██╗ ██████╗██╗  ██╗ ██████╗",
            r"   ██╔══██╗██╔════╝╚██╗ ██╔╝██╔════╝██║  ██║██╔═══██╗",
            r"   ██████╔╝███████╗ ╚████╔╝ ██║     ███████║██║   ██║",
            r"   ██╔═══╝ ╚════██║  ╚██╔╝  ██║     ██╔══██║██║   ██║",
            r"   ██║     ███████║   ██║   ╚██████╗██║  ██║╚██████╔╝",
            r"   ╚═╝     ╚══════╝   ╚═╝    ╚═════╝╚═╝  ╚═╝ ╚═════╝ "
        ]
        
        for line in banner_lines:
            print(f"{colors[0]}{line}{self.reset}")
            time.sleep(0.02)
        
        print()
        
        print(f" {self.gray}┌──────────────────────────────────────────────────────────────┐{self.reset}")
        print(f" {self.gray}│ {self.reset}Engine   {self.gray}» {self.gold}{faucet_name:<20} {self.gray}│ {self.reset}Version  {self.gray}» {self.sec}{self.version:<10} {self.gray}     │{self.reset}")
        print(f" {self.gray}│ {self.reset}Coder    {self.gray}» {self.pink}{self.author:<20} {self.gray}│ {self.reset}Solver   {self.gray}» {self.sec}FREE{self.reset} {self.gray}           │{self.reset}")
        print(f" {self.gray}└──────────────────────────────────────────────────────────────┘{self.reset}\n")

        if self.show_success and self.success_history:
            for past_success in self.success_history:
                print(f" {self.green}[SUCCESS]{self.reset} {past_success}")
                print(f" {self.gray}────────────────────────────────────────────────────────────{self.reset}")
            print()

    def info(self, message):
        self.type_text(f"  {self.gray}• {self.reset}{message}", self.gray, 0.001)

    def warning(self, message):
        self.type_text(f"  {self.yellow}! {self.reset}{message}", self.yellow, 0.002)

    def error(self, message):
        self.type_text(f"  {self.red}× {self.reset}{message}", self.red, 0.002)

    def success(self, message, faucet_name="ClaimCoin"):
        self.success_history.append(message)
        self.show_success = True
        self.show_banner(faucet_name)
    
    def show_menu_banner(self, faucet_name="ClaimCoin"):
        self.show_success = False
        self.show_banner(faucet_name)
    
    def show_work_banner(self, faucet_name="ClaimCoin"):
        self.show_success = True
        self.show_banner(faucet_name)

    def inline_status(self, text, color="\033[38;5;223m"):
        max_len = 80
        if len(text) > max_len:
            text = text[:max_len-3] + "..."
        sys.stdout.write(f"\r  {color}→ {self.reset}{text}")
        sys.stdout.flush()

    def clear_inline(self):
        sys.stdout.write("\r" + " " * 100 + "\r")
        sys.stdout.flush()

    def countdown(self, seconds, label="Interval Control"):
        if seconds <= 0:
            return
        
        bar_length = 30
        for i in range(seconds + 1):
            percent = (i / seconds) * 100
            filled = int(bar_length * i // seconds)
            bar = '■' * filled + '□' * (bar_length - filled)
            
            remaining = seconds - i
            if remaining >= 60:
                time_str = f"{remaining//60}m {remaining%60}s"
            else:
                time_str = f"{remaining}s"
            
            sys.stdout.write(f"\r  {self.yellow}⏳ {self.reset}{label} [{self.sec}{bar}{self.reset}] {self.gold}{percent:.0f}%{self.reset} {self.gray}({time_str}){self.reset}")
            sys.stdout.flush()
            if i < seconds:
                time.sleep(1)
        sys.stdout.write("\r" + " " * 100 + "\r")
        sys.stdout.flush()

bot = PsychoUI(typing_speed=0.002)

# ============================================================
# COLOR CODES FOR MENU
# ============================================================
C = {
    'header': '\033[38;5;147m',
    'menu': '\033[38;5;123m',
    'green': '\033[38;5;120m',
    'red': '\033[38;5;204m',
    'yellow': '\033[38;5;223m',
    'gray': '\033[38;5;243m',
    'gold': '\033[38;5;220m',
    'pink': '\033[38;5;212m',
    'orange': '\033[38;5;214m',
    'purple': '\033[38;5;135m',
    'reset': '\033[0m'
}

# ============================================================
# CONFIGURATION
# ============================================================
DOMAIN = "https://claimcoin.in"
LOGIN_URL = f"{DOMAIN}/login"
LOGIN_ACTION = f"{DOMAIN}/auth/login"
DASHBOARD_URL = f"{DOMAIN}/dashboard"
FAUCET_URL = f"{DOMAIN}/faucet"
FAUCET_VERIFY = f"{DOMAIN}/faucet/verify"

RECAPTCHA_SITEKEY = "6LdnVw4qAAAAAFPMxvegAK9JcBflI-0tb8YKMxZU"
RECAPTCHA_API = "https://bypassallshortlinks.space/rv3.php"

# FREE OCR API
OCR_BASE_URL = "https://nice-pet-sandboxhubaaa-600a0136.koyeb.app"
OCR_API_KEY = "free_ocr_api_key_2024"

SESSION_FILE = "claimcoin_session.json"
CONFIG_FILE = "claimcoin_config.json"
MEMORY_FILE = "antibot_memory.json"

# ============================================================
# MEMORY-BASED LEARNING SYSTEM
# ============================================================
class AntiBotMemory:
    def __init__(self):
        self.memory = {
            "successful_matches": [],
            "failed_matches": [],
            "ocr_corrections": {},
            "word_similarity_weights": {},
            "pattern_history": [],
            "success_count": 0,
            "fail_count": 0
        }
        self.load()
    
    def load(self):
        try:
            if os.path.exists(MEMORY_FILE):
                with open(MEMORY_FILE, 'r') as f:
                    saved = json.load(f)
                    self.memory.update(saved)
        except Exception:
            pass
    
    def save(self):
        try:
            with open(MEMORY_FILE, 'w') as f:
                json.dump(self.memory, f, indent=2)
        except Exception:
            pass
    
    def record_success(self, main_word, option_text, rel, similarity):
        self.memory["successful_matches"].append({
            "main_word": main_word,
            "option_text": option_text,
            "rel": rel,
            "similarity": similarity,
            "timestamp": time.time()
        })
        self.memory["success_count"] += 1
        
        if len(self.memory["successful_matches"]) > 1000:
            self.memory["successful_matches"] = self.memory["successful_matches"][-1000:]
        
        if main_word != option_text:
            if len(main_word) >= 2 and len(option_text) >= 2:
                if main_word[0] == option_text[0]:
                    self.memory["ocr_corrections"][option_text] = main_word
        
        self.save()
    
    def record_failure(self, main_word, option_text, rel):
        self.memory["failed_matches"].append({
            "main_word": main_word,
            "option_text": option_text,
            "rel": rel,
            "timestamp": time.time()
        })
        self.memory["fail_count"] += 1
        
        if len(self.memory["failed_matches"]) > 500:
            self.memory["failed_matches"] = self.memory["failed_matches"][-500:]
        
        if option_text in self.memory["ocr_corrections"]:
            del self.memory["ocr_corrections"][option_text]
        
        self.save()
    
    def get_correction(self, word):
        return self.memory["ocr_corrections"].get(word, word)
    
    def get_pattern_suggestion(self, main_words):
        pattern_key = "->".join(main_words)
        
        for history in self.memory["pattern_history"]:
            if history["pattern_key"] == pattern_key:
                return history.get("successful_order")
        
        return None
    
    def record_pattern(self, main_words, successful_order):
        pattern_key = "->".join(main_words)
        
        for i, history in enumerate(self.memory["pattern_history"]):
            if history["pattern_key"] == pattern_key:
                self.memory["pattern_history"][i] = {
                    "pattern_key": pattern_key,
                    "successful_order": successful_order,
                    "timestamp": time.time()
                }
                self.save()
                return
        
        self.memory["pattern_history"].append({
            "pattern_key": pattern_key,
            "successful_order": successful_order,
            "timestamp": time.time()
        })
        
        if len(self.memory["pattern_history"]) > 100:
            self.memory["pattern_history"] = self.memory["pattern_history"][-100:]
        
        self.save()
    
    def get_stats(self):
        return {
            "successes": self.memory["success_count"],
            "failures": self.memory["fail_count"],
            "corrections": len(self.memory["ocr_corrections"]),
            "patterns": len(self.memory["pattern_history"])
        }

antibot_memory = AntiBotMemory()

# ============================================================
# SESSION & CONFIG
# ============================================================
def save_session(cookies_dict, user_agent):
    data = {"cookies": cookies_dict, "user_agent": user_agent, "saved_at": time.time()}
    try:
        with open(SESSION_FILE, 'w') as f:
            json.dump(data, f)
        return True
    except Exception:
        return False

def load_session():
    try:
        if os.path.exists(SESSION_FILE):
            with open(SESSION_FILE, 'r') as f:
                return json.load(f)
    except Exception:
        pass
    return None

def save_config(config):
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f)
    except Exception:
        pass

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "email": "",
        "password": "",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

def get_input_with_default(prompt, default=""):
    if default:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "
    value = input(prompt).strip()
    return value if value else default

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# ============================================================
# RECAPTCHA V3 SOLVER
# ============================================================
def solve_recaptcha_v3(sitekey, pageurl, max_retries=3):
    for attempt in range(max_retries):
        try:
            payload = {"site_key": sitekey, "site_url": pageurl}
            resp = requests.post(RECAPTCHA_API, json=payload, timeout=30)
            result = resp.json()
            if result and result.get("token"):
                return result.get("token")
            time.sleep(2)
        except Exception:
            time.sleep(2)
    return None

# ============================================================
# OCR API FUNCTIONS - PARALLEL
# ============================================================
def ocr_check_balance():
    try:
        url = f"{OCR_BASE_URL}/balance.php"
        resp = requests.get(url, params={"apikey": OCR_API_KEY, "json": 1}, timeout=10)
        if resp.status_code == 200:
            return resp.json()
        return None
    except Exception:
        return None

def ocr_poll_result(job_id, max_attempts=30, delay=3):
    url = f"{OCR_BASE_URL}/res.php"
    params = {"apikey": OCR_API_KEY, "id": job_id, "json": 1}
    for attempt in range(max_attempts):
        time.sleep(delay)
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                result_data = response.json()
                status = result_data.get("status")
                request_val = result_data.get("request", "")
                if status == 1 or status == "OK":
                    return str(request_val)
                if status == 0 and request_val != "CAPCHA_NOT_READY":
                    return str(request_val)
                if request_val == "CAPCHA_NOT_READY":
                    continue
        except Exception:
            continue
    return None

def ocr_image_to_text(base64_image):
    url = f"{OCR_BASE_URL}/in.php"
    payload = {
        "apikey": OCR_API_KEY,
        "methods": "image-to-text",
        "base64_img": base64_image,
        "json": 1,
    }
    try:
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            res_json = response.json()
            if res_json.get("status") == 1 or "request" in res_json:
                job_id = res_json.get("request")
                return ocr_poll_result(job_id)
            elif res_json.get("status") == 0:
                return str(res_json.get("request", ""))
        return None
    except Exception:
        return None

# ============================================================
# OCR WORD MATCHING
# ============================================================

OCR_CORRECTIONS = {
    'gvm': 'gum', 'gum': 'gum',
    'rb': 'rib', 'rib': 'rib',
    'yok': 'yak', 'yak': 'yak',
    'y3p': 'yep', 'yep': 'yep',
    'my yv': 'yak',
    'eye': 'eye', '3 y 3': 'eye',
    'gum': 'gum', 'rib': 'rib', 'yak': 'yak', 'yep': 'yep',
    'yum': 'yum', 'yak': 'yak', 'yep': 'yep',
    'col': 'col', 'hot': 'hot', 'big': 'big',
    'org': 'org', 'blk': 'blk', 'gry': 'gry',
    'far': 'far', 'fog': 'fog', 'sky': 'sky',
    'tea': 'tea', 'ice': 'ice', 'pan': 'pan',
    'rib': 'rib', 'eye': 'eye', 'gum': 'gum',
    'win': 'win', 'sun': 'sun', 'log': 'log',
    'car': 'car', 'dog': 'dog', 'cat': 'cat',
    'red': 'red', 'box': 'box', 'cup': 'cup',
    'pen': 'pen', 'hat': 'hat', 'map': 'map',
    'bus': 'bus', 'fox': 'fox', 'sky': 'sky',
    'leg': 'leg', 'low': 'low', 'lux': 'lux',
    'bull': 'bull', 'goat': 'goat', 'ox': 'ox',
}

COLOR_MAP = {
    'red': 'red', 'blue': 'blue', 'blu': 'blue', 'green': 'green', 'grn': 'green', 'gm': 'green',
    'yellow': 'yellow', 'yllw': 'yellow', 'ylw': 'yellow',
    'pink': 'pink', 'pnk': 'pink', 'p1n': 'pink',
    'brown': 'brown', 'brn': 'brown', 'bmn': 'brown',
    'gray': 'gray', 'gry': 'gray', 'grey': 'gray',
    'black': 'black', 'blk': 'black', 'white': 'white', 'wht': 'white',
    'purple': 'purple', 'prpl': 'purple', 'orange': 'orange', 'orng': 'orange', 'org': 'orange',
    'gold': 'gold', 'silver': 'silver',
}

def clean_ocr_text(raw_text):
    if not raw_text:
        return ""
    text = str(raw_text).strip()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s]', '', text)
    return text.strip().lower()

def levenshtein_distance(s1, s2):
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]

def enhanced_word_similarity(w1, w2):
    if not w1 or not w2:
        return 0.0
    
    w1 = w1.lower().strip()
    w2 = w2.lower().strip()
    
    corrected_w1 = antibot_memory.get_correction(w1)
    corrected_w2 = antibot_memory.get_correction(w2)
    
    if corrected_w1 == w2:
        return 0.98
    if w1 == corrected_w2:
        return 0.98
    
    if w1 == w2:
        return 1.0
    
    if w1 in OCR_CORRECTIONS and OCR_CORRECTIONS[w1] == w2:
        return 0.95
    if w2 in OCR_CORRECTIONS and OCR_CORRECTIONS[w2] == w1:
        return 0.95
    
    if w1 in COLOR_MAP and w2 in COLOR_MAP:
        if COLOR_MAP[w1] == COLOR_MAP[w2]:
            return 0.95
    
    if len(w1) >= 2 and len(w2) >= 2:
        if w1[0] == w2[0] and w1[-1] == w2[-1]:
            return 0.85
    
    if len(w1) == 3 and len(w2) == 3 and w1[0] == w2[0]:
        return 0.75
    
    if len(w1) == 3 and len(w2) == 3 and w1[1] == w2[1]:
        return 0.70
    
    max_len = max(len(w1), len(w2))
    if max_len > 0:
        distance = levenshtein_distance(w1, w2)
        similarity = 1.0 - (distance / max_len)
        if similarity >= 0.4:
            return similarity * 0.8
    
    if len(w1) >= 2 and len(w2) >= 2:
        if abs(len(w1) - len(w2)) <= 1 and w1[0] == w2[0]:
            return 0.6
    
    return 0.0

def identify_text(text):
    if not text:
        return ('unknown', text, text)
    
    t = clean_ocr_text(text)
    if not t:
        return ('unknown', text, t)
    
    corrected = antibot_memory.get_correction(t)
    if corrected != t:
        return ('unknown', corrected, t)
    
    if t in OCR_CORRECTIONS:
        return ('unknown', OCR_CORRECTIONS[t], t)
    
    if t in COLOR_MAP:
        return ('color', COLOR_MAP[t], t)
    
    if t.isdigit():
        return ('number', t, t)
    
    return ('unknown', t, t)

# ============================================================
# PARALLEL OCR - Process all images simultaneously
# ============================================================
def process_single_image(img_b64, label):
    """Process a single image OCR"""
    raw = ocr_image_to_text(img_b64)
    if raw:
        cleaned = clean_ocr_text(str(raw))
        if cleaned:
            category, normalized, display = identify_text(cleaned)
            return {
                'raw': cleaned,
                'normalized': normalized,
                'category': category,
                'display': display,
                'label': label
            }
    return None

def process_images_parallel(main_base64, option_images, option_rels):
    """
    Process main image and all option images in parallel
    Returns: main_words, option_data
    """
    results = {}
    
    # Prepare all tasks
    tasks = []
    
    # Main image task
    tasks.append(('main', main_base64, 'Main'))
    
    # Option image tasks
    for i, (rel, img_b64) in enumerate(zip(option_rels, option_images)):
        tasks.append((rel, img_b64, f"Opt{i+1}"))
    
    # Process in parallel
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_task = {
            executor.submit(process_single_image, img_b64, label): (task_id, label)
            for task_id, img_b64, label in tasks
        }
        
        for future in as_completed(future_to_task):
            task_id, label = future_to_task[future]
            try:
                result = future.result(timeout=60)
                if result:
                    results[task_id] = result
            except Exception:
                pass
    
    # Extract main words
    main_words = None
    if 'main' in results:
        raw_text = results['main'].get('raw', '')
        if raw_text:
            parts = re.split(r'[\s,;:|]+', raw_text)
            parts = [p.strip() for p in parts if p.strip()]
            if len(parts) >= 2:
                main_words = parts
    
    # Extract option data
    option_data = {}
    for rel in option_rels:
        if rel in results:
            option_data[rel] = results[rel]
    
    return main_words, option_data

# ============================================================
# SOLVE SINGLE IMAGE - For testing only
# ============================================================
def solve_image_once(base64_image, img_label=""):
    raw = ocr_image_to_text(base64_image)
    if raw:
        cleaned = clean_ocr_text(str(raw))
        if cleaned:
            category, normalized, display = identify_text(cleaned)
            return {
                'raw': cleaned,
                'normalized': normalized,
                'category': category,
                'display': display
            }
    return None

# ============================================================
# PARSE MAIN IMAGE - For testing only
# ============================================================
def parse_main_image_sequence(main_base64):
    raw = ocr_image_to_text(main_base64)
    if raw:
        cleaned = clean_ocr_text(str(raw))
        if cleaned:
            parts = re.split(r'[\s,;:|]+', cleaned)
            parts = [p.strip() for p in parts if p.strip()]
            if len(parts) >= 2:
                return parts
    return None

# ============================================================
# MAIN ANTI-BOT SOLVER WITH PARALLEL OCR
# ============================================================
def solve_antibot_with_memory(html):
    """
    AntiBot solver using parallel OCR and memory-based learning
    """
    bot.inline_status("Solving AntiBot...")
    
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract Main Image
        main_base64 = None
        alert = soup.find('div', class_='alert-warning')
        if not alert:
            alert = soup.find('p', class_='alert-warning')
        if not alert:
            alert = soup.find('div', id='atb-instruction')
        
        if alert:
            main_img = alert.find('img')
            if main_img and 'src' in main_img.attrs:
                src = main_img['src']
                if 'base64,' in src:
                    main_base64 = src.split('base64,')[1]
        
        if not main_base64:
            for img in soup.find_all('img'):
                src = img.get('src', '')
                if 'base64,' in src:
                    main_base64 = src.split('base64,')[1]
                    break
        
        if not main_base64:
            bot.clear_inline()
            bot.error("Main image not found!")
            return None
        
        # Find ablinks Script
        script_tag = None
        for script in soup.find_all('script'):
            if script.string and 'ablinks' in script.string:
                script_tag = script
                break
        
        if not script_tag:
            bot.clear_inline()
            bot.error("ablinks script not found!")
            return None
        
        script_text = script_tag.string
        
        # Extract rels and images
        rels = []
        images = []
        
        pattern1 = re.findall(
            r'rel\s*=\s*["\'](\d+)["\'].*?src\s*=\s*["\']data:image/png;base64,([^"\']+)["\']',
            script_text, re.DOTALL
        )
        
        pattern2 = re.findall(
            r'rel\s*=\s*\\"(\d+)\\".*?src\s*=\s*\\"data:image/png;base64,([^\\]+)\\',
            script_text, re.DOTALL
        )
        
        pattern3 = re.findall(
            r'rel\s*=\s*&quot;(\d+)&quot;.*?src\s*=\s*&quot;data:image/png;base64,([^&]+)&quot;',
            script_text, re.DOTALL
        )
        
        if not pattern1 and not pattern2 and not pattern3:
            all_rels = re.findall(r'rel\s*=\s*["\']?(\d+)["\']?', script_text)
            all_images = re.findall(r'data:image/png;base64,([^"\'\s\\]+)', script_text)
            all_images = [img.replace('\\', '') for img in all_images]
            
            if all_rels and all_images:
                filtered = []
                for img in all_images:
                    if len(img) > 50 and img[:50] != main_base64[:50]:
                        filtered.append(img)
                
                if len(filtered) >= len(all_rels):
                    images = filtered[:len(all_rels)]
                    rels = all_rels
                elif len(all_images) >= len(all_rels):
                    images = all_images[-len(all_rels):]
                    rels = all_rels
                else:
                    min_len = min(len(all_rels), len(all_images))
                    rels = all_rels[:min_len]
                    images = all_images[:min_len]
        
        if pattern1:
            rels = [p[0] for p in pattern1]
            images = [p[1] for p in pattern1]
        elif pattern2:
            rels = [p[0] for p in pattern2]
            images = [p[1].replace('\\', '') for p in pattern2]
        elif pattern3:
            rels = [p[0] for p in pattern3]
            images = [p[1] for p in pattern3]
        
        if len(rels) < 2 or len(images) < 2:
            bot.clear_inline()
            bot.error("Not enough options!")
            return None
        
        min_len = min(len(rels), len(images))
        rels = rels[:min_len]
        images = images[:min_len]
        
        # STEP 1: Process all images in parallel
        main_words, option_data = process_images_parallel(main_base64, images, rels)
        
        bot.clear_inline()
        
        if not main_words or len(main_words) < 2:
            bot.error("Could not parse main image!")
            sorted_rels = sorted(rels, key=lambda x: int(x))
            return " " + " ".join(sorted_rels)
        
        if len(option_data) < 2:
            bot.error("Not enough OCR results!")
            sorted_rels = sorted(rels, key=lambda x: int(x))
            return " " + " ".join(sorted_rels)
        
        # Check if pattern exists in memory
        remembered_order = antibot_memory.get_pattern_suggestion(main_words)
        
        if remembered_order:
            bot.info(f"✅ Pattern found in memory!")
            return remembered_order
        
        # Match using enhanced similarity
        ordered_rels = []
        used_rels = set()
        
        for main_word in main_words:
            best_rel = None
            best_similarity = 0.0
            
            for rel, data in option_data.items():
                if rel in used_rels:
                    continue
                
                sim = enhanced_word_similarity(data['raw'], main_word)
                
                if sim > best_similarity:
                    best_similarity = sim
                    best_rel = rel
            
            if best_rel and best_similarity >= 0.4:
                ordered_rels.append(best_rel)
                used_rels.add(best_rel)
        
        # Add unmatched rels
        for rel in rels:
            if rel not in used_rels:
                ordered_rels.append(rel)
        
        if len(ordered_rels) >= 2:
            result = " " + " ".join(ordered_rels)
            
            # Record pattern
            antibot_memory.record_pattern(main_words, result)
            
            # Record successes
            for i, main_word in enumerate(main_words):
                if i < len(ordered_rels):
                    rel = ordered_rels[i]
                    if rel in option_data:
                        antibot_memory.record_success(
                            main_word,
                            option_data[rel]['raw'],
                            rel,
                            0.8
                        )
            
            return result
        
        # FALLBACK
        sorted_rels = sorted(rels, key=lambda x: int(x))
        result = " " + " ".join(sorted_rels)
        return result
        
    except Exception as e:
        bot.clear_inline()
        bot.error(f"AntiBot error: {str(e)}")
        return None

def solve_antibot_with_retry(html, session, max_retries=3):
    for attempt in range(max_retries):
        if attempt > 0:
            try:
                resp = session.get(FAUCET_URL, headers=session._headers(), timeout=15)
                if resp.status_code == 200:
                    html = resp.text
                else:
                    continue
            except Exception:
                continue
        
        result = solve_antibot_with_memory(html)
        if result:
            return result
        
        time.sleep(2)
    
    return None

# ============================================================
# MAIN BOT CLASS
# ============================================================
class ClaimCoinBot:
    def __init__(self, config):
        self.config = config
        self.email = config.get("email", "")
        self.password = config.get("password", "")
        self.user_agent = config.get("user_agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': self.user_agent})
        
        saved = load_session()
        if saved and saved.get("user_agent"):
            self.user_agent = saved["user_agent"]
            for name, value in saved["cookies"].items():
                self.session.cookies.set(name, value, domain="claimcoin.in")
        
        self.logged_in = False
        self.balance = 0
        self.username = ""
        self.total_claimed = 0
        self.main_words = []
        
    def _headers(self, extra=None):
        headers = {
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Connection': 'keep-alive',
            'Referer': DOMAIN,
        }
        if extra:
            headers.update(extra)
        return headers
    
    def _get_csrf(self, html):
        try:
            soup = BeautifulSoup(html, 'html.parser')
            csrf = soup.find('input', {'name': 'csrf_token_name'})
            if csrf and csrf.get('value'):
                return csrf.get('value')
            csrf = soup.find('input', {'id': 'token'})
            if csrf and csrf.get('value'):
                return csrf.get('value')
            return None
        except Exception:
            return None
    
    def _get_balance(self, html):
        try:
            match = re.search(r'<h2>([\d,]+)\s*CCP</h2>', html)
            if match:
                return float(match.group(1).replace(',', ''))
            return 0
        except Exception:
            return 0
    
    def _get_username(self, html):
        try:
            match = re.search(r'key="t-henry">([^<]+)</span>', html)
            if match:
                return match.group(1).strip()
            return None
        except Exception:
            return None
    
    def _get_timer(self, html):
        try:
            match = re.search(r'class="badge bg-primary counter" wait="(\d+)"', html)
            if match:
                return int(match.group(1))
            return 0
        except Exception:
            return 0
    
    def _get_swal_message(self, html):
        try:
            match = re.search(r"Swal\.fire\(\s*'([^']+)'\s*,\s*'([^']+)'\s*,\s*'([^']+)'\s*\)", html)
            if match:
                return {"title": match.group(1), "text": match.group(2), "icon": match.group(3)}
            return None
        except Exception:
            return None
    
    def is_logged_in(self):
        try:
            resp = self.session.get(DASHBOARD_URL, headers=self._headers(), timeout=10)
            if resp.status_code == 200:
                if '<title>Dashboard' in resp.text:
                    self.logged_in = True
                    self.balance = self._get_balance(resp.text)
                    self.username = self._get_username(resp.text)
                    return True
            return False
        except Exception:
            return False
    
    def login(self):
        try:
            resp = self.session.get(LOGIN_URL, headers=self._headers(), timeout=15)
            if resp.status_code != 200:
                return False
            
            html = resp.text
            csrf = self._get_csrf(html)
            if not csrf:
                return False
            
            payload = {
                'csrf_token_name': csrf,
                'email': self.email,
                'password': self.password
            }
            
            time.sleep(random.uniform(1, 2))
            
            resp = self.session.post(
                LOGIN_ACTION,
                data=payload,
                headers=self._headers({'Content-Type': 'application/x-www-form-urlencoded'}),
                timeout=30,
                allow_redirects=True
            )
            
            if '<title>Dashboard' in resp.text or '/dashboard' in resp.url:
                cookies = self.session.cookies.get_dict()
                save_session(cookies, self.user_agent)
                self.logged_in = True
                self.balance = self._get_balance(resp.text)
                self.username = self._get_username(resp.text)
                return True
            
            return False
        except Exception:
            return False
    
    def ensure_logged_in(self):
        if self.is_logged_in():
            return True
        return self.login()
    
    def claim_faucet(self):
        try:
            resp = self.session.get(FAUCET_URL, headers=self._headers(), timeout=15)
            if resp.status_code != 200:
                return False
            
            html = resp.text
            
            if 'READY' not in html:
                wait_time = self._get_timer(html)
                if wait_time > 0:
                    bot.info(f"Faucet cooldown: {wait_time}s")
                    bot.countdown(wait_time + 2, "Faucet Timer")
                    return self.claim_faucet()
                else:
                    return False
            
            csrf = self._get_csrf(html)
            if not csrf:
                return False
            
            # AntiBot with retry
            bot.inline_status("Solving AntiBot...")
            antibot = solve_antibot_with_retry(html, self.session, max_retries=3)
            bot.clear_inline()
            
            if not antibot:
                bot.warning("Failed to solve AntiBot!")
                return False
            
            # reCAPTCHA
            recaptcha_token = solve_recaptcha_v3(RECAPTCHA_SITEKEY, FAUCET_URL, max_retries=3)
            if not recaptcha_token:
                bot.warning("Failed to get reCAPTCHA token!")
                return False
            
            payload = {
                'captcha': 'recaptchav3',
                'recaptchav3': recaptcha_token,
                'antibotlinks': antibot,
                'csrf_token_name': csrf
            }
            
            time.sleep(random.uniform(1, 2))
            
            resp = self.session.post(
                FAUCET_VERIFY,
                data=payload,
                headers=self._headers({'Content-Type': 'application/x-www-form-urlencoded'}),
                timeout=30,
                allow_redirects=True
            )
            
            swal = self._get_swal_message(resp.text)
            if swal and swal['icon'] == 'success':
                self.total_claimed += 1
                self.balance = self._get_balance(resp.text)
                bot.success(f"Good job! {swal['text']}", "ClaimCoin")
                
                stats = antibot_memory.get_stats()
                bot.info(f"📊 Memory: {stats['successes']} successes, {stats['corrections']} corrections")
                return True
            
            wait_time = self._get_timer(resp.text)
            if wait_time > 0:
                bot.info(f"Next claim in: {wait_time}s")
                return "cooldown"
            
            return False
        except Exception as e:
            bot.warning(f"Faucet error: {str(e)}")
            return False
    
    def run(self):
        bot.show_work_banner("ClaimCoin")
        
        if not self.email or not self.password:
            bot.error("Email and Password required!")
            input("\nPress Enter to continue...")
            return
        
        if not self.ensure_logged_in():
            bot.error("Login failed!")
            input("\nPress Enter to continue...")
            return
        
        bot.info(f"Balance: {self.balance} CCP")
        bot.info(f"User: {self.username}")
        
        stats = antibot_memory.get_stats()
        bot.info(f"📚 Memory: {stats['successes']} successes, {stats['patterns']} patterns")
        
        cycle = 0
        
        while True:
            cycle += 1
            bot.info(f"--- Cycle {cycle} ---")
            bot.info(f"Total claims: {self.total_claimed}")
            
            if not self.is_logged_in():
                bot.info("Session expired. Re-logging...")
                if not self.login():
                    bot.error("Re-login failed!")
                    input("\nPress Enter to continue...")
                    break
            
            result = self.claim_faucet()
            
            if result == "cooldown":
                continue
            elif result == True:
                continue
            else:
                bot.info("Retrying in 5s...")
                bot.countdown(5, "Retry")

# ============================================================
# MENU FUNCTIONS
# ============================================================
def print_header(text):
    print(f"{C['header']}{'═'*55}{C['reset']}")
    print(f"{C['header']}  {text}{C['reset']}")
    print(f"{C['header']}{'═'*55}{C['reset']}")

def print_menu_option(key, value):
    print(f"  {C['menu']}▶ [{key}]{C['reset']} {value}")

def print_info(text):
    print(f"  {C['gray']}• {C['reset']}{text}")

def print_success(text):
    print(f"  {C['green']}✔ {C['reset']}{text}")

def print_error(text):
    print(f"  {C['red']}✘ {C['reset']}{text}")

def print_warning(text):
    print(f"  {C['yellow']}⚠ {C['reset']}{text}")

def print_instruction(text):
    print(f"  {C['orange']}ℹ {C['reset']}{text}")

def get_menu_choice(prompt, options):
    print(f"\n{C['gold']}{prompt}{C['reset']}")
    print(f"{C['gray']}{'─'*55}{C['reset']}")
    for key, value in options.items():
        print_menu_option(key, value)
    print(f"{C['gray']}{'─'*55}{C['reset']}")
    while True:
        choice = input(f"{C['menu']}Select option: {C['reset']}").strip()
        if choice in options:
            return choice
        print_error("Invalid option.")

def show_main_menu():
    clear_screen()
    bot.show_menu_banner("ClaimCoin")
    print_header("ClaimCoin Bot + MEMORY")
    
    menu_options = {
        '1': 'Set User Agent',
        '2': 'Set Account',
        '3': 'Start Bot',
        '4': 'Exit'
    }
    return get_menu_choice("Main Menu:", menu_options)

def set_account_menu(config):
    clear_screen()
    bot.show_menu_banner("ClaimCoin")
    print_header("Set Account")
    email = get_input_with_default("Email", config.get('email', ''))
    password = get_input_with_default("Password", config.get('password', ''))
    config['email'] = email
    config['password'] = password
    save_config(config)
    print_success("Saved!")
    input("\nPress Enter...")

def main():
    config = load_config()
    while True:
        try:
            choice = show_main_menu()
            if choice == '1':
                clear_screen()
                bot.show_menu_banner("ClaimCoin")
                print_header("User Agent")
                current = config.get('user_agent', 'Mozilla/5.0')
                new_ua = get_input_with_default("UA", current)
                config['user_agent'] = new_ua
                save_config(config)
                print_success("Saved!")
                input("\nPress Enter...")
            elif choice == '2':
                set_account_menu(config)
            elif choice == '3':
                clear_screen()
                bot.show_menu_banner("ClaimCoin")
                if not config.get('email') or not config.get('password'):
                    print_error("Set account first!")
                    input("\nPress Enter...")
                    continue
                bot_obj = ClaimCoinBot(config)
                try:
                    bot_obj.run()
                except KeyboardInterrupt:
                    bot.clear_inline()
                    print(f'\n{C["yellow"]}[STOPPED]{C["reset"]}')
                    time.sleep(1.5)
                except Exception as e:
                    bot.error(f"Error: {str(e)}")
                    input("\nPress Enter...")
            elif choice == '4':
                print(f"\n{C['yellow']}Exit...{C['reset']}")
                break
        except KeyboardInterrupt:
            print(f"\n{C['yellow']}Exit...{C['reset']}")
            break
        except Exception as e:
            print_error(f"Error: {str(e)}")
            input("\nPress Enter...")

if __name__ == "__main__":
    main()
