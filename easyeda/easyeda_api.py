# Global imports
import logging
import time
import requests

from easy_kicad import __version__

# Endpoint pointing directly to the hidden EasyEDA API (found by reverse-engineering the web editor)
API_ENDPOINT = "https://easyeda.com/api/products/{lcsc_id}/components?version=6.4.19.5"
ENDPOINT_3D_MODEL = "https://modules.easyeda.com/3dmodel/{uuid}"
ENDPOINT_3D_MODEL_STEP = "https://modules.easyeda.com/qAxj6KHrDKw4blvCG8QJPs7Y/{uuid}"

# ------------------------------------------------------------


class EasyedaApi:
    def __init__(self) -> None:
        # Standard browser User-Agent to avoid early blocking
        self.headers = {
            "Accept-Encoding": "gzip, deflate",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }

    def get_info_from_easyeda_api(self, lcsc_id: str) -> dict:
        # ⚡ Anti-Blocking: Short delay between parts
        time.sleep(1.0)
        
        max_retries = 1
        for attempt in range(max_retries + 1):
            try:
                r = requests.get(url=API_ENDPOINT.format(lcsc_id=lcsc_id), headers=self.headers, timeout=10)
                
                if r.status_code == 200:
                    api_response = r.json()
                    if not api_response or (
                        "code" in api_response and api_response["success"] is False
                    ):
                        logging.debug(f"API Error Response for {lcsc_id}: {api_response}")
                        return {}
                    return api_response
                
                # 🛑 Handle Rate Limiting (429) or Server Overload
                if r.status_code == 429 or attempt < max_retries:
                    wait_time = 5 * (attempt + 1)
                    logging.warning(f"⚠️ API Error {r.status_code} for {lcsc_id}. Waiting {wait_time}s and retrying... ({attempt+1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    logging.error(f"❌ API Error {r.status_code} for {lcsc_id}. Abandoning.")
                    return {}

            except (requests.exceptions.JSONDecodeError, ValueError) as e:
                logging.error(f"❌ Invalid JSON received for {lcsc_id}: {e}")
                return {}
            except Exception as e:
                if attempt < max_retries:
                    time.sleep(2)
                    continue
                logging.error(f"❌ Connection error for {lcsc_id}: {e}")
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
