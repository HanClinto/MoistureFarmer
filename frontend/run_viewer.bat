@echo off
echo Installing dependencies...
pip install -r requirements.txt

echo Starting TMX Viewer...
python tmx_viewer.py
pause
