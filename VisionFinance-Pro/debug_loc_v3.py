
import sys
import os

# Ensure path is correct
sys.path.append(os.getcwd())

try:
    import quant_core.utils.localization as loc
    print("DEBUG: Module imported successfully:", loc)
    print("DEBUG: loc file:", loc.__file__)
except Exception as e:
    print("DEBUG: Import failed:", e)
    sys.exit(1)

keys_to_check = [
    "ytd_warning",
    "whale_radar",
    "backtest_header",
    "settings_header",
    "robo_header",
    "sidebar_tip"
]

lang = "Türkçe"

print(f"--- Checking keys for language: {lang} ---")
for k in keys_to_check:
    val = loc.get_text(k, lang)
    print(f"Key: '{k}' -> Value: '{val}'")
    if val == k:
        print(f"!!! FAIL: Key {k} returned itself (raw key) !!!")
    else:
        print(f"PASS: Key {k} resolved correctly.")

print("--- Checking TRANSLATIONS dict structure ---")
if "Türkçe" in loc.TRANSLATIONS:
    print("Türkçe dict exists.")
    print("Keys in Türkçe:", list(loc.TRANSLATIONS["Türkçe"].keys())[:5], "...")
else:
    print("ERROR: Türkçe dict MISSING in TRANSLATIONS")
