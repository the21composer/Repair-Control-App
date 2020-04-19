from flask import Flask
from flask import render_template
from pymodm.connection import connect
from pymongo.write_concern import WriteConcern
from pymodm import EmbeddedMongoModel, MongoModel, fields
import datetime

# Connect to MongoDB and call the connection "my-app".
connect("mongodb://localhost:27017/myDatabase", alias="my-app")

class Error(EmbeddedMongoModel):
    time = fields.DateTimeField()
    errorID = fields.IntegerField()
    description = fields.CharField()
    class Meta:
        write_concern = WriteConcern(j=True)
        connection_alias = 'my-app'

class Equipment(MongoModel):
    machineID = fields.IntegerField()
    model = fields.CharField()
    revised_on = fields.DateTimeField()
    errors = fields.EmbeddedDocumentListField(Error)
    class Meta:
        write_concern = WriteConcern(j=True)
        connection_alias = 'my-app'

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/worker')
def worker():
    return render_template('worker.html')

@app.route('/site')
def site():
    # Example of some data
    for eq in Equipment.objects.all(): # Deleting old data...
        eq.delete()
    eq1 = Equipment(machineID=1, model='MODEL1').save()
    eq2 = Equipment(machineID=2, model='MODEL5').save()
    eq1.errors.append(Error(time=datetime.datetime.now(), errorID=1, description="ERROR1"))
    eq1.errors.append(Error(time=datetime.datetime.now(), errorID=2, description="ERROR4"))
    eq2.errors.append(Error(time=datetime.datetime.now(), errorID=112, description="MYSTERY"))
    eq1.save()
    eq2.save()
    Equipment(machineID=3, model='NOERR').save()
    Equipment(machineID=4, model='NOERR').save()
    # Created 2 Equipments with some errors and 2 Equipments without
    return render_template('site_manager.html', Equipment=Equipment)

@app.route('/repair')
def repair():
    return render_template('repair_manager.html')

@app.route('/foreman')
def foreman():
    return render_template('foreman.html') 