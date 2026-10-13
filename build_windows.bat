@echo off
setlocal

echo ===============================
echo Building PathoImage Toolkit
echo ===============================

REM Activate venv when present.
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo WARNING: venv not found. Using current Python environment.
)

REM Verify the build is using the expected dependency stack.
python -c "import sys, imagecodecs, zarr, bioio, bioio_bioformats, scyjava, jpype; print('Python:', sys.executable); print('BioIO:', bioio.__version__); print('Zarr:', zarr.__version__); print('BioIO Bio-Formats import: OK')"
python -c "from importlib.metadata import version; print('BioIO metadata:', version('bioio')); print('bioio-bioformats metadata:', version('bioio-bioformats')); print('scyjava metadata:', version('scyjava'))"
if errorlevel 1 (
    echo.
    echo ERROR: Required dependencies are missing from this Python environment.
    echo Run: python -m pip install -r requirements.txt
    pause
    exit /b 1
)

REM Clean previous builds.
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Build using the repository spec file and the active Python environment.
python -m PyInstaller --clean --noconfirm PathoImageToolkit.spec
if errorlevel 1 (
    echo ===============================
    echo BUILD FAILED
    echo ===============================
    pause
    exit /b 1
)

echo ===============================
echo BUILD COMPLETE
echo Output in dist

echo NOTE: VSI support uses BioIO/Bio-Formats and provisions a Zulu JDK 17 runtime on first use.
echo The first VSI open may therefore require an internet connection.
echo ===============================

pause
endlocal
