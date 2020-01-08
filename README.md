## Openstack Broker System Dashboard
- This is a Broker System for Openstack based coding education flatform.

### Feature
- Dashboard supports managing coding class environment 

- Class manager can creat Virutal Machine(VM) which is coding class environment on dashboard

- Dashboard manage VM's resource by learning model based on user's feedback data.

- VM resource update trigged by aodh alarm, time interval, click


### Web Server
```sh
npm i
npm start
```

### Files Storage
- Files are stored in `api/public/files`
- whenever a file is edited, the changes are persisted in the server
- Synchronised among connected clients (browsers)

### Flask Server
'''sh
cd api
python3 server.py
'''



