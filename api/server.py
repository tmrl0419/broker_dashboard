from flask import Flask, request, make_response
from flask_cors import CORS
from tensorflow.python.keras.backend import set_session
import tensorflow as tf
import json
import os
import datetime
import src.api as oa
import src.model as om
import src.heat as oh


app = Flask(__name__)

cors = CORS(
            app, 
            resources={
                r"/*": {"origin": "*"},
                r"/stackUpdate/*": {"origin": "*"},
                r"/login/*": {"origin": "*"},
                r"/instanceInfo/*": {"origin": "*"},
                r"/setAlarm/*": {"origin": "*"}
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

# 로그인 
@app.route("/login", methods=['POST'])
def login():
    """Login Form"""
    print("/login  <- ")
    print(request.get_json())
    data = request.get_json()
    id = data['id']
    password = data['password']
    token = oa.get_token(id,password)                                   # project_id의 리스트를 가져오기 위한 토큰 생성
    if token is None:                                                   # 토큰 생성 실패
        jsonResult = {
            'loginresult': None
        }
        resJson = json.dumps(jsonResult)
        return resJson
    names, uuid = oa.get_projectID(token)                               # 프로젝트 리스트 가져오기
    jsonResult = {
        'projects' : names,
        'uuid' : uuid,
        'loginresult': 'true'
    }

    resJson = json.dumps(jsonResult)
    print("/login  -> ")
    print(resJson)
    return resJson

# 프로젝트 토큰 생성
@app.route("/login/project", methods=['POST'])
def project():
    """Login with Project Form"""
    print("/login/project  <- ")
    print(request.get_json())
    data = request.get_json()
    id = data['id']
    password = data['password']
    uuid = data['uuid']

    token = oa.get_other_token(id,password,uuid)                        # 선택된 project의 토큰 생성
    if token is None:                                                   # 토큰 생성 실패
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
    
    with open('token.json',"w") as json_file:                           # Alarm 발생시 처리하기 위해 admin 토큰 저장
        entry = {'time': str(datetime.datetime.now()), 'token':token}
        json.dump(entry, json_file)

    resJson = json.dumps(jsonResult)
    print("/login/project  -> ")
    print(resJson)
    return resJson

# 프로젝트 인스턴스 리스트 요청
@app.route("/instanceInfo", methods=['GET'])
def instnaceInfo():
    """Instance Inforamtion"""
    print("/instanceInfo  <- ")
    token = request.args.get('token')
    server_names, server_uuid = oa.get_server_list(token)               # 인스턴스 리스트 가져오기
    data = []
    for i in range(len(server_uuid)):
        try:
            res = oa.get_resource_list(token, server_uuid[i])           # 인스턴스의 리소스 리스트 가져오기
            temp = list(oa.get_mesuare_list(token, res))                # 각 리소스의 사용량 가져오기
            element = {}
            element['name'] = server_names[i]
            element['cpu'] = round(temp[0],0)
            element['memory'] = round(temp[1]*100,0)
            element['disk'] = round(temp[2]*100, 0)
            element['flavor_cpu'] , element['flavor_memory'] ,element['flavor_storage'] = oa.get_resource_size(token,server_uuid[i])
            element['project_id'] = oa.get_server_info(token,server_uuid[i])['server']['tenant_id']
            data.append(element)
        except Exception as e:                                          # 측정 실패한 경우
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

# 스택 업데이트
@app.route("/stackUpdate", methods=['POST'])
def stackUpdate():
    print("/stackUpdate  <- ")
    global model
    global sess
    global graph
    with graph.as_default():
        set_session(sess)
        body = request.get_json()
        token = body['token']
        server_name = body['server_name']
        rating = int(body['rating'])
        project_id = body['project_id']
        server_id = oa.get_server_id(token, server_name)                # 인스턴스 이름을 이용해 UUID 가져오기
        filePath = os.getcwd()+'/rating_log/'+str(server_id)+'.json'    
        feeds= []
        if(os.path.isfile(filePath)):                                   # 인스턴스의 이전 로그가 존재한다면, 데이터 읽어오기
            with open(filePath, "r") as feedsjson:
                feeds = json.load(feedsjson)

        with open(filePath,"w") as json_file:                           # 인스턴스 로그 생성
            entry = {'time': str(datetime.datetime.now()), 'rating': rating, 'token': token, 'project_id':project_id, 'server_name':server_name}
            feeds.append(entry)
            json.dump(feeds, json_file)

        try:
            res = oa.get_resource_list(token, server_id)
            temp = list(oa.get_mesuare_list(token, res))
            cpu = round(temp[0],0)
            memory  = round(temp[1]*100,0)
            storage = round(temp[2]*100, 0)
            # cpu, memory, storage = 30, 80, 30                         # 테스트 값
            print(cpu,memory,storage)
            with graph.as_default():
                try:
                    # 현재 사용량, 피드백 정보를 바탕으로 CPU, Memory, DISK의 필요량 예측
                    pred_cpu, pred_memory, pred_storage = [ round(x,1) for x in om.predict( cpu, memory, storage, rating, model)]
                    print(pred_cpu, pred_memory, pred_storage)
                    # 필요량을 비탕으로 스택 업데이트
                    res = oa.stackUpdate(token, project_id, server_id, server_name, pred_cpu, pred_memory, pred_storage, rating)
                    return res
                except Exception as e:
                    print(e)
                    return {'reslut': False}
        except Exception as e:
            print(e)
            return {'reslut': False}

# 알람 생성
@app.route("/setAlarm", methods=['POST'])
def setAlarm():
    """Instance Inforamtion"""
    print("/setAlarm  <- ")
    body = request.get_json()
    token = body['token']
    alarmCPU = body['cpu']
    alarmMemory = body['memory']
    alarmDisk = body['disk']
    server_name = body['server_name']
    server_id = oa.get_server_id(token, server_name)
    # 현재 할당된 리소스의 크기 받아오기
    resource_cpu, resource_memory, resource_disk = oa.get_resource_size(token, server_id)
    if(alarmCPU):                                                       # CPU Threshold값이 들어온 경우
        oa.cpuAlarm(token,server_id,alarmCPU)                           # CPU 알람 생성
    if(alarmMemory):                                                    # Memory Threshold값이 들어온 경우
        alarmMemory =  (int(alarmMemory)*resource_memory*1024)/100.0    # 퍼센트로 값의 단위 변경
        oa.memoryAlarm(token,server_id,alarmCPU)                        # Memory 알람 생성
    if(alarmDisk):                                                      # Disk Threshold값이 들어온 경우
        alarmDisk =  (int(alarmDisk)*resource_disk*1024)/100.0          # 퍼센트로 값의 단위 변경
        oa.diskAlarm(token,server_id,alarmCPU)                          # Disk 알람 생성
    # 개별 생성이 아닌 한번에 생성하는 방법, 디버깅 필요
    # oa.createAlarm(token,server_id,alarmCPU,alarmMemory,alarmDisk)
    res = { "result" : True}
    print("/setAlarm  -> ")
    return res

# 인스턴스 생성 
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
        print(oh.createStack(project_id, server_name, stack_name, flavor,image, token)) # Stack 생성
    except Exception as e:
        print(e)
        return {"result": False}
    print("/createStack  -> ")
    return res

# Stack생성에 필요한 이미지 리스트, Flavor 리스트 받아오기
@app.route("/createInfo", methods=['GET'])
def createInfo():
    print("/createInfo  <- ")

    token = request.args.get('token')

    images = oa.get_image_list(token)                                   # 이미지 리스트 받아오기 
    flavors = oa.get_flavor_list(token)                                 # Flavor 리스트 받아오기
    
    image_list = { elem['id']: elem['name'] for elem in images['images'] }
    flavor_list = { elem['id']: elem['name'] for elem in flavors['flavors'] }

    res = {
        'images': image_list,
        'flavors': flavor_list
    }

    res = make_response(res)
    print("/createInfo  -> ")
    return res

# Task: 이미지 업로드
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

# 알람 이벤트 처리
@app.route("/alarmAlter", methods=['POST'])
def alarmAlter():
    print("/alarmAlter  <- ")
    print(request.get_json())
    data = request.get_json()
    alarm_id = data['alarm_id']

    if(os.path.isfile('token.json')):                                   # admin의 토큰 값 받아오기
        with open('token.json') as feedsjson:
            feeds = json.load(feedsjson)
            token = feeds['token']
    else:                                                               # 저장된 admin의 토큰 없을 시 
        res = {'result': 'False'}
        return res

    server_id = oa.get_server_id_by_alarm(alarm_id, token)              # 알람 ID 값으로 알람 발생 인스턴스 ID 조회
    
    filePath = os.getcwd()+'/rating_log/'+str(server_id)+'.json'
    
    if(os.path.isfile(filePath)):                                       # 알람 발생 인스턴스의 rating_log 받아오기
        with open(filePath,"r") as feedsjson :
            feeds = json.load(feedsjson)
    else:                                                               # 저장된 rating_log가 없을 시
        res = {'result': 'False'}
        return res
    
    instance_info = feeds[-1]                                           # rating_log의 가장 최근 값 저장
    project_id = instance_info['project_id']                         
    rating = instance_info['rating']
    server_name = instance_info['server_name']
    with graph.as_default():                                            # stackUpdate와 같은 과정 반복
        set_session(sess)
        try:
            res = oa.get_resource_list(token, server_id)
            temp = list(oa.get_mesuare_list(token, res))
            cpu = round(temp[0],0)
            memory  = round(temp[1]*100,0)
            storage = round(temp[2]*100, 0)
            print(cpu,memory, storage)
            with graph.as_default():
                try:
                    # 현재 사용량, 피드백 정보를 바탕으로 CPU, Memory, DISK의 필요량 예측
                    pred_cpu, pred_memory, pred_storage = [ round(x,1) for x in om.predict( cpu, memory, storage, rating, model)]
                    print(pred_cpu, pred_memory, pred_storage)
                    # 필요량을 비탕으로 스택 업데이트
                    res = oa.stackUpdate(token, project_id, server_id, server_name, pred_cpu, pred_memory, pred_storage, rating)
                    res = json.dumps(res)
                    return res
                except Exception as e:
                    print(e)
                    return {'reslut': False}
        except Exception as e:
            print(e)
            return {'reslut': False}


if __name__ == '__main__':
    app.run(host='localhost', port = 5000, debug = True)