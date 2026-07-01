#!/usr/bin/env python3
"""
OpenEarn Bot – ADVANCED DASHBOARD + LIVE LOGS
- 30s simulated ad watching
- Correct "OPEN EARN" banner
- Moving cooldown timers
- Live logs that actually work
"""

import os
import sys
import asyncio
import json
import time
import random
import re
import tempfile
import urllib.parse
import requests
from datetime import datetime, timezone
from urllib.parse import parse_qs, urlparse
from typing import Optional, Dict, List, Tuple, Any

# ========== COLORS ==========
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
BLUE = "\033[94m"
WHITE = "\033[97m"
BOLD = "\033[1m"
RESET = "\033[0m"

# ========== LOGGING ==========
LOG_FILE = "openearn.log"
LIVE_LOG = []  # Store last 10 log messages
LOG_LOCK = asyncio.Lock()

def add_log(message: str):
    """Add message to live log"""
    global LIVE_LOG
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    
    # Write to file
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry + "\n")
    
    # Update live log (keep last 10)
    LIVE_LOG.append(log_entry)
    if len(LIVE_LOG) > 10:
        LIVE_LOG.pop(0)

def log_api(endpoint: str, status: int, data: dict = None, error: str = None):
    timestamp = datetime.now().strftime("%H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] [API] {endpoint} -> {status}\n")
        if data:
            f.write(f"[{timestamp}] [API] Response: {json.dumps(data, indent=2)}\n")
        if error:
            f.write(f"[{timestamp}] [API] Error: {error}\n")
        f.write("-" * 80 + "\n")

# ========== CONFIG ==========
API_ID = 32744606
API_HASH = 'f58682565ec84dcd4e529a33246f07aa'
BOT_USERNAME = 'TheOpenEarnAppBot'
BASE_URL = "https://app.theopenearn.info/api"
AD_WATCH_DURATION = 30

TAPS_PER_REQUEST = 25
TOTAL_TAPS = 100

# ========== PROVIDER CONFIG ==========
PROVIDER_CONFIG = {
    'adsgram': {'ad_type': 'video', 'fallback': True},
    'monetag': {'ad_type': 'impression', 'fallback': True},
    'telega': {'ad_type': 'video', 'fallback': True},
    'richads': {'ad_type': 'video', 'fallback': True},
    'onclicka': {'ad_type': 'video', 'fallback': True},
    'taddy': {'ad_type': 'video', 'fallback': True},
    'gigapub': {'ad_type': 'video', 'fallback': True},
    'adsgram_task': {'ad_type': 'task', 'fallback': True},
}

# ========== SUPPRESS PYROGRAM WELCOME ==========
import contextlib
with contextlib.redirect_stdout(open(os.devnull, 'w')):
    from pyrogram import Client
    from pyrogram.raw.functions.messages import RequestWebView

