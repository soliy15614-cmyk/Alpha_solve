import logging
import asyncio
import os
import json
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import secrets

# Importing backend routing managers from your sub-scripts
from bypass import handle_shortlink_bypass
from turnstile import handle_turnstile_solve
from aruble import process_aruble_captcha  # New Aruble engine import

# ==================== CLEAN CONSOLE LOGGING SETUP ====================
logging.basicConfig(
    format="\033[1;30m[%Y-%m-%d %H:%M:%S]\033[0m %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)

C_GREEN = "\033[1;32m"
C_YELLOW = "\033[1;33m"
C_CYAN = "\033[1;36m"
C_RED = "\033[1;31m"
C_RESET = "\033[0m"

# ==================== CONFIGURATIONS ====================
BOT_TOKEN = "8803491256:AAFi8pjk4EKrFRhhwHpik6lCzBdys1-xSqM"
DATA_FILE = "users.json"
ADMIN_ID = 8475230034  # Dedicated Admin Telegram ID

# Global volatile memory state pointer mapping live Cloud Storage Files
CURRENT_TG_FILE_ID = None

# Async Lock to completely prevent Race Conditions during database I/O operations
db_lock = asyncio.Lock()

# Pricing Definitions
BYPASS_TOKENS = 3
TURNSTILE_TOKENS = 1
ARUBLE_TOKENS = 0.5  # Fixed at 0.5 tokens

TOKEN_CONVERSION = 10000  # $1.00 = 10,000 Tokens

BYPASS_USD_COST = BYPASS_TOKENS / TOKEN_CONVERSION
TURNSTILE_USD_COST = TURNSTILE_TOKENS / TOKEN_CONVERSION
ARUBLE_USD_COST = ARUBLE_TOKENS / TOKEN_CONVERSION
NEW_USER_BONUS_USD = 50 / TOKEN_CONVERSION

SHORTLINK_PRICES = ["cuty", "fastcut", "paycut", "sharecut", "justcut", "adlink", "tpi", "shrink.me", "exe", "ez4short", "shrinkme.click"]

# ==================== PURE TELEGRAM CLOUD DATABASE LOGIC ====================

async def find_last_database_file(app: Application) -> str:
    """
    Scans the Admin's chat history on startup to automatically locate 
    the absolute latest 'users.json' file sent by the bot or admin.
    """
    global CURRENT_TG_FILE_ID
    print(f"{C_YELLOW}[STARTUP] Scanning admin timeline for latest database state...{C_RESET}")
    try:
        # Fetch latest messages from Admin Chat
        async for message in app.bot.get_chat_history(chat_id=ADMIN_ID, limit=50):
            if message.document and message.document.file_name == "users.json":
                CURRENT_TG_FILE_ID = message.document.file_id
                print(f"{C_GREEN}[STARTUP] Successfully locked onto cloud database file_id: {CURRENT_TG_FILE_ID}{C_RESET}")
                return CURRENT_TG_FILE_ID
    except Exception as e:
        print(f"{C_RED}[STARTUP ERROR] Could not scan chat history: {e}{C_RESET}")
    return None

async def fetch_live_db(context: ContextTypes.DEFAULT_TYPE) -> dict:
    """Downloads the absolute latest JSON database file structure directly from Telegram Cloud safely."""
    global CURRENT_TG_FILE_ID
    
    if CURRENT_TG_FILE_ID:
        try:
            tg_file = await context.bot.get_file(CURRENT_TG_FILE_ID)
            await tg_file.download_to_drive(custom_path=DATA_FILE)
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"{C_RED}[CLOUD ERROR] Remote file tracking failed. Trying local file fallback: {e}{C_RESET}")

    # Fallback to local file if cloud link fails or is empty on memory
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

async def commit_and_push_db(data: dict, context: ContextTypes.DEFAULT_TYPE):
    """Saves records locally safely and pushes them cleanly onto Admin's Cloud Storage without deleting local copy."""
    global CURRENT_TG_FILE_ID
    try:
        # Write locally first
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)
        
        # Dispatch to Admin's Cloud Timeline
        with open(DATA_FILE, "rb") as document:
            msg = await context.bot.send_document(
                chat_id=ADMIN_ID,
                document=document,
                caption=f"📂 *Cloud Database Sync Live*\n⏱️ `{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC`"
            )
            CURRENT_TG_FILE_ID = msg.document.file_id
            
        # NOTE: Removed os.remove(DATA_FILE) to prevent empty database initialization on local crash
            
    except Exception as e:
        print(f"{C_RED}[CLOUD ERROR] Failed syncing state matrix onto Telegram Core: {e}{C_RESET}")

