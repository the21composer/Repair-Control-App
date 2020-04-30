from flask import Flask, flash, render_template, request, redirect, session
from bson.objectid import ObjectId
from pymodm.connection import connect
from pymongo.write_concern import WriteConcern
from pymodm import EmbeddedMongoModel, MongoModel, fields
from werkzeug.utils import secure_filename
import datetime
import uuid
import functools
import csv
import os

from app_models import User, Equipment, Error, Failure, Repair, Service, Telemetry, Сoefficients

SECRET_KEY = str(uuid.uuid4())
app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['UPLOAD_FOLDER'] = '../data/'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        for us in User.objects.all():
            us.delete()
        User('worker', '1', 'worker').save()
        User('repair_manager', '1', 'repair').save()
        User('site_manager', '1', 'site').save()
        User('foreman', '1', 'foreman').save()
        User('admin', '1', 'admin').save()
        return render_template('index.html', login=session.get('user'))
    else:
        for eq in Equipment.objects.all(): # Deleting old data...
            eq.delete()
        eq1 = Equipment(machineID=1, model='МАтом').save()
        eq2 = Equipment(machineID=2, model='КейсИн').save()
        eq3 = Equipment(machineID=3, model='МАтом').save()
        eq4 = Equipment(machineID=4, model='МАтом').save()
        eq5 = Equipment(machineID=5, model='КейсИн').save()
        eq1.errors.append(Error(time=datetime.datetime(2020, 3, 14, 12, 30), etype="Сбой координат", description="Неверное начальное положение"))
        eq1.errors.append(Error(time=datetime.datetime(2020, 3, 17, 15, 30), etype="Переполнение", description="Перезапущен из-за переполнения"))
        eq1.errors.append(Error(time=datetime.datetime(2020, 4, 9, 11, 00), etype="Сбой координат", description="Неверное начальное положение"))
        eq1.errors.append(Error(time=datetime.datetime(2020, 4, 13, 18, 30), etype="Неверный ввод", description="Ошибка в веденных параметрах"))
        eq1.errors.append(Error(time=datetime.datetime(2020, 4, 13, 14, 20), etype="Перегруз", description="Высокое давление"))
        eq1.telemetry.append(Telemetry(datetime.datetime(2020, 2, 14, 15, 10), 12, 120, 44, 33))
        eq1.telemetry.append(Telemetry(datetime.datetime(2020, 3, 14, 13, 30), 13, 100, 22, 45))
        eq1.telemetry.append(Telemetry(datetime.datetime(2020, 3, 28, 18, 40), 12, 120, 44, 33))
        eq1.telemetry.append(Telemetry(datetime.datetime(2020, 4, 12, 12, 50), 13, 100, 22, 45))
        eq1.telemetry.append(Telemetry(datetime.datetime(2020, 4, 18, 11, 20), 12, 120, 44, 33))
        eq1.telemetry.append(Telemetry(datetime.datetime(2020, 4, 21, 19, 10), 13, 100, 22, 45))
        eq1.failures.append(Failure(time=datetime.datetime(2020, 3, 21, 8, 15), ftype="Ошибка датчика", description="Неверные показания датчика температуры"))
        eq1.failures.append(Failure(time=datetime.datetime(2020, 4, 11, 7, 50), ftype="Падение давления", description="Критическое падение давления в клапане"))
        eq1.services.append(Service(datetime.datetime(2019, 11, 11, 7, 50), "Ремонт датчика", "Ремонт датчика температуры"))
        eq1.services.append(Service(datetime.datetime(2020, 1, 1, 7, 50), "Ремонт клапана", "Давление стабилизировано"))
        eq1.services.append(Service(datetime.datetime(2020, 2, 29, 7, 50), "Ремонт датчика", "Ремонт датчика температуры"))
        eq2.errors.append(Error(time=datetime.datetime(2020, 3, 24, 12, 40), etype="Сбой координат", description="Неверное начальное положение"))
        eq2.errors.append(Error(time=datetime.datetime(2020, 4, 12, 11, 30), etype="Неверный ввод", description="Ошибка в веденных параметрах"))
        eq2.errors.append(Error(time=datetime.datetime(2020, 4, 14, 10, 20), etype="Перегруз", description="Высокое давление"))
        eq2.telemetry.append(Telemetry(datetime.datetime(2020, 2, 14, 15, 10), 24, 120, 44, 53))
        eq2.telemetry.append(Telemetry(datetime.datetime(2020, 3, 14, 13, 30), 25, 100, 22, 45))
        eq2.telemetry.append(Telemetry(datetime.datetime(2020, 3, 28, 18, 40), 24, 120, 44, 49))
        eq2.telemetry.append(Telemetry(datetime.datetime(2020, 4, 12, 12, 50), 24, 100, 22, 55))
        eq2.telemetry.append(Telemetry(datetime.datetime(2020, 4, 18, 11, 20), 24, 120, 44, 63))
        eq2.telemetry.append(Telemetry(datetime.datetime(2020, 4, 21, 19, 10), 23, 100, 22, 55))
        eq2.services.append(Service(datetime.datetime(2019, 11, 11, 7, 50), "Ремонт датчика", "Ремонт датчика температуры"))
        eq2.services.append(Service(datetime.datetime(2020, 1, 1, 7, 50), "Ремонт клапана", "Давление стабилизировано"))
        eq2.services.append(Service(datetime.datetime(2020, 2, 29, 7, 50), "Ремонт датчика", "Ремонт датчика температуры"))
        eq1.save()
        eq2.save()
        Сoefficients(20).save()
        return render_template('index.html', login=session.get('user'), message='Тестовые данные загружены!')


