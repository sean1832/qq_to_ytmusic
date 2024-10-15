@echo off

rem Step 1: Check if venv exists, create and activate it if it doesn't
if not exist "venv" (
    echo Virtual environment not found. Creating one...
    python -m venv venv
    if errorlevel 1 (
        echo Failed to create virtual environment. Exiting...
    )
    echo Activating virtual environment...
    call "venv\Scripts\activate"
    echo Installing requirements...
    pip install -r requirements.txt
) else (
    echo Virtual environment found. Activating...
    call "venv\Scripts\activate"
)

rem Step 2: Check if oauth.json exists, call ytmusicapi oauth if it doesn't
if not exist "oauth.json" (
    echo oauth.json not found. Running ytmusicapi oauth...
    ytmusicapi oauth
    if errorlevel 1 (
        echo Failed to complete oauth setup. Exiting...
    )
) else (
    echo oauth.json found. Skipping oauth setup...
)

rem Step 3: Run the Python script
python youtube_music\main.py
if errorlevel 1 (
    echo Failed to run the youtube_music\main.py script. Exiting...
    
)

echo Script completed successfully.

pause