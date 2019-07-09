#!/usr/bin/python3
#Author: Basil Morrison

import pprint
import requests
import sys, time, os, re, traceback
import argparse, json
from pymongo import MongoClient

client = MongoClient()

client = MongoClient("mongodb://user:password@172.x.x.x/admin")
db = client['nmx']

collection = db['nmx_orangeburg_devices']

def parseCommandLine(program_description="Get NMX Data"):
    # Instantiate the argument parser
    parser=argparse.ArgumentParser(description=program_description)
    parser.add_argument("-T","--type",help='service type',default=False)
    parser.add_argument("-x","--nmx",help='NMX Mgmt IP',default=False)
    parser.add_argument("-mc","--PriDestIp",help='update json',default=False)
    parser.add_argument("-src","--PriSrcIp",help='update json',default=False)

    # Parse all of the arguments
    parseargs=parser.parse_args()
    # Return the parsed arguments class
    return parseargs

def getEnc(listofElements):  #get unique values from list while keeping list in order
    uniqueList = []
    for elem in listofElements:
        if elem not in uniqueList:
            uniqueList.append(elem)
    return uniqueList

class checkAvailable:
    def __init__(self):
        self.autoBuildParams = []  #variable used to pass between classes.. it holds the info for the first available encoder where a service can be built
        self.cli = parseCommandLine()
        if not len(sys.argv) > 1:
            print('no argumuments provided.. try again')
        else:
            if self.cli.type in 'hd':
                 results, availableEncoders = self.getAvailableHD()
                 availableEncoder = getEnc(availableEncoders)[1]  #get first element of unique list
                 for d in results:
                     for key, value in d.items():
                         if value in availableEncoder:
                             self.autoBuildParams.append(d)
                 #for i in results:
                 #   print('')

            elif self.cli.type in 'sd':
                 results, availableEncoders = self.getAvailableSD()
                 availableEncoder = getEnc(availableEncoders)[0]  #get first element of unique list
                 for d in results:
                     for key, value in d.items():
                         if value in availableEncoder:
                             self.autoBuildParams.append(d)
                 #for i in results:
                 #   print('')
            child = buildChannel(self.autoBuildParams) #create child class used to build service and pass it the autoBuildParameters

    def getAvailableHD(self):
        availableEncoders = []
        results = []
        allHD = []
        for i in  collection.find({'DeviceInfo.Name': { '$regex': 'ElecEncoder' }}, {'DeviceInfo.Name': 1, '_id': 0}): #I modified the regex value to reflect the encoder names on Orangeburg NMX
            allHD.append(i['DeviceInfo']['Name'])
            #print (allHD)
        for j in allHD:
            if 'Switch' not in j:
                if 'BU' not in j:
                    if 'Group' not in j:
                        for k in  collection.find({'DeviceInfo.Name': str(j)}, {'nmxIPAddress': 1, 'DeviceInfo.ID': 1, 'DeviceInfo.Name': 1, 'serviceList.ServiceName': 1, 'PortList': 1, '_id': 0}):
                           totalProfiles = len(k['serviceList'])
                           totalPorts = len(k['PortList'])
                           for j in range(0, totalPorts):
                               temp = {}
                               if totalProfiles < 9:
                                   try:
                                       if k['PortList'][j]['Name'] in 'GbE 5 Rx':
                                           temp['inDevID'] = k['DeviceInfo']['ID']
                                           temp['inPort5ID'] = k['PortList'][j]['ID']
                                           temp['nmxIP'] = k['nmxIPAddress']
                                           temp['encoder'] = k['DeviceInfo']['Name']
                                           temp['slot'] = 'available'
                                       if k['PortList'][j]['Name'] in 'GbE 6 Rx':
                                           temp['inDevID'] = k['DeviceInfo']['ID']
                                           temp['inPort6ID'] = k['PortList'][j]['ID']
                                           temp['nmxIP'] = k['nmxIPAddress']
                                           temp['encoder'] = k['DeviceInfo']['Name']
                                           temp['slot'] = 'available'
                                       if k['PortList'][j]['Name'] in 'GbE 7 Tx':
                                           temp['outDevID'] = k['DeviceInfo']['ID']
                                           temp['outPort7ID'] = k['PortList'][j]['ID']
                                           temp['nmxIP'] = k['nmxIPAddress']
                                           temp['encoder'] = k['DeviceInfo']['Name']
                                           temp['slot'] = 'available'
                                       if k['PortList'][j]['Name'] in 'GbE 8 Tx':
                                           temp['outDevID'] = k['DeviceInfo']['ID']
                                           temp['outPort8ID'] = k['PortList'][j]['ID']
                                           temp['nmxIP'] = k['nmxIPAddress']
                                           temp['encoder'] = k['DeviceInfo']['Name']
                                           temp['slot'] = 'available'
                                           availableEncoders.append(k['DeviceInfo']['Name'])
                                   except KeyError:
                                           #print(traceback.format_exc())
                                           print (k['nmxIPAddress'] + ' ' + k['DeviceInfo']['Name'] + ' Port not found')
                               else:
                                           temp['nmxIP'] = k['nmxIPAddress']
                                           temp['encoder'] = k['DeviceInfo']['Name']
                                           temp['slot'] = 'full'
                               if temp:
                                  results.append(temp)
        return results, availableEncoders

    def getAvailableSD(self):
        availableEncoders = []
        results = []
        allSD = []
        for i in  collection.find({'DeviceInfo.Name': { '$regex': 'ElecEncoder' }}, {'DeviceInfo.Name': 1, '_id': 0}):
            allSD.append(i['DeviceInfo']['Name'])
            #print (allSD)
        for j in allSD:
            if 'Switch' not in j:
                if 'BU' not in j:
                    if 'Group' not in j:
                        for k in  collection.find({'DeviceInfo.Name': str(j)}, {'nmxIPAddress': 1, 'DeviceInfo.ID': 1, 'DeviceInfo.Name': 1, 'serviceList.ServiceName': 1, 'PortList': 1, '_id': 0}):
                           totalProfiles = len(k['serviceList'])
                           totalPorts = len(k['PortList'])
                           for j in range(0, totalPorts):
                               temp = {}
                               if totalProfiles < 9:
                                   try:
                                       if k['PortList'][j]['Name'] in 'GbE 5 Rx':
                                           temp['inDevID'] = k['DeviceInfo']['ID']
                                           temp['inPort5ID'] = k['PortList'][j]['ID']
                                           temp['nmxIP'] = k['nmxIPAddress']
                                           temp['encoder'] = k['DeviceInfo']['Name']
                                           temp['slot'] = 'available'
                                       if k['PortList'][j]['Name'] in 'GbE 6 Rx':
                                           temp['inDevID'] = k['DeviceInfo']['ID']
                                           temp['inPort6ID'] = k['PortList'][j]['ID']
                                           temp['nmxIP'] = k['nmxIPAddress']
                                           temp['encoder'] = k['DeviceInfo']['Name']
                                           temp['slot'] = 'available'
                                       if k['PortList'][j]['Name'] in 'GbE 7 Tx':
                                           temp['outDevID'] = k['DeviceInfo']['ID']
                                           temp['outPort7ID'] = k['PortList'][j]['ID']
                                           temp['nmxIP'] = k['nmxIPAddress']
                                           temp['encoder'] = k['DeviceInfo']['Name']
                                           temp['slot'] = 'available'
                                       if k['PortList'][j]['Name'] in 'GbE 8 Tx':
                                           temp['outDevID'] = k['DeviceInfo']['ID']
                                           temp['outPort8ID'] = k['PortList'][j]['ID']
                                           temp['nmxIP'] = k['nmxIPAddress']
                                           temp['encoder'] = k['DeviceInfo']['Name']
                                           temp['slot'] = 'available'
                                           availableEncoders.append(k['DeviceInfo']['Name'])

                                   except KeyError:
                                           #print(traceback.format_exc())
                                           print (k['nmxIPAddress'] + ' ' + k['DeviceInfo']['Name'] + ' Port not found')
                               else:
                                           temp['nmxIP'] = k['nmxIPAddress']
                                           temp['encoder'] = k['DeviceInfo']['Name']
                                           temp['slot'] = 'full'
                               if temp:
                                  results.append(temp)
        return results, availableEncoders