def logged_in(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if 'user' not in session:
            return redirect('/login')
        if session['objects'] != func.__name__:
            return redirect('/')
        return func(*args, **kwargs)
    return wrapper

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if session.get('user'):
            return redirect(session['objects'])
        else:
            return render_template('login.html')
    else:
        try:
            user = User.objects.get({'_id': request.form['loginIn'], 'password': request.form['passwordIn']})
        except User.DoesNotExist:
            return render_template('login.html', error='Неверный логин или пароль')
        else:
            session['user'] = user.login
            session['objects'] = user.role
        return redirect(user.role)

@app.route('/worker', methods=['GET', 'POST'])
@logged_in
def worker():
    if request.method == 'GET':
        return render_template('worker.html', Repair=Repair, login=session['user'])
    else:
        repID = request.form.get('ID')
        repair = Repair.objects.get({'_id':  ObjectId(repID)})
        if request.form[repID] == '0':
            repair.completed = False
            repair.in_progress = False
        elif request.form[repID] == '1':
            repair.in_progress = True
        else:
            repair.completed = True
        repair.save()
        return render_template('worker.html', Repair=Repair, login=session['user'])

@app.route('/site', methods=['GET', 'POST'])
@logged_in
def site():
    if request.method == 'GET':
        # Example of some data
        for eq in Equipment.objects.all():
            Tsum = 0
            Tmiddle = 0.0
            Qm = 0
            timenow = datetime.datetime.now()
            if (eq.services):
                for q in range(len(eq.services)):
                    if q != 0:
                        tdelta = eq.services[q].time - eq.services[q-1].time
                        Tsum += tdelta.total_seconds()
                Tmiddle = Tsum / len(eq.services)
            if (Tmiddle):
                if (eq.errors):
                    for q in eq.errors:
                        past = timenow - q.time
                        if (past.total_seconds() < 31*24*60*60):
                            Qm += 1
                if (eq.failures):
                    for q in eq.failures:
                        past =  timenow - q.time
                        if (past.total_seconds() < 31*24*60*60):
                            Qm += 5
                days_to_repair = Tmiddle/(24*60*60)*(1-Qm/Сoefficients.objects[0].to_repair)
            else:
                days_to_repair = -1
            eq.repair_predict = days_to_repair
            eq.save()

        # Created 2 Equipments with some errors and 2 Equipments without
        return render_template('site_manager.html', Equipment=Equipment, login=session['user'])
    else:
        rep = Repair(machineID=request.form.get('id'), rtype=request.form.get('type'), description=request.form.get('message')).save()
        rep.in_progress = False
        rep.completed = False
        return render_template('site_manager.html', Equipment=Equipment, login=session['user'])

@app.route('/repair', methods=['GET', 'POST'])
@logged_in
def repair():
    if request.method == 'GET':
        return render_template('repair_manager.html',  Repair=Repair, login=session['user'])
    else:
        if (request.form.get('ID')):
            try:
                repID = request.form.get('ID')
                repair = Repair.objects.get({'_id':  ObjectId(repID)})
                repair.deadline = datetime.datetime.strptime(request.form[repID], '%d.%m.%Y %H:%M')
                repair.save()
            except:
                return render_template('repair_manager.html',  Repair=Repair, login=session['user'], error='Неверный формат даты. Должен быть: д.м.г чч:мм')
        else:
            repID = request.form.get('closeID')
            repair = Repair.objects.get({'_id':  ObjectId(repID)})
            eq = Equipment.objects.get({'machineID': repair.machineID})
            print(eq.machineID)
            eq.services.append(Service(time=datetime.datetime.now(), stype=repair.rtype, description=repair.description))
            eq.save()
            print("saved")
            repair.delete()
            return render_template('repair_manager.html',  Repair=Repair, login=session['user'])
        return render_template('repair_manager.html',  Repair=Repair, login=session['user'])

@app.route('/foreman')
@logged_in
def foreman():
    return render_template('foreman.html', Equipment=Equipment, login=session['user']) 

@app.route('/admin', methods=['GET', 'POST'])
@logged_in
def admin():
    if request.method == 'GET':
        return render_template('admin.html', login=session['user'])
    else:
        for eq in Equipment.objects.all(): # Deleting old data...
            eq.delete()
        for repair in Repair.objects.all(): #iterator?
            repair.delete()
        return render_template('admin.html', login=session['user'], message='Успех')

@app.route('/admin/files', methods=['GET', 'POST'])
def files():
    if request.method == 'GET':
        #тут будет скачка файлов
        return render_template('files.html', login=session['user'])
    else:
        if 'file' in request.files:
            file = request.files['file']
            if file:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                if request.form.get('type') == '1':
                    errfile = open(app.config['UPLOAD_FOLDER']+filename, encoding='UTF-8')
                    errreader = csv.reader(errfile, delimiter=',')
                    for i in list(errreader):
                        try:
                            eq = Equipment.objects.get({'machineID': int(i[1])})
                            eq.errors.append(Error(time=datetime.datetime.strptime(i[0], '%Y-%m-%d %H:%M:%S'), etype=i[2], description="Нет описания"))
                            eq.save()
                        except ValueError:
                            continue
                elif request.form.get('type') == '2':
                    failfile = open(app.config['UPLOAD_FOLDER']+filename, encoding='UTF-8')
                    failreader = csv.reader(failfile, delimiter=',')
                    for i in list(failreader):
                        try:
                            eq = Equipment.objects.get({'machineID': int(i[1])})
                            eq.failures.append(Failure(time=datetime.datetime.strptime(i[0], '%Y-%m-%d %H:%M:%S'), ftype=i[2], description="Нет описания"))
                            eq.save()
                        except ValueError:
                            continue
                elif request.form.get('type') == '3':
                    repfile = open(app.config['UPLOAD_FOLDER']+filename, encoding='UTF-8')
                    repreader = csv.reader(repfile, delimiter=',')
                    for i in list(repreader):
                        try:
                            eq = Equipment.objects.get({'machineID': int(i[1])})
                            eq.services.append(Service(time=datetime.datetime.strptime(i[0], '%Y-%m-%d %H:%M:%S'), stype=i[2], description="Нет описания"))
                            eq.save()
                        except ValueError:
                            continue
                elif request.form.get('type') == '4':
                    for eq in Equipment.objects.all(): # Deleting old data...
                        eq.delete()
                    eqfile = open(app.config['UPLOAD_FOLDER']+filename, encoding='UTF-8')
                    eqreader = csv.reader(eqfile, delimiter=',')
                    for i in list(eqreader):
                        try:
                            q = Equipment(machineID=int(i[0]), model=i[1]).save()
                        except ValueError:
                            continue
            return render_template('files.html', login=session['user'], message='Файл успешно загружен')
        return render_template('files.html', login=session['user'], message='Ошибка, недопустимый файл')

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('objects', None)
    flash('You have been successfully logged out.')
    return redirect('/')

def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()