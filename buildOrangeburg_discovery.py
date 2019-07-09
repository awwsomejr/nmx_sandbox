#!/usr/bin/python3
#Author: Basil Morrison

import pprint
import requests
import sys, os, re, traceback
import argparse, json
import time
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
    parser.add_argument("-e","--encoder",help='Encoder name',default=False)
    parser.add_argument("-ip","--inport",help='Encoder name',default=False)
    parser.add_argument("-op","--outport",help='Encoder name',default=False)
    parser.add_argument("-sn","--serviceName",help='update json',default=False)
    parser.add_argument("-mc","--PriDestIp",help='update json',default=False)
    parser.add_argument("-src","--PriSrcIp",help='update json',default=False)
    ###############################
    #Input ABR params
    parser.add_argument("-abrmc","--abrPriDestIp",help='update json',default=False)
    parser.add_argument("-abrsrc","--abrPriSrcIp",help='update json',default=False)
    parser.add_argument("-abrpcrpid","--abrPcrPid",help='update json',default=False)
    parser.add_argument("-abrpmtpid","--abrPmtPid",help='update json',default=False)
    parser.add_argument("-abrsvcnum","--abrSvcNum",help='update json',default=False)
    parser.add_argument("-abrprov","--abrProvider",help='update json',default=False)
    parser.add_argument("-abrpid","--abrPid0",help='update json',default=False)
    parser.add_argument("-abrpidd","--abrPid1",help='update json',default=False)
    parser.add_argument("-abrpiddd","--abrPid2",help='update json',default=False)
    parser.add_argument("-abrpidddd","--abrPid3",help='update json',default=False)
    parser.add_argument("-abrpiddddd","--abrPid4",help='update json',default=False)
    parser.add_argument("-abrpidddddd","--abrPid5",help='update json',default=False)
    parser.add_argument("-abrpiddddddd","--abrPid6",help='update json',default=False)
    parser.add_argument("-abrtrid","--abrTrId",help='update json',default=False)
    parser.add_argument("-abrnetid","--abrNetId",help='update json',default=False)

    # Parse all of the arguments
    parseargs=parser.parse_args()
    # Return the parsed arguments class
    return parseargs

class checkAvailable:
    def __init__(self):
        self.autoBuildParams = []  #variable used to pass between classes.. it holds the info for the first available encoder where a service can be built

        self.cli = parseCommandLine()
        if not len(sys.argv) > 1:
            print('no argumuments provided.. try again')
        else:
            if self.cli.type in 'hd':
                self.token = 'ElecEncoder'
                self.getIds(self.token)

            elif self.cli.type in 'sd':
                 self.token = 'ElecEncoder'
                 self.getIds(self.token)

    def getIds(self, token):
        results = []
        ALL = []
        for i in  collection.find({'DeviceInfo.Name': { '$regex': token }}, {'DeviceInfo.Name': 1, '_id': 0}): #I modified the regex value to reflect the encoder names on Orangeburg NMX
            ALL.append(i['DeviceInfo']['Name'])
            #print (ALL)
        for j in ALL:
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
                                   except KeyError:
                                           #print(traceback.format_exc())
                                           print (k['nmxIPAddress'] + ' ' + k['DeviceInfo']['Name'] + ' Port not found')
                               else:
                                           temp['nmxIP'] = k['nmxIPAddress']
                                           temp['encoder'] = k['DeviceInfo']['Name']
                                           temp['slot'] = 'full'
                               if temp:
                                  if temp not in results:
                                     results.append(temp)
        temp = []
        for d in results:
            for key, value in d.items():
              if value in self.cli.encoder:
                if d['slot'] in 'available':
                  temp.append(d)
        if '5' in self.cli.inport:
           in_device = temp[0]['inDevID']
           in_port = temp[0]['inPort5ID']
        if '6' in self.cli.inport:
           in_device = temp[1]['inDevID']
           in_port = temp[1]['inPort6ID']
        if '7' in self.cli.outport:
           out_device = temp[2]['outDevID']
           out_port = temp[2]['outPort7ID']
        if '8' in self.cli.outport:
           out_device = temp[3]['outDevID']
           out_port = temp[3]['outPort8ID']

        child = buildChannel(in_device, in_port, out_device, out_port)

