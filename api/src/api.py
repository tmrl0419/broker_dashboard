import requests
import json
import datetime

url_base = "http://localhost/"

def get_projectID(token):
    url = url_base + "identity/v3/auth/projects"
    headers = {'Content-Type': 'application/json', 'X-Auth-Token': token}
    res = requests.get(url, headers=headers)
    body = res.json()

    projects_name = [x['name'] for x in body['projects'] if not x['name'] == "invisible_to_admin"]
    projects_uuid = [ x['id'] for x in body['projects'] if not x['name'] == "invisible_to_admin"]

    return projects_name, projects_uuid

# for ask what kinds of instances admin control on dashboard
def get_server_list(token):
    server_uuid = []
    server_names = []
    url = url_base + "compute/v2.1/servers"
    headers = {'Content-Type': 'application/json', 'X-Auth-Token': token}
    res = requests.get(url, headers=headers)
    body = res.json()
    server_uuid = [ x['id'] for x in body['servers']]
    server_names = [ x['name'] for x in body['servers']]
    return server_names, server_uuid

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
                     }
            }
        }

    # pixed header
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    # TODO get project id
    res = requests.post(url_base + 'identity/v3/auth/tokens', headers=headers, data=json.dumps(data), verify=True)
    token = res.headers['X-Subject-Token']
    return token

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

    res = requests.post(url_base + 'identity/v3/auth/tokens', headers=headers, data=json.dumps(data), verify=True)
    token = res.headers['X-Subject-Token']

    return token

def get_resource_list(token, instance_uuid):
    url = url_base + "metric/v1/resource/generic/%s"%(instance_uuid)
    headers = {'Content-Type': 'application/json, */*', 'X-Auth-Token':token}
    res = requests.get( url, headers = headers )
    body = res.json()
    print(body)
    return body

def get_mesuare_list(token, body):
    now = datetime.datetime.now()
    five_mins = datetime.timedelta(minutes=5)
    five_mins_ago = now - five_mins
    headers = {'Content-Type': 'application/json, */*', 'X-Auth-Token': token}
    PARAMS = {'start': None, 'granularity': None, 'resample': None, 'stop': None, 'aggregation': None, 'refresh': False}

    url = url_base + 'metric/v1/metric/%s/measures'%(body['metrics']['cpu_util'])
    res = requests.get(url = url, headers = headers, params= PARAMS )
    cpu = res.json()[-1][2]/100

    url = url_base + 'metric/v1/metric/%s/measures' % (body['metrics']['memory.usage'])
    res = requests.get(url=url, headers=headers, params=PARAMS)
    memory = res.json()[-1][2]/(1024)

    url = url_base + 'metric/v1/metric/%s/measures' % (body['metrics']['memory'])
    res = requests.get(url=url, headers=headers, params=PARAMS)
    memory /= res.json()[-1][2]/(1024)

    url = url_base + 'metric/v1/metric/%s/measures' % (body['metrics']['disk.usage'])
    res = requests.get(url=url, headers=headers, params=PARAMS)
    disk = res.json()[-1][2]/(8*1024*1024*1024)

    url = url_base + 'metric/v1/metric/%s/measures' % (body['metrics']['disk.root.size'])
    res = requests.get(url=url, headers=headers, params=PARAMS)
    disk /= res.json()[-1][2]

    return cpu, memory, disk

#'''openstack metric show'''

def get_server_info(token,server_uuid):
    headers = {'Content-Type': 'application/json', 'X-Auth-Token': token}
    url = url_base + 'compute/v2.1/servers/%s'%server_uuid
    res = requests.get(url=url, headers=headers)
    return res.json()

def get_flavor_info(token, flavorID):
    headers = {'Content-Type': 'application/json', 'X-Auth-Token': token}
    url = url_base + 'compute/v2.1/os-simple-tenant-usage/%s' % flavorID
    res = requests.get(url=url, headers=headers)
    print(res.__dict__)
    #return res.json()

if __name__ == '__main__':
    token = get_token('admin','devstack')
    get_projectID(token)
    get_server_list(token)
    get_server_info(token)
