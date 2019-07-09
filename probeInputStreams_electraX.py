#!/usr/bin/env python3
#Author: Basil Morrison

import time
import json
import requests
import logging
import sys
import pprint
import os, re
import operator
import traceback
import urllib3
from pymongo import MongoClient as Connection

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PORTLIST = []


def load_mongo():
    conn = Connection('mongodb://user:password@172.16.168.111/admin')
   
    return conn.nmx

def drop_mongodb(db):
    cur = db.nmx_input_electraX
    cur.drop()

def insert_logs_mongodb(db, data):
    cur = db.nmx_input_electraX
    try:
        cur.insert_many(data)
    except Exception as e:
        print('Insert into Mongo logs failed: {}'.format(e))
        sys.exit()


#########################################################

def get_data(url, nmx, token):
    #print (url)
    url2 = get_base_url() + nmx + url
    head = {
       'Accept': 'application/json',
       'Authorization': 'Bearer ' + token
    }
    try:
        groups = requests.get(url2, verify=False, headers=head)
        if not groups.content:
            return ''
        devices = json.loads(groups.content)
        devices = (json.dumps(devices, indent=2, sort_keys=True))
        json_parsed = json.loads(devices)
    except Exception as e:
        pprint.pprint(groups.content)
        print(traceback.format_exc())
        sys.exit()
    #return dev7, port7, dev8, port8
    return json_parsed

########################################################
def authenticate(index):
    username = get_username()
    password = get_password()
    data = { "username" : username, "password" : password }

    url = get_base_url() + index + '/api/Domain/v2/AccessToken'

    result = requests.post(url, json=data, verify=False)

    x = json.loads(result.content)

    token = x['access_token']

    return token

##############################
def get_base_url():
    return "https://"
#############################
def get_password():
    return 'password'

############################
def get_username():
    return 'user'

############################
def main():
  nmxs = ["10.x.x.x", "10.x.x.x", "10.x.x.x", "10.x.x.x"]
 
  db  = load_mongo()
  drop_mongodb(db)
  for i in nmxs:
    index = i
    #print (index)
    token = authenticate(index)
    deviceIDs = get_data('/api/Topology/v2/Devices', index, token)
    input_sources = {}
    try:
        for d in deviceIDs:
           if (d['DeviceInfo']['DeviceType']) in 'Electra X': 
                for i in range(0, len(d['PortList'])):
                    if (d['PortList'][i]['Name']) in 'GbE 5 Rx':
                            p5 = d['PortList'][i]['ID']
                            d5 = d['DeviceInfo']['ID']
                            #print (d5 + ',' + p5)
                            inputSources = get_data('/api/Services/v2/InputSources?device=' + d5 + '&port=' + p5, index, token)
                            #print(inputSources)
                            if inputSources:
                                data = (json.dumps(inputSources, indent=2, sort_keys=True))
                                myList = json.loads(data)
                                insert_logs_mongodb(db, myList)

    except:
           pass
       

############################

if __name__ == "__main__":
        main()