class buildChannel:
    def __init__(self, in_device, in_port, out_device, out_port):
        self.cli = parseCommandLine()

        if self.cli.type in 'hd':
            hd_abr = self.create_HD(in_device, in_port, out_device, out_port)
            print(hd_abr)

        if self.cli.type in 'sd':
            sd_abr = self.create_SD(in_device, in_port, out_device, out_port)
            print(sd_abr)


    def create_HD(self, in_device, in_port, out_device, out_port):

        fh = open('new_hd_abr_Template.json', 'r')
        data = fh.read()
        data = eval(data)
        data['InputSourceList'][0]['DeviceId'] = in_device
        data['InputSourceList'][0]['DevicePortId'] = in_port
        data['OutputTransportList'][0]['DeviceId'] = out_device
        data['OutputTransportList'][0]['DevicePortId'] = out_port
        typ = 'HD'
        
        inputSourceDiscovery = self.discoverService(in_device, in_port, out_device, out_port)
        prDestIP, prDestPort, prSrcIP, transpID, audPIDS, dpiPID, datPID, vidPID, PMTPid, PCRPid, Provider, ServiceNumber, ServiceName  = self.getInputParameters(inputSourceDiscovery)
        updatedTemplate = self.modify_HD_ABR_template(prDestIP, prDestPort, prSrcIP, transpID, audPIDS, dpiPID, datPID, vidPID, PMTPid, PCRPid, Provider, ServiceNumber, ServiceName, typ, data)
        post = self.postService(updatedTemplate)

    def create_SD(self, in_device, in_port, out_device, out_port):

        fh = open('new_sd_abr_Template.json', 'r')
        data = fh.read()
        data = eval(data)
        data['InputSourceList'][0]['DeviceId'] = in_device
        data['InputSourceList'][0]['DevicePortId'] = in_port
        data['OutputTransportList'][0]['DeviceId'] = out_device
        data['OutputTransportList'][0]['DevicePortId'] = out_port
        typ = 'SD'

        inputSourceDiscovery = self.discoverService(in_device, in_port, out_device, out_port)
        prDestIP, prDestPort, prSrcIP, transpID, audPIDS, dpiPID, datPID, vidPID, PMTPid, PCRPid, Provider, ServiceNumber, ServiceName  = self.getInputParameters(inputSourceDiscovery)
        updatedTemplate = self.modify_HD_ABR_template(prDestIP, prDestPort, prSrcIP, transpID, audPIDS, dpiPID, datPID, vidPID, PMTPid, PCRPid, Provider, ServiceNumber, ServiceName, typ, data)
        post = self.postService(updatedTemplate)


    def postService(self, updatedTemplate):
        def post(token, updatedTemplate):
            data  = (updatedTemplate)
            head = {
                     'Content-Type': 'application/json',
                     'Authorization': 'Bearer ' + token
                    }
            url2 = get_base_url() + '/api/ServiceConfiguration/v2/Services'
            r = requests.post(url2, json=data, verify=False, headers=head)
            print (r.status_code, r.reason)
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
        post = post(token, updatedTemplate)

    def modify_HD_ABR_template(self, prDestIP, prDestPort, prSrcIP, transpID, audPIDS, dpiPID, datPID, vidPID, PMTPid, PCRPid, Provider, ServiceNumber, ServiceName, typ, data):
        ###Input######## 
        data['InputSourceList'][0]['Name'] = ServiceName 
        data['InputSourceList'][0]['InputTransport']['Name'] = ServiceName 
        data['InputSourceList'][0]['InputIPConfigInfo']['PrimarySocketDestIP'] = prDestIP 
        data['InputSourceList'][0]['InputIPConfigInfo']['PrimarySocketDestPort'] = prDestPort 
        data['InputSourceList'][0]['InputIPConfigInfo']['PrimarySocketSrcIP'] = prSrcIP 
        data['InputSourceList'][0]['InputServiceList'][0]['Name'] = ServiceName 
        data['InputSourceList'][0]['InputServiceList'][0]['PCRPid'] = PCRPid 
        data['InputSourceList'][0]['InputServiceList'][0]['PMTPid'] = PMTPid 
        data['InputSourceList'][0]['InputServiceList'][0]['ServiceNumber'] = ServiceNumber 
        data['InputSourceList'][0]['InputServiceList'][0]['Provider'] = Provider
        num2 = len(data['InputSourceList'][0]['InputStreamList'])
        for i in range(0, num2):
            if 'Video' in data['InputSourceList'][0]['InputStreamList'][i]['StreamType']:
                data['InputSourceList'][0]['InputStreamList'][i]['PID'] = vidPID
                data['InputSourceList'][0]['InputStreamList'][i]['Name'] = ServiceName + ' Video'
            if 'Data' in data['InputSourceList'][0]['InputStreamList'][i]['StreamType']:
                data['InputSourceList'][0]['InputStreamList'][i]['PID'] = datPID
                data['InputSourceList'][0]['InputStreamList'][i]['Name'] = ServiceName + ' Data'
            else:
                datPID = 0
            if 'DPI' in data['InputSourceList'][0]['InputStreamList'][i]['StreamType']:
                data['InputSourceList'][0]['InputStreamList'][i]['PID'] = dpiPID
                data['InputSourceList'][0]['InputStreamList'][i]['Name'] = ServiceName + ' DPI'
            else:
                dpiPID = 0
        num3 = len(audPIDS)
        for i in range(0, num3):
            if 'Audio' in data['InputSourceList'][0]['InputStreamList'][i]['StreamType']:
                data['InputSourceList'][0]['InputStreamList'][i]['PID'] = audPIDS[i]
                data['InputSourceList'][0]['InputStreamList'][i]['Name'] = ServiceName + ' Audio' + str(i)
        ###Output########
        data['OutputTransportList'][0]['Name'] = ServiceName + ' HD ABR'
        data['OutputTransportList'][0]['OutputServiceList'][0]['Name'] = ServiceName + ' ABR'
        data['OutputTransportList'][0]['OutputServiceList'][0]['PCRPid'] = int(self.cli.abrPcrPid)
        data['OutputTransportList'][0]['OutputServiceList'][0]['ServiceNumber'] = ServiceNumber
        data['OutputTransportList'][0]['OutputServiceList'][0]['Provider'] = self.cli.abrProvider
        num1 = len(data['OutputTransportList'][0]['MWProfileList'])
        num2 = len(data['OutputTransportList'][0]['MWProfileList'][0]['StreamList'])
        for i in range(0, num1):
            data['OutputTransportList'][0]['MWProfileList'][i]['DestinationIPAddress'] = self.cli.abrPriDestIp
            data['OutputTransportList'][0]['MWProfileList'][i]['SourceIpAddress'] = self.cli.abrPriSrcIp
            for j in range(0, num2):
                data['OutputTransportList'][0]['MWProfileList'][i]['StreamList'][j]['Name'] = ServiceName + ' ABR'
                data['OutputTransportList'][0]['MWProfileList'][i]['StreamList'][j]['PID'] = int(eval('self.cli.abrPid'+str(j)))
        data['OutputTransportList'][0]['TransportInfo']['NetworkID'] = int(self.cli.abrNetId)
        data['OutputTransportList'][0]['TransportInfo']['TransportID'] = int(self.cli.abrTrId)
        return data

    def getInputParameters(self, inputSourceDiscovery):
        audPIDS = []
        num = len(inputSourceDiscovery['InputSourceList'][0]['InputServiceList'])
        num2 = len(inputSourceDiscovery['InputSourceList'][0]['InputStreamList'])
        inpTrans = inputSourceDiscovery['InputSourceList'][0]['InputTransport']
        inpConf = inputSourceDiscovery['InputSourceList'][0]['InputIPConfigInfo']
        counter = 0
        for i in range(0, num):
            if self.cli.serviceName in inputSourceDiscovery['InputSourceList'][0]['InputServiceList'][i]['Name']:
                counter += 1
                ServiceNumber = inputSourceDiscovery['InputSourceList'][0]['InputServiceList'][i]['ServiceNumber']
                ServiceName = inputSourceDiscovery['InputSourceList'][0]['InputServiceList'][i]['Name']
                Provider = inputSourceDiscovery['InputSourceList'][0]['InputServiceList'][i]['Provider']
                PCRPid = inputSourceDiscovery['InputSourceList'][0]['InputServiceList'][i]['PCRPid']
                PMTPid = inputSourceDiscovery['InputSourceList'][0]['InputServiceList'][i]['PMTPid']
                servid = inputSourceDiscovery['InputSourceList'][0]['InputServiceList'][i]['ID']
                for i in range(0, num2):
                   if str(servid) in inputSourceDiscovery['InputSourceList'][0]['InputStreamList'][i]['ServiceIDs']:
                       if 'Video' in inputSourceDiscovery['InputSourceList'][0]['InputStreamList'][i]['StreamType']:
                           vidPID = inputSourceDiscovery['InputSourceList'][0]['InputStreamList'][i]['PID']
                       if 'Data' in inputSourceDiscovery['InputSourceList'][0]['InputStreamList'][i]['StreamType']:
                           datPID = inputSourceDiscovery['InputSourceList'][0]['InputStreamList'][i]['PID']
                       else:
                           datPID = 0
                       if 'DPI' in inputSourceDiscovery['InputSourceList'][0]['InputStreamList'][i]['StreamType']:
                           dpiPID = inputSourceDiscovery['InputSourceList'][0]['InputStreamList'][i]['PID']
                       else:
                           dpiPID = 0
                for i in range(0, num2):
                    if str(servid) in inputSourceDiscovery['InputSourceList'][0]['InputStreamList'][i]['ServiceIDs']:
                        if 'Audio' in inputSourceDiscovery['InputSourceList'][0]['InputStreamList'][i]['StreamType']:
                            audPIDS.append(inputSourceDiscovery['InputSourceList'][0]['InputStreamList'][i]['PID'])
        if counter == 0:
            print('\"' + self.cli.serviceName + '\"' + ' was not found on the input.. Please verify your multicast addr, source addr, & servicename and try again..')
            sys.exit()
        transpID = inputSourceDiscovery['InputSourceList'][0]['InputTransport']['TransportID']
        prSrcIP = inputSourceDiscovery['InputSourceList'][0]['InputIPConfigInfo']['PrimarySocketSrcIP']
        prDestIP = inputSourceDiscovery['InputSourceList'][0]['InputIPConfigInfo']['PrimarySocketDestIP']
        prDestPort = inputSourceDiscovery['InputSourceList'][0]['InputIPConfigInfo']['PrimarySocketDestPort']
        return prDestIP, prDestPort, prSrcIP, transpID, audPIDS, dpiPID, datPID, vidPID, PMTPid, PCRPid, Provider, ServiceNumber, ServiceName

    def discoverService(self, in_device, in_port, out_device, out_port):
        def disc(token, in_device, in_port, out_device, out_port):
            res = {}
            data1 = {"Description": "Discovery", "DeviceId":  str(in_device), "DevicePortId": str(in_port), "IpAddressStart": str(self.cli.PriDestIp), "IpAddressEnd": str(self.cli.PriDestIp),  "IpPortStart": 10000, "IpPortEnd": 10000, "SsmSource": [str(self.cli.PriSrcIp)]}
            head = {
                     'Accept': 'application/json',
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
        discoveredSources = disc(token, in_device, in_port, out_device, out_port)
        return discoveredSources

checkAvailable()

