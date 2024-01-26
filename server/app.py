from flask import Flask ,request, session
from flask import jsonify
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from models import SysInfo, db ,User,AmbientTemperatureHTTP,AmbientTemperatureMQTT
from config import ApplicationConfig
from flask_session import Session
from pysnmp.hlapi import getCmd, SnmpEngine, CommunityData, UdpTransportTarget, ContextData, ObjectType, ObjectIdentity,nextCmd
from datetime import datetime
app = Flask(__name__)
app.config.from_object(ApplicationConfig)

serverSession = Session(app)
CORS(app)

db.init_app(app)

with app.app_context():
    db.create_all()

bcrypt = Bcrypt(app)


ip_target = '127.0.0.1'
community = 'public'


def get_snmp_data(oid):
    errorIndication, errorStatus, errorIndex, varBinds = next(
        getCmd(SnmpEngine(),
               CommunityData('public'),  # Replace 'public' with your SNMP community string
               UdpTransportTarget(('localhost', 161)),  # Replace with your SNMP server details
               ContextData(),
               ObjectType(ObjectIdentity(oid)))
    )

    if errorIndication:
        print(f"SNMP error: {errorIndication}")
        return None
    elif errorStatus:
        print(f"SNMP error: {errorStatus.prettyPrint()}")
        return None
    else:
        return varBinds[0][1]



