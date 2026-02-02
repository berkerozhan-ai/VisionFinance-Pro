@echo off
echo Debugging Launch...
echo.
echo 1. Killing old processes...
taskkill /F /IM streamlit.exe >nul 2>&1
taskkill /F /IM python.exe >nul 2>&1
echo.
echo 2. Installing NLTK Data (Crucial for TextBlob)...
python -m textblob.download_corpora
echo.
echo 3. Validating Imports...
python -c "import streamlit; import feedparser; import textblob; print('Libraries OK')"
if %errorlevel% neq 0 (
    echo LIBRARY ERROR!
    pause
    exit /b
)
echo.
echo 4. Starting Streamlit (Port 8501)...
streamlit run dashboard.py --server.port 8501 --server.address localhost
pause
