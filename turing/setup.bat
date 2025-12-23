SET "venv=%CD%\django_venv"

IF NOT EXIST "%venv%" (
    py -m venv "%venv%"
    IF ERRORLEVEL 1 python3 -m venv "%venv%"
    REM The above line is here because Python's app from Microsoft's store does not ship with py (sigh)
    CALL "%venv%\Scripts\activate.bat"
    python -m pip install --upgrade pip
    pip install -r requirements.txt

    copy Turing\settings.ini.example Turing\settings.ini

    python manage.py makemigrations
    python manage.py makemigrations engine
    python manage.py migrate
    SET "admin-command=from django.contrib.auth import get_user_model; get_user_model().objects.create_superuser('admin', '', 'admin')"
    ECHO %%admin-command%% | python manage.py shell
) ELSE (
    CALL "%venv%\Scripts\activate.bat"
)

python manage.py runserver --insecure 0.0.0.0:8000
