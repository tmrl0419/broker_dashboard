from flask import Flask, request, make_response
from flask_cors import CORS
import json
import src.api as oa
import src.model as om
import src.heat as oh
import tensorflow as tf
from tensorflow.python.keras.backend import set_session

app = Flask(__name__)
cors = CORS(app, resources={
  r"/login/*": {"origin": "*"},
  r"/instanceInfo/*": {"origin": "*"},
})

sess = tf.Session()
graph = tf.get_default_graph()
set_session(sess)
model = om.load_model('model/model')


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
    data = []
    print(token)
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

# write rating cpu memory log ( '{uuid}.json' )
# always get admin token and use it
@app.route("/stackUpdate", methods=['GET'])
def stackUpdate():
    print("/stackUpdate  <- ")
    global model
    global sess
    global graph
    with graph.as_default():
        
        set_session(sess)

        server_name = request.args.get('name')
        server_uuid = request.args.get('uuid')
        rating = request.args.get('rating')
        token = request.args.get('token')
        project_id = request.args.get('project_id')

        # print( oh.extractTemplate("admin","test","admin-openrc.sh",token) )

        try:
            res = oa.get_resource_list(token, server_uuid)
            temp = list(oa.get_mesuare_list(token, res))
            cpu = round(temp[0]*100,0)
            memory  = round(temp[1]*100,0)
            storage = round(temp[2]*100, 0)
            cpu = 80
            memory  = 80
            storage = 80
            # data store ( Object file ) Swift 

            print(cpu,memory,storage)
            with graph.as_default():
                try:
                    pred_cpu, pred_memory, pred_storage = [ round(x,1) for x in om.predict( cpu, memory, storage, rating, model)]
                    print(pred_cpu, pred_memory, pred_storage)
                    if( pred_cpu != 1 or pred_memory != 1  or pred_storage != 1 ):
                        print("Need to Change")
                        print(oa.get_resource_size(token,server_uuid))
                        cpu, memory, storage = oa.get_resource_size(token,server_uuid)
                        cpu *= pred_cpu.round()
                        memory *= pred_memory.round(1)
                        storage *= pred_storage
                        memory = memory.round(1)*1024
                        storage = storage.round(1)
                        print(cpu,memory,storage)
                        print("Asdf")
                        try:
                            print(oa.create_flavor(token, 'tetttt', int(cpu), int(memory), int(storage)))
                        except Exception as e:
                            print(e)
                            pass
                        print("hihi")
                        oh.resizeTemplate(project_id, server_name, server_uuid, 'tetttt', token)
                        # resize here
                    else:
                        if(rating <= 20):
                            print("Need to copy and move")
                        else: 
                            print("Don't need change")

                    jsonResult = {
                        'pred_cpu': pred_cpu,
                        'pred_memory': pred_memory,
                        'pred_disk': pred_storage
                    }
                    resJson = json.dumps(str(jsonResult))
                    print("/stackUpdate  -> ")
                    print(resJson)
                    res = {'result': True}
                    return res
                except Exception as e:
                    print(e)
                    return {'reslut': False}
        except Exception as e:
            return {'reslut': False}
    

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
    oa.createAlarm(token,instance_uuid,alarmCPU,alarmMemory,alarmDisk)
    res = { result: True}
    print("/setAlarm  -> ")
    return res


if __name__ == '__main__':
    app.run(host='localhost', port = 5000, debug = True)