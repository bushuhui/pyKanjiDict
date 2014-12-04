path=%cd%\progs\python24;%cd%\progs\python24\dlls;%cd%\progs\mysql\bin;%path%
set REDIRECT_STATUS=CGI
set ROOT_DIR=%cd%
set PYTHONPATH=%cd%\lib
set MYSQL_ROOT=%cd%\progs\mysql
progs\Python24\python.exe lib\pyhttpd.py %1
