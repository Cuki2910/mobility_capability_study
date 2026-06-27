"""
fetch_route_details.py
======================
Fetches all VinBus route details from the API and saves decrypted JSON.
Uses urllib with headers mimicking a browser (same as read_url_content succeeds with).
"""
import binascii, json, os, sys, time
import urllib.request, urllib.error
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

KEY = b'ViNbus2o21#K3(y)th3BUSNiElectric'
BASE = "https://vbcore-api.vinbus.vn"
RAW_DIR = r"d:\GREEN-X\mobility-capability-study\data\raw\vinbus_raw_json"
DETAIL_DIR = os.path.join(RAW_DIR, 'details')
os.makedirs(DETAIL_DIR, exist_ok=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'vi-VN,vi;q=0.9,en;q=0.8',
    'Referer': 'https://maps.vinbus.vn/',
    'Origin': 'https://maps.vinbus.vn',
}

def decrypt(hex_str):
    raw = binascii.unhexlify(hex_str.strip().strip('"'))
    iv, ct = raw[:16], raw[16:]
    return json.loads(unpad(AES.new(KEY, AES.MODE_CBC, iv).decrypt(ct), AES.block_size).decode('utf-8'))

def fetch_url(url, timeout=20):
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        return None

# Test connectivity first
print("Testing API connectivity...", file=sys.stderr)
test = fetch_url(f"{BASE}/client/auth/decrypt_key", timeout=10)
if test:
    print(f"  Connected! Key: {test}", file=sys.stderr)
else:
    print("  Cannot reach API directly. Will try with SSL bypass...", file=sys.stderr)
    import ssl
    ssl._create_default_https_context = ssl._create_unverified_context
    test = fetch_url(f"{BASE}/client/auth/decrypt_key", timeout=15)
    if test:
        print(f"  Connected with SSL bypass! Key: {test}", file=sys.stderr)
    else:
        print("  Still cannot connect. Network is blocked for direct Python requests.", file=sys.stderr)
        print("  The API is only accessible via the cloud fetcher tool.", file=sys.stderr)
        sys.exit(1)

# Load route IDs
with open(os.path.join(RAW_DIR, 'detail_urls.txt')) as f:
    routes = [(line.split('\t')[0].strip(), line.split('\t')[1].strip()) 
              for line in f if '\t' in line]

print(f"Fetching {len(routes)} route details...", file=sys.stderr)
success = 0
skipped = 0
failed = 0

for i, (route_id, url) in enumerate(routes):
    out_path = os.path.join(DETAIL_DIR, f'detail_{route_id}.json')
    if os.path.exists(out_path):
        skipped += 1
        continue
    
    hex_payload = fetch_url(url)
    if not hex_payload:
        print(f"  [{i+1}/{len(routes)}] FAIL route {route_id}", file=sys.stderr)
        failed += 1
        continue
    
    try:
        detail = decrypt(str(hex_payload))
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(detail, f, ensure_ascii=False, indent=2)
        success += 1
        if success % 10 == 0:
            print(f"  [{i+1}/{len(routes)}] {success} fetched so far...", file=sys.stderr)
    except Exception as e:
        print(f"  [{i+1}/{len(routes)}] DECRYPT FAIL route {route_id}: {e}", file=sys.stderr)
        failed += 1
    
    time.sleep(0.5)  # be polite

print(f"\nDone: {success} fetched, {skipped} skipped, {failed} failed", file=sys.stderr)
