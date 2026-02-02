import shutil
import os

src = r"c:/Users/Efe/.gemini/antigravity/scratch/financial_analyst"
dst = r"c:/Users/Efe/Desktop/VisionFinance-Pro"

# Custom check to skip .git and other hidden folders
def ignore_patterns(path, names):
    return [n for n in names if n.startswith(".") or n == "__pycache__" or n == "venv" or n.endswith(".pyc") or n == "raw"]

if os.path.exists(dst):
    print(f"Klasör zaten var, temizleniyor: {dst}")
    try:
        shutil.rmtree(dst)
    except Exception as e:
        print(f"Hata: {e}")

print(f"Kopyalanıyor: {src} -> {dst}")
shutil.copytree(src, dst, ignore=ignore_patterns)
print("ISLEM TAMAM! Dosyalar masaustune aktarildi.")
