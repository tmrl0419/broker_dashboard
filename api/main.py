import src.model as sm
import src.api as sa

#model = sm.load_model('model/model')


def login(id,passwd):
    token = token = sa.get_token(id,passwd)
    names, uuid = sa.get_projectID(token)
    #TODO : UI ask specific proejct name
    print("PLEASE SELECT PROJECT NAME")
    print(names)
    index = int(input())
    token = sa.get_other_token(id,passwd,uuid[index])
    print(token)
    return token

def server_info(token):
    servers_names, servers_uuid = sa.get_server_list(token)
    # TODO : UI ask specific server name
    print("PLEASE SELECT SERVER NAME")
    print(servers_names)
    index = int(input())
    server = sa.get_server_info(token, servers_uuid[index])
    return servers_uuid[index]
    #return data

def get_resource_info(token,uuid):
    res = sa.get_resource_list(token,uuid)
    return sa.get_mesuare_list(token, res)


if __name__ =='__main__':
    token = login('admin','devstack')
    #instance_uuid = server_info(token)
    #cpu, memory, disk = get_resource_info(token, instance_uuid)
    #print(cpu,memory,disk)
    #print("PLEASE INPUT RATING DATA")
    #rating = int(input())
    #sm.predict( cpu, memory, disk, rating, model)