class buildChannel:
    def __init__(self, autoBuildParams): #This is used to create the service on the first encoder with an available slot
        self.cli = parseCommandLine()

        if self.cli.type in 'hd':
            hd_abr = self.create_HD_ABR(autoBuildParams)
            #print(hd_abr)

        if self.cli.type in 'sd':
            sd_abr = self.create_SD_ABR(autoBuildParams)
            #print(sd_abr)

    def create_HD_ABR(self, autoBuildParams):
        for line in autoBuildParams:
            #print(line)
            if 'inPort5ID' in line:
                prt5id = line['inPort5ID']
            if 'outPort7ID' in line:
                prt7id = line['outPort7ID']
            if 'outPort8ID' in line:
                prt8id = line['outPort8ID']
            if 'inPort6ID' in line:
                prt6id = line['inPort6ID']
            if 'inDevID' in line:
                devid = line['inDevID']
       
        def postService(token, devid, prt5id):
            data1  = {"Description": "Discovery", "DeviceId":  str(devid), "DevicePortId": str(prt5id), "IpAddressStart": str(self.cli.PriDestIp), "IpAddressEnd": str(self.cli.PriDestIp),  "IpPortStart": 10000, "IpPortEnd": 10000, "SsmSource": [str(self.cli.PriSrcIp)]} 
            head = {
                     'Content-Type': 'application/json',
                     'Authorization': 'Bearer ' + token
                    }
            url2 = get_base_url() + '/api/SourceDiscovery/v2/Discovery'
            ing = requests.post(url2, json=data1, verify=False, headers=head)
            ingest = json.loads(ing.content)
            res = ingest["ID"]
            res = res.strip('{')
            res = res.strip('}')
            url3 = get_base_url() + '/api/SourceDiscovery/v2/Discovery/' + res + '/Status'
            stat = requests.get(url3, verify=False, headers=head)
            while 'Pending' in json.loads(stat.content)['Status']:
                stat = requests.get(url3, verify=False, headers=head)
                time.sleep(1)
            url3 = get_base_url() + '/api/SourceDiscovery/v2/Discovery/' + res + '/Result'
            stat = requests.get(url3, verify=False, headers=head)
            discoveredSources = json.loads(stat.content)
            return discoveredSources
        def get_username():
            return 'user'
        def get_base_url():
            return "https://" + self.cli.nmx
        def get_password():
            return 'password'
        def authenticate():
            username = get_username()
            password = get_password()
            data = { "username" : username, "password" : password }
            url = get_base_url() + '/api/Domain/v2/AccessToken'
            result = requests.post(url, json=data, verify=False)
            x = json.loads(result.content)
            token = x['access_token']
            return token
        token = authenticate()
        post = postService(token, devid, prt5id)
        if post['InputSourceList']:
            print (post['InputSourceList'])
        else:
            print(self.cli.PriDestIp + '@' + self.cli.PriSrcIp + ' was not found on the input.. Please verify your multicast/source addr and try again..')


    def create_SD_ABR(self, autoBuildParams):
        for line in autoBuildParams:
            #print(line)
            if 'inPort5ID' in line:
                prt5id = line['inPort5ID']
            if 'outPort7ID' in line:
                prt7id = line['outPort7ID']
            if 'outPort8ID' in line:
                prt8id = line['outPort8ID']
            if 'inPort6ID' in line:
                prt6id = line['inPort6ID']
            if 'inDevID' in line:
                devid = line['inDevID']

        def postService(token, devid, prt5id):
            data1  = {"Description": "Discovery", "DeviceId":  str(devid), "DevicePortId": str(prt5id), "IpAddressStart": str(self.cli.PriDestIp), "IpAddressEnd": str(self.cli.PriDestIp),  "IpPortStart": 10000, "IpPortEnd": 10000, "SsmSource": [str(self.cli.PriSrcIp)]}
            head = {
                     'Content-Type': 'application/json',
                     'Authorization': 'Bearer ' + token
                    }
            url2 = get_base_url() + '/api/SourceDiscovery/v2/Discovery'
            ing = requests.post(url2, json=data1, verify=False, headers=head)
            ingest = json.loads(ing.content)
            res = ingest["ID"]
            res = res.strip('{')
            res = res.strip('}')
            url3 = get_base_url() + '/api/SourceDiscovery/v2/Discovery/' + res + '/Status'
            stat = requests.get(url3, verify=False, headers=head)
            while 'Pending' in json.loads(stat.content)['Status']:
                stat = requests.get(url3, verify=False, headers=head)
                time.sleep(1)
            url3 = get_base_url() + '/api/SourceDiscovery/v2/Discovery/' + res + '/Result'
            stat = requests.get(url3, verify=False, headers=head)
            discoveredSources = json.loads(stat.content)
            return discoveredSources
        def get_username():
            return 'user'
        def get_base_url():
            return "https://" + self.cli.nmx
        def get_password():
            return 'password'
        def authenticate():
            username = get_username()
            password = get_password()
            data = { "username" : username, "password" : password }
            url = get_base_url() + '/api/Domain/v2/AccessToken'
            result = requests.post(url, json=data, verify=False)
            x = json.loads(result.content)
            token = x['access_token']
            return token
        token = authenticate()
        post = postService(token, devid, prt5id)
        if post['InputSourceList']:
            print (post['InputSourceList'])
        else:
            print(self.cli.PriDestIp + '@' + self.cli.PriSrcIp + ' was not found on the input.. Please verify your multicast/source addr and try again..')


checkAvailable()

