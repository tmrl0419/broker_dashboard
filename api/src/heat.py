import yaml, codecs, copy, requests, json, time

import string
from random import *

rdlist = list(string.ascii_letters)
rdlist += list(string.digits)
rdlist += "_"
url_base = "http://localhost"
def createHash() -> str:
    pbuf = ""
    for j in range(0, randint(16, 25)):
        pbuf += choice(rdlist)
    return pbuf

def updateStack(project_id : str, stack_name : str, stack_id : str, HOT : dict, x_auth_token: str) :
    headers = { 'X-Auth-Token': x_auth_token, 'Content-Type': 'application/json' }
    url = url_base+ "/heat-api/v1/%s/stacks/%s/%s" % (project_id, stack_name, stack_id)
    param = { "template" : HOT }
    print("update here1")
    tmp = requests.put(url, headers=headers, data=json.dumps(param))
    print("update here2")
    print(tmp.json())


def extractTemplate(project_id : str, stack_name : str, stack_id : str, x_auth_token: str) -> dict :
    headers = { 'X-Auth-Token': x_auth_token, 'Content-Type': 'application/json' }
    url = url_base+ "/heat-api/v1/%s/stacks/%s/%s/template" % (project_id, stack_name, stack_id)
    tmp = requests.get(url, headers = headers)
    return tmp.json()

def saveTemplate(account : str, container : str, _object : str, HOT : dict, x_auth_token: str) :
    headers = { 'X-Auth-Token': x_auth_token, 'Content-Type': 'html/text' }
    url = url_base+ ":8080/v1/AUTH_%s/%s/%s" % (account, container, _object)
    tmp = requests.put(url, headers=headers, data=yaml.dump(HOT))
    return tmp

def createSnapshotVolume(project_id : str, volume_id : str, x_auth_token : str) -> str :
    headers = {'X-Auth-Token': x_auth_token, 'Content-Type': 'application/json'}
    param = {
        "snapshot": {
            "name": "%s_backup" % (volume_id),
            "description": "Backup for resizing",
            "volume_id": volume_id,
            "force": True,
            "metadata": {
                "key": "v3"
            }
        }
    }
    url = url_base+ "/volume/v3/%s/snapshots" % (project_id)
    tmp = requests.post(url, headers=headers, data=json.dumps(param))
    gotJson = tmp.json()
    print(gotJson)
    return gotJson["snapshot"]["id"]

## create the snapshot and returns its ID

def deleteSnapshotVolume(project_id : str, snapshot_id : str, x_auth_token : str) :
    headers = {'X-Auth-Token': x_auth_token, 'Content-Type': 'application/json'}
    url = url_base+ "/volume/v3/%s/snapshots/%s" % (project_id, snapshot_id)
    tmp = requests.delete(url, headers = headers)
    return tmp

    ## just delete the snapshot

def searchStackID(project_id : str, stack : str, x_auth_token : str) -> str :
    headers = {'X-Auth-Token': x_auth_token, 'Content-Type': 'application/json'}
    url = url_base+ "/heat-api/v1/%s/stacks" % (project_id)
    tmp = requests.get(url, headers = headers)

    lresult = tmp.json()
    searchResult = ""
    vlist = lresult["stacks"]

    for v in vlist :
        if stack in v["stack_name"] :
            searchResult = v["id"]
            break
    return searchResult

def getVolumeInfo(project_id : str, server_id : str, x_auth_token : str) -> dict :
    headers = {'X-Auth-Token': x_auth_token, 'Content-Type': 'application/json'}
    url = url_base+ "/compute/v2.1/servers/%s/os-volume_attachments" % (server_id)
    tmp = requests.get(url, headers = headers)
    lresult = tmp.json()
    vlist = lresult["volumeAttachments"]
    vid = vlist[0]["volumeId"]

    url_v = url_base+ "/volume/v3/%s/volumes/%s" % (project_id, vid)
    tmp_v = requests.get(url_v, headers = headers)
    vSearchResult = tmp_v.json()

    volumeRealName = vSearchResult["volume"]["name"]
    name_split = volumeRealName.split("-")
    print(name_split)
    return { "id" : vid, "name" : name_split[1] }

