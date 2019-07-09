#!/usr/bin/python3
#Author: Basil Morrison
#######################
import pprint
import sys, os, re, traceback
import argparse, json
from pymongo import MongoClient


client = MongoClient()
client = MongoClient("mongodb://user:password@172.16.168.111/admin")
db = client['nmx']

orIn = []
orOut = []
andIn = []
andOut = []

def parseCommandLine(program_description="Get NMX Data"):
    # Instantiate the argument parser
    parser=argparse.ArgumentParser(description=program_description)
    parser.add_argument("-s","--src",help='Src IP',default=False)
    parser.add_argument("-m","--mc",help='Multicast IP',default=False)
    parser.add_argument("-i","--deviceip",help='NMX Mgmt IP',default=False)
    parser.add_argument("-d","--device",help='Encoder IP',default=False)
    parser.add_argument("-n","--servicename",help='NMX Service Name (Ex: nameOutDOOR HD)',default=False)
    parser.add_argument("-p","--pid",help='Stream Component Pid',default=False)
    parser.add_argument("-r","--pcr",help='Stream Component Pcr',default=False)
    parser.add_argument("-t","--pmt",help='Stream Component Pmt',default=False)
    parser.add_argument("-a","--useand",help='Use $and',action='store_true',default=False)
    parser.add_argument("-o","--useor",help='Use $or',action='store_true',default=False)
    # Parse all of the arguments
    parseargs=parser.parse_args()
    # Return the parsed arguments class
    return parseargs

