import logging
import json
import os
import secrets
import string
import asyncio
import random
import aiohttp
from io import BytesIO
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telethon import TelegramClient

# ==================== CLEAN CONSOLE LOGGING SETUP ====================
logging.basicConfig(
    format="\033[1;30m[%Y-%m-%d %H:%M:%S]\033[0m %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telethon").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)

C_GREEN = "\033[1;32m"
C_YELLOW = "\033[1;33m"
C_CYAN = "\033[1;36m"
C_RED = "\033[1;31m"
C_RESET = "\03="
# ======================================================================

# Config
BOT_TOKEN = "8803491256:AAFi8pjk4EKrFRhhwHpik6lCzBdys1-xSqM"
ADMIN_ID = 8475230034
MASTER_API_KEY = "9eac3a07ef1e3d5a484414138f945112"
TOKEN_RATE = 10000  # 1 USD = 10,000 Tokens

# New Backup API Keys
TERTUYUL_API_KEY = "21ec69494f27ca9d673e2ba5ecfa3d12"
BYPASSALL_API_KEY = "jUPQAhwftyQV4CxUaUmDzwVHqBn4fqTs"

# Telethon Userbot Config
API_ID = 28752231
API_HASH = "ec1c1f2c30e2f1855c3edee7e348480b"

# Memory Variables
cached_data = {}
last_doc_msg_id = None
DB_FILE_NAME = "users.json"

# Telethon Client
client = TelegramClient("alpha_session", API_ID, API_HASH)

async def load_data_from_telegram_file():
    global cached_data, last_doc_msg_id
    try:
        async for message in client.iter_messages("me", limit=30):
            if message.document and message.document.attributes:
                for attr in message.document.attributes:
                    if hasattr(attr, 'file_name') and attr.file_name == DB_FILE_NAME:
                        file_bytes = await client.download_media(message, file=BytesIO())
                        file_bytes.seek(0)
                        cached_data = json.loads(file_bytes.read().decode('utf-8'))
                        last_doc_msg_id = message.id
                        print(f"{C_GREEN}[SYSTEM] Database successfully synchronized from Telegram Cloud!{C_RESET}")
                        return cached_data
    except Exception as e:
        print(f"{C_RED}[ERROR] Failed to fetch database from Telegram Cloud: {e}{C_RESET}")

    if os.path.exists(DB_FILE_NAME):
        try:
            with open(DB_FILE_NAME, "r") as f:
                cached_data = json.load(f)
                print(f"{C_YELLOW}[SYSTEM] Local backup database file loaded!{C_RESET}")
                return cached_data
        except:
            pass

    cached_data = {}
    return cached_data

async def save_data_to_telegram_file(data):
    global last_doc_msg_id, cached_data
    cached_data = data
    try:
        json_bytes = json.dumps(data, indent=4).encode('utf-8')
        file_to_upload = BytesIO(json_bytes)
        file_to_upload.name = DB_FILE_NAME

        if last_doc_msg_id:
            try:
                await client.delete_messages("me", last_doc_msg_id)
            except:
                pass

        new_msg = await client.send_file("me", file_to_upload, caption="📊 Alpha Solver Database File [Do Not Delete]")
        last_doc_msg_id = new_msg.id
        print(f"{C_CYAN}[CLOUD DB] Database file updated and uploaded safely.{C_RESET}")
    except Exception as e:
        print(f"{C_RED}[ERROR] Database cloud sync failed: {e}{C_RESET}")

# ==================== BACKUP API FUNCTIONS ====================

async def solve_bypassallshortlinks(session, url, sitekey):
    try:
        submit_url = f"https://bypassallshortlinks.space/in.php?key={BYPASSALL_API_KEY}&method=turnstile&pageurl={url}&sitekey={sitekey}"
        async with session.get(submit_url, timeout=30) as r:
            response = await r.text()

        if response.startswith("OK|"):
            task_id = response.split("|")[1]
            for _ in range(30):
                await asyncio.sleep(1)
                poll_url = f"https://bypassallshortlinks.space/res.php?id={task_id}&key={BYPASSALL_API_KEY}"
                async with session.get(poll_url, timeout=30) as pr:
                    poll_response = await pr.text()
                if poll_response.startswith("OK|"):
                    return poll_response.split("|")[1]
                elif "CAPCHA_NOT_READY" not in poll_response:
                    break
    except:
        pass
    return None

async def solve_tertuyul(session, url, sitekey):
    try:
        payload = {'key': TERTUYUL_API_KEY, 'method': 'turnstile', 'sitekey': sitekey, 'pageurl': url, 'json': '1'}
        async with session.post('http://api.tertuyul.my.id/in.php', data=payload, timeout=30) as r:
            task = await r.json()

        if 'request' in task and str(task['request']).isdigit():
            task_id = task['request']
            for _ in range(30):
                await asyncio.sleep(1)
                poll_url = f"http://api.tertuyul.my.id/res.php?key={TERTUYUL_API_KEY}&id={task_id}&action=get&json=1"
                async with session.get(poll_url, timeout=30) as pr:
                    result = await pr.json()
                if 'request' in result and str(result['request']).startswith("OK|"):
                    return result['request'].split("|")[1]
                elif 'request' in result and result['request'] != 'CAPCHA_NOT_READY':
                    break
    except:
        pass
    return None

