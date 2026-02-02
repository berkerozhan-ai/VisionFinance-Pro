
import sys
import os

# Add local dir to path
sys.path.append(os.getcwd())

try:
    from quant_core.utils.localization import TRANSLATIONS, get_text
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

print("--- DEBUG LOCALIZATION ---")
print(f"Keys in English: {len(TRANSLATIONS.get('English', {}))}")
print(f"threshold_info in English: {'threshold_info' in TRANSLATIONS['English']}")
if 'threshold_info' in TRANSLATIONS['English']:
    print(f"Value: {TRANSLATIONS['English']['threshold_info']}")
else:
    print("MISSING: threshold_info")

print(f"risk_mgmt in English: {'risk_mgmt' in TRANSLATIONS['English']}")
print(f"stop_loss in English: {'stop_loss' in TRANSLATIONS['English']}")

print("--- GET TEXT TEST ---")
print(f"get_text('threshold_info'): {get_text('threshold_info', 'English')}")
