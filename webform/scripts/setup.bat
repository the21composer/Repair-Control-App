py -m venv venv
cmd /k "venv\Scripts\activate & python -m pip install --upgrade pip & pip install flask & pip install pymodm & set FLASK_APP=..\src\app.py & flask run"
pause