# ==============================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    username = update.effective_user.username or "No Username"
    print(f"{C_GREEN}[COMMAND] User @{username} ({user_id}) triggered /start{C_RESET}")

    global cached_data
    if user_id not in cached_data:
        cached_data[user_id] = {
            "username": update.effective_user.username or "User",
            "balance": 0.01,
            "requests_sent": 0,
            "request_history": []
        }
        asyncio.create_task(save_data_to_telegram_file(cached_data))
    await send_main_menu(update, user_id)

async def send_main_menu(update: Update, user_id: str):
    global cached_data
    user = cached_data.get(user_id, {"balance": 0.0})
    tokens = int(user["balance"] * TOKEN_RATE)
    text = (f"👋 *Welcome to Alpha Solver Bot!*\n\n"
            f"💰 *Balance:* `{tokens} Tokens`\n"
            f"⚡ *Cost per Solve:* `0.7 - 1.0 Tokens`\n\n"
            "💡 *Use:* `/turnstile <URL> <SITEKEY>`")
    keyboard = [
        [InlineKeyboardButton("💰 Balance", callback_data="view_balance"), InlineKeyboardButton("📊 Status", callback_data="view_status")],
        [InlineKeyboardButton("💳 Deposit", callback_data="view_deposit")]
    ]
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# இந்த மெயின் பங்க்ஷன் தான் ஒரே நபர் அனுப்பும் பல ரிக்வெஸ்ட்களை தனித்தனி திரெட்களாக பிரித்து பேரலலாக இயக்கும்
async def turnstile_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    username = update.effective_user.username or "No Username"
    
    # 1. கன்கரண்ட் ஆர்குமெண்ட்ஸ் மேனேஜ்மென்ட் (மிக முக்கிய மாற்றம்)
    # ஒரே நேரத்தில் வரும் பல ரிக்வெஸ்ட்களின் URL மற்றும் Sitekey குழம்பாமல் இருக்க, லோக்கல் வேரியபிளாக பிரிக்கப்படுகிறது.
    local_args = list(context.args)
    if len(local_args) < 2:
        await update.message.reply_text("⚠️ *Format:* `/turnstile <URL> <SITEKEY>`", parse_mode="Markdown")
        return

    global cached_data
    if user_id not in cached_data:
        await update.message.reply_text("❌ *Please start the bot first using /start*", parse_mode="Markdown")
        return

    if cached_data[user_id]["balance"] < (1.0 / TOKEN_RATE):
        await update.message.reply_text("❌ *Insufficient Tokens! Minimum 1 Token required to solve.*", parse_mode="Markdown")
        return

    # 2. அசிங்க்ரோனஸ் டாஸ்க் உருவாக்கம் (Simultaneous Processing Execution)
    # இந்த குறிப்பிட்ட ரிக்வெஸ்ட்டை தனி ஒரு பேக்கிரவுண்ட் டாஸ்க்காக மாற்றி இயக்குகிறோம். 
    # இதன் மூலம் ஒரே நபர் அடுத்த வினாடியே இன்னொரு ரிக்வெஸ்ட் அனுப்பினாலும், பாட் அதை உடனடியாக ஏற்கும்.
    target_url = local_args[0]
    target_sitekey = local_args[1]
    
    asyncio.create_task(
        process_captcha_task(update, user_id, username, target_url, target_sitekey)
    )