async def cloud_get_or_create_user(user_id: str, username: str, context: ContextTypes.DEFAULT_TYPE) -> dict:
    """Manages active user profile maps within the pure Cloud Memory Stream Loop with strict safe-locks."""
    async with db_lock:  # Enforces sequential operations to avoid overwrites
        db = await fetch_live_db(context)
        modified = False
        
        if user_id not in db:
            db[user_id] = {
                "username": username or f"user_{user_id}",
                "balance": NEW_USER_BONUS_USD,
                "api_key": secrets.token_urlsafe(24),
                "requests_sent": 0,
                "request_history": []
            }
            modified = True
            print(f"{C_GREEN}[CLOUD DB] Onboarded new consumer account {user_id} straight to Telegram Cloud.{C_RESET}")
        else:
            if username and db[user_id].get("username") != username:
                db[user_id]["username"] = username
                modified = True
                
        if modified:
            await commit_and_push_db(db, context)
            
        return db[user_id]

# ==================== AUTOMATIC MESSAGE PURGE ====================
async def schedule_delete_messages(context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_ids: list, delay: int = 60):
    """Quietly deletes temporary execution footprint logs after exactly 1 minute (60 seconds)."""
    await asyncio.sleep(delay)
    for msg_id in message_ids:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=msg_id)
        except Exception:
            pass 

# ==================== MASTER ADMIN CONTROLS ====================

async def receive_telegram_json_backup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Triggered ONLY when Admin drops a manual users.json file into the chat for emergency recoveries."""
    global CURRENT_TG_FILE_ID
    sender_id = update.effective_user.id
    if sender_id != ADMIN_ID:
        return

    document = update.message.document
    if document.file_name == "users.json":
        status_msg = await update.message.reply_text("📥 *Emergency Manual Database Detected! Intercepting cloud reference...*", parse_mode="Markdown")
        
        async with db_lock:  # Secure the ecosystem during critical manual rewrite
            try:
                CURRENT_TG_FILE_ID = document.file_id
                db_test = await fetch_live_db(context)
                
                # Force commit to lock the newly inserted records natively
                await commit_and_push_db(db_test, context)
                
                await status_msg.edit_text(f"✅ *Emergency Data Restored!* Loaded `{len(db_test)}` profiles from your uploaded file successfully.", parse_mode="Markdown")
            except Exception as e:
                await status_msg.edit_text(f"❌ *Manual Overwrite Failed:* `{str(e)}`", parse_mode="Markdown")

async def manual_backup_cmd_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender_id = update.effective_user.id
    if sender_id != ADMIN_ID:
        return

    status_msg = await update.message.reply_text("⏳ *Reading live stream state...*", parse_mode="Markdown")
    async with db_lock:
        try:
            db = await fetch_live_db(context)
            await commit_and_push_db(db, context)
            await status_msg.edit_text("✅ *Manual Backup Executed! Fresh state saved to your chat timeline.*", parse_mode="Markdown")
        except Exception as e:
            await status_msg.edit_text(f"❌ *Backup Interrupted:* `{str(e)}`", parse_mode="Markdown")

async def set_balance_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Adds USD value converted to tokens to the user's existing balance safely."""
    sender_id = update.effective_user.id
    chat_id = update.effective_chat.id
    user_msg_id = update.message.message_id

    if sender_id != ADMIN_ID:
        msg = await update.message.reply_text("❌ *Unauthorized Access!*", parse_mode="Markdown")
        asyncio.create_task(schedule_delete_messages(context, chat_id, [user_msg_id, msg.message_id]))
        return

    args = context.args
    if len(args) < 2:
        msg = await update.message.reply_text("⚠️ Usage: `/set <userid> <usdvalue>`", parse_mode="Markdown")
        asyncio.create_task(schedule_delete_messages(context, chat_id, [user_msg_id, msg.message_id]))
        return

    target_user_id = args[0]
    try:
        added_usd_val = float(args[1])
    except ValueError:
        msg = await update.message.reply_text("❌ *Invalid Metric Value!*", parse_mode="Markdown")
        asyncio.create_task(schedule_delete_messages(context, chat_id, [user_msg_id, msg.message_id]))
        return

    async with db_lock:
        db = await fetch_live_db(context)
        
        if target_user_id not in db:
            db[target_user_id] = {
                "username": f"user_{target_user_id}",
                "balance": 0.0,
                "api_key": secrets.token_urlsafe(24),
                "requests_sent": 0,
                "request_history": []
            }

        current_balance = db[target_user_id].get("balance", 0.0)
        new_usd_val = current_balance + added_usd_val
        db[target_user_id]["balance"] = new_usd_val
        
        await commit_and_push_db(db, context)

    added_tokens = round(added_usd_val * TOKEN_CONVERSION, 2)
    total_tokens = round(new_usd_val * TOKEN_CONVERSION, 2)
    
    await update.message.reply_text(
        f"✅ *Success!* \n\n"
        f"👤 Account: `{target_user_id}`\n"
        f"➕ Added: `+{added_tokens} Tokens`\n"
        f"💰 Total Current Balance: `*{total_tokens} Tokens*`",
        parse_mode="Markdown"
    )

    try:
        await context.bot.send_message(
            chat_id=int(target_user_id),
            text=(
                f"💳 *Deposit Confirmed!*\n\n"
                f"💰 Admin credited your account with: `{added_tokens} Tokens`\n"
                f"📊 Total Wallet Balance: `{total_tokens} Tokens` (${new_usd_val:.4f} USD)"
            ),
            parse_mode="Markdown"
        )
    except Exception:
        pass

