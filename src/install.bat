@echo off
echo Installing required libraries for SONUS CORRECT...
where py >nul 2>&1
if %errorlevel%==0 (
    py -m pip install pandas pyyaml ttkthemes numpy matplotlib scipy
    echo Installation complete.
    goto end
)

where python >nul 2>&1
if %errorlevel%==0 (
    python -m pip install pandas pyyaml ttkthemes numpy matplotlib scipy
    echo Installation complete.
    goto end
)

echo Do not find Python.
:end
