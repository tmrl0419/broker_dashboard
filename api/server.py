from flask import Flask, request, make_response
from flask_cors import CORS
import json
import src.api as oa
import src.model as om
import src.heat as oh
import tensorflow as tf
import datetime
from tensorflow.python.keras.backend import set_session

app = Flask(__name__)
cors = CORS(
            app, 
            resources={
                r"/*": {"origin": "*"},
                r"/stackUpdate/*": {"origin": "*"},
                r"/login/*": {"origin": "*"},
                r"/instanceInfo/*": {"origin": "*"},
                # r"/setAlarm/*": {"origin": "*"}
            }
        )

sess = tf.Session()
graph = tf.get_default_graph()
set_session(sess)
model = om.load_model('model/model')
set_session(sess)

@app.route('/', methods=['POST'])
def hello_world():
    return 'Hello world'

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
    for i in range(len(server_uuid)):
        try:
            res = oa.get_resource_list(token, server_uuid[i])
            temp = list(oa.get_mesuare_list(token, res))
            element = {}
            element['name'] = server_names[i]
            element['cpu'] = round(temp[0],0)
            element['memory'] = round(temp[1]*100,0)
            element['disk'] = round(temp[2]*100, 0)
            element['flavor_cpu'] , element['flavor_memory'] ,element['flavor_storage'] = oa.get_resource_size(token,server_uuid[i])
            element['project_id'] = oa.get_server_info(token,server_uuid[i])['server']['tenant_id']
            data.append(element)
        except Exception as e:
            element = {}
            element['name'] = server_names[i]
            element['flavor_cpu'] , element['flavor_memory'] ,element['flavor_storage'] = oa.get_resource_size(token,server_uuid[i])
            element['project_id'] = oa.get_server_info(token,server_uuid[i])['server']['tenant_id']
            data.append(element)
            print(e)
            pass
    jsonResult = {
        'data': data
    }
    res = make_response(jsonResult)
    print("/instanceInfo  -> ")
    # print(resJson)
    return res

# write rating cpu memory log ( '{uuid}.json' )
# always get admin token and use it
@app.route("/stackUpdate", methods=['POST'])
def stackUpdate():
    print("/stackUpdate  <- ")
    global model
    global sess
    global graph
    with graph.as_default():
        set_session(sess)
        body = request.get_json()
        print(body)
        token = body['token']
        server_name = body['server_name']
        rating = int(body['rating'])
        print(rating)
        project_id = body['project_id']
        server_id = oa.get_server_id(token, server_name)
        try:
            res = oa.get_resource_list(token, server_id)
            temp = list(oa.get_mesuare_list(token, res))
            cpu = round(temp[0],0)
            memory  = round(temp[1]*100,0)
            storage = round(temp[2]*100, 0)
            # cpu = 30
            # memory = 80
            # storage = 30
            # data store ( Object file ) Swift 
            print(cpu,memory,storage)
            with graph.as_default():
                try:
                    pred_cpu, pred_memory, pred_storage = [ round(x,1) for x in om.predict( cpu, memory, storage, rating, model)]
                    print(pred_cpu, pred_memory, pred_storage)
                    if( pred_cpu != 1 or pred_memory != 1  or pred_storage != 1 ):
                        print("Need to Change")
                        cpu, memory, storage = oa.get_resource_size(token,server_id)
                        cpu *= pred_cpu.round()
                        memory *= pred_memory.round(1)
                        storage *= pred_storage
                        memory = memory.round(1)*1024
                        storage = storage.round(1)
                        flavor_prevID = oa.get_flavor_id(token,server_id)
                        flavor_name = server_name + str(datetime.datetime.now())
                        try:
                            oa.create_flavor(token, flavor_name, int(cpu), int(memory), int(storage))
                            try:
                                print( oh.resizeTemplate(project_id, server_name, server_id, flavor_name, token) )
                            except Exception as e:
                                print(e)
                                pass       
                            # flavor remove
                            # oa.remove_flavor(token, flavor_prevID)
                        except Exception as e:
                            print(e)
                            pass
                        # resize here
                    else:
                        if(rating <= 20):
                            print("Need to copy and move")
                            oh.copyTemplate(project_id, server_name, server_id, token)
                            res={'result': 'alternative'}
                            return res
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
            print(e)
            return {'reslut': False}


def setAlarm():
    """Instance Inforamtion"""
    print("/setAlarm  <- ")
    body = request.get_json()
    print(body)
    token = body['token']
    alarmCPU = body['cpu']
    alarmMemory = body['memory']
    alarmDisk = body['disk']
    server_name = body['server_name']
    server_id = oa.get_server_id(token, server_name)
    print(alarmCPU, alarmMemory, alarmDisk)
    resource_cpu , resource_memory, resource_disk = get_resource_size(token, server_uuid)
    # null로 보냈으면 cpu, 0으로 보냈으면 != 0
    if(alarmCPU):
        oa.cpuAlarm(token,server_id,alarmCPU)
    if(alarmMemory):
        alarmMemory =  (int(alarmMemory)*resource_memory*1024)/100.0
        oa.memoryAlarm(token,server_id,alarmCPU)
    if(alarmDisk):
        alarmDisk =  (int(alarmDisk)*resource_disk*1024)/100.0
        oa.diskAlarm(token,server_id,alarmCPU)
    #composite rule alarm
    #oa.createAlarm(token,server_id,alarmCPU,alarmMemory,alarmDisk)
    res = { "result" : True}
    print("/setAlarm  -> ")
    return res

@app.route("/createStack", methods=['POST'])
def createStack():
    print("/createStack  <- ")
    data = request.get_json()
    print(data)
    project_id = data['project_id']
    server_name= data['server_name']
    stack_name = data['stack_name']
    flavor =  data['flavor']
    image =  data['image']
    token =  data['token']
    res = {"result":True}
    try:
        print(oh.createStack(project_id, server_name, stack_name, flavor,image, token))
    except Exception as e:
        print(e)
        return {"result": False}
    print("/createStack  -> ")
    return res

@app.route("/createInfo", methods=['GET'])
def createInfo():
    print("/createInfo  <- ")

    token = request.args.get('token')

    images = oa.get_image_list(token)
    flavors = oa.get_flavor_list(token)
    
    image_list = { elem['id']: elem['name'] for elem in images['images'] }
    flavor_list = { elem['id']: elem['name'] for elem in flavors['flavors'] }

    res = {
        'images': image_list,
        'flavors': flavor_list
    }

    res = make_response(res)
    print("/createInfo  -> ")
    return res

@app.route("/uploadImage", methods=['POST'])
def uploadImage():
    print("/uploadImage  <- ")
    req = request.get_json()
    token = req['token']
    File = req['file']
    print("File: ", File)
    res = {
        'result': 'True'
    }

    res = make_response(res)
    print("/uploadImage  -> ")
    return res



if __name__ == '__main__':
    app.run(host='localhost', port = 5000, debug = True)