def flavorVolumeSize(project_id : str, flavor : str, x_auth_token) -> int :
    headers = {'X-Auth-Token': x_auth_token, 'Content-Type': 'application/json'}
    url = url_base+ "/compute/v2.1/flavors/detail"
    tmp = requests.get(url, headers = headers)

    lresult = tmp.json()
    flavorList = lresult["flavors"]

    volumeSize = 0
    for f in flavorList :
        if f["name"] == flavor :
            volumeSize = f["disk"]
            break

    return volumeSize

def copyTemplate(project_id : str, server_name : str, server_id : str, x_auth_token : str) -> dict :
    name_split = server_name.split("-")
    stack = name_split[0]
    instance = name_split[1]
    volumeInfo = getVolumeInfo(project_id, server_id, x_auth_token)

    newInstance = createHash()
    newVolume = newInstance + "_volume"
    newAttachment = newInstance + "_Attachment"
    snapshotID = createSnapshotVolume(project_id, volumeInfo["id"], x_auth_token)
    stackID = searchStackID(project_id, stack, x_auth_token)

    print(stack)
    HOT = extractTemplate(project_id, stack, stackID, x_auth_token)
    print(HOT)
    HOT["resources"][newInstance] = copy.deepcopy(HOT["resources"][instance])
    HOT["resources"][newVolume] = copy.deepcopy(HOT["resources"][volumeInfo["name"]])
    HOT["resources"][newVolume]["properties"]["snapshot_id"] = snapshotID
    HOT["resources"][newAttachment] = {
        "type": "OS::Cinder::VolumeAttachment",
        "properties": {
            "instance_uuid": { "get_resource": newInstance },
            "volume_id": { "get_resource": newVolume },
            "mountpoint": "/dev/vda"
        }
    }

    saveTemplate(project_id, "TemplateContainer", server_name+".yaml", yaml.dump(HOT), x_auth_token)
    print(HOT)
    updateStack(project_id, stack, stackID, HOT, x_auth_token)
    time.sleep(120)
    deleteSnapshotVolume(project_id, snapshotID, x_auth_token)

    return HOT


def resizeTemplate(project_id : str, server_name : str, server_id : str, flavor : str, x_auth_token : str) -> dict :
    print(project_id, server_name, server_id, flavor, x_auth_token)
    name_split = server_name.split("-")
    print(name_split)
    stack = name_split[0]
    instance = name_split[1]
    print(stack,instance)
    volumeInfo = getVolumeInfo(project_id, server_id, x_auth_token)
    print("resize here0")
    stackID = searchStackID(project_id, stack, x_auth_token)
    print("resize here1")
    snapshotID = createSnapshotVolume(project_id, volumeInfo["id"], x_auth_token)
    print("resize here2")

    newVolume = createHash() + "_volume"
    print("resize here3")
    HOT = extractTemplate(project_id, stack, stackID, x_auth_token)
    HOT["resources"][instance]["properties"]["flavor"] = flavor
    HOT["resources"][newVolume] = copy.deepcopy(HOT["resources"][volumeInfo["name"]])
    HOT["resources"][newVolume]["properties"]["size"] = flavorVolumeSize(project_id, flavor, x_auth_token)
    HOT["resources"][newVolume]["properties"]["snapshot_id"] = snapshotID
    HOT["resources"][instance+"_attachment"] = {
        "type": "OS::Cinder::VolumeAttachment",
        "properties": {
            "instance_uuid": { "get_resource": instance },
            "volume_id": { "get_resource": newVolume }
        }
    }
    print(HOT)
    print("resize here4")
    updateStack(project_id, stack, stackID, HOT, x_auth_token)
    time.sleep(240)
    del HOT["resources"][volumeInfo["name"]]
    print("resize here5")
    print(HOT)
    deleteSnapshotVolume(project_id, snapshotID, x_auth_token)
    updateStack(project_id, stack, stackID, HOT, x_auth_token)
    saveTemplate(project_id, "TemplateContainer", server_name+".yaml", yaml.dump(HOT), x_auth_token)
    print("resize here6")
    return HOT


