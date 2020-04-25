py -m venv venv
cmd /k "venv\Scripts\activate & set FLASK_APP=..\src\app.py & flask run"
pause
