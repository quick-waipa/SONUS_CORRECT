#!/bin/bash
echo "Installing required libraries for SONUS CORRECT..."

if command -v python3 >/dev/null 2>&1; then
    python3 -m pip install --upgrade pip
    python3 -m pip install pandas pyyaml ttkthemes numpy matplotlib scipy
    echo "Installation complete."
    exit 0
fi

if command -v py >/dev/null 2>&1; then
    py -m pip install --upgrade pip
    py -m pip install pandas pyyaml ttkthemes numpy matplotlib scipy
    echo "Installation complete."
    exit 0
fi

if command -v python >/dev/null 2>&1; then
    python -m pip install --upgrade pip
    python -m pip install pandas pyyaml ttkthemes numpy matplotlib scipy
    echo "Installation complete."
    exit 0
fi

echo "Python not found."
exit 1
