import requests
import json
import datetime
import src.heat as oh

url_base = "http://localhost"

### Keystone API
def get_token(id,passwd):
    data = \
        {"auth":
            {
                "identity":
                    {"password":
                         {"user":
                              {"domain":
                                   {"name": "Default"},
                               "password": passwd,
                               "name": id
                               }
                          },
                     "methods": ["password"]
                     },
                "scope": 
                    {"system": {
                        "all": True
                        }
                    }
            }
        }


    # pixed header
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    # TODO get project id
    res = requests.post(url_base + '/identity/v3/auth/tokens', headers=headers, data=json.dumps(data), verify=True)
    try:
        token = res.headers['X-Subject-Token']
        return token
    except Exception as e:
        print(e)
        return None

def get_other_token(id, passwd, projectID):
    data = \
        {"auth":
            {
                "identity":
                    {"password":
                         {"user":
                              {"domain":
                                   {"name": "Default"},
                               "password": passwd,
                               "name": id
                               }
                          },
                     "methods": ["password"]
                     }                
            }
        }
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

    data['auth']['scope'] = {
        "project":
            {"id": projectID }
    }

    res = requests.post(url_base + '/identity/v3/auth/tokens', headers=headers, data=json.dumps(data), verify=True)
    token = res.headers['X-Subject-Token']

    return token

def get_token_by_token(token,project_id):
    data = \
        {
            "auth": {
                "identity": {
                    "methods": [
                        "token"
                    ],
                    "token": {
                        "id": token
                    }
                },
                "scope": {
                    "project": {
                        "id": project_id
                    }
                }
            }
        }


    # pixed header
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json', "X-Auth-Token":token}
    # TODO get project id
    res = requests.post(url_base + '/identity/v3/auth/tokens', headers=headers, data=json.dumps(data), verify=True)
    try:
        token = res.headers['X-Subject-Token']
        return token
    except Exception as e:
        print(e)
        return None



### Project API
def get_projectID(token):
    url = url_base + "/identity/v3/auth/projects"
    headers = {'Content-Type': 'application/json', 'X-Auth-Token': token}
    res = requests.get(url, headers=headers)
    body = res.json()

    projects_name = [x['name'] for x in body['projects'] if not x['name'] == "invisible_to_admin"]
    projects_uuid = [ x['id'] for x in body['projects'] if not x['name'] == "invisible_to_admin"]

    return projects_name, projects_uuid

### Instance API

# for ask what kinds of instances admin control on dashboard
def get_server_list(token):
    server_uuid = []
    server_names = []
    url = url_base + "/compute/v2.1/servers"
    headers = {'Content-Type': 'application/json', 'X-Auth-Token': token}
    res = requests.get(url, headers=headers)
    body = res.json()
    try:
        server_uuid = [ x['id'] for x in body['servers']]
        server_names = [ x['name'] for x in body['servers']]
    except:
        pass
    
    return server_names, server_uuid

def get_server_id(token, server_name):
    server_names, server_uuid = get_server_list(token)
    index = -1
    for i in range(len(server_names)):
        if(server_name == server_names[i]):
            index = i
            break
    if(index != -1):
        return server_uuid[index]
    else:
        return -1


def get_server_info(token,server_uuid):
    headers = {'Content-Type': 'application/json', 'X-Auth-Token': token}
    url = url_base + '/compute/v2.1/servers/%s'%server_uuid
    res = requests.get(url=url, headers=headers)
    return res.json()


def get_resource_list(token, server_uuid):
    url = url_base + "/metric/v1/resource/generic/%s"%(server_uuid)
    headers = {'Content-Type': 'application/json, */*', 'X-Auth-Token':token}
    res = requests.get( url, headers = headers)
    body = res.json()
    return body


def get_resource_size(token, server_uuid):
    body = get_resource_list(token,server_uuid)

    headers = {'Content-Type': 'application/json, */*', 'X-Auth-Token': token}
    PARAMS = {'start': None, 'granularity': None, 'resample': None, 'stop': None, 'aggregation': None, 'refresh': False}
    try:
        url = url_base + '/metric/v1/metric/%s/measures' % (body['metrics']['vcpus'])
        res = requests.get(url=url, headers=headers, params=PARAMS)
        cpu = res.json()[-1][2]

        url = url_base + '/metric/v1/metric/%s/measures' % (body['metrics']['disk.root.size'])
        res = requests.get(url=url, headers=headers, params=PARAMS)
        disk = res.json()[-1][2]


        url = url_base + '/metric/v1/metric/%s/measures' % (body['metrics']['memory'])
        res = requests.get(url=url, headers=headers, params=PARAMS)
        memory = res.json()[-1][2]/(1024)

        return cpu, memory, disk
    except Exception as e:
        print(e)
        return None


