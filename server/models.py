from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4
import datetime
#init db
db = SQLAlchemy()

def get_uuid():
    return uuid4().hex

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.String(32),primary_key = True ,unique= True, default = get_uuid)
    username = db.Column(db.String(32),unique=True)
    password = db.Column(db.String(32),nullable=False)

class SysInfo(db.Model):
    __tablename__ = "sysinfo"
    id = db.Column(db.Integer, primary_key=True)
    memory_usage = db.Column(db.String(64))
    cpu_usage = db.Column(db.String(64))
    disk_description = db.Column(db.JSON)
    disk_usage = db.Column(db.JSON)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    

class AmbientTemperatureHTTP(db.Model):
    __tablename__ = "ambient_temperature_http"
    id = db.Column(db.Integer, primary_key=True)
    temperature = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class AmbientTemperatureMQTT(db.Model):
    __tablename__ = "ambient_temperature_mqtt"
    id = db.Column(db.Integer, primary_key=True)
    temperature = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
