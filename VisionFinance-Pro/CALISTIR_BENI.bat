@echo off
echo ===================================================
echo   FINANSAL GEMI PRO - BASLATILIYOR 🚀
echo ===================================================
echo.
echo Gerekli kutuphaneler kontrol ediliyor...
pip install -r requirements.txt
echo.
echo Uygulama aciliyor... Lutfen bekleyin...
echo Tarayiciniz 5 saniye icinde otomatik acilacaktir.
echo.
echo Eger acilmazsa su adrese tiklayin: http://localhost:8501
echo.
echo ===================================================
streamlit run dashboard.py
pause
