sudo apt-get install python3-venv
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install flask
pip install pymodm
export FLASK_APP=../src/app.py
flask run
