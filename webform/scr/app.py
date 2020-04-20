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
    
class Failure(EmbeddedMongoModel):
    time = fields.DateTimeField()
    failureID = fields.IntegerField()
    description = fields.CharField()
    class Meta:
        write_concern = WriteConcern(j=True)
        connection_alias = 'my-app'

class Repair(MongoModel):
    deadline = fields.DateTimeField()
    machineID = fields.IntegerField()
    repairID = fields.IntegerField()
    description = fields.CharField()
    in_progress = fields.BooleanField()
    completed = fields.BooleanField()
    class Meta:
        write_concern = WriteConcern(j=True)
        connection_alias = 'my-app'

class Equipment(MongoModel):
    machineID = fields.IntegerField()
    model = fields.CharField()
    revised_on = fields.DateTimeField()
    errors = fields.EmbeddedDocumentListField(Error)
    failures = fields.EmbeddedDocumentListField(Failure)
    class Meta:
        write_concern = WriteConcern(j=True)
        connection_alias = 'my-app'

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/worker')
def worker():
    for repair in Repair.objects.all(): #iterator?
        repair.delete()
    Repair(datetime.datetime.now(), 3, 5, "Small repair", False, False).save()
    Repair(datetime.datetime.now(), 2, 4, "Wonderful repair", True, False).save()
    Repair(datetime.datetime.now(), 1, 666, "Cute repair", True, False).save()
    Repair(datetime.datetime.now(), 3, 333, "I wanna live", False, False).save()
    Repair(datetime.datetime.now(), 2, 222, "I am tired of writing descriptions", False, True).save()
    Repair(datetime.datetime.now(), 1, 123, "Ok?", False, True).save()
    return render_template('worker.html', Repair=Repair)

@app.route('/site')
def site():
    # Example of some data
    for eq in Equipment.objects.all(): # Deleting old data...
        eq.delete()
    eq1 = Equipment(machineID=1, model='MODEL1').save()
    eq2 = Equipment(machineID=2, model='MODEL5').save()
    eq1.errors.append(Error(time=datetime.datetime.now(), errorID=1, description="ERROR1"))
    eq1.errors.append(Error(time=datetime.datetime.now(), errorID=2, description="ERROR4"))
    eq1.failures.append(Failure(time=datetime.datetime.now(), failureID=5, description="FAILURETYPE5"))
    eq1.failures.append(Failure(time=datetime.datetime.now(), failureID=2, description="FAILURETYPE2"))
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