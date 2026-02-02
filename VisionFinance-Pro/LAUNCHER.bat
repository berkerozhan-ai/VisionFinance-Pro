@echo off
:: Finansal Gemi Launcher
:: Bu dosya projenin bulundugu klasore gider ve dashboard'u baslatir.

echo ---------------------------------------------------
echo   FINANSAL GEMI PRO - BASLATILIYOR 🚀
echo ---------------------------------------------------
echo.

:: 1. Proje klasorune git (Nerede olursaniz olun buraya doner)
cd /d "c:\Users\Efe\.gemini\antigravity\scratch\financial_analyst"

:: 2. Gerekli kutuphaneleri kontrol et (Opsiyonel, hiz icin atlaniyor)

:: 3. Uygulamayi baslat
echo Uygulama aciliyor... Lutfen bekleyin...
echo Tarayiciniz otomatik acilacaktir.
echo.
echo Link: http://localhost:8502
echo.

streamlit run dashboard.py --server.port 8502

:: 4. Hata olursa ekrani kapatma
if %errorlevel% neq 0 (
    echo.
    echo BIR HATA OLUSTU!
    pause
)
