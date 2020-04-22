from pymodm import EmbeddedMongoModel, MongoModel, fields, connect
from pymongo.write_concern import WriteConcern

# Connect to MongoDB and call the connection "my-app".
connect("mongodb://localhost:27017/ma_app")

class Error(EmbeddedMongoModel):
    time = fields.DateTimeField()
    etype = fields.CharField()
    description = fields.CharField()

    
class Failure(EmbeddedMongoModel):
    time = fields.DateTimeField()
    ftype = fields.CharField()
    description = fields.CharField()


class Repair(MongoModel):
    deadline = fields.DateTimeField()
    machineID = fields.IntegerField()
    rtype = fields.CharField()
    description = fields.CharField()
    in_progress = fields.BooleanField()
    completed = fields.BooleanField()


class Equipment(MongoModel):
    machineID = fields.IntegerField()
    model = fields.CharField()
    revised_on = fields.DateTimeField()
    errors = fields.EmbeddedDocumentListField(Error)
    failures = fields.EmbeddedDocumentListField(Failure)


class User(MongoModel):
    login = fields.CharField(primary_key=True, required=True)
    password = fields.CharField(required=True)
    role = fields.CharField(required=True)
