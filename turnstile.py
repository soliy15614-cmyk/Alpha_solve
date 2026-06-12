import asyncio
import random
import aiohttp
from datetime import datetime

# ==================== CONFIGURATIONS ====================
MASTER_API_KEY = "9eac3a07ef1e3d5a484414138f945112"
TERTUYUL_API_KEY = "21ec69494f27ca9d673e2ba5ecfa3d12"
BYPASSALL_API_KEY = "jUPQAhwftyQV4CxUaUmDzwVHqBn4fqTs"

# Console Log Colors
C_GREEN = "\033[1;32m"
C_YELLOW = "\033[1;33m"
C_RED = "\033[1;31m"
C_RESET = "\033[0m"

# ==================== BACKUP API ROUTINES ====================

async def _solve_bypassall(session: aiohttp.ClientSession, url: str, sitekey: str) -> str or None:
    """Fallback solver using the bypassallshortlinks provider."""
    try:
        submit_url = f"https://bypassallshortlinks.space/in.php?key={BYPASSALL_API_KEY}&method=turnstile&pageurl={url}&sitekey={sitekey}"
        async with session.get(submit_url, timeout=20) as r:
            response = await r.text()
            
        if response.startswith("OK|"):
            task_id = response.split("|")[1]
            # Poll for the token result
            for _ in range(40):
                await asyncio.sleep(2)
                poll_url = f"https://bypassallshortlinks.space/res.php?id={task_id}&key={BYPASSALL_API_KEY}"
                async with session.get(poll_url, timeout=15) as pr:
                    poll_response = await pr.text()
                if poll_response.startswith("OK|"):
                    return poll_response.split("|")[1]
                elif "CAPCHA_NOT_READY" not in poll_response:
                    break
    except Exception:
        pass
    return None

async def _solve_tertuyul(session: aiohttp.ClientSession, url: str, sitekey: str) -> str or None:
    """Fallback solver using the tertuyul provider."""
    try:
        payload = {
            'key': TERTUYUL_API_KEY, 
            'method': 'turnstile', 
            'sitekey': sitekey, 
            'pageurl': url, 
            'json': '1'
        }
        async with session.post('http://api.tertuyul.my.id/in.php', data=payload, timeout=20) as r:
            task = await r.json()
            
        if 'request' in task and str(task['request']).isdigit():
            task_id = task['request']
            # Poll for the token result
            for _ in range(40):
                await asyncio.sleep(2)
                poll_url = f"http://api.tertuyul.my.id/res.php?key={TERTUYUL_API_KEY}&id={task_id}&action=get&json=1"
                async with session.get(poll_url, timeout=15) as pr:
                    result = await pr.json()
                if 'request' in result and str(result['request']).startswith("OK|"):
                    return result['request'].split("|")[1]
                elif 'request' in result and result['request'] != 'CAPCHA_NOT_READY':
                    break
    except Exception:
        pass
    return None

# ==================== MAIN RESOLVER MANAGER ====================

async def handle_turnstile_solve(url: str, sitekey: str) -> str or None:
    """
    Orchestrates the captcha resolution process. 
    Attempts the primary API engine before rotating through fallbacks.
    """
    print(f"{C_YELLOW}[CAPTCHA] Processing Turnstile request for: {url[:50]}...{C_RESET}")
    start_time = datetime.now()
    solved_token = None

    try:
        async with aiohttp.ClientSession() as session:
            # --- PHASE 1: Primary API Requests ---
            for attempt in range(1, 5):
                if (datetime.now() - start_time).seconds > 100:
                    break
                try:
                    async with session.post(
                        "https://api.xsolve.me/task",
                        headers={"X-Api-Key": MASTER_API_KEY},
                        json={"mode": "turnstile", "url": url, "sitekey": sitekey},
                        timeout=20
                    ) as r:
                        if r.status == 200:
                            res = await r.json()
                            solved_token = res.get('token')
                            if solved_token:
                                print(f"{C_GREEN}[CAPTCHA] Successfully resolved via Primary Engine.{C_RESET}")
                                return solved_token
                except Exception:
                    pass
                await asyncio.sleep(1.5)

            # --- PHASE 2: Fallback API Router ---
            if not solved_token and (datetime.now() - start_time).seconds < 100:
                fallbacks = [_solve_tertuyul, _solve_bypassall]
                random.shuffle(fallbacks) # Randomize redundancy paths
                
                for fallback_func in fallbacks:
                    if (datetime.now() - start_time).seconds > 100:
                        break
                    solved_token = await fallback_func(session, url, sitekey)
                    if solved_token:
                        print(f"{C_GREEN}[CAPTCHA] Successfully resolved via Backup Engine.{C_RESET}")
                        return solved_token
                        
    except Exception:
        pass

    # Safe fallback completion state
    print(f"{C_RED}[CAPTCHA] Resolution failed or exceeded safe time bounds.{C_RESET}")
    return None

