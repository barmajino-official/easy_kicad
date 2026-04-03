# Global imports
import logging
import time
import random
import json
import subprocess
import requests

from helpers import __version__

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
                # 🛡️ THE NUCLEAR OPTION: Using 'curl' directly
                # Force IPv4 (-4) as sometimes Docker IPv6 triggers WAF blocks
                url = API_ENDPOINT.format(lcsc_id=lcsc_id)
                cmd = [
                    "curl", "-s", "-L", "-4",
                    "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "-H", "Referer: https://easyeda.com/editor",
                    "-H", "Accept: application/json",
                    "--max-time", "15",
                    url
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    try:
                        api_response = json.loads(result.stdout)
                    except json.JSONDecodeError:
                        logging.error(f"❌ Received non-JSON response from curl for {lcsc_id}. Possible block. Body: {result.stdout[:200]}")
                        time.sleep(30)
                        continue

                    if not api_response or (
                        "code" in api_response and api_response["success"] is False
                    ):
                        logging.warning(f"⚠️ EasyEDA Server returned failure for {lcsc_id}: {api_response}")
                        return {}
                    return api_response
                
                # Handle curl errors
                logging.warning(f"⚠️ Curl failed with code {result.returncode} for {lcsc_id}. Error: {result.stderr[:100]}")
                time.sleep(10)
                continue

            except Exception as e:
                if attempt < max_retries:
                    logging.warning(f"🔌 Connection error in curl bridge: {e}. Retrying in 5s...")
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

    def _download_with_curl(self, url: str, label: str) -> bytes:
        """Download a file using the curl bridge to bypass redirect loops and WAF."""
        try:
            # -L follows redirects, -4 forces IPv4, -s is silent
            cmd = [
                "curl", "-s", "-L", "-4",
                "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "-H", "Referer: https://easyeda.com/editor",
                "--max-time", "60",
                url
            ]
            print(f"  └─ {label}: Initiating curl download...", end="", flush=True)
            result = subprocess.run(cmd, capture_output=True)
            
            if result.returncode == 0 and len(result.stdout) > 0:
                print(f" Done ({len(result.stdout) // 1024} KB)")
                return result.stdout
            
            logging.error(f"\n❌ Curl download failed for {url}. Code: {result.returncode}")
            return None
        except Exception as e:
            logging.error(f"\n❌ Fatal error in curl download: {e}")
            return None

    def get_raw_3d_model_obj(self, uuid: str) -> str:
        url = ENDPOINT_3D_MODEL.format(uuid=uuid)
        content = self._download_with_curl(url, "Downloading OBJ")
        if content:
            return content.decode('utf-8', errors='ignore')
        return None

    def get_step_3d_model(self, uuid: str) -> bytes:
        url = ENDPOINT_3D_MODEL_STEP.format(uuid=uuid)
        return self._download_with_curl(url, "Downloading STEP")
