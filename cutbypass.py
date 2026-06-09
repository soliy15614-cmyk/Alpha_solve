import time
import re
import json
import sys
import threading
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
import requests
from colorama import init, Fore, Style
# fake-useragent லைப்ரரியை இறக்குமதி செய்கிறோம்
from fake_useragent import UserAgent

# Colorama-வை ரீசெட் செய்யத் தயார்படுத்துகிறோம்
init(autoreset=True)

class AutomationWorkflow:
    def __init__(self, target_url):
        self.initial_url = target_url
        self.session = requests.Session()
        
        # UserAgent ஆப்ஜெக்ட்டை உருவாக்குகிறோம்
        ua = UserAgent()
        # மொபைல் பிரவுசர் பயனர் ஏஜென்ட்டைத் தானாகத் தேர்ந்தெடுக்கிறோம்
        random_mobile_ua = ua.mobile
        
        self.session.headers.update({
            "User-Agent": random_mobile_ua,
        })
        self.is_running = True
        self.final_result_url = None
        self.error_message = None

    def animate_loading(self):
        """திரையில் அழகான அனிமேஷனைக் காட்டும் செயல்பாடு"""
        chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        index = 0
        while self.is_running:
            sys.stdout.write(f"\r{Fore.CYAN}{chars[index % len(chars)]} {Fore.YELLOW}Processing, please wait...")
            sys.stdout.flush()
            index += 1
            time.sleep(0.1)

        sys.stdout.write("\r" + " " * 60 + "\r")
        sys.stdout.flush()

    def process_logic(self):
        """பின்னணியில் நடக்கும் அனைத்து நெட்வொர்க் வேலைகள்"""
        try:
            # STEP 1: முதலாவது தளம்
            response = self.session.get(self.initial_url, allow_redirects=True)
            redirected_url = response.url

            parsed_url = urlparse(redirected_url)
            queries = parse_qs(parsed_url.query)
            ssid = queries.get("ssid", [None])[0]

            if not ssid:
                self.error_message = "Failed to extract SSID from link."
                self.is_running = False
                return

            csrf_match = re.search(r'const csrfToken\s*=\s*"([^"]+)"', response.text)
            if not csrf_match:
                self.error_message = "Failed to extract CSRF token."
                self.is_running = False
                return
            csrf_token_1 = csrf_match.group(1)

            # 10 விநாடிகள் கட்டாயக் காத்திருப்பு
            time.sleep(10)

            # Verification requests (3 முறை)
            session_api_url = f"https://starkroboticsfrc.com/api/session/{ssid}"
            headers_1 = {"x-csrf-token": csrf_token_1}
            for _ in range(3):
                res = self.session.get(session_api_url, headers=headers_1)
                if not res.json().get("success"):
                    self.error_message = "Session API synchronization failed."
                    self.is_running = False
                    return

            # IP முகவரி வாங்குதல்
            ip_res = self.session.get("https://ipv4.icanhazip.com")
            current_ip = ip_res.text.strip()

            # PATCH கோரிக்கை
            patch_url = f"https://starkroboticsfrc.com/api/session/{ssid}"
            patch_headers_1 = {
                "x-csrf-token": csrf_token_1,
                "content-type": "application/json",
                "sec-ch-ua-mobile": "?1",
                "accept": "*/*",
                "origin": "https://starkroboticsfrc.com",
                "x-requested-with": "mark.via.gp",
                "sec-fetch-site": "same-origin",
                "sec-fetch-mode": "cors"
            }
            payload_data = {
                "ssid": ssid,
                "currentIp": current_ip,
                "ipType": "IPv4",
                "ipv4": current_ip,
                "ipv6": None,
                "hcaptchaToken": None
            }

            patch_res = self.session.patch(patch_url, headers=patch_headers_1, json=payload_data)
            redirect_t_co = patch_res.json().get("redirect")

            # t.co இடைநிலை வழிமாற்றம்
            t_co_res = self.session.get(redirect_t_co)
            url_match = re.search(r'location\.replace\("([^"]+)"\)', t_co_res.text)
            second_site_url = url_match.group(1).replace(r'\/', '/')

            # இரண்டாவது தளம் (law.ravellawfirm.com) பக்கத்தை அணுகுதல்
            second_site_res = self.session.get(second_site_url)

            # HTML இலிருந்து finalDestination URL-ஐத் தேடுதல்
            final_url_match = re.search(r'&quot;finalDestination&quot;:\[\d+,&quot;([^&"\s]+)&quot;\]', second_site_res.text)
            if not final_url_match:
                final_url_match = re.search(r'"finalDestination":\[\d+,"([^"]+)"\]', second_site_res.text)

            if not final_url_match:
                self.error_message = "Could not parse final token destination from server."
                self.is_running = False
                return

            final_paycut_url = final_url_match.group(1).replace(r'\/', '/')

            # FINAL PAYCUT GET REQUEST
            self.session.headers.update({
                'referer': 'https://starkroboticsfrc.com/',
                'upgrade-insecure-requests': '1',
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-dest': 'document'
            })

            paycut_page_res = self.session.get(final_paycut_url)

            # Form டோக்கன்களைப் பிரித்தெடுத்தல்
            soup = BeautifulSoup(paycut_page_res.text, "html.parser")
            form = soup.find("form", id="go-link")

            if not form:
                self.error_message = "Form data block is missing from target page."
                self.is_running = False
                return

            form_data = {}
            for input_tag in form.find_all("input"):
                name = input_tag.get("name")
                value = input_tag.get("value", "")
                if name:
                    form_data[name] = value

            post_headers = {
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'X-Requested-With': 'XMLHttpRequest',
                'Origin': 'https://paycut.net',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Dest': 'empty',
                'Referer': final_paycut_url,
            }

            # FINAL POST REQUEST
            post_url = "https://paycut.net/links/go"
            final_response = self.session.post(post_url, data=form_data, headers=post_headers)

            try:
                res_data = final_response.json()
                if res_data.get("status") == "success" or "url" in res_data:
                    self.final_result_url = res_data.get("url").replace(r'\/', '/')
                else:
                    self.error_message = "Server did not return a success link payload."
            except:
                url_find = re.search(r'"url"\s*:\s*"([^"]+)"', final_response.text)
                if url_find:
                    self.final_result_url = url_find.group(1).replace(r'\/', '/')
                else:
                    self.error_message = "Failed to parse final JSON response structure."

        except Exception as e:
            self.error_message = f"Network or system fault occurred: {str(e)}"

        self.is_running = False

    def start(self):
        worker_thread = threading.Thread(target=self.process_logic)
        worker_thread.start()
        self.animate_loading()
        worker_thread.join()

        if self.final_result_url:
            print(f"{Fore.GREEN}{Style.BRIGHT}[✔] SUCCESS: Bypass URL Completed Successfully!")
            print(f"{Fore.LIGHTMAGENTA_EX}{Style.BRIGHT}{self.final_result_url}")
            print(f"\n{Fore.GREEN}ok done")
        else:
            print(f"{Fore.RED}{Style.BRIGHT}[✘] BYPASS FAILED")
            print(f"{Fore.LIGHTRED_EX}Reason: {self.error_message}")


if __name__ == "__main__":
    print(f"{Fore.BLUE}{Style.BRIGHT}==========================================")
    print(f"{Fore.BLUE}{Style.BRIGHT}     PAYCUT LINK BYPASS AUTOMATION        ")
    print(f"{Fore.BLUE}{Style.BRIGHT}==========================================\n")

    user_input = input(f"{Fore.WHITE}Please Enter Shortlink URL: ").strip()

    if user_input:
        workflow = AutomationWorkflow(user_input)
        workflow.start()
    else:
        print(f"{Fore.RED}No input URL detected. Exiting.")

