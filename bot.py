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

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Config
BOT_TOKEN = "8803491256:AAFi8pjk4EKrFRhhwHpik6lCzBdys1-xSqM"
ADMIN_ID = 8475230034
MASTER_API_KEY = "9eac3a07ef1e3d5a484414138f945112"
TOKEN_RATE = 10000  # 1 USD = 10,000 Tokens

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
    """Fetches the latest users.json file from Saved Messages and loads it into memory"""
    global cached_data, last_doc_msg_id
    try:
        async for message in client.iter_messages("me", limit=30):
            if message.document and message.document.attributes:
                for attr in message.document.attributes:
                    if hasattr(attr, 'file_name') and attr.file_name == DB_FILE_NAME:
                        # Download directly into memory (BytesIO) to protect storage
                        file_bytes = await client.download_media(message, file=BytesIO())
                        file_bytes.seek(0)
                        cached_data = json.loads(file_bytes.read().decode('utf-8'))
                        last_doc_msg_id = message.id
                        logger.info("📁 Database loaded successfully from Telegram Cloud!")
                        return cached_data
    except Exception as e:
        logger.error(f"Error downloading DB file from Telegram: {e}")
    
    # Fallback to local file if cloud file is not found on first run
    if os.path.exists(DB_FILE_NAME):
        try:
            with open(DB_FILE_NAME, "r") as f:
                cached_data = json.load(f)
                logger.info("📂 Local backup database file loaded successfully!")
                return cached_data
        except:
            pass

    cached_data = {}
    return cached_data

async def save_data_to_telegram_file(data):
    """Saves changes into a new users.json file and uploads it to Saved Messages, deleting the old one"""
    global last_doc_msg_id, cached_data
    cached_data = data
    
    try:
        # Convert JSON data to an in-memory file object
        json_bytes = json.dumps(data, indent=4).encode('utf-8')
        file_to_upload = BytesIO(json_bytes)
        file_to_upload.name = DB_FILE_NAME
        
        # Delete the previous database message to keep the chat clean
        if last_doc_msg_id:
            try:
                await client.delete_messages("me", last_doc_msg_id)
            except:
                pass
        
        # Upload the updated file
        new_msg = await client.send_file("me", file_to_upload, caption="📊 Alpha Solver Database File [Do Not Delete]")
        last_doc_msg_id = new_msg.id
        logger.info("💾 Database file updated successfully in Telegram Cloud!")
    except Exception as e:
        logger.error(f"Error uploading DB file to Telegram: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    data = cached_data
    if user_id not in data:
        data[user_id] = {
            "username": update.effective_user.username or "User",
            "balance": 0.01,
            "requests_sent": 0,
            "request_history": []
        }
        await save_data_to_telegram_file(data)
    await send_main_menu(update, user_id)

async def send_main_menu(update: Update, user_id: str):
    data = cached_data
    user = data.get(user_id, {"balance": 0.0})
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

async def turnstile_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("⚠️ *Format:* `/turnstile <URL> <SITEKEY>`", parse_mode="Markdown")
        return

    data = cached_data
    if user_id not in data:
        await update.message.reply_text("❌ *Please start the bot first using /start*", parse_mode="Markdown")
        return

    cost_tokens = round(random.uniform(0.7, 1.0), 2)
    cost_usd = cost_tokens / TOKEN_RATE

    if data[user_id]["balance"] < cost_usd:
        await update.message.reply_text("❌ *Insufficient Tokens!*", parse_mode="Markdown")
        return

    msg = await update.message.reply_text("🔄 *Processing...*", parse_mode="Markdown")

    async with aiohttp.ClientSession() as session:
        for _ in range(10):
            try:
                async with session.post(
                    "https://api.xsolve.me/task",
                    headers={"X-Api-Key": MASTER_API_KEY},
                    json={"mode": "turnstile", "url": args[0], "sitekey": args[1]},
                    timeout=20
                ) as r:
                    if r.status == 200:
                        res = await r.json()
                        data[user_id]["balance"] -= cost_usd
                        data[user_id]["requests_sent"] += 1
                        data[user_id]["request_history"].append(datetime.now().isoformat())
                        
                        await save_data_to_telegram_file(data)
                        await msg.edit_text(f"✅ *Solved!*\n🔑 Token: `{res['token']}`\n📉 *Cost:* `{cost_tokens} Tokens`", parse_mode="Markdown")
                        return
            except:
                pass
            await asyncio.sleep(0.5)
    await msg.edit_text("❌ `CAPTCHA_UNSOLVABLE`")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    data = cached_data
    user = data.get(user_id, {})

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
        data = cached_data
        
        # பயனர் டேட்டாபேஸில் இல்லை என்றால் புதிய கணக்கை உருவாக்குதல்
        if t_user not in data:
            data[t_user] = {"username": "User", "balance": 0.0, "requests_sent": 0, "request_history": []}
        
        # பழைய தொகையுடன் புதிய தொகையைக் கூட்டுதல் (Top-up)
        old_balance = data[t_user].get("balance", 0.0)
        new_balance = old_balance + amt_to_add
        data[t_user]["balance"] = round(new_balance, 4) # 4 தசம புள்ளிகளுக்கு ரவுண்ட் செய்தல்
        
        # கிளவுடில் சேமித்தல்
        await save_data_to_telegram_file(data)
        
        total_tokens = int(data[t_user]["balance"] * TOKEN_RATE)
        added_tokens = int(amt_to_add * TOKEN_RATE)
        
        await update.message.reply_text(f"✅ Added {added_tokens} Tokens to {t_user}.\n📊 New Total: {total_tokens} Tokens.")
        
        try:
            await context.bot.send_message(int(t_user), f"💰 Your balance has been topped up with {added_tokens} Tokens!\n📈 Total Balance: {total_tokens} Tokens.")
        except:
            pass
    except Exception as e:
        logger.error(f"Error in setbalance: {e}")
        await update.message.reply_text("⚠️ *Usage:* `/setbalance [ID] [AMOUNT]`\nExample: `/setbalance 8475230034 0.01`")

async def main():
    logger.info("Connecting to Telegram Account...")
    await client.connect()
    
    if not await client.is_user_authorized():
        phone = input("Please enter your phone (e.g. +94...): ")
        await client.send_code_request(phone)
        code = input("Please enter the code you received: ")
        await client.sign_in(phone, code)

    logger.info("Connected! Automatically loading database file from Saved Messages...")
    await load_data_from_telegram_file()

    # Telegram Bot Initialization
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("turnstile", turnstile_handler))
    app.add_handler(CommandHandler("setbalance", set_balance))
    app.add_handler(CallbackQueryHandler(button_handler))

    logger.info("Bot is successfully running...")
    
    async with app:
        await app.initialize()
        await app.start()
        await app.updater.start_polling()
        while True:
            await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
