py -m venv venv
cmd /k "venv\Scripts\activate & python -m pip install --upgrade pip & pip install flask & set FLASK_APP=..\scr\app.py & flask run"
pause