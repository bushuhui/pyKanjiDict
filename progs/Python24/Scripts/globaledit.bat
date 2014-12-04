@echo off
if NOT "%_4ver%" == "" c:\python24\python.exe -c "from MoinMoin.scripts.globaledit import run; run()" %$
if     "%_4ver%" == "" c:\python24\python.exe -c "from MoinMoin.scripts.globaledit import run; run()" %*
