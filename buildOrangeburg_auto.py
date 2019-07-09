#!/usr/bin/python3
#Author: Basil Morrison

import pprint
import requests
import sys, os, re, traceback
import argparse, json
from pymongo import MongoClient

client = MongoClient()

client = MongoClient("mongodb://user:password@172.16.100.11/admin")
db = client['nmx']

collection = db['nmx_orangeburg_devices']

def parseCommandLine(program_description="Get NMX Data"):
    # Instantiate the argument parser
    parser=argparse.ArgumentParser(description=program_description)
    parser.add_argument("-T","--type",help='service type',default=False)
    parser.add_argument("-x","--nmx",help='NMX Mgmt IP',default=False)
    parser.add_argument("-e","--encoder",help='Encoder name',default=False)

    parser.add_argument("-bkmc","--bkDestIp",help='update json',default=False)
    parser.add_argument("-bkpt","--bkDestPt",help='update json',default=False)
    parser.add_argument("-bksr","--bkDestSrcIp",help='update json',default=False)
    parser.add_argument("-prip","--priDestIp",help='update json',default=False)
    parser.add_argument("-prpt","--priDestPt",help='update json',default=False)
    parser.add_argument("-prsr","--priSrcIp",help='update json',default=False)
    #Input params
    parser.add_argument("-sn","--serviceName",help='update json',default=False)
    parser.add_argument("-slpcr","--svcListPcr0",help='update json',default=False)
    parser.add_argument("-slpid","--svcListPid0",help='update json',default=False)
    parser.add_argument("-slnum","--svcListNum0",help='update json',default=False)
    parser.add_argument("-slpcrr","--svcListPcr1",help='update json',default=False)
    parser.add_argument("-slpidd","--svcListPid1",help='update json',default=False)
    parser.add_argument("-slnumm","--svcListNum1",help='update json',default=False)
    parser.add_argument("-trid","--transptId",help='update json',default=False)
    parser.add_argument("-mpa","--mp2a1",help='update json',default=False)
    parser.add_argument("-mpaa","--mp2a2",help='update json',default=False)
    parser.add_argument("-mpaaa","--mp2a3",help='update json',default=False)
    parser.add_argument("-mpv","--mp2v1",help='update json',default=False)
    parser.add_argument("-avca","--avca1",help='update json',default=False)
    parser.add_argument("-avcaa","--avca2",help='update json',default=False)
    parser.add_argument("-avcaaa","--avca3",help='update json',default=False)
    parser.add_argument("-avcv","--avcv1",help='update json',default=False)
    #Output params
    parser.add_argument("-opcrpid","--pcrPid0",help='update json',default=False)
    parser.add_argument("-opmtpid","--pmtPid0",help='update json',default=False)
    parser.add_argument("-opmtPID","--pmtPid",help='update json',default=False)
    parser.add_argument("-osdtpid","--sdtPid",help='update json',default=False)
    parser.add_argument("-oaudpid","--audPid1",help='update json',default=False)
    parser.add_argument("-ovidpid","--vidPid1",help='update json',default=False)
    parser.add_argument("-oaudpidd","--audPid2",help='update json',default=False)
    parser.add_argument("-opatpid","--patPid1",help='update json',default=False)
    parser.add_argument("-onetid","--netId",help='update json',default=False)
    parser.add_argument("-oscvnum","--svcNum",help='update json',default=False)
    parser.add_argument("-outMulti","--omulti",help='update json',default=False)
    parser.add_argument("-outDprt","--odstprt1",help='update json',default=False)
    parser.add_argument("-outSrc","--osrcaddr",help='update json',default=False)
    parser.add_argument("-outSprt","--osrcpt1",help='update json',default=False)
    parser.add_argument("-outDprtt","--odstprt2",help='update json',default=False)
    parser.add_argument("-outSrcc","--osrcpt2",help='update json',default=False)
    parser.add_argument("-otrid","--trId",help='update json',default=False)

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
        for i in  collection.find({'DeviceInfo.Name': { '$regex': 'SD' }}, {'DeviceInfo.Name': 1, '_id': 0}):
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
            print(hd_abr)

        if self.cli.type in 'sd':
            sd_abr = self.create_SD_ABR(autoBuildParams)
            print(sd_abr)

        if self.cli.type in 'cbr':
            cbr = self.create_CBR(autoBuildParams)
            print(cbr)

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
        fh = open('hd_abr_Template.txt', 'r')
        data = fh.read()
        data = eval(data)
        data['InputSourceList'][0]['DeviceId'] = devid
        data['InputSourceList'][0]['DevicePortId'] = prt5id
        data['OutputTransportList'][0]['DeviceId'] = devid
        data['OutputTransportList'][0]['DevicePortId'] = prt7id
        typ = 'HD'

        result = self.modify_HD_template(data, typ)

        ######################
        ### post service #####
        ######################
        def postService(token, result):
            data  = (result)
            head = {
                     'Content-Type': 'application/json',
                     'Authorization': 'Bearer ' + token
                    }
            url2 = get_base_url() + '/api/ServiceConfiguration/v2/Services'
            r = requests.post(url2, json=data, verify=False, headers=head)
            print (r.status_code, r.reason)

        def authenticate():
             username = get_username()
             password = get_password()
             data = { "username" : username, "password" : password }
             url = get_base_url() + '/api/Domain/v2/AccessToken'
             result = requests.post(url, json=data, verify=False)
             x = json.loads(result.content)
             token = x['access_token']
             return token
        def get_base_url():
              return "https://10.250.69.221"
        def get_password():
             return 'harmonic'
        def get_username():
             return 'Administrator'
        token = authenticate()
        post = postService(token, result)
        #########################
        ########################


        return result

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
        fh = open('sd_abr_Template.txt', 'r')
        data = fh.read()
        data = eval(data)
        data['InputSourceList'][0]['DeviceId'] = devid
        data['InputSourceList'][0]['DevicePortId'] = prt5id
        data['OutputTransportList'][0]['DeviceId'] = devid
        data['OutputTransportList'][0]['DevicePortId'] = prt7id

        return data

    def create_CBR(self, autoBuildParams):
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
        fh = open('/home/dsops/scripts/nmx/SANDBOX/cbr_Template.txt', 'r')
        data = fh.read()
        data = eval(data)
        data['InputSourceList'][0]['DeviceId'] = devid
        data['InputSourceList'][0]['DevicePortId'] = prt5id
        data['OutputTransportList'][0]['DeviceId'] = devid
        data['OutputTransportList'][0]['DevicePortId'] = prt7id

        #print(data)
        return data

    def modify_HD_template(self, data, typ):
       ###################   INPUT   #################################################################################
        data['InputSourceList'][0]['InputIPConfigInfo']['BackupSocketDestIP'] = self.cli.bkDestIp
        data['InputSourceList'][0]['InputIPConfigInfo']['BackupSocketDestPort'] = int(self.cli.bkDestPt)
        data['InputSourceList'][0]['InputIPConfigInfo']['BackupSocketSrcIP'] = self.cli.bkDestSrcIp
        data['InputSourceList'][0]['InputIPConfigInfo']['PrimarySocketDestIP'] = self.cli.priDestIp
        data['InputSourceList'][0]['InputIPConfigInfo']['PrimarySocketDestPort'] = int(self.cli.priDestPt)
        data['InputSourceList'][0]['InputIPConfigInfo']['PrimarySocketSrcIP'] = self.cli.priSrcIp
        #
        data['InputSourceList'][0]['InputServiceList'][0]['Name'] = self.cli.serviceName + ' ' + typ + ' MP2'
        data['InputSourceList'][0]['InputServiceList'][0]['PCRPid'] = int(self.cli.svcListPcr0)
        data['InputSourceList'][0]['InputServiceList'][0]['PMTPid'] = int(self.cli.svcListPid0)
        data['InputSourceList'][0]['InputServiceList'][0]['ServiceNumber'] = int(self.cli.svcListNum0)
        data['InputSourceList'][0]['InputServiceList'][1]['Name'] = self.cli.serviceName + ' ' + typ + ' AVC'
        data['InputSourceList'][0]['InputServiceList'][1]['PCRPid'] = int(self.cli.svcListPcr1)
        data['InputSourceList'][0]['InputServiceList'][1]['PMTPid'] = int(self.cli.svcListPid1)
        data['InputSourceList'][0]['InputServiceList'][1]['ServiceNumber'] = int(self.cli.svcListNum1)
        #
        data['InputSourceList'][0]['InputStreamList'][0]['Name'] = self.cli.serviceName + ' ' + typ + ' MP2 AC-3 Eng Audio'
        data['InputSourceList'][0]['InputStreamList'][0]['PID'] = int(self.cli.mp2a1)
        data['InputSourceList'][0]['InputStreamList'][1]['Name'] = self.cli.serviceName + ' ' + typ + ' AVC AC-3 Eng Audio'
        data['InputSourceList'][0]['InputStreamList'][1]['PID'] = int(self.cli.avca1)
        data['InputSourceList'][0]['InputStreamList'][2]['Name'] = self.cli.serviceName + ' ' + typ + ' MP2 AC-3 Eng Audio'
        data['InputSourceList'][0]['InputStreamList'][2]['PID']  = int(self.cli.mp2a2)
        data['InputSourceList'][0]['InputStreamList'][3]['Name'] = self.cli.serviceName + ' ' + typ + ' MP2 Video'
        data['InputSourceList'][0]['InputStreamList'][3]['PID'] = int(self.cli.mp2v1)
        data['InputSourceList'][0]['InputStreamList'][4]['Name'] = self.cli.serviceName + ' ' + typ + ' AVC AC-3 Eng Audio'
        data['InputSourceList'][0]['InputStreamList'][4]['PID'] = int(self.cli.avca2)
        data['InputSourceList'][0]['InputStreamList'][5]['Name'] = self.cli.serviceName + ' ' + typ + ' AVC Video'
        data['InputSourceList'][0]['InputStreamList'][5]['PID'] = int(self.cli.avcv1)
        data['InputSourceList'][0]['InputStreamList'][6]['Name'] = self.cli.serviceName + ' ' + typ + ' MP2 AC-3 Eng Audio'
        data['InputSourceList'][0]['InputStreamList'][6]['PID'] = int(self.cli.mp2a3)
        data['InputSourceList'][0]['InputStreamList'][7]['Name'] = self.cli.serviceName + ' ' + typ + ' AVC AC-3 Eng Audio'
        data['InputSourceList'][0]['InputStreamList'][7]['PID'] = int(self.cli.avca3)
        #
        data['InputSourceList'][0]['InputTransport']['Name'] = self.cli.serviceName + ' ' + typ
        data['InputSourceList'][0]['InputTransport']['TransportID'] = int(self.cli.transptId)
        data['InputSourceList'][0]['Name'] = self.cli.serviceName + ' Group'
        #################   OUTPUT    #############################################################################
        data['OutputTransportList'][0]['Name'] = self.cli.serviceName
        data['OutputTransportList'][0]['OutputServiceList'][0]['Name'] = self.cli.serviceName + ' ' + typ + ' AVC'
        data['OutputTransportList'][0]['OutputServiceList'][0]['PCRPid'] = int(self.cli.pcrPid0)
        data['OutputTransportList'][0]['OutputServiceList'][0]['PMTPid'] = int(self.cli.pmtPid0)
        data['OutputTransportList'][0]['OutputStreamList'][0]['Name'] = self.cli.serviceName + ' ' + typ + ' AVC AC-3 Eng Audio'
        data['OutputTransportList'][0]['OutputStreamList'][0]['PID'] = int(self.cli.audPid1)
        data['OutputTransportList'][0]['OutputStreamList'][1]['Name'] = self.cli.serviceName + ' ' + typ + ' AVC SDT'
        data['OutputTransportList'][0]['OutputStreamList'][1]['PID'] = int(self.cli.sdtPid)
        data['OutputTransportList'][0]['OutputStreamList'][2]['Name'] = self.cli.serviceName + ' ' + typ + ' AVC AC-3 Eng Audio'
        data['OutputTransportList'][0]['OutputStreamList'][2]['PID'] = int(self.cli.audPid1)
        data['OutputTransportList'][0]['OutputStreamList'][3]['Name'] = self.cli.serviceName + ' ' + typ + ' AVC Video'
        data['OutputTransportList'][0]['OutputStreamList'][3]['PID'] = int(self.cli.vidPid1)
        data['OutputTransportList'][0]['OutputStreamList'][4]['Name'] = self.cli.serviceName + ' ' + typ + ' AVC PMT'
        data['OutputTransportList'][0]['OutputStreamList'][4]['PID'] = int(self.cli.pmtPid)
        data['OutputTransportList'][0]['OutputStreamList'][5]['Name'] = self.cli.serviceName + ' ' + typ + ' AVC AC-3 Eng Audio'
        data['OutputTransportList'][0]['OutputStreamList'][5]['PID'] = int(self.cli.audPid2)
        data['OutputTransportList'][0]['OutputStreamList'][6]['Name'] = self.cli.serviceName + ' ' + typ + ' AVC PAT'
        data['OutputTransportList'][0]['OutputStreamList'][6]['PID'] = int(self.cli.patPid1)
        data['OutputTransportList'][0]['TransportInfo']['NetworkID'] = int(self.cli.netId)
        data['OutputTransportList'][0]['TransportInfo']['OriginalNetworkID'] = int(self.cli.netId)
        data['OutputTransportList'][0]['TransportInfo']['OutputIPProperties']['DestinationIPAddress'] = self.cli.omulti
        data['OutputTransportList'][0]['TransportInfo']['OutputIPProperties']['DestinationPort'] = int(self.cli.odstprt1)
        data['OutputTransportList'][0]['TransportInfo']['OutputIPProperties']['SourceIpAddress'] = self.cli.osrcaddr
        data['OutputTransportList'][0]['TransportInfo']['OutputIPProperties']['SourcePort'] = int(self.cli.osrcpt1)
        data['OutputTransportList'][0]['TransportInfo']['TransportID'] = int(self.cli.trId)
        data['OutputTransportList'][1]['Name'] = self.cli.serviceName + typ + ' AVC PAT'
        data['OutputTransportList'][1]['OutputServiceList'][0]['Name'] = self.cli.serviceName + ' ' + typ + ' MP2'
        data['OutputTransportList'][1]['OutputServiceList'][0]['PCRPid'] = int(self.cli.pcrPid0)
        data['OutputTransportList'][1]['OutputServiceList'][0]['PMTPid'] = int(self.cli.pmtPid0)
        data['OutputTransportList'][1]['OutputStreamList'][0]['Name'] = self.cli.serviceName + ' ' + typ + ' MP2 AC-3 Eng Audio'
        data['OutputTransportList'][1]['OutputStreamList'][0]['PID'] = int(self.cli.audPid1)
        data['OutputTransportList'][1]['OutputStreamList'][1]['Name'] = self.cli.serviceName + ' ' + typ + ' MP2 SDT'
        data['OutputTransportList'][1]['OutputStreamList'][1]['PID'] = int(self.cli.sdtPid)
        data['OutputTransportList'][1]['OutputStreamList'][2]['Name'] = self.cli.serviceName + ' ' + typ + ' MP2 AC-3 Eng Audio'
        data['OutputTransportList'][1]['OutputStreamList'][2]['PID'] = int(self.cli.audPid1)
        data['OutputTransportList'][1]['OutputStreamList'][3]['Name'] = self.cli.serviceName + ' ' + typ + ' MP2 Video'
        data['OutputTransportList'][1]['OutputStreamList'][3]['PID'] = int(self.cli.vidPid1)
        data['OutputTransportList'][1]['OutputStreamList'][4]['Name'] = self.cli.serviceName + ' ' + typ + ' MP2 PMT'
        data['OutputTransportList'][1]['OutputStreamList'][4]['PID'] = int(self.cli.pmtPid)
        data['OutputTransportList'][1]['OutputStreamList'][5]['Name'] = self.cli.serviceName + ' ' + typ + ' MP2 AC-3 Eng Audio'
        data['OutputTransportList'][1]['OutputStreamList'][5]['PID'] = int(self.cli.audPid2)
        data['OutputTransportList'][1]['OutputStreamList'][6]['Name'] = self.cli.serviceName + ' ' + typ + ' MP2 PAT'
        data['OutputTransportList'][1]['OutputStreamList'][6]['PID'] = int(self.cli.patPid1)
        data['OutputTransportList'][1]['TransportInfo']['OutputIPProperties']['DestinationIPAddress'] = self.cli.omulti
        data['OutputTransportList'][1]['TransportInfo']['OutputIPProperties']['DestinationPort'] = int(self.cli.odstprt2)
        data['OutputTransportList'][1]['TransportInfo']['OutputIPProperties']['SourceIpAddress'] = self.cli.osrcaddr
        data['OutputTransportList'][1]['TransportInfo']['OutputIPProperties']['SourcePort'] = int(self.cli.osrcpt2)

        return data

checkAvailable()

