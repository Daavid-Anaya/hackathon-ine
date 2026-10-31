@echo off
setlocal
set "PUBLISHED_PORT="
for /f "delims=" %%P in ('docker compose --project-directory "%~dp0..\.." --file "%~dp0..\..\compose.yaml" port web 8080') do set "PUBLISHED_PORT=%%P"
if not "%PUBLISHED_PORT%"=="127.0.0.1:4321" (
  echo ERROR: Docker debe publicar la web en 127.0.0.1:4321; se obtuvo %PUBLISHED_PORT%
  exit /b 1
)
powershell.exe -NoProfile -Command "$ErrorActionPreference = 'Stop'; $response = Invoke-WebRequest -UseBasicParsing -Uri 'http://127.0.0.1:4321/' -TimeoutSec 10; if ($response.StatusCode -ne 200 -or $response.Content -notmatch 'Demostrador institucional') { throw 'Respuesta HTTP inesperada desde el equipo' }; 'CORRECTO: puerto local de Docker y acceso HTTP desde el equipo'"
exit /b %errorlevel%
