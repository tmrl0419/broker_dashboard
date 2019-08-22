from flask import Flask, request
import json
import src.api as oa
import src.model as om
import tensorflow as tf

app = Flask(__name__)
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
    names, uuid = oa.get_projectID(token)

    jsonResult = {
        'projects' : names,
        'uuid' : uuid
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
    
    jsonResult = {
        'token' : token
    }

    resJson = json.dumps(jsonResult)
    print("/login/project  -> ")
    print(resJson)
    return resJson

@app.route("/instanceInfo", methods=['get'])
def instnaceInfo():
    """Instance Inforamtion"""
    print("/instanceInfo  <- ")
    # data = request.get_json()
    token = request.headers.get('token')
    server_names, server_uuid = oa.get_server_list(token)

    names = []
    measures = []
    for i in range(len(server_uuid)):
        try:
            res = oa.get_resource_list(token, server_uuid[i])
            measures.append(oa.get_mesuare_list(token, res))
            names.append(server_names[i])
        except:
            pass
    
    jsonResult = {
        'instance': names,
        'data': measures
    }

    resJson = json.dumps(jsonResult)
    print("/instanceInfo  -> ")
    print(resJson)
    return resJson

@app.route("/predict", methods=['get'])
def predict():
    global model
    global graph
    with graph.as_default():
        """Instance Inforamtion"""
        print("/predict  <- ")
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
        print("/predict  -> ")
        print(resJson)
        return resJson

if __name__ == '__main__':
    app.run(host='localhost', port = 5000, debug = True)