"""
From internet
"""

import requests

apiKey1 = "<MyApiKey>"
token = "<MyInfluxDBToken>"

server = "http://localhost:3000/"
url = server + "api/datasources/"
headers = {"Authorization":"Bearer "+apiKey1,
    "Content-Type":"application/json",
    "Accept":"application/json"
}

my_json = {
    "orgId":1,
    "name":"InfluxDB",
    "type":"influxdb",
    "typeLogoUrl":"",
    "access":"proxy",
    "url":"http://localhost:8086",
    "password":"",
    "user":"",
    "database":"",
    "basicAuth":False,
    "basicAuthUser":"",
    "basicAuthPassword":"",
    "withCredentials":False,
    "isDefault":False,
    "jsonData":{
        "defaultBucket":"test_bucket",
        "httpMode":"POST",
        "organization":"<OrgName>",
        "version":"Flux"
    },
    "secureJsonData":{
        "token": token
    },
    "version":2,
    "readOnly":False
}

r = requests.post(url = url.format('/api/datasources'), headers = headers, json = my_json, verify=False)

data = r.json()
print(data)