# ========== HELPER FUNCTIONS ==========
def get_balance(headers):
    try:
        resp = requests.get(f"{BASE_URL}/user", headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return data.get('balance', '0'), data.get('tot_balance', '0')
    except:
        pass
    return None, None

async def refresh_tg_data(session_str):
    client = Client(":memory:", session_string=session_str, api_id=API_ID, api_hash=API_HASH)
    await client.connect()
    bot_peer = await client.resolve_peer(BOT_USERNAME)
    web_view = await client.invoke(
        RequestWebView(peer=bot_peer, bot=bot_peer, url="https://app.theopenearn.com/", platform="ios")
    )
    parsed = urlparse(web_view.url)
    fragment = parse_qs(parsed.fragment)
    tg_data = fragment['tgWebAppData'][0]
    await client.disconnect()
    return tg_data

def build_headers(tg_data):
    headers = {
        'Authorization': f"tma {tg_data}",
        'Accept': '*/*',
        'Accept-Language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1'
    }
    return headers

# ========== PYROGRAM LOGIN ==========
async def pyrogram_login(phone):
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        session_path = tmp.name
    client = Client(session_path, api_id=API_ID, api_hash=API_HASH)
    await client.connect()
    try:
        sent_code = await client.send_code(phone)
        print(f"{BOLD}{GREEN}Enter confirmation code: {RESET}", end="")
        code = input().strip()
        try:
            await client.sign_in(phone, sent_code.phone_code_hash, code)
        except Exception:
            print(f"{BOLD}{GREEN}Enter 2FA password: {RESET}", end="")
            pwd = input().strip()
            await client.check_password(pwd)
        me = await client.get_me()
        session_str = await client.export_session_string()
        await client.disconnect()
        os.unlink(session_path)
        return me, session_str
    except Exception as e:
        await client.disconnect()
        os.unlink(session_path)
        raise e

async def add_accounts():
    print(f"\n{BOLD}{CYAN}🔹 ADD TELEGRAM ACCOUNTS{RESET}")
    print(f"{BOLD}{'─' * 50}{RESET}")
    num = int(input(f"{BOLD}{YELLOW}How many accounts to add? : {RESET}"))
    new_accounts = []
    for i in range(num):
        print(f"\n{BOLD}{MAGENTA}--- Account {i+1} ---{RESET}")
        phone = input(f"{BOLD}{GREEN}Phone number (with country code): {RESET}").strip()
        print(f"{BOLD}{YELLOW}ℹ️ Logging in...{RESET}")
        try:
            me, session_str = await pyrogram_login(phone)
            username = me.username or phone
            new_accounts.append({
                "phone": phone,
                "session": session_str,
                "username": username
            })
            print(f"{BOLD}{GREEN}✅ Account {username} added.{RESET}")
        except Exception as e:
            print(f"{BOLD}{RED}❌ Login failed: {e}{RESET}")
    return new_accounts

async def manage_accounts():
    existing = []
    if os.path.exists("pyro_accounts.json"):
        with open("pyro_accounts.json", "r") as f:
            existing = json.load(f)
        if existing:
            print(f"\n{BOLD}{CYAN}🔹 EXISTING ACCOUNTS{RESET}")
            print(f"{BOLD}{'─' * 50}{RESET}")
            for acc in existing:
                print(f"{BOLD}{GREEN}  - {acc.get('username', acc['phone'])}{RESET}")
            add_more = input(f"\n{BOLD}{YELLOW}Add more accounts? (y/n): {RESET}").strip().lower()
            if add_more == 'y':
                new_accs = await add_accounts()
                existing.extend(new_accs)
                with open("pyro_accounts.json", "w") as f:
                    json.dump(existing, f, indent=4)
            return existing
    new_accs = await add_accounts()
    if new_accs:
        with open("pyro_accounts.json", "w") as f:
            json.dump(new_accs, f, indent=4)
    return new_accs

# ========== BANNER ==========
def banner():
    return f"""
{CYAN}╔══════════════════════════════════════════════════════════════════════════╗{RESET}
{CYAN}║{RESET} {MAGENTA}  ██████╗ ██████╗ ███████╗███╗   ██╗    ███████╗ █████╗ ██████╗ ███╗   ██╗{RESET} {CYAN}║{RESET}
{CYAN}║{RESET} {MAGENTA} ██╔═══╝ ██╔══██╗██╔════╝████╗  ██║    ██╔════╝██╔══██╗██╔══██╗████╗  ██║{RESET} {CYAN}║{RESET}
{CYAN}║{RESET} {MAGENTA} ██║     ██████╔╝█████╗  ██╔██╗ ██║    █████╗  ███████║██████╔╝██╔██╗ ██║{RESET} {CYAN}║{RESET}
{CYAN}║{RESET} {MAGENTA} ██║     ██╔═══╝ ██╔══╝  ██║╚██╗██║    ██╔══╝  ██╔══██║██╔══██╗██║╚██╗██║{RESET} {CYAN}║{RESET}
{CYAN}║{RESET} {MAGENTA} ╚██████╗██║     ███████╗██║ ╚████║    ███████╗██║  ██║██║  ██║██║ ╚████║{RESET} {CYAN}║{RESET}
{CYAN}║{RESET} {MAGENTA}  ╚═════╝╚═╝     ╚══════╝╚═╝  ╚═══╝    ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝{RESET} {CYAN}║{RESET}
{CYAN}╠══════════════════════════════════════════════════════════════════════════╣{RESET}
{CYAN}║{RESET} {GREEN}🚀 OPEN EARN BOT - ADVANCED DASHBOARD {YELLOW}v2.0 {CYAN}║{RESET}
{CYAN}╚══════════════════════════════════════════════════════════════════════════╝{RESET}
"""

# ========== ACCOUNT ENGINE ==========
class AccountEngine:
    def __init__(self, account_info):
        self.phone = account_info['phone']
        self.username = account_info['username']
        self.session_str = account_info['session']
        self.headers = None
        self.next_tap = time.time()
        self.next_ad = time.time()
        self.balance = "0"
        self.tot = "0"
        self.info = "INIT"
        self.progress = ""
        self.user_id = None
        self.user_data = None
        self.ad_session_active = False
        self.last_tx_id = None
        self.total_ads = 0
        self.total_tot = 0
        self.total_ton = 0.0
        self.providers_status = {}
        self.running = True
        self.ad_timer = 0
        self.current_provider = ""
        self.last_log = ""
        self.update_status()

    def update_status(self):
        return {
            'username': self.username,
            'info': self.info,
            'progress': self.progress,
            'balance': self.balance,
            'tot': self.tot,
            'total_ads': self.total_ads,
            'total_tot': self.total_tot,
            'total_ton': self.total_ton,
            'providers': self.providers_status,
            'ad_timer': self.ad_timer,
            'current_provider': self.current_provider
        }

    def log(self, message: str):
        """Add log message with account prefix"""
        log_msg = f"[{self.username}] {message}"
        add_log(log_msg)
        self.last_log = message
        self.update_status()

    async def fetch_initial_tg_data(self):
        try:
            tg_data = await refresh_tg_data(self.session_str)
            self.headers = build_headers(tg_data)
            
            params = dict(urllib.parse.parse_qsl(tg_data))
            user_param = params.get('user', '')
            if user_param:
                user_json = json.loads(urllib.parse.unquote(user_param))
                self.user_id = str(user_json.get('id', ''))
            
            resp = requests.get(f"{BASE_URL}/user", headers=self.headers, timeout=10)
            log_api("/user", resp.status_code, resp.json() if resp.status_code == 200 else None)
            
            if resp.status_code == 200:
                self.user_data = resp.json()
                self.balance = str(self.user_data.get('balance', '0'))
                self.tot = str(self.user_data.get('tot_balance', '0'))
                self.log(f"💰 Balance: {self.balance} TON, TOT: {self.tot}")
            
            self.info = "🟢 READY"
            return True
        except Exception as e:
            self.log(f"❌ Fetch error: {e}")
            return False

    async def get_daily_ad_status(self) -> Tuple[Optional[List[str]], Optional[Dict]]:
        try:
            resp = requests.get(f"{BASE_URL}/ads/daily-status", headers=self.headers, timeout=10)
            
            if resp.status_code == 200:
                data = resp.json()
                log_api("/ads/daily-status", resp.status_code, data)
                
                providers = data.get('providers', {})
                self.providers_status = {}
                available = []
                
                for name, info in providers.items():
                    remaining = info.get('remaining', 0)
                    blocked = info.get('blocked', False)
                    cooldown = info.get('cooldown_remaining', 0)
                    limit = info.get('limit', 0)
                    used = info.get('used', 0)
                    
                    self.providers_status[name] = {
                        'remaining': remaining,
                        'blocked': blocked,
                        'cooldown': cooldown,
                        'limit': limit,
                        'used': used
                    }
                    
                    if remaining > 0 and not blocked and cooldown == 0:
                        available.append(name)
                
                return available, self.providers_status
            else:
                return None, None
                
        except Exception as e:
            self.log(f"❌ Daily status error: {e}")
            return None, None

    async def simulate_watch_ad(self, provider: str):
        """Simulate watching an ad with countdown"""
        self.current_provider = provider
        self.info = f"📺 WATCHING {provider.upper()}"
        self.ad_timer = AD_WATCH_DURATION
        
        for remaining in range(AD_WATCH_DURATION, 0, -1):
            if not self.running:
                return
            self.ad_timer = remaining
            self.progress = f"⏳ {remaining}s"
            self.update_status()
            await asyncio.sleep(1)
        
        self.ad_timer = 0

    async def complete_ad(self, provider: str) -> Optional[Dict]:
        """Complete an ad with simulation"""
        try:
            self.ad_session_active = True
            
            # Simulate watching ad
            await self.simulate_watch_ad(provider)
            
            config = PROVIDER_CONFIG.get(provider, {'ad_type': 'video', 'fallback': True})
            ad_type = config.get('ad_type', 'video')
            fallback = config.get('fallback', True)
            
            payload = {
                "ad_type": ad_type,
                "provider": provider,
                "watched": True,
                "fallback": fallback
            }
            
            self.info = f"💰 CLAIMING {provider.upper()}"
            self.progress = "claiming..."
            
            resp = requests.post(
                f"{BASE_URL}/ads/complete",
                json=payload,
                headers=self.headers,
                timeout=30
            )
            
            self.ad_session_active = False
            
            log_api("/ads/complete", resp.status_code, resp.json() if resp.status_code == 200 else resp.text)
            
            if resp.status_code == 200:
                data = resp.json()
                
                reward = data.get('reward', 0)
                is_bonus = data.get('is_bonus', False)
                base_reward = data.get('base_reward', 0)
                bonus_reward = data.get('bonus_reward', 0)
                tot_reward = data.get('tot_reward', 0)
                new_balance = data.get('new_balance')
                tx_id = data.get('tx_id')
                mines_eligible = data.get('mines_eligible', False)
                is_tot_only = data.get('is_tot_only', False)
                
                ton_reward = reward if reward > 0 else (base_reward + bonus_reward)
                
                if new_balance:
                    self.balance = str(new_balance)
                if tot_reward:
                    self.tot = str(float(self.tot) + tot_reward if self.tot else tot_reward)
                
                self.total_ads += 1
                self.total_tot += tot_reward if tot_reward else 0
                self.total_ton += ton_reward if ton_reward else 0
                
                if provider in self.providers_status:
                    self.providers_status[provider]['remaining'] -= 1
                
                # Show reward
                reward_msg = f"✅ {provider}: 💰 +{ton_reward} TON | 💎 +{tot_reward} TOT"
                if is_bonus:
                    reward_msg += " | 🎉 BONUS!"
                if is_tot_only:
                    reward_msg += " | 📌 TOT-only"
                self.log(reward_msg)
                
                if mines_eligible and tx_id and tx_id != self.last_tx_id:
                    self.last_tx_id = tx_id
                    await self.play_mines(tx_id, provider)
                
                await self.check_and_spin_wheel()
                return data
            elif resp.status_code == 429:
                error = resp.json()
                detail = error.get('detail', '')
                match = re.search(r'(\d+)\s*s', detail)
                wait = int(match.group(1)) if match else 30
                self.info = "⏳ RATE_LIMIT"
                self.progress = f"{wait}s"
                self.log(f"⏳ Rate limited: {wait}s")
                return None
            else:
                self.info = "❌ FAILED"
                self.progress = str(resp.status_code)
                self.log(f"❌ Ad failed: {resp.status_code}")
                return None
                
        except Exception as e:
            self.ad_session_active = False
            self.log(f"❌ Ad error: {e}")
            return None

    async def play_mines(self, tx_id: str, provider: str, difficulty: int = 3):
        self.info = "🎮 MINES"
        self.progress = "playing..."
        self.log(f"🎮 Starting Mines game...")
        mines_headers = self.headers.copy()
        mines_headers['Referer'] = 'https://app.theopenearn.info/mines'
        
        try:
            start = requests.post(
                f"{BASE_URL}/mines/start",
                json={"ad_reward_tx_id": tx_id, "ad_provider": provider, "mines_count": difficulty},
                headers=mines_headers,
                timeout=15
            )
            
            if start.status_code != 200:
                self.log(f"❌ Mines start failed: {start.status_code}")
                return
            
            game_data = start.json()
            game_id = game_data.get('game_id')
            if not game_id:
                self.log("❌ No game_id")
                return
            
            used = []
            clicks = random.randint(2, 3)
            
            for i in range(clicks):
                tile = random.randint(0, 24)
                while tile in used:
                    tile = random.randint(0, 24)
                used.append(tile)
                
                click = requests.post(
                    f"{BASE_URL}/mines/{game_id}/click",
                    json={"cell_index": tile},
                    headers=mines_headers,
                    timeout=10
                )
                
                if click.status_code == 200:
                    result = click.json()
                    if result.get('status') in ['busted', 'hit_mine']:
                        self.progress = "💥 BUSTED"
                        self.log("💥 Hit a mine!")
                        return
                await asyncio.sleep(0.5)
            
            cash = requests.post(
                f"{BASE_URL}/mines/{game_id}/cashout",
                json={},
                headers=mines_headers,
                timeout=10
            )
            
            if cash.status_code == 200:
                cash_data = cash.json()
                new_bal = cash_data.get('new_balance')
                if new_bal:
                    self.balance = str(new_bal)
                reward = cash_data.get('reward', 0)
                if reward > 0:
                    self.log(f"🎉 Mines won: +{reward}")
                    self.progress = f"💰 +{reward}"
                
        except Exception as e:
            self.log(f"❌ Mines error: {e}")

    async def check_and_spin_wheel(self):
        try:
            stat = requests.get(f"{BASE_URL}/wheel/status", headers=self.headers, timeout=10)
            if stat.status_code != 200:
                return
            data = stat.json()
            free_spins = data.get('free_spins_available', 0)
            if free_spins > 0:
                self.info = "🎰 WHEEL"
                self.progress = "spinning..."
                self.log(f"🎰 Spinning wheel ({free_spins} free spins)")
                spin = requests.post(
                    f"{BASE_URL}/wheel/spin",
                    json={"is_paid": False},
                    headers=self.headers,
                    timeout=10
                )
                if spin.status_code == 200:
                    sd = spin.json()
                    self.balance = str(sd.get('new_balance', self.balance))
                    self.log("🎉 Wheel spin complete!")
                await asyncio.sleep(1)
        except Exception as e:
            pass

    async def watch_ad_cycle(self):
        self.info = "🔍 CHECKING ADS"
        self.progress = "fetching..."
        
        available, providers = await self.get_daily_ad_status()
        
        if not available:
            min_cooldown = None
            for name, info in providers.items():
                cd = info.get('cooldown', 0)
                if cd > 0:
                    if min_cooldown is None or cd < min_cooldown:
                        min_cooldown = cd
            
            if min_cooldown:
                self.info = "⏳ COOLDOWN"
                self.progress = f"{min_cooldown}s"
                return time.time() + min_cooldown
            else:
                self.info = "📭 NO ADS"
                self.progress = "waiting..."
                self.log("📭 No ads available")
                return time.time() + 60
        
        self.info = "📺 WATCHING ADS"
        success_count = 0
        
        for provider in available:
            self.log(f"▶️ Starting {provider} ad...")
            result = await self.complete_ad(provider)
            
            if result:
                success_count += 1
            else:
                if self.info == "⏳ RATE_LIMIT":
                    return time.time() + 60
        
        if success_count > 0:
            self.log(f"✅ Completed {success_count} ads!")
            
        self.info = "🟢 READY"
        self.progress = "waiting..."
        return time.time() + 5

    async def tapping_cycle(self):
        self.info = "👆 TAPPING"
        self.progress = "0/100"
        url = f"{BASE_URL}/earn"
        tap_headers = self.headers.copy()
        tap_headers['Referer'] = 'https://app.theopenearn.info/earn'
        tap_headers['Origin'] = 'https://app.theopenearn.info'
        total_taps = 0
        
        while self.running and total_taps < TOTAL_TAPS:
            remaining = TOTAL_TAPS - total_taps
            taps = min(TAPS_PER_REQUEST, remaining)
            payload = {"taps": taps}
            
            try:
                resp = requests.post(url, json=payload, headers=tap_headers, timeout=10)
                
                if resp.status_code == 200:
                    data = resp.json()
                    total_taps += taps
                    self.progress = f"{total_taps}/{TOTAL_TAPS}"
                    
                    if data.get('cycle_complete') == True or total_taps >= TOTAL_TAPS:
                        bal, tot = get_balance(self.headers)
                        if bal:
                            self.balance = bal
                            self.tot = tot
                        
                        cooldown_until = data.get('cooldown_until')
                        if cooldown_until:
                            cooldown_time = datetime.fromisoformat(cooldown_until.replace('Z', '+00:00'))
                            wait = max(0, (cooldown_time - datetime.now(timezone.utc)).total_seconds())
                            self.info = "⏳ TAP COOLDOWN"
                            self.progress = f"{int(wait)}s"
                            self.log(f"⏳ Tap cooldown: {int(wait)}s")
                            return time.time() + wait
                        else:
                            self.info = "🟢 READY"
                            self.progress = ""
                            return time.time() + 210
                    await asyncio.sleep(0.5)
                elif resp.status_code == 429:
                    error = resp.json()
                    detail = error.get('detail', '')
                    match = re.search(r'(\d+)\s*s', detail)
                    wait = int(match.group(1)) if match else 30
                    self.info = "⏳ RATE LIMIT"
                    self.progress = f"{wait}s"
                    self.log(f"⏳ Tap rate limit: {wait}s")
                    return time.time() + wait
                else:
                    await asyncio.sleep(5)
                    return time.time() + 60
            except Exception as e:
                await asyncio.sleep(5)
                return time.time() + 60
        
        self.info = "🟢 READY"
        self.progress = ""
        return time.time() + 60

    async def run(self):
        if not await self.fetch_initial_tg_data():
            self.info = "❌ LOGIN FAIL"
            return
        
        self.next_tap = time.time()
        self.next_ad = time.time()
        
        self.info = "🟢 READY"
        self.progress = "starting..."
        self.log("🚀 Started")
        
        while self.running:
            now = time.time()
            
            if self.ad_session_active:
                await asyncio.sleep(1)
                continue
            
            if now >= self.next_ad:
                self.next_ad = await self.watch_ad_cycle()
                if self.next_ad > now + 60:
                    self.next_tap = max(self.next_tap, now + 10)
            elif now >= self.next_tap:
                self.next_tap = await self.tapping_cycle()
            else:
                wait = min(self.next_tap - now, self.next_ad - now)
                if wait > 0:
                    if wait < 60:
                        for remaining in range(int(wait), 0, -1):
                            if not self.running:
                                break
                            self.progress = f"{remaining}s"
                            if remaining % 10 == 0:
                                self.info = "⏳ WAITING"
                            await asyncio.sleep(1)
                    else:
                        self.info = "⏳ WAITING"
                        self.progress = f"{int(wait)}s"
                        await asyncio.sleep(min(wait, 30))
            
            await asyncio.sleep(0.5)

    def stop(self):
        self.running = False

# ========== DASHBOARD ==========
def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def format_number(num: str) -> str:
    try:
        return f"{float(num):.8f}"
    except:
        return num

def format_cooldown(seconds: int) -> str:
    if seconds <= 0:
        return "READY"
    if seconds < 60:
        return f"{seconds}s"
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes}m {secs}s"

