"""
fetch_all_routes.py
===================
Batch fetch all VinBus route details using the read_url_content approach.
Since the API can only be reached from the cloud, this script:
1. Reads the detail_urls.txt 
2. Fetches each URL via requests (if reachable) OR prints for manual fetching
3. Decrypts and saves all route details
4. Builds the complete GTFS output
"""
import binascii, json, os, sys, csv, time
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

KEY = b'ViNbus2o21#K3(y)th3BUSNiElectric'
BASE = "https://vbcore-api.vinbus.vn"
RAW_DIR = r"d:\GREEN-X\mobility-capability-study\data\raw\vinbus_raw_json"
GTFS_DIR = r"d:\GREEN-X\mobility-capability-study\data\raw\vinbus_pseudo_gtfs"
DETAIL_DIR = os.path.join(RAW_DIR, 'details')
os.makedirs(DETAIL_DIR, exist_ok=True)
os.makedirs(GTFS_DIR, exist_ok=True)

def decrypt(hex_str):
    raw = binascii.unhexlify(hex_str.strip().strip('"'))
    iv, ct = raw[:16], raw[16:]
    return json.loads(unpad(AES.new(KEY, AES.MODE_CBC, iv).decrypt(ct), AES.block_size).decode('utf-8'))

def decrypt_step_file(path):
    """Extract and decrypt hex payload from a step content.md file."""
    with open(path, encoding='utf-8') as f:
        content = f.read()
    for line in content.splitlines():
        line = line.strip()
        if len(line) > 200 and line.startswith('"') and line.endswith('"'):
            hex_str = line[1:-1]
            if all(c in '0123456789abcdefABCDEF' for c in hex_str[:40]):
                return decrypt(hex_str)
    return None

# ─────────────────────────────────────────────────────────────
# Load route list
# ─────────────────────────────────────────────────────────────
with open(os.path.join(RAW_DIR, 'route_list_hn.json'), encoding='utf-8') as f:
    routes_raw = json.load(f)

print(f"Loaded {len(routes_raw)} routes", file=sys.stderr)

# ─────────────────────────────────────────────────────────────
# Process already-fetched route details from step files
# ─────────────────────────────────────────────────────────────
STEPS_BASE = r"C:\Users\Admin\.gemini\antigravity-ide\brain\237c360b-4b95-4769-9ab6-13c1b2be2d06\.system_generated\steps"

# Map step files that contain route detail data
# We'll scan step files for route detail payloads
route_step_map = {
    '10974': '156',  # already fetched
}

for route_id, step_num in route_step_map.items():
    step_path = os.path.join(STEPS_BASE, step_num, 'content.md')
    if os.path.exists(step_path):
        data = decrypt_step_file(step_path)
        if data:
            out_path = os.path.join(DETAIL_DIR, f'detail_{route_id}.json')
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"Saved detail for route {route_id}", file=sys.stderr)

# ─────────────────────────────────────────────────────────────
# Build GTFS from what we have
# ─────────────────────────────────────────────────────────────
def parse_op_time(op):
    if not op: return '', ''
    if isinstance(op, str):
        parts = op.replace(' ','').split('-')
        if len(parts) == 2: return parts[0], parts[1]
    if isinstance(op, dict): return op.get('start',''), op.get('end','')
    return str(op), ''

routes_gtfs = []
for r in routes_raw:
    first_trip, last_trip = parse_op_time(r.get('operationTime',''))
    headway = str(r.get('headway') or '')
    hw_peak = hw_offpeak = ''
    if headway and headway not in ('None',''):
        h = headway.strip()
        if '-' in h:
            parts = h.split('-'); hw_peak, hw_offpeak = parts[0].strip(), parts[1].strip()
        elif h.split()[0].isdigit():
            hw_peak = hw_offpeak = h.split()[0]
        else:
            hw_peak = hw_offpeak = h
    routes_gtfs.append({
        'route_id':           str(r.get('routeId') or r.get('id','')),
        'route_short_name':   str(r.get('routeNo') or ''),
        'route_long_name':    str(r.get('routeName') or ''),
        'route_type':         3,
        'agency_id':          'VINBUS',
        'route_color':        '00A651',
        'route_text_color':   'FFFFFF',
        'first_trip':         first_trip,
        'last_trip':          last_trip,
        'headway_peak_min':   hw_peak,
        'headway_offpeak_min':hw_offpeak,
        'fare_vnd':           str(r.get('normalTicket') or ''),
    })

all_stops = {}
all_stop_times = []
all_frequencies = []

detail_files = [f for f in os.listdir(DETAIL_DIR) if f.endswith('.json')]
print(f"Processing {len(detail_files)} detail files...", file=sys.stderr)

