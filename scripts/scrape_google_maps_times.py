"""
Scrape motorcycle travel times from Google Maps web for validation OD pairs.
Uses Playwright headless Chromium. Falls back to car time if motorcycle mode
is not available for the route in Vietnam.
"""
from __future__ import annotations
import json, sys, time, io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

OD_PAIRS = [
    (0, "VOP Gate",      20.9929, 105.9451, "BV Song Hong",       20.9832, 105.9232),
    (1, "VOP Gate",      20.9929, 105.9451, "THCS Da Ton",        20.9874, 105.9327),
    (2, "VOP Gate",      20.9929, 105.9451, "Brighton College",   20.9932, 105.9391),
    (3, "VOP Gate",      20.9929, 105.9451, "Tram yt Kieu Ky",   20.9803, 105.9587),
    (4, "VOP Gate",      20.9929, 105.9451, "BV Gia Lam",         21.0094, 105.9440),
    (5, "Da Ton SE",     20.9705, 105.9503, "BV Song Hong",       20.9832, 105.9232),
    (6, "Da Ton SE",     20.9705, 105.9503, "TH Nong nghiep",     21.0045, 105.9386),
    (7, "Kieu Ky NE",   21.0100, 105.9510, "Brighton College",   20.9932, 105.9391),
    (8, "Trau Quy W",   21.0046, 105.9226, "Circle K",           21.0015, 105.9432),
    (9, "Trau Quy W",   21.0046, 105.9226, "BV Gia Lam",         21.0094, 105.9440),
]

def maps_url(olat, olon, dlat, dlon, mode="2"):
    # travelmode: 0=car, 1=transit, 2=walk, 3=bike, 9=motorcycle (not always present)
    # We'll navigate and try to select motorcycle, fall back to car
    return (
        f"https://www.google.com/maps/dir/{olat},{olon}/{dlat},{dlon}/"
        f"@{(olat+dlat)/2},{(olon+dlon)/2},13z/data=!4m2!4m1!3e0"  # 3e0 = driving
    )

def parse_duration_text(text: str) -> float | None:
    """Parse '7 min', '1 hr 5 min', '25 min' -> float minutes."""
    import re
    text = text.strip().lower()
    hr = re.search(r'(\d+)\s*(?:hr|gio|tiếng|h\b)', text)
    mn = re.search(r'(\d+)\s*(?:min|ph)', text)
    if not hr and not mn:
        return None
    return (int(hr.group(1)) * 60 if hr else 0) + (int(mn.group(1)) if mn else 0)

