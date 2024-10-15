@echo off

rem Step 1: Check if venv exists, create and activate it if it doesn't
if not exist "venv" (
    echo Virtual environment not found. Creating one...
    python -m venv venv
    if errorlevel 1 (
        echo Failed to create virtual environment. Exiting...
        exit /b 1
    )
    echo Activating virtual environment...
    call "venv\Scripts\activate"
    echo Installing requirements...
    pip install -r requirements.txt
) else (
    echo Virtual environment found. Activating...
    call "venv\Scripts\activate"
)

rem Step 2: Run the Python script
python qq_music\fetch.py
if errorlevel 1 (
    echo Failed to run the `qq_music\fetch.py` script. Exiting...
    exit /b 1
)

pause