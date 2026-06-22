# Android Emulator Status for Motorcycle Spot-Check

Date: 2026-06-22

## Installed

- Android SDK command-line tools: `19.0`
- Platform tools: `adb 37.0.0`
- Emulator: `36.6.11.0`
- AVD: `mobility_maps_api36`
- System image: `system-images;android-36;google_apis_playstore;x86_64`
- Google Maps package present: `com.google.android.apps.maps`
- Google Maps version observed: `25.11.01.735126028`

## Result

- Emulator boots and Google Maps opens OD directions from `outputs/validation/manual_motorcycle_validation_template.csv`.
- OD 0 was opened successfully with quoted Google Maps URL.
- Google Maps on this AVD exposed Drive, Transit, Walk, and Bicycle modes, but not a Motorcycle / Two-wheeler mode.
- A `travelmode=two-wheeler` deep link was tested and still opened Drive mode.

## Evidence

- `outputs/validation/emulator_maps_od1_route2.png`: OD 0 opened in Drive mode.
- `outputs/validation/emulator_maps_od1_twowheeler.png`: `two-wheeler` deep link still opened Drive mode.

## Caveat

Do not fill `google_maps_android_minutes` from this emulator run. The Android emulator is installed and usable for route opening, but this AVD does not currently provide a motorcycle-mode measurement. The validation remains a physical Android Google Maps task unless a Google Maps build/account/region setup exposes Motorcycle mode.

## Helper

Open OD 0 and save screenshot:

```powershell
python scripts/android_maps_emulator.py --sample-id 0 --mode driving --screenshot outputs/validation/emulator_maps_od0.png
```

Try the two-wheeler deep link:

```powershell
python scripts/android_maps_emulator.py --sample-id 0 --mode two-wheeler --screenshot outputs/validation/emulator_maps_od0_twowheeler.png
```
