py -m venv venv
cmd /k "venv\Scripts\activate & set FLASK_APP=..\scr\app.py & flask run"
pause