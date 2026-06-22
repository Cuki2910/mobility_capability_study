"""Open manual validation OD pairs in Google Maps on an Android emulator.

This is a workflow helper only. It does not scrape Google Maps and does not
write measured motorcycle times; those must be read from the Android UI.
"""
from __future__ import annotations

import argparse
import csv
import os
import subprocess
import sys
import time
from pathlib import Path


DEFAULT_CSV = Path("outputs/validation/manual_motorcycle_validation_template.csv")
DEFAULT_AVD = "mobility_maps_api36"


def sdk_root() -> Path:
    root = os.environ.get("ANDROID_SDK_ROOT") or os.environ.get("ANDROID_HOME")
    if root:
        return Path(root)
    return Path.home() / "AppData" / "Local" / "Android" / "Sdk"


def adb_path() -> Path:
    return sdk_root() / "platform-tools" / "adb.exe"


def emulator_path() -> Path:
    return sdk_root() / "emulator" / "emulator.exe"


def run(cmd: list[str], check: bool = True, capture: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=check, text=True, capture_output=capture)


def load_pair(csv_path: Path, sample_id: str) -> dict[str, str]:
    with csv_path.open(newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        if str(row.get("sample_id", "")) == str(sample_id):
            return row
    raise SystemExit(f"sample_id not found: {sample_id}")


def maps_url(row: dict[str, str], mode: str) -> str:
    base = row.get("google_maps_directions_url") or ""
    if base and mode == "driving":
        return base
    origin = f"{row['origin_lat']},{row['origin_lon']}"
    dest = f"{row['destination_lat']},{row['destination_lon']}"
    return (
        "https://www.google.com/maps/dir/?api=1"
        f"&origin={origin}&destination={dest}&travelmode={mode}"
    )


def start_emulator(avd: str) -> None:
    subprocess.Popen(
        [str(emulator_path()), "-avd", avd, "-netdelay", "none", "-netspeed", "full"],
        cwd=str(emulator_path().parent),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def wait_for_device(timeout_s: int) -> None:
    deadline = time.time() + timeout_s
    adb = str(adb_path())
    while time.time() < deadline:
        out = run([adb, "devices"], check=False, capture=True).stdout
        if "\tdevice" in out:
            for _ in range(60):
                boot = run([adb, "shell", "getprop", "sys.boot_completed"], check=False, capture=True).stdout.strip()
                if boot == "1":
                    return
                time.sleep(2)
        time.sleep(3)
    raise SystemExit("emulator did not become ready before timeout")


def open_url(url: str) -> None:
    adb = str(adb_path())
    run([adb, "shell", "am", "force-stop", "com.google.android.apps.maps"], check=False)
    time.sleep(1)
    # Quote the URL for the device shell; otherwise & splits the command.
    run([adb, "shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", f"'{url}'"])


def screenshot(path: Path) -> None:
    adb = str(adb_path())
    remote = "/sdcard/mobility_maps_screenshot.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    run([adb, "shell", "screencap", "-p", remote])
    run([adb, "pull", remote, str(path)])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--sample-id", default="0")
    parser.add_argument("--avd", default=DEFAULT_AVD)
    parser.add_argument("--start", action="store_true", help="start the emulator before opening Maps")
    parser.add_argument("--wait", type=int, default=180, help="seconds to wait for emulator boot")
    parser.add_argument("--mode", default="driving", choices=["driving", "two-wheeler", "walking", "bicycling", "transit"])
    parser.add_argument("--screenshot", type=Path)
    args = parser.parse_args(argv)

    if args.start:
        start_emulator(args.avd)
    wait_for_device(args.wait)

    row = load_pair(args.csv, args.sample_id)
    url = maps_url(row, args.mode)
    open_url(url)
    print(f"opened sample_id={args.sample_id}: {row['origin_name']} -> {row['destination_name']}")
    print(url)

    if args.screenshot:
        time.sleep(12)
        screenshot(args.screenshot)
        print(f"screenshot: {args.screenshot}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