def get_mesuare_list(token, body):

    now = datetime.datetime.now()
    five_mins = datetime.timedelta(minutes=5)
    five_mins_ago = now - five_mins

    headers = {'Content-Type': 'application/json, */*', 'X-Auth-Token': token}
    PARAMS = {'start': None, 'granularity': None, 'resample': None, 'stop': None, 'aggregation': None, 'refresh': False}

    url = url_base + '/metric/v1/metric/%s/measures'%(body['metrics']['cpu_util'])
    res = requests.get(url = url, headers = headers, params= PARAMS )
    cpu = res.json()[-1][2]
    
    url = url_base + '/metric/v1/metric/%s/measures' % (body['metrics']['memory.usage'])
    res = requests.get(url=url, headers=headers, params=PARAMS)
    memory = res.json()[-1][2]/(1024)
    
    url = url_base + '/metric/v1/metric/%s/measures' % (body['metrics']['memory'])
    res = requests.get(url=url, headers=headers, params=PARAMS)
    memory /= res.json()[-1][2]/(1024)

    url = url_base + '/metric/v1/metric/%s/measures' % (body['metrics']['disk.usage'])
    res = requests.get(url=url, headers=headers, params=PARAMS)
    disk = res.json()[-1][2]/(8*1024*1024*1024)

    url = url_base + '/metric/v1/metric/%s/measures' % (body['metrics']['disk.root.size'])
    res = requests.get(url=url, headers=headers, params=PARAMS)
    disk /= res.json()[-1][2]

    return cpu, memory, disk


# def get_stack_resource_list(token, project_id):
#     url = url_base + "/heat-api/v1/%s/stacks" %(project_id)
#     headers = {'Content-Type': 'application/json, */*', 'X-Auth-Token':token}
#     res = requests.get( url, headers = headers )
#     # print(res.json())
#     body = res.json()['stacks']
#     for elem in body:
#         url = url_base + "/heat-api/v1/%s/stacks/%s/%s/resources?type=OS::Nova::Server"%(project_id,elem['stack_name'],elem['id'])
#         headers = {'Content-Type': 'application/json, */*', 'X-Auth-Token':token, "id": elem['id']}
#         res = requests.get( url, headers = headers ).json()["resources"]
#         for i in res:
#             resource_uuid = i["physical_resource_id"]
#             resource_list = get_resource_list(token,resource_uuid)
        
#     return body




###  Flavor API 
def get_flavor_id(token, server_uuid):
    flavor_id = get_server_info(token, server_uuid)['server']['flavor']['id']
    return flavor_id

def get_flavor_name(token, server_uuid):
    flavor_id = get_server_info(token, server_uuid)['server']['flavor']['id']
    headers = {'Content-Type': 'application/json', 'X-Auth-Token': token}
    url = url_base + '/compute/v2.1/flavors/%s' % flavor_id
    res = requests.get(url=url, headers=headers)
    return res.json()['flavor']['name']

def remove_flavor(token, flavor_id):
    headers = {'Content-Type': 'application/json', 'X-Auth-Token': token}
    url = url_base + '/compute/v2.1/flavors/%s' % flavor_id
    res = requests.delete(url=url, headers=headers)
    return res


def create_flavor(token, flavor_name, vcpus, memory, storage):
    headers = {'Content-Type': 'application/json', 'X-Auth-Token': token}
    url = url_base + '/compute/v2.1/flavors'
    print(vcpus,memory,storage)
    req = {
        "flavor": {
            "name": flavor_name,
            "ram": memory,
            "vcpus": vcpus,
            "disk": storage
        }
    }
    res = requests.post(url, headers=headers, data=json.dumps(req))
    return res.json()


def get_flavor_list(token):
    headers = {'Content-Type': 'application/json', 'X-Auth-Token': token}
    url = url_base + '/compute/v2.1/flavors'
    res = requests.get(url, headers=headers)
    return res.json()

# def get_flavor_info(token, flavorID):
#     headers = {'Content-Type': 'application/json', 'X-Auth-Token': token}
#     url = url_base + '/compute/v2.1/os-simple-tenant-usage/%s' % flavorID
#     res = requests.get(url=url, headers=headers)
#     return res.json()



### Image API 
def get_image_list(token):
    headers = {'Content-Type': 'application/json', 'X-Auth-Token': token}
    url = url_base + '/image/v2/images'
    res = requests.get(url=url, headers=headers)
    return res.json()