def dashboard(engines: List[AccountEngine]):
    """Live dashboard"""
    clear_screen()
    
    # Show banner
    print(banner())
    print()
    
    # Account stats
    print(f"{CYAN}╔══════════════════════════════════════════════════════════════════════════════════════╗{RESET}")
    print(f"{CYAN}║{RESET} {WHITE}{BOLD}{'ACCOUNT':<14} {'STATUS':<24} {'PROGRESS':<20} {'BALANCE':<16} {'TOT':<10} {'ADS':<6}{RESET} {CYAN}║{RESET}")
    print(f"{CYAN}╠══════════════════════════════════════════════════════════════════════════════════════╣{RESET}")
    
    for eng in engines:
        status = eng.update_status()
        
        info = status['info']
        info_display = info[:22] if len(info) > 22 else info
        
        # Progress display
        progress_display = status['progress']
        if status['ad_timer'] > 0:
            progress_display = f"⏱️ {status['ad_timer']}s"
        
        print(f"{CYAN}║{RESET} {GREEN}{BOLD}{status['username']:<14}{RESET} ", end="")
        print(f"{WHITE}{info_display:<24}{RESET} ", end="")
        print(f"{MAGENTA}{progress_display:<20}{RESET} ", end="")
        print(f"{YELLOW}{format_number(status['balance']):<16}{RESET} ", end="")
        print(f"{CYAN}{status['tot']:<10}{RESET} ", end="")
        print(f"{WHITE}{status['total_ads']:<6}{RESET} {CYAN}║{RESET}")
    
    # Provider status
    if engines and engines[0].providers_status:
        print(f"{CYAN}╠══════════════════════════════════════════════════════════════════════════════════════╣{RESET}")
        print(f"{CYAN}║{RESET} {WHITE}{BOLD}📊 AD PROVIDERS (cooldown updates in real-time){RESET} {CYAN}║{RESET}")
        print(f"{CYAN}╠══════════════════════════════════════════════════════════════════════════════════════╣{RESET}")
        
        print(f"{CYAN}║{RESET} {BLUE}{'Provider':<16}{RESET} ", end="")
        print(f"{BLUE}{'Remaining':<10}{RESET} ", end="")
        print(f"{BLUE}{'Used':<8}{RESET} ", end="")
        print(f"{BLUE}{'Cooldown':<16}{RESET} ", end="")
        print(f"{BLUE}{'Status':<12}{RESET} {CYAN}║{RESET}")
        
        sorted_providers = sorted(
            engines[0].providers_status.items(),
            key=lambda x: x[1].get('cooldown', 0),
            reverse=True
        )
        
        for name, info in sorted_providers:
            remaining = info.get('remaining', 0)
            used = info.get('used', 0)
            cooldown = info.get('cooldown', 0)
            blocked = info.get('blocked', False)
            
            if cooldown > 0:
                status_text = f"⏳ {format_cooldown(cooldown)}"
                status_color = YELLOW
            elif blocked:
                status_text = "🚫 BLOCKED"
                status_color = RED
            elif remaining > 0:
                status_text = "🟢 READY"
                status_color = GREEN
            else:
                status_text = "⚪ DONE"
                status_color = WHITE
            
            print(f"{CYAN}║{RESET} {WHITE}{name[:16]:<16}{RESET} ", end="")
            print(f"{GREEN}{remaining:<10}{RESET} ", end="")
            print(f"{YELLOW}{used:<8}{RESET} ", end="")
            print(f"{status_color}{status_text:<16}{RESET} ", end="")
            print(f"{status_color}{status_text:<12}{RESET} {CYAN}║{RESET}")
    
    # Live logs - Fixed: shows actual logs without auto-refresh issues
    print(f"{CYAN}╠══════════════════════════════════════════════════════════════════════════════════════╣{RESET}")
    print(f"{CYAN}║{RESET} {WHITE}{BOLD}📝 LIVE LOGS (last 8){RESET} {CYAN}║{RESET}")
    print(f"{CYAN}╠══════════════════════════════════════════════════════════════════════════════════════╣{RESET}")
    
    # Get current logs (safe copy)
    current_logs = LIVE_LOG.copy() if LIVE_LOG else ["Waiting for logs..."]
    
    for log in current_logs[-8:]:
        # Truncate if too long
        if len(log) > 75:
            log = log[:72] + "..."
        print(f"{CYAN}║{RESET} {WHITE}{log:<82}{RESET} {CYAN}║{RESET}")
    
    # Footer
    print(f"{CYAN}╚══════════════════════════════════════════════════════════════════════════════════════╝{RESET}")
    print(f"{YELLOW}💡 Press Ctrl+C to stop | Logs: {LOG_FILE} | Simulated: {AD_WATCH_DURATION}s{RESET}")

