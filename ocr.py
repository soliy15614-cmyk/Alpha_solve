import httpx
import asyncio
import logging

logger = logging.getLogger(__name__)

# CONFIGURATIONS
API_KEY = "868d78793d83aacd4009cec59dc96a44"
SUBMIT_URL = "https://api.waryono.my.id/in.php"
RESULT_URL = "https://api.waryono.my.id/res.php"

async def process_ocr_captcha(base64_img: str) -> str:
    """
    Mengambil payload base64 (dari teks input ataupun hasil konversi foto),
    mengirimkannya ke API Waryono, dan melakukan polling async hingga selesai.
    """
    payload = {
        "apikey": API_KEY,
        "methods": "image-to-text",
        "base64_img": base64_img,
        "json": 1
    }

    # Menggunakan httpx.AsyncClient dengan limits timeout yang disesuaikan untuk upload gambar
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            # ── Langkah 1: Kirim Tugas (Submit Task) ───────────────────
            response = await client.post(SUBMIT_URL, json=payload)
            if response.status_code != 200:
                return "error_submit_failed"
            
            res_data = response.json()
            if res_data.get("status") != 1:
                return f"error_{res_data.get('request', 'unknown')}"
            
            request_id = res_data.get("request")
            
            # ── Langkah 2: Polling Hasil secara Async ──────────────────
            # Melakukan perulangan maksimal 30 kali dengan jeda 5 detik (Total 150 detik)
            for _ in range(30):
                await asyncio.sleep(5)  # Jeda non-blocking agar bot tidak hang
                
                poll_url = f"{RESULT_URL}?apikey={API_KEY}&action=get&id={request_id}&json=1"
                poll_response = await client.get(poll_url)
                
                if poll_response.status_code != 200:
                    continue
                
                poll_data = poll_response.json()
                
                # Jika status sukses (1), kembalikan teks hasil CAPTCHA
                if poll_data.get("status") == 1:
                    return str(poll_data.get("request"))
                
                # Sembunyikan pesan jika server mengembalikan status gagal solve secara internal
                if poll_data.get("request") in ["ERROR_CAPTCHA_UNSOLVABLE", "ERROR_WRONG_CAPTCHA_ID"]:
                    return f"error_{poll_data.get('request')}"
            
            return "error_timeout"

        except Exception as e:
            # Mengembalikan string dengan awalan 'error_' agar disembunyikan oleh main.py
            return f"error_exception_{str(e)}"

