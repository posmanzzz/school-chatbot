@echo off
ECHO ==================================================
ECHO  Docker Container Rebuild Script
ECHO ==================================================
ECHO.
ECHO Stopping and removing existing containers...
docker-compose down
IF %ERRORLEVEL% NEQ 0 (
    ECHO Failed to stop containers.
    PAUSE
    EXIT /B 1
)

ECHO.
ECHO Rebuilding and starting containers...
docker-compose up --build
IF %ERRORLEVEL% NEQ 0 (
    ECHO Failed to build and start containers.
    PAUSE
    EXIT /B 1
)

ECHO.
ECHO ==================================================
ECHO  Process complete! The application is running.
ECHO ==================================================
ECHO.
PAUSE
