import asyncio
import re
import json
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# ==================== CONFIGURATIONS ====================
WARYONO_API_KEY = "868d78793d83aacd4009cec59dc96a44"
BYPASSALL_API_KEY = "jUPQAhwftyQV4CxUaUmDzwVHqBn4fqTs"

# Terminal Output Color Palettes
C_GREEN = "\033[1;32m"
C_YELLOW = "\033[1;33m"
C_RED = "\033[1;31m"
C_RESET = "\033[0m"

# Service Mapping Lists
WARYONO_SUPPORTED_LINKS = ["cuty", "exe", "tpi", "shrinkme.click", "shrink.me"]
BYPASSALL_LINKS = ["paycut", "sharecut", "justcut", "fastcut"]

# ==================== URL CLEANER ====================
def clean_url(url: str) -> str or None:
    """Removes markdown tags, asterisks, and emojis from the extracted URL."""
    if not url:
        return None
    url = url.replace('*', '').replace('\\', '')
    for emoji in ['✅', '✔️', '✔', '🔗', '🔓', '🎯', '👉', '🔑']:
        url = url.replace(emoji, '')
    url = url.strip()
    
    # Extract clean http/https URL structure
    url_match = re.search(r'(https?://[^\s*]+)', url)
    if url_match:
        url = url_match.group(1).strip()
        
    while url and url[-1] in '*,.;:!?|\\"\'`~@#$%^&()[]{}<>':
        url = url[:-1]
        
    return url if (url.startswith('http://') or url.startswith('https://')) else None

# ==================== HELPER IDENTIFIER ====================
def detect_link_type(url: str) -> str or None:
    """Detects shortlink service type from incoming URL patterns."""
    url_lower = url.lower().replace("https://", "").replace("http://", "").replace("www.", "")

    for link in BYPASSALL_LINKS:
        if link in url_lower:
            return link
            
    if "cuty.io" in url_lower or "cuty" in url_lower:
        return "cuty"
    if "exe.io" in url_lower or "exeygo" in url_lower or "exe" in url_lower:
        return "exe"
    if "tpi.li" in url_lower or "tpi" in url_lower:
        return "tpi"
    if "shrinkme.click" in url_lower:
        return "shrinkme.click"
    if "shrink.me" in url_lower:
        return "shrink.me"
    if "ez4short.com" in url_lower or "ez4short" in url_lower:
        return "ez4short"
    if "link.adlink.click" in url_lower or "adlink" in url_lower:
        return "adlink"
        
    return None

# ==================== METHOD 1: BYPASSALL API ====================
async def bypass_via_bypassall(url: str) -> str or None:
    """Bypasses Paycut, Sharecut, Justcut, and Fastcut via bypassallshortlinks API."""
    params = {'api_key': BYPASSALL_API_KEY, 'url': url}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://bypassallshortlinks.space/api.php", params=params, timeout=30) as r:
                response_text = await r.text()
                
                # Parsing JSON response and handling backslashes dynamically
                response = json.loads(response_text)
                if response.get('success') and response.get('bypassed_url'):
                    raw_url = response.get('bypassed_url')
                    return clean_url(raw_url)
    except Exception:
        pass
    return None