def cpuAlarm(token, server_uuid, cpu):
    alter_url = 'http://localhost:5000/alarmAlter?uuid='+server_uuid
    data = {
        'alarm_actions': [alter_url],
        'ok_actions': ['https://localhost:5000/ok'],
        'name': 'cpu_hi',
        'gnocchi_resources_threshold_rule': {
            'evaluation_periods': 1,
            'metric': 'cpu_util',
            'resource_id': server_uuid,
            'aggregation_method': 'mean',
            'granularity': '300',
            'threshold': cpu,
            'comparison_operator': 'gt',
            'resource_type': 'instance'
        },
        'insufficient_data_actions': ['https://localhost:5000/nodata'],
        'type': 'gnocchi_resources_threshold',
        'description': 'CPU High Average'
    }

    headers = {
        'X-Auth-Token': token,
        "Content-Type": "application/json"}
    res = requests.post(url_base+":8042/v2/alarms", headers=headers, data=json.dumps(data))

    # res = requests.post(URL, headers=headers, data = data)
    s = res.content
    u = str(s)
    print(u)

def memoryAlarm(token, server_uuid, memory):
    alter_url = 'http://localhost:5000/alarmAlter'#?uuid='+server_uuid'

    data = {
        'alarm_actions': [alter_url],
         'ok_actions': ['https://localhost:5000/ok'],
        'name': 'memory_hi',
        'gnocchi_resources_threshold_rule': {
            'evaluation_periods': 1,
            'metric': 'memory.usage',
            'resource_id': server_uuid,
            'aggregation_method': 'mean',
            'granularity': '300',
            'threshold': memory,
            'comparison_operator': 'gt',
            'resource_type': 'instance'
        },
        'insufficient_data_actions': ['https://localhost:5000/nodata'],
        'type': 'gnocchi_resources_threshold',
        'description': 'CPU High Average'
    }

    headers = {
        'X-Auth-Token': token,
        "Content-Type": "application/json"}
    res = requests.post(url_base+":8042/v2/alarms", headers=headers, data=json.dumps(data))

    # res = requests.post(URL, headers=headers, data = data)
    s = res.content
    u = str(s)
    print(u)


def diskAlarm(token, server_uuid, disk):
    alter_url = 'http://localhost:5000/alarmAlter?uuid='+server_uuid
    data = {
        'alarm_actions': [alter_url],
         'ok_actions': ['https://localhost:5000/ok'],
        'name': 'disk_hi',
        'gnocchi_resources_threshold_rule': {
            'evaluation_periods': 1,
            'metric': 'disk.usage',
            'resource_id': server_uuid,
            'aggregation_method': 'mean',
            'granularity': '300',
            'threshold': disk,
            'comparison_operator': 'gt',
            'resource_type': 'instance'
        },
        'insufficient_data_actions': ['https://localhost:5000/nodata'],
        'type': 'gnocchi_resources_threshold',
        'description': 'CPU High Average'
    }

    headers = {
        'X-Auth-Token': token,
        "Content-Type": "application/json"}
    res = requests.post(url_base+":8042/v2/alarms", headers=headers, data=json.dumps(data))

    # res = requests.post(URL, headers=headers, data = data)
    s = res.content
    u = str(s)
    print(u)


### COMPOSIT ALARM DOESN'T WORK, NEED TO FIX IT
def createAlarm(token, server_uuid, cpu, memory, disk):
    resource_cpu , resource_memory, resource_disk = get_resource_size(token, server_uuid)
    print(resource_cpu , resource_memory, resource_disk )
    memory =  (int(memory)*resource_memory*1024)/100.0
    disk = (int(disk)*resource_disk*1024)/100.0
    alarmName = server_uuid+"Alarm"
    data = {
        'alarm_actions': ['http://localhost:5000/alarmAlter?uuid={server_uuid}'],
        'ok_actions': ['https://localhost:5000/ok'],
        'insufficient_data_actions': ['https://localhost:5000/nodata'],
        'name': alarmName,
        'type': 'composite',
        'composite_rule': {
            "or": [
                {
                    "threshold": cpu if cpu!= None else 10000,
                    "metric": "cpu_util",
                    "type": "gnocchi_resources_threshold",
                    "resource_id": server_uuid,                    
                    "resource_type": "instance",
                    "aggregation_method": "last",
                    "granularity": "300",
                    'comparison_operator': 'gt'
                },
                {
                    "threshold": memory if memory!= None else 10000,
                    "metric": "memory.usage",
                    "type": "gnocchi_resources_threshold",
                    "resource_id": server_uuid,
                    "resource_type": "instance",
                    "aggregation_method": "last",
                    "granularity": "300"
                },
                {
                    "threshold": disk if disk!= None else 10000,
                    "metric": "disk.usage",
                    "type": "gnocchi_resources_threshold",
                    "resource_id": server_uuid,
                    "resource_type": "instance",
                    "aggregation_method": "last",
                    "granularity": "300",
                }
            ]
        }
    }
    headers = {
        'X-Auth-Token': token,
        "Content-Type": "application/json"}
    res = requests.post(url_base+":8042/v2/alarms", headers=headers, data=json.dumps(data))
    s = res.content
    u = str(s)
    print(u)
    return 

