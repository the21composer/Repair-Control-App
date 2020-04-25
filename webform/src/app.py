from flask import Flask, flash, render_template, request, redirect, session
from bson.objectid import ObjectId
from pymodm.connection import connect
from pymongo.write_concern import WriteConcern
from pymodm import EmbeddedMongoModel, MongoModel, fields
import datetime
import uuid
import functools
import csv

from app_models import User, Equipment, Error, Failure, Repair, Service, Telemetry

SECRET_KEY = str(uuid.uuid4())
app = Flask(__name__)
app.secret_key = SECRET_KEY

@app.route('/')
def index():
    for us in User.objects.all():
        us.delete()
    User('worker', '1', 'worker').save()
    User('repair_manager', '1', 'repair').save()
    User('site_manager', '1', 'site').save()
    User('foreman', '1', 'foreman').save()
    User('admin', '1', 'admin').save()
    return render_template('index.html', login=session.get('user'))


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
        eqfile = open('../data/equipment.csv', encoding='UTF-8')
        eqreader = csv.reader(eqfile, delimiter=',')
        for i in list(eqreader):
            try:
                eq = Equipment(machineID=int(i[0]), model=i[1]).save()
            except ValueError:
                continue
        errfile = open('../data/errors.csv', encoding='UTF-8')
        errreader = csv.reader(errfile, delimiter=',')
        for i in list(errreader):
            try:
                eq = Equipment.objects.get({'machineID': int(i[1])})
                eq.errors.append(Error(time=datetime.datetime.strptime(i[0], '%Y-%m-%d %H:%M:%S'), etype=i[2], description="Нет описания"))
                eq.save()
            except ValueError:
                continue
        failfile = open('../data/failures.csv', encoding='UTF-8')
        failreader = csv.reader(failfile, delimiter=',')
        for i in list(failreader):
            try:
                eq = Equipment.objects.get({'machineID': int(i[1])})
                eq.failures.append(Failure(time=datetime.datetime.strptime(i[0], '%Y-%m-%d %H:%M:%S'), ftype=i[2], description="Нет описания"))
                eq.save()
            except ValueError:
                continue
        repfile = open('../data/repair.csv', encoding='UTF-8')
        repreader = csv.reader(repfile, delimiter=',')
        for i in list(repreader):
            try:
                eq = Equipment.objects.get({'machineID': int(i[1])})
                eq.services.append(Service(time=datetime.datetime.strptime(i[0], '%Y-%m-%d %H:%M:%S'), stype=i[2], description="Нет описания"))
                eq.save()
            except ValueError:
                continue
        # telfile = open('../data/telemetry.csv', encoding='UTF-8')
        # telfile = csv.reader(telfile, delimiter=',')
        # for i in list(telfile):
        #     try:
        #         eq = Equipment.objects.get({'machineID': int(i[1])})
        #         eq.telemetry.append(Telemetry(datetime.datetime.strptime(i[0], '%Y-%m-%d %H:%M:%S'), int(i[2]), int(i[3]), int(i[4]), int(i[5])))
        #         eq.save()
        #     except ValueError:
        #         continue
        return render_template('files.html', login=session['user'], message='Успех')

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