# ==================== METHOD 2: WARYONO SHORTLINK API ====================
async def bypass_via_waryono(url: str) -> str or None:
    """Bypasses shortlinks using the waryono API microservice engine."""
    submit_url = 'https://api.waryono.my.id/in.php'
    payload = {
        'apikey': WARYONO_API_KEY,
        'methods': 'shortlink',
        'url': url,
        'json': 1
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(submit_url, json=payload, timeout=20) as r:
                res = await r.json()
            
            if res.get('status') != 1:
                return None
                
            request_id = res.get('request')
            poll_url = f"https://api.waryono.my.id/res.php?apikey={WARYONO_API_KEY}&action=get&id={request_id}&json=1"
            
            for _ in range(30):
                await asyncio.sleep(5)
                async with session.get(poll_url, timeout=15) as pr:
                    poll_res = await pr.json()
                    
                if poll_res.get('status') == 1:
                    return poll_res.get('request')
                if poll_res.get('request') == 'ERROR_CAPTCHA_UNSOLVABLE':
                    break
    except Exception:
        pass
    return None

# ==================== METHOD 3: EZ4SHORT SCRAPER ====================
async def bypass_ez4short(url: str) -> str or None:
    """Asynchronous implementation of the ez4short crawler mechanism."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://game5s.com/"
    }
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, timeout=15) as r:
                if r.status != 200:
                    return None
                html = await r.text()
                current_url = str(r.url)

            soup = BeautifulSoup(html, "html.parser")
            form = soup.select_one("form#go-link")
            if not form:
                return None

            hidden_inputs = {}
            for input_tag in form.find_all("input"):
                name = input_tag.get("name")
                value = input_tag.get("value", "")
                if name:
                    hidden_inputs[name] = value

            action_path = form.get("action") or "/links/go"
            action_url = urljoin(current_url, action_path)

            await asyncio.sleep(3.2)

            post_headers = {
                "Origin": "https://ez4short.com",
                "Referer": current_url,
                "X-Requested-With": "XMLHttpRequest",
                "Accept": "application/json, text/javascript, */*; q=0.01",
            }

            async with session.post(action_url, data=hidden_inputs, headers=post_headers, timeout=15) as pr:
                payload = await pr.json()

            if payload.get("status") == "success" and payload.get("url"):
                return payload.get("url")
    except Exception:
        pass
    return None

# ==================== METHOD 4: ADLINK SCRAPER ====================
async def bypass_adlink(url: str) -> str or None:
    """Asynchronous layout processor for link.adlink.click domain trees."""
    mapped = url.replace("link.adlink.click", "blog.adlink.click")
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.diudemy.com/"
    }
    
    def parse_hidden(html, name):
        soup = BeautifulSoup(html, "html.parser")
        el = soup.find("input", {"name": name})
        return el["value"] if el else ""

    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(mapped, timeout=15) as r:
                html = await r.text()

            if 'name="ad_form_data"' not in html:
                return None

            post_data = {
                "_method": "POST",
                "_csrfToken": parse_hidden(html, "_csrfToken"),
                "ad_form_data": parse_hidden(html, "ad_form_data"),
                "_Token[fields]": parse_hidden(html, "_Token[fields]"),
                "_Token[unlocked]": parse_hidden(html, "_Token[unlocked]")
            }

            await asyncio.sleep(5)

            post_headers = {
                "User-Agent": "Mozilla/5.0",
                "Referer": mapped,
                "Accept": "application/json,text/javascript,*/*;q=0.01",
                "X-Requested-With": "XMLHttpRequest",
                "Content-Type": "application/x-www-form-urlencoded",
            }

            async with session.post("https://blog.adlink.click/links/go", data=post_data, headers=post_headers, timeout=15) as pr:
                json_data = await pr.json()

            final_url = json_data.get("url")
            if final_url and "limit.php" not in final_url:
                return final_url
    except Exception:
        pass
    return None

# ==================== CORE ROUTER MANAGER ====================
async def handle_shortlink_bypass(url: str) -> tuple:
    """
    Main orchestration router called by main.py.
    Returns: (bypassed_url_string or None, link_type_string)
    """
    link_type = detect_link_type(url)
    
    if not link_type:
        print(f"{C_RED}[BYPASS] Unsupported domain shape pattern checked.{C_RESET}")
        return None, None

    print(f"{C_YELLOW}[BYPASS] Routing dynamic channel for [{link_type}] link.{C_RESET}")
    result_url = None

    try:
        if link_type in BYPASSALL_LINKS:
            result_url = await bypass_via_bypassall(url)
        elif link_type in WARYONO_SUPPORTED_LINKS:
            result_url = await bypass_via_waryono(url)
        elif link_type == "ez4short":
            result_url = await bypass_ez4short(url)
        elif link_type == "adlink":
            result_url = await bypass_adlink(url)
    except Exception:
        pass 

    if result_url:
        print(f"{C_GREEN}[BYPASS] Successfully bypassed link type: {link_type}{C_RESET}")
        return result_url, link_type
        
    print(f"{C_RED}[BYPASS] Processing finished with a failure condition.{C_RESET}")
    return None, link_type