def stackUpdate(token, project_id, server_id, server_name, pred_cpu, pred_memory, pred_storage, rating):
    if( pred_cpu != 1 or pred_memory != 1  or pred_storage != 1 ):
        print("Need to Change")
        cpu, memory, storage = get_resource_size(token,server_id)
        cpu *= pred_cpu.round()
        memory *= pred_memory.round(1)
        storage *= pred_storage
        memory = memory.round(1)*1024
        storage = storage.round(1)
        # flavor_prevID = get_flavor_id(token,server_id)
        flavor_name = server_name + str(datetime.datetime.now())
        try:
            create_flavor(token, flavor_name, int(cpu), int(memory), int(storage))
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

def get_server_id_by_alarm(alarm_id, token):
    url = url_base+":8042/v2/alarms/"+alarm_id
    headers = {'Content-Type': 'application/json', 'X-Auth-Token': token}
    res = requests.get(url, headers=headers)
    body = res.json()
    resource_id = body['gnocchi_resources_threshold_rule']['resource_id']
    return resource_id

if __name__ == '__main__':
    #flavor_id = get_flavor_id('gAAAAABdqLq6saLrqjBVA4p_e2qPTavL16-1Mqv7AP-kYb4b_NP0i1pFkrieZxMbYUrChAy-745b5FYHMl2KBUljb7znwU4DiEej7sKrxcHNFXo5RC2tPRBWRXP2PxjxWi_P9zTd7MvITx2dyZVUkBqOcOl2ykUrZPW6CVR3G55peqFeT3y5zCg', 'e6a04013-38aa-4ba6-a30f-88eb20d976ea')
    get_server_id_by_alarm('412fa434-5e59-496d-84a7-f5d59127bd46')
    # print(flavor_id)
    # print(get_flavor_name('gAAAABdqLq6saLrqjBVA4p_e2qPTavL16-1Mqv7AP-kYb4b_NP0i1pFkrieZxMbYUrChAy-745b5FYHMl2KBUljb7znwU4DiEej7sKrxcHNFXo5RC2tPRBWRXP2PxjxWi_P9zTd7MvITx2dyZVUkBqOcOl2ykUrZPW6CVR3G55peqFeT3y5zCg', flavor_id))
    # flavor = get_server_info('gAAAAABdpRhwm8DR6Yd4clbmRXquEsLhJ_sD53walnGxgVra4G7BnapscMRdvWe8R3nguVxOmL3lz1GIEKEL1bl_TVeGKoSj9Q2796tLu5QwJxiF442T0mkbEeYB9ncpXTWtAXML5Gonl_zXuysfHPA0xhfy3Cs904ahIPuz2Gr3yJKhiW-DGqQ', '7e07034a-caf0-421c-a0af-333936e6a15c')['server']['flavor']
    # print(get_flavor_info('gAAAAABdpRhwm8DR6Yd4clbmRXquEsLhJ_sD53walnGxgVra4G7BnapscMRdvWe8R3nguVxOmL3lz1GIEKEL1bl_TVeGKoSj9Q2796tLu5QwJxiF442T0mkbEeYB9ncpXTWtAXML5Gonl_zXuysfHPA0xhfy3Cs904ahIPuz2Gr3yJKhiW-DGqQ', flavor['id'])
    # token = get_other_token('admin','devstack','admin')
    # token = get_token('admin','devstack')
    # token = get_other_token('admin','devstack','0462be6630d042d086302acac64bead0')
    # print(get_stack_resource_list('gAAAAABdqH2dpRKewingV81VRJL4CeCQod69F3bpzcmxsinNcjTN3oxoA8CNen5RaP_dEE5jSGGqpfd4ET-TQcq5qFHYnru6xxjmKbEcBMHcGAZJJF5m8sPXATRA5gZeSmoG3A2bNFmHpS65UIVcgG3c9aNm7yTGkt2Vs7V84YgPOuAVb-CBWI4', 'admin'))
    # get_projectID(token)
    # get_server_list(token)
    # createAlarm(token, '7e07034a-caf0-421c-a0af-333936e6a15c', 0,0,0)
    # get_server_info(token, '7e07034a-caf0-421c-a0af-333936e6a15c')