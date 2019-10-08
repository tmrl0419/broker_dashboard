from flask import Flask, request, make_response
from flask_cors import CORS
import json
import src.api as oa
import src.model as om
import tensorflow as tf

app = Flask(__name__)
cors = CORS(app, resources={
  r"/login/*": {"origin": "*"},
  r"/instanceInfo/*": {"origin": "*"},
})
model = om.load_model('model/model')
graph = tf.get_default_graph()
print(model)
@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route("/login", methods=['POST'])
def login():
    """Login Form"""
    print("/login  <- ")
    print(request.get_json())
    data = request.get_json()
    id = data['id']
    password = data['password']
    token = oa.get_token(id,password)
    if token is None:
        jsonResult = {
            'loginresult': None
        }
        resJson = json.dumps(jsonResult)
        return resJson
    names, uuid = oa.get_projectID(token)

    jsonResult = {
        'projects' : names,
        'uuid' : uuid,
        'loginresult': 'true'
    }
    resJson = json.dumps(jsonResult)
    print("/login  -> ")
    print(resJson)
    return resJson

@app.route("/login/project", methods=['POST'])
def project():
    """Login with Project Form"""
    print("/login/project  <- ")
    print(request.get_json())
    data = request.get_json()
    id = data['id']
    password = data['password']
    uuid = data['uuid']

    token = oa.get_other_token(id,password,uuid)
    if token is None:
        jsonResult = {
            'token' : token,
            'loginresult': False
        }
        resJson = json.dumps(jsonResult)    
        print("/login/project  -> ")
        print(resJson)
        return resJson

    jsonResult = {
        'token' : token,
        'loginresult': True
    }
    resJson = json.dumps(jsonResult)
    print("/login/project  -> ")
    print(resJson)
    return resJson

@app.route("/instanceInfo", methods=['GET'])
def instnaceInfo():
    """Instance Inforamtion"""
    print("/instanceInfo  <- ")
    token = request.args.get('token')
    server_names, server_uuid = oa.get_server_list(token)
    print(server_names)
    data = []
    for i in range(len(server_uuid)):
        try:
            res = oa.get_resource_list(token, server_uuid[i])
            temp = list(oa.get_mesuare_list(token, res))
            element = {}
            element['name'] = server_names[i]
            element['cpu'] = round(temp[0]*100,0)
            element['memory'] = round(temp[1]*100,0)
            element['disk'] = round(temp[2]*100, 0)
            data.append(element)
        except Exception as e:
            pass
    jsonResult = {
        'data': data
    }
    res = make_response(jsonResult)
    resJson = json.dumps(jsonResult)
    print("/instanceInfo  -> ")
    print(resJson)
    return res

@app.route("/stackUpdate", methods=['get'])
def stackUpdate():
    print("/stackUpdate  <- ")
    global model
    global graph
    with graph.as_default():
        """Instance Inforamtion"""
        # data = request.get_json()
        cpu = request.headers.get('cpu')
        memory = request.headers.get('memory')
        disk = request.headers.get('disk')
        rating = request.headers.get('rating')
        try:
            pred_cpu, pred_memory, pred_disk = om.predict( cpu, memory, disk, rating, model)
        except Exception as e:
            print(e)

    jsonResult = {
        'pred_cpu': pred_cpu,
        'pred_memory': pred_memory,
        'pred_disk': pred_disk
    }

    resJson = json.dumps(str(jsonResult))
    print("/stackUpdate  -> ")
    print(resJson)
    res = {'result': True}
    return res

@app.route("/setAlarm", methods=['POST'])
def setAlarm():
    """Instance Inforamtion"""
    print("/setAlarm  <- ")
    body = request.get_json()
    token = body['token']
    instance_uuid = body['instance_uuid']
    alarmCPU = body['cpu']
    alarmMemory = body['memory']
    alarmDisk = body['disk']
    oa.createAlarm(toekn,instance_uuid,alarmCPU,alarmMemory,alarmDisk)

    print("/setAlarm  -> ")
    return res


if __name__ == '__main__':
    app.run(host='localhost', port = 5000, debug = True)