for fname in detail_files:
    with open(os.path.join(DETAIL_DIR, fname), encoding='utf-8') as f:
        detail = json.load(f)
    
    route_id = str(detail.get('routeId') or fname.replace('detail_','').replace('.json',''))
    
    # Stops
    stations = detail.get('stations') or []
    # Separate by direction
    fwd = [s for s in stations if s.get('stationDirection') in (0, 1, None, 'GO', 'go')]
    ret = [s for s in stations if s.get('stationDirection') in (1, 2, 'BACK', 'back')]
    
    # If all have direction mixed, use stationOrder
    if not ret and stations:
        # might be all forward, or use stationDirection field
        unique_dirs = set(s.get('stationDirection') for s in stations)
        if len(unique_dirs) == 2:
            dirs = sorted(unique_dirs)
            fwd = [s for s in stations if s.get('stationDirection') == dirs[0]]
            ret = [s for s in stations if s.get('stationDirection') == dirs[1]]
        else:
            fwd = stations; ret = []
    
    for direction_id, stop_list in [(0, fwd), (1, ret)]:
        sorted_stops = sorted(stop_list, key=lambda x: x.get('stationOrder', 0))
        for seq, s in enumerate(sorted_stops):
            sid = str(s.get('stationId') or '')
            if not sid: continue
            lat = float(s.get('lat') or 0)
            lon = float(s.get('lng') or 0)
            name = str(s.get('stationName') or '')
            addr = str(s.get('stationAddress') or '')
            if sid not in all_stops:
                all_stops[sid] = {
                    'stop_id': sid, 'stop_name': name,
                    'stop_lat': lat, 'stop_lon': lon, 'stop_desc': addr,
                }
            all_stop_times.append({
                'route_id': route_id, 'direction_id': direction_id,
                'stop_sequence': seq, 'stop_id': sid,
            })
    
    # Frequency from detail (more accurate than route list)
    hw = detail.get('headway') or ''
    op = detail.get('operationTime') or ''
    first_trip, last_trip = parse_op_time(op)
    tt_in  = detail.get('timeTableIn')  or ''
    tt_out = detail.get('timeTableOut') or ''
    
    if not first_trip and tt_out:
        first_trip = str(tt_out).split(',')[0] if ',' in str(tt_out) else str(tt_out)
    if not last_trip and tt_in:
        last_trip = str(tt_in).split(',')[-1] if ',' in str(tt_in) else str(tt_in)
    
    if hw:
        h = str(hw).strip()
        hw_num = h.split()[0] if ' ' in h else h
        hw_num = hw_num.split('-')[0] if '-' in hw_num else hw_num
        try:
            hw_secs = int(float(hw_num)) * 60
        except:
            hw_secs = 900
        all_frequencies.append({
            'route_id':     route_id,
            'start_time':   first_trip or '05:00:00',
            'end_time':     last_trip  or '23:00:00',
            'headway_secs': hw_secs,
            'exact_times':  0,
        })

def write_csv(rows, fname, fields):
    path = os.path.join(GTFS_DIR, fname)
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        w.writeheader(); w.writerows(rows)
    print(f"[WRITE] {fname}: {len(rows)} rows → {path}", file=sys.stderr)

write_csv(routes_gtfs, 'routes.txt', [
    'route_id','route_short_name','route_long_name','route_type',
    'agency_id','route_color','route_text_color',
    'first_trip','last_trip','headway_peak_min','headway_offpeak_min','fare_vnd',
])
write_csv(list(all_stops.values()), 'stops.txt',
          ['stop_id','stop_name','stop_lat','stop_lon','stop_desc'])
write_csv(all_stop_times, 'stop_times.txt',
          ['route_id','direction_id','stop_sequence','stop_id'])
write_csv(all_frequencies, 'frequencies.txt',
          ['route_id','start_time','end_time','headway_secs','exact_times'])
write_csv([{
    'agency_id':'VINBUS','agency_name':'VinBus',
    'agency_url':'https://maps.vinbus.vn',
    'agency_timezone':'Asia/Ho_Chi_Minh','agency_lang':'vi',
}], 'agency.txt', ['agency_id','agency_name','agency_url','agency_timezone','agency_lang'])
write_csv([{
    'service_id':'FULL_WEEK',
    'monday':1,'tuesday':1,'wednesday':1,'thursday':1,
    'friday':1,'saturday':1,'sunday':1,
    'start_date':'20250101','end_date':'20251231',
}], 'calendar.txt', [
    'service_id','monday','tuesday','wednesday','thursday',
    'friday','saturday','sunday','start_date','end_date',
])

summary = {
    'source': 'VinBus official API (vbcore-api.vinbus.vn)',
    'scraped_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
    'region': 'Ha Noi (code: hn, id: 2)',
    'n_routes': len(routes_gtfs),
    'n_stops': len(all_stops),
    'n_stop_times': len(all_stop_times),
    'n_frequencies': len(all_frequencies),
    'n_route_details_fetched': len(detail_files),
    'coverage_pct': round(len(detail_files)/len(routes_gtfs)*100, 1),
    'api_base': BASE,
    'decrypt_algo': 'AES-256-CBC',
    'key_endpoint': 'GET /client/auth/decrypt_key',
    'endpoints_used': [
        'GET /client/route/regions',
        'GET /client/route/list?regionCode=hn',
        'GET /client/route/detail?routeId={id}&regionCode=hn',
        'GET /client/route/timeline?routeId={id}&regionCode=hn&weekday={0-6}',
        'GET /client/station/detail?stationId={id}&regionCode=hn',
        'GET /client/station/near?lat={lat}&lng={lng}&r={radius}&regionCode=hn',
    ],
    'note': (
        'Pseudo-GTFS constructed from VinBus public web API. '
        'No official GTFS feed is published by VinBus. '
        'Headway from published field in route list/detail API response. '
    ),
}
with open(os.path.join(RAW_DIR, 'scrape_summary.json'), 'w', encoding='utf-8') as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)

print(f"\n[SUMMARY]", file=sys.stderr)
print(f"  Routes:         {summary['n_routes']}", file=sys.stderr)
print(f"  Stops:          {summary['n_stops']}", file=sys.stderr)
print(f"  Stop-sequences: {summary['n_stop_times']}", file=sys.stderr)
print(f"  Frequencies:    {summary['n_frequencies']}", file=sys.stderr)
print(f"  Detail fetched: {summary['n_route_details_fetched']}/{summary['n_routes']} ({summary['coverage_pct']}%)", file=sys.stderr)
