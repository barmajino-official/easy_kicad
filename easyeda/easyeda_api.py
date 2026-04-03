# Global imports
import logging
import time
import random
import requests

from easy_kicad import __version__

# Endpoint pointing directly to the hidden EasyEDA API (found by reverse-engineering the web editor)
API_ENDPOINT = "https://easyeda.com/api/products/{lcsc_id}/components?version=6.4.19.5"
ENDPOINT_3D_MODEL = "https://modules.easyeda.com/3dmodel/{uuid}"
ENDPOINT_3D_MODEL_STEP = "https://modules.easyeda.com/qAxj6KHrDKw4blvCG8QJPs7Y/{uuid}"

# ------------------------------------------------------------


class EasyedaApi:
    def __init__(self) -> None:
        # 🌐 Perfect Browser Mimicry
        self.headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Host": "easyeda.com",
            "Pragma": "no-cache",
            "Referer": "https://easyeda.com/editor",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
        }

    def get_info_from_easyeda_api(self, lcsc_id: str) -> dict:
        # ⚡ Anti-Blocking: Random delay between parts (2 to 7 seconds)
        delay = random.uniform(2.0, 7.0)
        time.sleep(delay)
        
        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                r = requests.get(url=API_ENDPOINT.format(lcsc_id=lcsc_id), headers=self.headers, timeout=12)
                
                if r.status_code == 200:
                    try:
                        api_response = r.json()
                    except ValueError:
                        logging.error(f"❌ Received non-JSON response for {lcsc_id}. Possible block.")
                        time.sleep(30)
                        continue

                    if not api_response or (
                        "code" in api_response and api_response["success"] is False
                    ):
                        logging.warning(f"⚠️ EasyEDA Server returned failure for {lcsc_id}: {api_response}")
                        return {}
                    return api_response
                
                # 🛑 Handle Rate Limiting (429)
                if r.status_code == 429:
                    logging.warning(f"🚨 Rate Limited! Waiting 60s before retry... ({attempt+1}/{max_retries})")
                    time.sleep(60)
                    continue
                
                # 🛑 Handle Server Overload (5xx)
                if r.status_code >= 500:
                    logging.warning(f"⚠️ Server Error {r.status_code}. Waiting 15s... ({attempt+1}/{max_retries})")
                    time.sleep(15)
                    continue
                
                # 🛑 Handle Other Errors
                if attempt < max_retries:
                    wait_time = 5 * (attempt + 1)
                    logging.warning(f"⚠️ API Error {r.status_code} for {lcsc_id}. Waiting {wait_time}s... ({attempt+1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    logging.error(f"❌ API Error {r.status_code} for {lcsc_id}. Giving up on this part.")
                    return {}

            except requests.exceptions.Timeout:
                logging.warning(f"⏳ Timeout for {lcsc_id}. Waiting 10s... ({attempt+1}/{max_retries})")
                time.sleep(10)
                continue
            except Exception as e:
                if attempt < max_retries:
                    logging.warning(f"🔌 Connection error: {e}. Retrying in 5s...")
                    time.sleep(5)
                    continue
                logging.error(f"❌ Fatal error for {lcsc_id}: {e}")
                return {}
        return {}

    def get_cad_data_of_component(self, lcsc_id: str) -> dict:
        cp_cad_info = self.get_info_from_easyeda_api(lcsc_id=lcsc_id)
        if cp_cad_info == {}:
            return {}
        return cp_cad_info["result"]

    def _download_with_progress(self, url: str, label: str) -> bytes:
        """Download a file with a manual progress bar."""
        try:
            r = requests.get(url, headers=self.headers, stream=True)
            if r.status_code != 200:
                return None
            
            total_size = int(r.headers.get('content-length', 0))
            chunk_size = 1024 * 16 # 16KB
            downloaded = 0
            content = bytearray()
            
            for chunk in r.iter_content(chunk_size=chunk_size):
                content.extend(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    percent = int(100 * downloaded / total_size)
                    bar = "#" * (percent // 10) + "-" * (10 - (percent // 10))
                    print(f"\r  └─ {label}: [{bar}] {percent}% ({downloaded // 1024} KB / {total_size // 1024} KB)", end="", flush=True)
            
            if total_size > 0:
                print() # New line after finishing
            return bytes(content)
        except Exception as e:
            logging.error(f"Download error for {url}: {e}")
            return None

    def get_raw_3d_model_obj(self, uuid: str) -> str:
        url = ENDPOINT_3D_MODEL.format(uuid=uuid)
        content = self._download_with_progress(url, "Downloading OBJ")
        if content:
            return content.decode('utf-8', errors='ignore')
        return None

    def get_step_3d_model(self, uuid: str) -> bytes:
        url = ENDPOINT_3D_MODEL_STEP.format(uuid=uuid)
        return self._download_with_progress(url, "Downloading STEP")
