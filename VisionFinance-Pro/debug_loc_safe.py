
import sys
import os

sys.path.append(os.getcwd())

try:
    import quant_core.utils.localization as loc
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

keys_to_check = [
    "whale_radar",
    "ytd_warning",
    "backtest_header",
    "settings_header",
    "sidebar_tip"
]

print("--- DIAGNOSTICS ---")
if "English" not in loc.TRANSLATIONS:
    print("CRITICAL: English dictionary missing!")
else:
    print(f"English dict size: {len(loc.TRANSLATIONS['English'])}")

if "Türkçe" not in loc.TRANSLATIONS:
    print("CRITICAL: Türkçe dictionary missing!")
else:
    print(f"Türkçe dict size: {len(loc.TRANSLATIONS['Türkçe'])}")

print("\n--- KEY CHECK (English Fallback) ---")
# Check if key exists in English
for k in keys_to_check:
    in_eng = k in loc.TRANSLATIONS["English"]
    print(f"Key '{k}' in English? {in_eng}")

print("\n--- KEY CHECK (Türkçe) ---")
# Check if key exists in Turkish
for k in keys_to_check:
    if "Türkçe" in loc.TRANSLATIONS:
        in_tr = k in loc.TRANSLATIONS["Türkçe"]
        print(f"Key '{k}' in Türkçe? {in_tr}")

print("\n--- TEST GET_TEXT ---")
try:
    val = loc.get_text("whale_radar", "Türkçe")
    # Print repr to see safe string
    print(f"get_text('whale_radar', 'Türkçe') => {repr(val)}")
except Exception as e:
    print(f"get_text FAILED: {e}")
