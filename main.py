#!/usr/bin/env python3
"""
PSYCHO BOT LAUNCHER - Premium Multi-Bot Launcher
"""

import os
import sys
import time
import subprocess

# ============================================================
# PSYCHO UI - Premium UI Framework
# ============================================================
class PsychoUI:
    def __init__(self, typing_speed=0.002):
        self.speed = typing_speed

        # Premium Color Palette
        self.pri = "\033[38;5;147m"      # Purple Blue
        self.sec = "\033[38;5;123m"      # Cyan
        self.gray = "\033[38;5;243m"     # Gray
        self.green = "\033[38;5;120m"    # Green
        self.red = "\033[38;5;204m"      # Red
        self.yellow = "\033[38;5;223m"   # Yellow
        self.gold = "\033[38;5;220m"     # Gold
        self.pink = "\033[38;5;212m"     # Pink
        self.orange = "\033[38;5;214m"   # Orange
        self.purple = "\033[38;5;135m"   # Purple
        self.reset = "\033[0m"

    def type_text(self, text, color="", delay=0.001):
        full_text = f"{color}{text}{self.reset}\n"
        for char in full_text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(delay)

    def show_banner(self):
        os.system('cls' if os.name == 'nt' else 'clear')

        # Animated Gradient Banner
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

        # Dashboard Grid
        print(f" {self.gray}┌──────────────────────────────────────────────────────────────┐{self.reset}")
        print(f" {self.gray}│ {self.reset}Telegram {self.gray}» {self.pink}@PSYCHOBOT1{self.reset}          {self.gray}│ {self.reset}Developer {self.gray}» {self.sec}@ALPHAPYTHON12{self.reset} {self.gray}│{self.reset}")
        print(f" {self.gray}│ {self.reset}Status   {self.gray}» {self.green}● ONLINE{self.reset}             {self.gray}│ {self.reset}Type     {self.gray}» {self.gold}LAUNCHER{self.reset}        {self.gray}│{self.reset}")
        print(f" {self.gray}└──────────────────────────────────────────────────────────────┘{self.reset}\n")

    def info(self, message):
        self.type_text(f"  {self.gray}• {self.reset}{message}", self.gray, 0.001)

    def warning(self, message):
        self.type_text(f"  {self.yellow}⚠ {self.reset}{message}", self.yellow, 0.002)

    def error(self, message):
        self.type_text(f"  {self.red}✘ {self.reset}{message}", self.red, 0.002)

    def success(self, message):
        self.type_text(f"  {self.green}✔ {self.reset}{message}", self.green, 0.001)

    def inline_status(self, text, color="\033[38;5;223m"):
        sys.stdout.write(f"\r  {color}▶ {self.reset}{text}")
        sys.stdout.flush()

    def clear_inline(self):
        sys.stdout.write("\r" + " " * 90 + "\r")
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
# LAUNCHER FUNCTIONS
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
        print_error("Invalid option. Please try again.")

def launch_bot(script_name, display_name=""):
    bot.show_banner()
    print_header(f"Launching {display_name or script_name}")
    bot.info(f"Starting {script_name}...")
    time.sleep(1)
    try:
        subprocess.run([sys.executable, script_name])
    except KeyboardInterrupt:
        print(f'\n{C["yellow"]}[STOPPED] Returned to main launcher.{C["reset"]}')
        time.sleep(1.5)
    except Exception as e:
        bot.error(f"Failed to launch {script_name}: {e}")
        time.sleep(2)

def launch_earncrypto():
    if os.path.exists("bot.py"):
        launch_bot("bot.py", "EarnCryptoWrs Bot")
    else:
        bot.show_banner()
        print_error("bot.py not found in current directory!")
        print_info("Please make sure bot.py is in the same folder.")
        time.sleep(2)

def launch_coinpayu():
    if os.path.exists("coin.py"):
        launch_bot("coin.py", "CoinPayuFree Bot")
    else:
        bot.show_banner()
        print_error("coin.py not found in current directory!")
        print_info("Please make sure coin.py is in the same folder.")
        time.sleep(2)

def launch_altcryp():
    if os.path.exists("altcryp.py"):
        launch_bot("altcryp.py", "Altcryp Bot")
    else:
        bot.show_banner()
        print_error("altcryp.py not found in current directory!")
        print_info("Please make sure altcryp.py is in the same folder.")
        time.sleep(2)

def launch_mixcrypto():
    if os.path.exists("mix.py"):
        launch_bot("mix.py", "Mix-Crypto-BTC Bot")
    else:
        bot.show_banner()
        print_error("mix.py not found in current directory!")
        print_info("Please make sure mix.py is in the same folder.")
        time.sleep(2)

def launch_claimcoin():
    """Launch ClaimCoin.in Bot"""
    if os.path.exists("cc.py"):
        launch_bot("cc.py", "ClaimCoin.in Bot")
    else:
        bot.show_banner()
        print_error("cc.py not found in current directory!")
        print_info("Please make sure cc.py is in the same folder.")
        time.sleep(2)

def launch_tfaucet():
    """Launch TFaucet Bot"""
    if os.path.exists("tf.py"):
        launch_bot("tf.py", "TFaucet Bot")
    else:
        bot.show_banner()
        print_error("tf.py not found in current directory!")
        print_info("Please make sure tf.py is in the same folder.")
        time.sleep(2)

# ============================================================
# MAIN MENU
# ============================================================
def main_menu():
    while True:
        bot.show_banner()
        print_header("PSYCHO BOT LAUNCHER")

        menu_options = {
            '1': 'ALPHA SOLVER',
            '2': 'BOT VIP',
            '3': 'BOT FREE',
            '4': 'EXIT'
        }

        choice = get_menu_choice("Main Menu:", menu_options)

        if choice == '1':
            bot.show_banner()
            print_header("ALPHA SOLVER")
            print_warning("ALPHA SOLVER is currently not available on this server.")
            print_info("Please check back later or contact @PSYCHOBOT1")
            time.sleep(3)

        elif choice == '2':
            bot.show_banner()
            print_header("BOT VIP")
            print_warning("BOT VIP is currently not available on this server.")
            print_info("Please check back later or contact @PSYCHOBOT1")
            time.sleep(3)

        elif choice == '3':
            free_menu()

        elif choice == '4':
            bot.show_banner()
            print_success("Thank you for using PSYCHO BOT Launcher!")
            print_info("Exiting...")
            time.sleep(1)
            sys.exit(0)

# ============================================================
# FREE MENU
# ============================================================
def free_menu():
    while True:
        bot.show_banner()
        print_header("BOT FREE")

        free_options = {
            '1': 'EarnCryptoWrs Bot',
            '2': 'CoinPayuFree Bot',
            '3': 'Altcryp Bot',
            '4': 'Mix-Crypto-BTC Bot',
            '5': 'ClaimCoin.in Bot',
            '6': 'TFaucet Bot',
            '7': 'Back to Main Menu'
        }

        choice = get_menu_choice("Free Bots:", free_options)

        if choice == '1':
            launch_earncrypto()

        elif choice == '2':
            launch_coinpayu()

        elif choice == '3':
            launch_altcryp()

        elif choice == '4':
            launch_mixcrypto()

        elif choice == '5':
            launch_claimcoin()

        elif choice == '6':
            launch_tfaucet()

        elif choice == '7':
            return

# ============================================================
# MAIN ENTRY
# ============================================================
if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        bot.show_banner()
        print_info("Launcher terminated by operator.")
        time.sleep(1)
        sys.exit(0)