def scrape_pair(page, sid, oname, olat, olon, dname, dlat, dlon) -> dict:
    url = maps_url(olat, olon, dlat, dlon)
    print(f"\n[{sid}] {oname} -> {dname}", flush=True)
    print(f"     URL: {url}", flush=True)

    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(4000)

    result = {
        "sample_id": sid,
        "mode_used": None,
        "minutes": None,
        "raw_text": None,
        "error": None,
    }

    # Try clicking motorcycle mode button (aria-label varies by language)
    moto_selectors = [
        '[data-travel_mode="9"]',          # motorcycle travel mode id
        '[aria-label*="otocycle"]',
        '[aria-label*="xe máy"]',
        '[aria-label*="Motorcycle"]',
        '[data-tooltip*="otorcycle"]',
        'button[jsaction*="travelmode"][data-index="4"]',
    ]
    moto_found = False
    for sel in moto_selectors:
        try:
            btn = page.locator(sel).first
            if btn.count() > 0:
                btn.click(timeout=3000)
                page.wait_for_timeout(2000)
                moto_found = True
                result["mode_used"] = "motorcycle"
                print(f"     Clicked motorcycle mode ({sel})", flush=True)
                break
        except Exception:
            continue

    if not moto_found:
        result["mode_used"] = "car (motorcycle button not found)"
        print(f"     Motorcycle mode not found, using car routing", flush=True)

    # Wait for route card to appear
    page.wait_for_timeout(3000)

    # Try multiple selectors for the travel time
    time_selectors = [
        # route summary card - time text
        '[jstcache] .fontHeadlineSmall',
        'div[data-trip-time]',
        '.section-trip-time span',
        '[aria-label*="min"]',
        # new Maps UI
        'div.UdvAnf span',
        'div.x3AX1-LfntMc-header-title-sTF4bf-header span:first-child',
        '.MespJc .fontBodyMedium',
        # generic: find element containing "min" near route header
        'h1.fontHeadlineSmall',
        '.fontHeadlineSmall',
    ]

    found_text = None
    for sel in time_selectors:
        try:
            els = page.locator(sel).all()
            for el in els:
                txt = el.inner_text(timeout=2000).strip()
                val = parse_duration_text(txt)
                if val is not None and 0 < val < 120:
                    found_text = txt
                    result["minutes"] = val
                    result["raw_text"] = txt
                    break
            if result["minutes"]:
                break
        except Exception:
            continue

    # Fallback: grab all text from page and search for duration pattern
    if result["minutes"] is None:
        import re
        try:
            body = page.inner_text("body", timeout=5000)
            # Find patterns like "7 min", "1 giờ 5 phút"
            matches = re.findall(r'\d+\s*(?:min|ph[uú]t|giờ|hr)', body, re.I)
            for m in matches:
                val = parse_duration_text(m)
                if val and 0 < val < 120:
                    result["minutes"] = val
                    result["raw_text"] = m + " (scraped from body)"
                    break
        except Exception:
            pass

    if result["minutes"]:
        print(f"     -> {result['minutes']} min ({result['raw_text']}) via {result['mode_used']}", flush=True)
    else:
        result["error"] = "could not parse travel time from page"
        print(f"     -> FAILED to parse time", flush=True)
        # Save screenshot for debugging
        try:
            shot = Path(f"outputs/validation/debug_pair_{sid}.png")
            shot.parent.mkdir(exist_ok=True)
            page.screenshot(path=str(shot))
            print(f"     Screenshot: {shot}", flush=True)
        except Exception:
            pass

    return result


def main():
    from playwright.sync_api import sync_playwright

    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--lang=en-US"])
        ctx = browser.new_context(
            locale="en-US",
            timezone_id="Asia/Ho_Chi_Minh",
            viewport={"width": 1280, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
        )
        page = ctx.new_page()

        # Accept cookies / consent if shown
        page.goto("https://www.google.com/maps", wait_until="domcontentloaded", timeout=20000)
        page.wait_for_timeout(2000)
        for sel in ['button[aria-label*="Accept"]', 'button[aria-label*="Agree"]',
                    '#L2AGLb', 'button:has-text("Accept all")', 'button:has-text("I agree")']:
            try:
                btn = page.locator(sel).first
                if btn.count() > 0:
                    btn.click(timeout=2000)
                    print("Dismissed consent dialog", flush=True)
                    page.wait_for_timeout(1500)
                    break
            except Exception:
                pass

        for pair in OD_PAIRS:
            sid, oname, olat, olon, dname, dlat, dlon = pair
            try:
                r = scrape_pair(page, sid, oname, olat, olon, dname, dlat, dlon)
            except Exception as e:
                r = {"sample_id": sid, "mode_used": None, "minutes": None,
                     "raw_text": None, "error": str(e)}
                print(f"[{sid}] EXCEPTION: {e}", flush=True)
            results.append(r)
            time.sleep(1.5)

        browser.close()

    # Print summary
    print("\n" + "="*70, flush=True)
    print(f"{'ID':>2}  {'Origin/Dest':40s}  {'Mode':25s}  {'Min':>5}  {'Raw'}", flush=True)
    print("-"*70, flush=True)
    labels = [(f"{p[1]}->{p[4]}") for p in OD_PAIRS]
    for r, lbl in zip(results, labels):
        mins = f"{r['minutes']:.0f}" if r['minutes'] else "FAIL"
        mode = (r['mode_used'] or "")[:24]
        raw = (r['raw_text'] or r['error'] or "")[:20]
        print(f"{r['sample_id']:>2}  {lbl:40s}  {mode:25s}  {mins:>5}  {raw}", flush=True)

    # Save JSON
    out = Path("outputs/validation/gmaps_scrape_results.json")
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nSaved: {out}", flush=True)
    return 0

if __name__ == "__main__":
    sys.exit(main())
