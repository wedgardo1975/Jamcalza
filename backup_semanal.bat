@echo off
for /f "tokens=2 delims==" %%i in ('wmic os get localdatetime /value') do set dt=%%i
set FECHA=%dt:~0,4%-%dt:~4,2%-%dt:~6,2%

aws s3 cp s3://jamcalza-store-imagenes/data/catalog.json s3://jamcalza-store-imagenes/backups/catalog-%FECHA%.json

echo Backup del %FECHA% completado.