class getData:
    def __init__(self):
        self.cli = parseCommandLine()
        query = "{}"
        if not len(sys.argv) > 1:
            print ('')
        else:
            #arguments = []
            query = []
            query2 = []
            if  self.cli.useand:
                if self.cli.servicename:
                    andIn.append({'Name': self.cli.servicename})
                if self.cli.mc:
                    andIn.append({'InputIPConfigInfo.PrimarySocketDestIP': self.cli.mc})
                if self.cli.src:
                    andIn.append({'InputIPConfigInfo.PrimarySocketSrcIP':self.cli.src})
                if self.cli.pid:
                    andIn.append({'InputStreamList.PID': int(self.cli.pid)})
                if self.cli.pcr:
                    andIn.append({'InputServiceList.PCRPid': int(self.cli.pcr)})
                if self.cli.pmt:
                    andIn.append({'InputServiceList.PMTPid': int(self.cli.pmt)})
                query2.append(self.getAndIn())
                self.query2 = query
                print(self.query2)
                #print('Hello')

            elif  self.cli.useor:
                if self.cli.servicename:
                    orIn.append({'Name': self.cli.servicename})
                if self.cli.mc:
                    orIn.append({'InputIPConfigInfo.PrimarySocketDestIP': self.cli.mc})
                if self.cli.src:
                    orIn.append({'InputIPConfigInfo.PrimarySocketSrcIP':self.cli.src})
                if self.cli.pid:
                    orIn.append({'InputStreamList.PID': int(self.cli.pid)})
                if self.cli.pcr:
                    orIn.append({'InputServiceList.PCRPid': int(self.cli.pcr)})
                if self.cli.pmt:
                    orIn.append({'InputServiceList.PMTPid': int(self.cli.pmt)})
                query2.append(self.getOrIn())
                self.query2 = query
                #print(self.query2)


            elif self.cli.servicename:
                query.append(self.getNameIn())

            elif self.cli.mc:
                query.append(self.getMulticastIn()) 

            elif self.cli.src:
                query.append(self.getSrcIn())

            elif self.cli.pid:
                query.append(self.getPidIn())

            elif self.cli.pcr:
                query.append(self.getPcrIn())

            elif self.cli.pmt:
                query.append(self.getPmtIn())

            elif self.cli.device:
                query.append(self.getEncInfo())


    def getAndIn(self):
           tempID = []
           collectionIn = db['nmx_input_electraX']
           collectionSl = db['nmx_serviceList']
           collectionOut = db['nmx_output']

           for i in  collectionIn.find( { '$and': andIn }, {'_id': 0} ):
                print(i)
           for i in  collectionIn.find( { '$and': andIn }, {'InputServiceList.ID': 1, '_id': 0} ):
                num = len(i['InputServiceList'])
                for j in range(0, num):
                    tempID.append((i['InputServiceList'][j]['ID']))
           for j in tempID:
                for k in  collectionSl.find({'serviceList': { '$elemMatch': {'ID': str(j)}}}, {'_id': 0}):
                     if (k['CardList'][0]['CardType'] in 'Output Card'):
                        print(k)
                try:
                    for l in  collectionOut.find({'MWProfileList': { '$elemMatch': {'InputServiceID': str(j)}}}, {'_id': 0}):
                        print(l)
                except:
                    for l in  collectionOut.find({'OutputServiceList': { '$elemMatch': {'Name': str(j)}}}, {'_id': 0}):
                         print(l)

    def getOrIn(self):
           tempID = []
           collectionIn = db['nmx_input_electraX']
           collectionSl = db['nmx_serviceList']
           collectionOut = db['nmx_output']

           for i in  collectionIn.find( { '$or': orIn },  {'_id': 0} ):
                print(i)
           for i in  collectionIn.find( { '$and': orIn }, {'InputServiceList.ID': 1, '_id': 0} ):
                num = len(i['InputServiceList'])
                for j in range(0, num):
                    tempID.append((i['InputServiceList'][j]['ID']))
           for j in tempID:
                for k in  collectionSl.find({'serviceList': { '$elemMatch': {'ID': str(j)}}}, {'_id': 0}):
                     if (k['CardList'][0]['CardType'] in 'Output Card'):
                        print(k)
                try:
                    for l in  collectionOut.find({'MWProfileList': { '$elemMatch': {'InputServiceID': str(j)}}}, {'_id': 0}):
                        print(l)
                except:
                    for l in  collectionOut.find({'OutputServiceList': { '$elemMatch': {'Name': str(j)}}}, {'_id': 0}):
                         print(l)

    def getAnyIn(self):
           collection = db['nmx_input_electraX']
           for i in  collection.find({ anyIn }):
                print(i)

    def getAnyOut(self):
           collection = db['nmx_output']
           for i in  collection.find({ anyOut }):
                print(i)

    def getNameIn(self):
        tempID = []
        collectionIn = db['nmx_input_electraX']
        collectionSl = db['nmx_serviceList']
        collectionOut = db['nmx_output']

        token = re.compile('{}'.format(self.cli.servicename), re.IGNORECASE)
        for i in  collectionIn.find({'InputServiceList': { '$elemMatch': { 'Name': token}}}, {'_id': 0}):
            print (i)
        for i in  collectionIn.find( { 'InputServiceList': { '$elemMatch': { 'Name': token}}}, {'InputServiceList.ID': 1, '_id': 0} ):
              num = len(i['InputServiceList'])
              for j in range(0, num):
                  tempID.append((i['InputServiceList'][j]['ID']))
        for j in tempID:
            for k in  collectionSl.find({'serviceList': { '$elemMatch': {'ID': str(j)}}}, {'_id': 0}):
                 if (k['CardList'][0]['CardType'] in 'Output Card'):
                     print(k)
            try:
                 for l in  collectionOut.find({'MWProfileList': { '$elemMatch': {'InputServiceID': str(j)}}}, {'_id': 0}):
                     print(l)
            except:
                 for l in  collectionOut.find({'OutputServiceList': { '$elemMatch': {'Name': str(j)}}}, {'_id': 0}):
                     print(l)

    def getMulticastIn(self):
        tempID = []
        collectionIn = db['nmx_input_electraX']
        collectionSl = db['nmx_serviceList']
        collectionOut = db['nmx_output']

        multiIn = []
        token = re.compile('{}'.format(self.cli.mc), re.IGNORECASE)
        for i in  collectionIn.find({'InputIPConfigInfo.PrimarySocketDestIP': token}, {'_id': 0}):
            print (i)
        for i in  collectionIn.find( {'InputIPConfigInfo.PrimarySocketDestIP': token}, {'InputServiceList.ID': 1, '_id': 0} ):
              num = len(i['InputServiceList'])
              for j in range(0, num):
                  tempID.append((i['InputServiceList'][j]['ID']))
        for j in tempID:
            for k in  collectionSl.find({'serviceList': { '$elemMatch': {'ID': str(j)}}}, {'_id': 0}):
                 if (k['CardList'][0]['CardType'] in 'Output Card'):
                     print(k)
            try:
                 for l in  collectionOut.find({'MWProfileList': { '$elemMatch': {'InputServiceID': str(j)}}}, {'_id': 0}):
                     print(l)
            except:
                 for l in  collectionOut.find({'OutputServiceList': { '$elemMatch': {'Name': str(j)}}}, {'_id': 0}):
                     print(l)

    def getSrcIn(self):
        tempID = []
        collectionIn = db['nmx_input_electraX']
        collectionSl = db['nmx_serviceList']
        collectionOut = db['nmx_output']

        token = re.compile('{}'.format(self.cli.src), re.IGNORECASE)
        for i in  collectionIn.find({'InputIPConfigInfo.PrimarySocketSrcIP': token}, {'_id': 0}): 
            print (i)
        for i in  collectionIn.find( { 'InputServiceList': { '$elemMatch': { 'Name': token}}}, {'InputServiceList.ID': 1, '_id': 0} ):
              num = len(i['InputServiceList'])
              for j in range(0, num):
                  tempID.append((i['InputServiceList'][j]['ID']))
        for j in tempID:
            for k in  collectionSl.find({'serviceList': { '$elemMatch': {'ID': str(j)}}}, {'_id': 0}):
                 if (k['CardList'][0]['CardType'] in 'Output Card'):
                     print(k)
            try:
                 for l in  collectionOut.find({'MWProfileList': { '$elemMatch': {'InputServiceID': str(j)}}}, {'_id': 0}):
                     print(l)
            except:
                 for l in  collectionOut.find({'OutputServiceList': { '$elemMatch': {'Name': str(j)}}}, {'_id': 0}):
                     print(l)

    def getPidIn(self):
        tempID = []
        collectionIn = db['nmx_input_electraX']
        collectionSl = db['nmx_serviceList']
        collectionOut = db['nmx_output']

        for i in  collectionIn.find({'InputStreamList.PID': int(self.cli.pid)}, {'_id': 0}):
            print (i)
        for i in  collectionIn.find({'InputStreamList.PID': int(self.cli.pid)}, {'InputServiceList.ID': 1, '_id': 0} ):
              num = len(i['InputServiceList'])
              for j in range(0, num):
                  tempID.append((i['InputServiceList'][j]['ID']))
        for j in tempID:
            for k in  collectionSl.find({'serviceList': { '$elemMatch': {'ID': str(j)}}}, {'_id': 0}):
                 if (k['CardList'][0]['CardType'] in 'Output Card'):
                     print(k)
            try:
                 for l in  collectionOut.find({'MWProfileList': { '$elemMatch': {'InputServiceID': str(j)}}}, {'_id': 0}):
                     print(l)
            except:
                 for l in  collectionOut.find({'OutputServiceList': { '$elemMatch': {'Name': str(j)}}}, {'_id': 0}):
                     print(l)
 
    def getPcrIn(self):
        tempID = []
        collectionIn = db['nmx_input_electraX']
        collectionSl = db['nmx_serviceList']
        collectionOut = db['nmx_output']

        for i in  collectionIn.find({'InputServiceList.PCRPid': int(self.cli.pcr)}, {'_id': 0}): 
            print (i)
        for i in  collectionIn.find({'InputStreamList.PCRPid': int(self.cli.pid)}, {'InputServiceList.ID': 1, '_id': 0} ):
              num = len(i['InputServiceList'])
              for j in range(0, num):
                  tempID.append((i['InputServiceList'][j]['ID']))
        for j in tempID:
            for k in  collectionSl.find({'serviceList': { '$elemMatch': {'ID': str(j)}}}, {'_id': 0}):
                 if (k['CardList'][0]['CardType'] in 'Output Card'):
                     print(k)
            try:
                 for l in  collectionOut.find({'MWProfileList': { '$elemMatch': {'InputServiceID': str(j)}}}, {'_id': 0}):
                     print(l)
            except:
                 for l in  collectionOut.find({'OutputServiceList': { '$elemMatch': {'Name': str(j)}}}, {'_id': 0}):
                     print(l)

    def getPmtIn(self):
        tempID = []
        collectionIn = db['nmx_input_electraX']
        collectionSl = db['nmx_serviceList']
        collectionOut = db['nmx_output']

        for i in  collectionIn.find({'InputServiceList.PMTPid': int(self.cli.pmt)}, {'_id': 0}):
            print (i)
        for i in  collectionIn.find({'InputStreamList.PMTPid': int(self.cli.pid)}, {'InputServiceList.ID': 1, '_id': 0} ):
              num = len(i['InputServiceList'])
              for j in range(0, num):
                  tempID.append((i['InputServiceList'][j]['ID']))
        for j in tempID:
            for k in  collectionSl.find({'serviceList': { '$elemMatch': {'ID': str(j)}}}, {'_id': 0}):
                 if (k['CardList'][0]['CardType'] in 'Output Card'):
                     print(k)
            try:
                 for l in  collectionOut.find({'MWProfileList': { '$elemMatch': {'InputServiceID': str(j)}}}, {'_id': 0}):
                     print(l)
            except:
                 for l in  collectionOut.find({'OutputServiceList': { '$elemMatch': {'Name': str(j)}}}, {'_id': 0}):
                     print(l)

    def getEncInfo(self):
        enc = []
        collection = db['nmx_serviceList']
        token = re.compile('{}'.format(self.cli.device), re.IGNORECASE)
        for i in  collection.find({'DeviceInfo.IPAddress': token}):
                 enc.append(i)
        return enc

getData()
