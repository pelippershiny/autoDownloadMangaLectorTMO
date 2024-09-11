@echo off
REM Verificar si pip está instalado y si no, instalarlo
python -m ensurepip --default-pip

REM Instalar los módulos necesarios desde requirements.txt
pip install -r requirements.txt

REM Ejecutar el script get_manga.py y mostrar la salida en la consola
python get_manga.py

REM Pausar para que la ventana de la consola no se cierre inmediatamente
pause