# resizeTemplate(PID, "selab_test-hello-z3sza4r3he3p", "235ca8bb-4db1-4c44-84f9-0732e14d6513", "m1.medium", X_Auth_Token)


def createStack(project_id : str, server_name : str, stack_name : str, flavor : str, image : str, x_auth_token : str) :
    print(project_id, flavor, x_auth_token)
    size = flavorVolumeSize(project_id, flavor ,x_auth_token)
    print(size)
    template = {
        "heat_template_version" : "2018-08-31",
        "resources" : {
            server_name : {
                "type" : "OS::Nova::Server",
                "properties" : {
                    "flavor" : flavor,
                    "image" : image,
                    "networks" : [ {"network" : "public"} ]
                },
            },
            server_name + "_volume" : {
                "type" : "OS::Cinder::Volume",
                "properties" : {
                    "size" : size,
                    "volume_type" : "lvmdriver-1"
                },
            },
            server_name + "_attachment" : {
                "type" : "OS::Cinder::VolumeAttachment",
                "properties" : {
                    "instance_uuid" : { "get_resource" : server_name },
                    "volume_id" : { "get_resource" : server_name+"_volume" },
                },
            }
        }
    }
    
    param = { "template" : template, "stack_name" : stack_name }
    headers = { 'X-Auth-Token': x_auth_token, 'Content-Type': 'application/json' }
    url = url_base+"/heat-api/v1/%s/stacks" % (project_id)
    tmp = requests.post(url, headers=headers, data=json.dumps(param))
    print(tmp.json())

def newResource(project_id : str, name : str, img : str, flavor : str, size : int, x_auth_token : str) -> dict :
    name_split = name.split("-")
    stack = name_split[0]
    instance = name_split[1]
    volumeInfo = getVolumeInfo(project_id, server_id, x_auth_token)
    stackID = searchStackID(project_id, stack, x_auth_token)
    HOT = extractTemplate(project_id, stack, stackID, x_auth_token)

    HOT["resources"][name+"_instance"] = {
        "type": "OS::Nova::Server",
        "properties": {
            "flavor": flavor,
            "image": img,
            "networks": [{"network": "public"}]
        }
    }

    HOT["resources"][name+"_volume"] = {
        "type": "OS::Cinder::Volume",
        "properties": {
            "size": size,
            "volume_type": "lvmdriver-1"
        }
    }

    HOT["resources"][name+"_volumeattachment"] = {
        "type": "OS::Cinder::VolumeAttachment",
        "properties": {
            "instance_uuid": { "get_resource": name+"_instance" },
            "volume_id": { "get_resource": name+"_volume" },
            "mountpoint": "/dev/vda"
        }
    }

    updateStack(project_id, stack, stackID, HOT, x_auth_token)
    return HOT

'''
/v3/{project_id}/volumes/{volume_id} [GET] : Show a volume`s details, getVolumeName() : return volume["volume"]["name"].split("-")
/servers/{server_id}/os-volume_attachments : Get a volume`s details, getAttachedVolume() : return attachments["volumeAttachments"][0]["tag"] --> ?? is correct??
'''

if __name__ == '__main__':
    createStack('cf1aecc1d9b1432fb37d9c5eaa7c0fe6', 'test', 'test','ds1G','cirros-0.3.5-x86_64-disk', 'gAAAAABdyW0jQD_O_Dq5YXRqFPLQ86FDYgWHKxkyL0AOEmTwwpAIMS4YNUg48lawC_Zdm7mF8UfBUIlMi1m-TxwJhfE6Djoyqe52MnfP4MiqIsoILOlYf8v4JiWSSb7bcB4vj1xhP7iYfkmLDl5PT3YgbRKaN0lPSCHmXCtxiAKNPDp6auv5LFQ')