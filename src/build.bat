pip install pyinstaller
pyinstaller .\SonusCorrect.py -F --icon=ico.ico --hidden-import=tkinter
move /Y .\dist\SonusCorrect.exe .\
rmdir /S /Q dist

echo build complete.