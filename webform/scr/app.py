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
    etype = fields.CharField()
    description = fields.CharField()
    class Meta:
        write_concern = WriteConcern(j=True)
        connection_alias = 'my-app'
    
class Failure(EmbeddedMongoModel):
    time = fields.DateTimeField()
    ftype = fields.CharField()
    description = fields.CharField()
    class Meta:
        write_concern = WriteConcern(j=True)
        connection_alias = 'my-app'

class Repair(MongoModel):
    deadline = fields.DateTimeField()
    machineID = fields.IntegerField()
    rtype = fields.CharField()
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
    Repair(datetime.datetime.now(), 3, "rep_5", "Small repair", False, False).save()
    Repair(datetime.datetime.now(), 2, "rep_4", "Wonderful repair", True, False).save()
    Repair(datetime.datetime.now(), 1, "rep_777", "Cute repair", True, False).save()
    Repair(datetime.datetime.now(), 3, "rep_333", "I wanna live", False, False).save()
    Repair(datetime.datetime.now(), 2, "rep_222", "I am tired of writing descriptions", False, True).save()
    Repair(datetime.datetime.now(), 1, "rep_123", "Ok?", False, True).save()
    return render_template('worker.html', Repair=Repair)

@app.route('/site')
def site():
    # Example of some data
    for eq in Equipment.objects.all(): # Deleting old data...
        eq.delete()
    eq1 = Equipment(machineID=1, model='MODEL1').save()
    eq2 = Equipment(machineID=2, model='MODEL5').save()
    eq1.errors.append(Error(time=datetime.datetime.now(), etype="WRONG_INPUT", description="ERROR1"))
    eq1.errors.append(Error(time=datetime.datetime.now(), etype="OUT_OF_TIME", description="ERROR4"))
    eq1.failures.append(Failure(time=datetime.datetime.now(), ftype="OVERPOWER", description="FAILURETYPE5"))
    eq1.failures.append(Failure(time=datetime.datetime.now(), ftype="POWER_LOSS", description="FAILURETYPE2"))
    eq2.errors.append(Error(time=datetime.datetime.now(), etype="unknown", description="MYSTERY"))
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

@app.route('/clear')
def clear():
    for eq in Equipment.objects.all(): # Deleting old data...
        eq.delete()
    for repair in Repair.objects.all(): #iterator?
        repair.delete()
    return 'Deleted!'