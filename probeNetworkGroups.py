#!/usr/bin/env python3
#Author:  Basil Morrison
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



def load_mongo():
    conn = Connection('mongodb://user:password@172.16.168.111/admin')
   
    return conn.nmx

def drop_mongodb(db):
    cur = db.nmx_networkgroups
    cur.drop()

def insert_logs_mongodb(db, data):
    cur = db.nmx_networkgroups
    try:
        cur.insert_many(data)
    except Exception as e:
        print('Insert into Mongo logs failed: {}'.format(e))
        sys.exit()
#########################################################

def get_data(url, nmx, token):
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
  NETWORKGRP = []
  nmxs = ["10.248.219.184", "10.248.219.188", "10.248.219.186", "10.248.219.190"]
  #nmxs = ["10.248.219.186"]
  db  = load_mongo()
  drop_mongodb(db)
  for i in nmxs:
    index = i
#    print(i)
    token = authenticate(index)
    networkGrps = get_data('/api/Topology/v2/NetworkGroups', index, token)
    if networkGrps:
        data = (json.dumps(networkGrps, indent=2, sort_keys=True))
        myList = json.loads(data)
        insert_logs_mongodb(db, myList)

############################



if __name__ == "__main__":
  try:
    main()
  except BaseException as e:
      print(e)
      sys.exit()