# ========== MAIN ==========
async def main():
    clear_screen()
    print(banner())
    print()
    print(f"{YELLOW}📝 Logs saved to: {LOG_FILE}{RESET}")
    print(f"{YELLOW}⏱️ Simulated ad watching: {AD_WATCH_DURATION}s{RESET}")
    print()
    
    accounts = await manage_accounts()
    if not accounts:
        print(f"{BOLD}{RED}❌ No accounts available. Exiting.{RESET}")
        sys.exit(1)
    
    print(f"\n{BOLD}{GREEN}✅ Loaded {len(accounts)} account(s){RESET}")
    print(f"{BOLD}{CYAN}Starting automation...{RESET}\n")
    await asyncio.sleep(2)
    
    engines = [AccountEngine(acc) for acc in accounts]
    tasks = [asyncio.create_task(eng.run()) for eng in engines]
    
    # Dashboard updater - fixed: only updates display, doesn't modify logs
    async def update_dashboard():
        while True:
            dashboard(engines)
            await asyncio.sleep(1)
    
    dash_task = asyncio.create_task(update_dashboard())
    
    try:
        await asyncio.gather(*tasks, dash_task)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Stopping all accounts...{RESET}")
        for eng in engines:
            eng.stop()
        await asyncio.sleep(2)
        print(f"{GREEN}All accounts stopped!{RESET}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n{RED}Fatal error: {e}{RESET}")
        sys.exit(1)