# ==================== BOT SYSTEM COMMANDS ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    username = update.effective_user.username
    print(f"{C_GREEN}[CMD] @{username or user_id} executed /start{C_RESET}")
    
    await cloud_get_or_create_user(user_id, username, context)
    
    text = (
        "💡 *Alpha Solver Bot*\n\n"
        "Welcome to the high-speed link bypass & captcha solving engine.\n\n"
        "⚡ *Available Commands:*\n"
        "• `/status` or `/balance` - View your account balance and stats\n"
        "• `/price` - Check service pricing\n"
        "• `/deposits` - How to add funds to your wallet\n\n"
        "🤖 *Solvers:*\n"
        "• `/turnstile <URL> <SITEKEY>`\n"
        "• `/aruble <BASE64_PAYLOAD>`\n"
        "• `/bypass <URL>`"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def status_and_balance_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    username = update.effective_user.username
    
    user_data = await cloud_get_or_create_user(user_id, username, context)
    usd_balance = user_data.get("balance", 0.0)
    token_balance = round(usd_balance * TOKEN_CONVERSION, 2)
    req_sent = user_data.get("requests_sent", 0)
    history = user_data.get("request_history", [])
    
    last_used = "Never"
    if history:
        try:
            dt = datetime.fromisoformat(history[-1])
            last_used = dt.strftime("%Y-%m-%d %H:%M:%S UTC")
        except Exception:
            last_used = str(history[-1])

    text = (
        "📊 *Your System Profile & Status*\n\n"
        f"👤 *Username:* @{user_data.get('username')}\n"
        f"🆔 *Account ID:* `{user_id}`\n"
        f"💰 *Your Balance:* `{token_balance} Tokens` (${usd_balance:.6f})\n"
        f"🔑 *API Key:* `{user_data.get('api_key')}`\n"
        f"📈 *Total Requests Processed:* `{req_sent}`\n"
        f"🕒 *Last Activity Logged:* `{last_used}`\n\n"
        "✅ *Core Operations:* `Operational`\n"
        "🤖 *Engine Mode:* `True Cloud Native Sync + SafeLock`"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def price_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rates = "\n".join([f"`{name}` → `{BYPASS_TOKENS} Tokens`" for name in SHORTLINK_PRICES])
    text = (
        f"🏷️ *Service Price List*\n\n"
        f"🔑 *Turnstile Captcha:* `{TURNSTILE_TOKENS} Token`\n"
        f"🧩 *Aruble Captcha:* `{ARUBLE_TOKENS} Token`\n\n"
        f"🔗 *Shortlink Bypass (All Links Fixed Rate):*\n{rates}"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def deposits_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    text = (
        "💳 *Token Funding Wallet System*\n\n"
        "• Payment Option: FaucetPay USDC Only\n"
        "• Conversion Ratio: $1.00 = 10,000 Tokens\n\n"
        "📌 *Refill Procedure:*\n"
        "1. Complete transaction via FaucetPay (USDC).\n"
        "2. Direct-message Admin: @alphapython12\n\n"
        f"🆔 *Your Account ID:* `{user_id}`"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

# ==================== CAPTCHA RESOLUTION INTERFACES ====================

async def turnstile_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_msg_id = update.message.message_id
    user_id = str(update.effective_user.id)
    username = update.effective_user.username
    args = context.args

    if len(args) < 2:
        msg = await update.message.reply_text("⚠️ Usage: `/turnstile <URL> <SITEKEY>`", parse_mode="Markdown")
        asyncio.create_task(schedule_delete_messages(context, chat_id, [user_msg_id, msg.message_id], delay=60))
        return

    user_data = await cloud_get_or_create_user(user_id, username, context)
    if user_data.get("balance", 0.0) < TURNSTILE_USD_COST:
        msg = await update.message.reply_text("❌ *Insufficient Balance!* Please refill your wallet.", parse_mode="Markdown")
        asyncio.create_task(schedule_delete_messages(context, chat_id, [user_msg_id, msg.message_id], delay=60))
        return

    target_url = args[0]
    sitekey = args[1]
    status_msg = await update.message.reply_text("🔄 *Processing Captcha Request...*", parse_mode="Markdown")
    
    solved_token = await handle_turnstile_solve(target_url, sitekey)

    if solved_token:
        async with db_lock:
            db = await fetch_live_db(context)
            db[user_id]["balance"] = max(0.0, db[user_id]["balance"] - TURNSTILE_USD_COST)
            db[user_id]["requests_sent"] += 1
            db[user_id]["request_history"].append(datetime.utcnow().isoformat())
            await commit_and_push_db(db, context)

        await status_msg.edit_text(f"✅ *Solved!*\n\n🔑 `{solved_token}`\n📉 `{TURNSTILE_TOKENS} Token Used`", parse_mode="Markdown")
    else:
        await status_msg.edit_text("❌ *Turnstile Solver Operations Failed!*", parse_mode="Markdown")

    asyncio.create_task(schedule_delete_messages(context, chat_id, [user_msg_id, status_msg.message_id], delay=60))

async def aruble_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_msg_id = update.message.message_id
    user_id = str(update.effective_user.id)
    username = update.effective_user.username
    args = context.args

    if len(args) < 1:
        msg = await update.message.reply_text("⚠️ Usage: `/aruble <BASE64_PAYLOAD>`", parse_mode="Markdown")
        asyncio.create_task(schedule_delete_messages(context, chat_id, [user_msg_id, msg.message_id], delay=60))
        return

    user_data = await cloud_get_or_create_user(user_id, username, context)
    if user_data.get("balance", 0.0) < ARUBLE_USD_COST:
        msg = await update.message.reply_text("❌ *Insufficient Balance!* Please refill your wallet.", parse_mode="Markdown")
        asyncio.create_task(schedule_delete_messages(context, chat_id, [user_msg_id, msg.message_id], delay=60))
        return

    base64_payload = args[0]
    status_msg = await update.message.reply_text("🔄 *Processing Aruble Captcha Request...*", parse_mode="Markdown")
    
    solved_token = await process_aruble_captcha(base64_payload)

    if solved_token and "error" not in solved_token:
        async with db_lock:
            db = await fetch_live_db(context)
            db[user_id]["balance"] = max(0.0, db[user_id]["balance"] - ARUBLE_USD_COST)
            db[user_id]["requests_sent"] += 1
            db[user_id]["request_history"].append(datetime.utcnow().isoformat())
            await commit_and_push_db(db, context)

        await status_msg.edit_text(f"✅ *Aruble Captcha Solved!*\n\n🔑 `{solved_token}`\n📉 `{ARUBLE_TOKENS} Token Used`", parse_mode="Markdown")
    else:
        await status_msg.edit_text("❌ *Aruble Solver Operations Failed! Check payload.*", parse_mode="Markdown")

    asyncio.create_task(schedule_delete_messages(context, chat_id, [user_msg_id, status_msg.message_id], delay=60))

# ==================== SHORTLINK BYPASS INTERFACE ====================

async def bypass_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_msg_id = update.message.message_id
    user_id = str(update.effective_user.id)
    username = update.effective_user.username
    args = context.args

    if len(args) < 1:
        msg = await update.message.reply_text("⚠️ Usage: `/bypass <URL>`", parse_mode="Markdown")
        asyncio.create_task(schedule_delete_messages(context, chat_id, [user_msg_id, msg.message_id], delay=60))
        return

    user_data = await cloud_get_or_create_user(user_id, username, context)
    if user_data.get("balance", 0.0) < BYPASS_USD_COST:
        msg = await update.message.reply_text("❌ *Insufficient Balance!* Please refill your wallet.", parse_mode="Markdown")
        asyncio.create_task(schedule_delete_messages(context, chat_id, [user_msg_id, msg.message_id], delay=60))
        return

    target_url = args[0]
    status_msg = await update.message.reply_text("🔄 *Processing URL Bypass Routine...*", parse_mode="Markdown")

    bypassed_url, link_type = await handle_shortlink_bypass(target_url)

    if bypassed_url:
        async with db_lock:
            db = await fetch_live_db(context)
            db[user_id]["balance"] = max(0.0, db[user_id]["balance"] - BYPASS_USD_COST)
            db[user_id]["requests_sent"] += 1
            db[user_id]["request_history"].append(datetime.utcnow().isoformat())
            await commit_and_push_db(db, context)

        await status_msg.edit_text(
            f"✅ *Bypassed!*\n\n🔗 *Service:* `{link_type}`\n🎯 *Destination:* `{bypassed_url}`\n📉 *Charged:* `{BYPASS_TOKENS} Tokens`",
            parse_mode="Markdown"
        )
    else:
        await status_msg.edit_text("❌ *Shortlink Bypass Engine Interrupted!*", parse_mode="Markdown")

    asyncio.create_task(schedule_delete_messages(context, chat_id, [user_msg_id, status_msg.message_id], delay=60))

# ==================== PROGRAM ENTRY POINT ====================

def main():
    print(f"{C_CYAN}{'═' * 50}{C_RESET}")
    print(f"{C_GREEN}   ⚡ ALPHA PURE TELEGRAM CLOUD ENGINE ONLINE ⚡{C_RESET}")
    print(f"{C_CYAN}{'═' * 50}{C_RESET}")

    app = Application.builder().token(BOT_TOKEN).build()
    
    # Run Startup History Scan Task before Polling Starts to find the latest file
    loop = asyncio.get_event_loop()
    loop.run_until_complete(find_last_database_file(app))

    # Non-blocking concurrent handlers
    app.add_handler(CommandHandler("start", start, block=False))
    app.add_handler(CommandHandler("status", status_and_balance_handler, block=False))
    app.add_handler(CommandHandler("balance", status_and_balance_handler, block=False))
    app.add_handler(CommandHandler("price", price_handler, block=False))
    app.add_handler(CommandHandler("deposits", deposits_handler, block=False))
    
    # Solver Handlers
    app.add_handler(CommandHandler("turnstile", turnstile_handler, block=False))
    app.add_handler(CommandHandler("aruble", aruble_handler, block=False))
    app.add_handler(CommandHandler("bypass", bypass_handler, block=False))
    
    # Secure Admin Handlers
    app.add_handler(CommandHandler("set", set_balance_handler, block=False))
    app.add_handler(CommandHandler("backup", manual_backup_cmd_handler, block=False))
    
    # System Document Streams (Strict filter for document from Admin only)
    app.add_handler(MessageHandler(filters.Document.FileExtension("json"), receive_telegram_json_backup, block=False))

    print(f"{C_GREEN}[READY] Polling active in 100% Cloud native database loop configuration...{C_RESET}\n")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()