def walk_snmp_data(host, oid):
    result = []
    for (errorIndication,
         errorStatus,
         errorIndex,
         varBinds) in nextCmd(SnmpEngine(),
                              CommunityData(community),
                              UdpTransportTarget((host, 161)),
                              ContextData(),
                              ObjectType(ObjectIdentity(oid)),
                              lexicographicMode=False):
        if errorIndication:
            print(errorIndication)
            break
        elif errorStatus:
            print('%s at %s' % (errorStatus.prettyPrint(),
                                errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
            break
        else:
            for varBind in varBinds:
                result.append(varBind)
    return result


@app.route("/disk/description", methods=["GET"])
def get_disk_description():
    oid = "1.3.6.1.2.1.25.2.3.1.3"
    result = walk_snmp_data(ip_target, oid)
    if result:
        return jsonify({"Disk Description": [str(varBind[1]) for varBind in result]})
    else:
        return jsonify({"Error": "Failed to retrieve disk description"}), 500


@app.route("/disk/usage", methods=["GET"])
def get_disk_usage():
    oid = "1.3.6.1.2.1.25.2.3.1.6"
    result = walk_snmp_data(ip_target, oid)
    if result:
        return jsonify({"Disk Usage": [int(varBind[1]) for varBind in result]})
    else:
        return jsonify({"Error": "Failed to retrieve disk usage"}), 500



# OIDs for the requested information
memory_total_oid = "1.3.6.1.4.1.2021.4.5.0"  # UCD-SNMP-MIB::memTotalReal
cpu_usage_oid = "1.3.6.1.4.1.2021.11.11.0"  # UCD-SNMP-MIB::ssCpuIdle

@app.route("/memory", methods=["GET"])
def get_memory_info():
    memory_total = get_snmp_data(memory_total_oid)
    return jsonify({"memory usage": str(memory_total)})


@app.route("/cpu", methods=["GET"])
def get_cpu_info():
    cpu_usage = get_snmp_data(cpu_usage_oid)
    return jsonify({"cpu usage": str(cpu_usage)})


@app.route("/@me",methods = ["GET"])
def get_current_user():
    user_id = session.get("user_id")
    
    if not user_id:
        return jsonify({"Error": "unauthorized"}), 401
    user = User.query.filter_by(id= user_id).first()
    return jsonify({
        "id":user.id,
        "username":user.username
    })

@app.route("/register", methods=['POST'])
def register():
    username = request.json["username"]
    password = request.json["password"]
    user_exists = User.query.filter_by(username=username).first() is not None
    if user_exists:
        return jsonify({
            "Error" : "User already exists"
        }),409
    hashedPassword = bcrypt.generate_password_hash(password)
    newUser = User(username=username, password=hashedPassword)
    db.session.add(newUser)
    db.session.commit()

    return jsonify({
        "id": newUser.id,
        "username": newUser.username
    })
    
@app.route("/login", methods=["POST"])
def login():
    username = request.json["username"]
    password = request.json["password"]
    user = User.query.filter_by(username=username).first()

    if user is None:
        return jsonify({"Error": "unauthorized"}), 401
    
    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({"Error": "unauthorized"}), 401

    session["user_id"] = user.id

    return jsonify({
        "id": user.id,
        "username": user.username
    })



@app.route("/sysinfo", methods=["GET"])
def getSysInfo():
    memory_total_oid = "1.3.6.1.4.1.2021.4.5.0"  # UCD-SNMP-MIB::memTotalReal
    cpu_usage_oid = "1.3.6.1.4.1.2021.11.11.0"  # UCD-SNMP-MIB::ssCpuIdle
    
    oid_disk_description = "1.3.6.1.2.1.25.2.3.1.3"
    result_disk_description = walk_snmp_data(ip_target, oid_disk_description)
    
    oid_disk_usage = "1.3.6.1.2.1.25.2.3.1.6"
    result_disk_usage = walk_snmp_data(ip_target, oid_disk_usage)
    
    result_memory_total = get_snmp_data(memory_total_oid)
    result_cpu_usage = get_snmp_data(cpu_usage_oid)
    if result_disk_description and result_cpu_usage and result_disk_usage and result_memory_total:
        return jsonify({
            "memory usage": str(result_memory_total),
            "cpu usage": str(result_cpu_usage),
            "Disk Usage": [int(varBind[1]) for varBind in result_disk_usage],
            "Disk Description": [str(varBind[1]) for varBind in result_disk_description]
        })


@app.route("/sysinfo/store", methods=["GET"])
def get_and_store_sysinfo():
    url = "http://127.0.0.1:5002/sysinfo"
    response = requests.get(url)
    data = response.json()

    if data:
        sysinfo = SysInfo(
            memory_usage=data["memory usage"],
            cpu_usage=data["cpu usage"],
            disk_description=data["Disk Description"],
            disk_usage=data["Disk Usage"]
            
        )

        db.session.add(sysinfo)
        db.session.commit()

        return "Sysinfo stored successfully", 200
    else:
        return "Failed to fetch sysinfo", 500
    
def get_sysinfo():
    sysinfo_entries = SysInfo.query.all()
    sysinfo_list = []

    for entry in sysinfo_entries:
        sysinfo_dict = {
            "id": entry.id,
            "memory_usage": entry.memory_usage,
            "cpu_usage": entry.cpu_usage,
            "disk_description": entry.disk_description,
            "disk_usage": entry.disk_usage,
            "timestamp":entry.timestamp
            
        }
        sysinfo_list.append(sysinfo_dict)
    return sysinfo_list


@app.route("/get_sysinfo", methods=["GET"])
def fetch_sysinfo():
    sysinfo_list = get_sysinfo()
    return jsonify(sysinfo_list)

    
###################################################
# part 2 (IOT devices)
from random import uniform
import threading
import time
from flask_mqtt import Mqtt
import json


app.config['MQTT_BROKER_URL'] = 'localhost'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_USERNAME'] = ''
app.config['MQTT_PASSWORD'] = ''
app.config['MQTT_REFRESH_TIME'] = 1.0 

mqtt = Mqtt(app)

ambient_temperature_http = 25.0
ambient_temperature_mqtt = 25.0


@app.route('/ambient_temperature_http', methods=['GET'])
def get_ambient_temperature_http():
    global ambient_temperature_http
    new_ambient_temperature = AmbientTemperatureHTTP(temperature=ambient_temperature_http,timestamp=datetime.utcnow())
    db.session.add(new_ambient_temperature)
    db.session.commit()
    return jsonify({'ambient_temperature_http': ambient_temperature_http})

@app.route('/ambient_temperature_mqtt', methods=['GET'])
def get_ambient_temperature_mqtt():
    global ambient_temperature_mqtt
    new_ambient_temperature = AmbientTemperatureMQTT(temperature=ambient_temperature_mqtt,timestamp=datetime.utcnow())
    db.session.add(new_ambient_temperature)
    db.session.commit()
    return jsonify({'ambient_temperature_mqtt': ambient_temperature_mqtt})


def update_ambient_temperature_http():
    global ambient_temperature_http
    while True:
        ambient_temperature_http = round(uniform(20.0, 30.0), 2)
        time.sleep(10)

def update_ambient_temperature_mqtt():
    global ambient_temperature_mqtt
    while True:
        ambient_temperature_mqtt = round(uniform(20.0, 30.0), 2)
        mqtt.publish('ambient_temperature_mqtt', json.dumps({'ambient_temperature_mqtt': ambient_temperature_mqtt}))
        time.sleep(5)
        
@app.route('/ambient_temperature_http/all', methods=['GET'])
def get_all_ambient_temperature_http():
    ambient_temperatures_http = AmbientTemperatureHTTP.query.all()
    result = [{
        'id': ambient.id,
        'temperature': ambient.temperature,
        'timestamp': ambient.timestamp
    } for ambient in ambient_temperatures_http]
    return jsonify(result)

@app.route('/ambient_temperature_mqtt/all', methods=['GET'])
def get_all_ambient_temperature_mqtt():
    ambient_temperatures_mqtt = AmbientTemperatureMQTT.query.all()
    result = [{
        'id': ambient.id,
        'temperature': ambient.temperature,
        'timestamp': ambient.timestamp
    } for ambient in ambient_temperatures_mqtt]
    return jsonify(result)     




update_thread_http = threading.Thread(target=update_ambient_temperature_http)
update_thread_mqtt = threading.Thread(target=update_ambient_temperature_mqtt)

update_thread_http.start()
update_thread_mqtt.start()


##############
import requests











if __name__ == '__main__':
    app.run(debug=True,port=5002)

