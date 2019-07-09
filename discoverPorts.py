#!/usr/bin/python3
#Author: Basil Morrison

import pprint
import sys, os, re, traceback
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
    parser.add_argument("-s","--src",help='Src IP',default=False)
    parser.add_argument("-m","--mc",help='Multicast IP',default=False)
    parser.add_argument("-x","--nmx",help='NMX Mgmt IP',default=False)
    parser.add_argument("-e","--encoder",help='Encoder name',default=False)
    parser.add_argument("-n","--servicename",help='NMX Service Name (Ex: nameOutDOOR HD)',default=False)
    parser.add_argument("-p","--pid",help='Stream Component Pid',default=False)
    parser.add_argument("-r","--pcr",help='Stream Component Pcr',default=False)
    parser.add_argument("-t","--pmt",help='Stream Component Pmt',default=False)
    # Parse all of the arguments
    parseargs=parser.parse_args()
    # Return the parsed arguments class
    return parseargs


class checkStatus:
    def __init__(self):
        self.cli = parseCommandLine()
        if not len(sys.argv) > 1:
            print('no argumuments provided.. try again')
        else:
            if self.cli.type in 'hd':
                 results = self.getStatusHD()
                 for i in results:
                    print(i)
            elif self.cli.type in 'sd':
                results = self.getStatusSD()
                for i in results:
                    print(i)

    def getStatusHD(self):
        results = []
        allHD = []
        for i in  collection.find({'DeviceInfo.Name': { '$regex': 'ElecEncoder' }}, {'DeviceInfo.Name': 1, '_id': 0}):
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

                                   except KeyError:
                                           #print(traceback.format_exc())
                                           print (k['nmxIPAddress'] + ' ' + k['DeviceInfo']['Name'] + ' Port not found')
                               else:
#                                           temp['inputDevID'] = k['DeviceInfo']['ID']
#                                           temp['inputPortID'] = k['PortList'][j]['ID']
                                           temp['nmxIP'] = k['nmxIPAddress']
                                           temp['encoder'] = k['DeviceInfo']['Name']
                                           temp['slot'] = 'full'
                                           #print (k['nmxIPAddress'] + ' ' + k['DeviceInfo']['Name'] + ' - Full')
                               if temp:
                                  results.append(temp)
        return results

    def getStatusSD(self):
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

                                   except KeyError:
                                           #print(traceback.format_exc())
                                           print (k['nmxIPAddress'] + ' ' + k['DeviceInfo']['Name'] + ' Port not found')
                               else:
#                                           temp['inputDevID'] = k['DeviceInfo']['ID']
#                                           temp['inputPortID'] = k['PortList'][j]['ID']
                                           temp['nmxIP'] = k['nmxIPAddress']
                                           temp['encoder'] = k['DeviceInfo']['Name']
                                           temp['slot'] = 'full'
                                           #print (k['nmxIPAddress'] + ' ' + k['DeviceInfo']['Name'] + ' - Full')
                               if temp:
                                  results.append(temp)
        return results



checkStatus()
#buildChannel()