# ஒவ்வொரு தனித்தனி ரிக்வெஸ்ட்டையும் பேரலலாக பிராசஸ் செய்யும் பிரத்யேக பங்க்ஷன்
async def process_captcha_task(update, user_id, username, url, sitekey):
    global cached_data
    
    # ஒவ்வொரு தனி ரிக்வெஸ்ட்டுக்கும் தனித்துவமான "Processing" மெசேஜ் ஐடி உருவாக்கப்படுகிறது. 
    # இதனால் ஒரு ரிக்வெஸ்ட்டின் மெசேஜ் மற்றொன்றை பாதிக்காது.
    print(f"{C_YELLOW}[TASK-START] Parallel execution started for @{username} | Sitekey: {sitekey[:10]}...{C_RESET}")
    msg = await update.message.reply_text(f"🔄 *Processing Captcha...*\n🔑 Sitekey: `{sitekey[:10]}...`", parse_mode="Markdown")
    
    solved_token = None
    used_backup = False

    async with aiohttp.ClientSession() as session:
        # Xsolve API மூலம் 4 முறை முயற்சி செய்தல்
        for attempt in range(1, 5):
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
                            break
            except:
                pass
            await asyncio.sleep(0.5)

        # Failover: ரேண்டம் சிங்கிள் பேக்கப் சிஸ்டம்
        if not solved_token:
            backup_apis = [solve_tertuyul, solve_bypassallshortlinks]
            first_choice = random.choice(backup_apis)
            second_choice = backup_apis[1] if first_choice == backup_apis[0] else backup_apis[0]

            solved_token = await first_choice(session, url, sitekey)
            if solved_token:
                used_backup = True
            else:
                solved_token = await second_choice(session, url, sitekey)
                if solved_token:
                    used_backup = True

    # கட்டணம் மற்றும் முடிவு அப்டேட்
    if solved_token:
        if used_backup:
            cost_tokens = 1.0  
        else:
            cost_tokens = round(random.uniform(0.7, 1.0), 2)  

        cost_usd = cost_tokens / TOKEN_RATE
        
        # மெமரி அப்டேட்
        cached_data[user_id]["balance"] -= cost_usd
        cached_data[user_id]["requests_sent"] += 1
        cached_data[user_id]["request_history"].append(datetime.now().isoformat())

        # கிளவுட் ஸ்டோரேஜ் சேவிங் டாஸ்க் (பின்னணியில் நடக்கும்)
        asyncio.create_task(save_data_to_telegram_file(cached_data))
        
        # இந்த குறிப்பிட்ட டாஸ்க்கிற்கான மெசேஜ் மட்டும் அப்டேட் ஆகும்
        await msg.edit_text(f"✅ *Solved!*\n🔑 Token: `{solved_token}`\n📉 *Cost:* `{cost_tokens} Tokens`", parse_mode="Markdown")
        print(f"{C_GREEN}[TASK-SUCCESS] Completed for @{username} | Sitekey: {sitekey[:10]}...{C_RESET}")
    else:
        await msg.edit_text(f"❌ `CAPTCHA_UNSOLVABLE`\n🔑 Sitekey: `{sitekey[:10]}...`")
        print(f"{C_RED}[TASK-FAILED] Completely failed for @{username} | Sitekey: {sitekey[:10]}...{C_RESET}")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    username = query.from_user.username or "No Username"
    global cached_data
    user = cached_data.get(user_id, {})

    if query.data == "view_balance":
        await query.edit_message_text(f"💰 *Balance:* `{int(user.get('balance', 0) * TOKEN_RATE)} Tokens`", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="back")]]))
    elif query.data == "view_status":
        hist = user.get("request_history", [])
        now = datetime.now()
        today = len([t for t in hist if datetime.fromisoformat(t).date() == now.date()])
        msg = f"📊 *Usage Status*\n\n📅 Today: `{today}`\n📈 Total: `{user.get('requests_sent', 0)}`"
        await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="back")]]))
    elif query.data == "view_deposit":
        msg = f"💳 *Deposit Details*\n\nMinimum: $0.10\nAdmin: @alphapython12\nID: `{user_id}`"
        await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="back")]]))
    elif query.data == "back":
        await send_main_menu(update, user_id)

async def set_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    try:
        t_user, amt_to_add = context.args[0], float(context.args[1])
        global cached_data

        if t_user not in cached_data:
            cached_data[t_user] = {"username": "User", "balance": 0.0, "requests_sent": 0, "request_history": []}

        old_balance = cached_data[t_user].get("balance", 0.0)
        new_balance = old_balance + amt_to_add
        cached_data[t_user]["balance"] = round(new_balance, 4)

        asyncio.create_task(save_data_to_telegram_file(cached_data))

        total_tokens = int(cached_data[t_user]["balance"] * TOKEN_RATE)
        added_tokens = int(amt_to_add * TOKEN_RATE)

        print(f"{C_GREEN}[ADMIN ACTION] Added {added_tokens} tokens to User: {t_user}. New Total: {total_tokens}{C_RESET}")
        await update.message.reply_text(f"✅ Added {added_tokens} Tokens to {t_user}.\n📊 New Total: {total_tokens} Tokens.")

        try:
            await context.bot.send_message(int(t_user), f"💰 Your balance has been topped up with {added_tokens} Tokens!\n📈 Total Balance: {total_tokens} Tokens.")
        except:
            pass
    except Exception as e:
        logger.error(f"Error in setbalance: {e}")
        await update.message.reply_text("⚠️ *Usage:* `/setbalance [ID] [AMOUNT]`")

async def main():
    os.system('clear' if os.name == 'posix' else 'cls') 
    print(f"{C_CYAN}===================================================={C_RESET}")
    print(f"{C_GREEN}          ⚡ ALPHA CAPTCHA SOLVER SYSTEM ⚡          {C_RESET}")
    print(f"{C_CYAN}===================================================={C_RESET}")
    print(f"[SYSTEM] Establishing secure connection to Telegram Userbot...")

    await client.connect()

    if not await client.is_user_authorized():
        phone = input("Please enter your phone (e.g. +94...): ")
        await client.send_code_request(phone)
        code = input("Please enter the code you received: ")
        await client.sign_in(phone, code)

    print(f"[SYSTEM] Synchronizing latest cloud state storage...")
    await load_data_from_telegram_file()

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("turnstile", turnstile_handler))
    app.add_handler(CommandHandler("setbalance", set_balance))
    app.add_handler(CallbackQueryHandler(button_handler))

    print(f"{C_GREEN}[READY] Server dashboard listening for active tasks...{C_RESET}\n")

    async with app:
        await app.initialize()
        await app.start()
        await app.updater.start_polling()
        while True:
            await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())

