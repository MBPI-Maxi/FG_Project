@echo off

REM Run Django Commands

echo Making Migrations...
python manage.py makemigrations
echo.

echo Applying Migrations...
python manage.py migrate
echo.

echo Starting Development Server...
python manage.py runserver
echo.