#!/usr/bin/env python3
#Author: Basil Morrison

import pprint
import paramiko
import sys, time, os, re, traceback
import argparse, json
import mysql.connector
from mysql.connector import Error

def parseCommandLine(program_description="Get Shuffle Data"):
    parser=argparse.ArgumentParser(description=program_description)
    parser.add_argument("-ssr","--strSvr",help='Stream Server',default=False)
    parser.add_argument("-os","--outStr",help='Out Stream',default=False)
    parser.add_argument("-nos","--nOutStr",help='New Out Stream',default=False)
    parser.add_argument("-of","--oldFr",help='Old Frequency',default=False)
    parser.add_argument("-nf","--newFr",help='New Frequency',default=False)
    parser.add_argument("-crid","--curRegId",help='Current Region ID',default=False)
    parser.add_argument("-nrid","--newRegId",help='New Region ID',default=False)
    parser.add_argument("-drid","--diffRegId",help='Diff Reg ID',default=False)

    parseargs=parser.parse_args()
    return parseargs

def create_bin(curRegIds):
    binary = []
    numList = []
    spl = curRegIds.split(',')
    for i in spl:
        numList.append(int(i))
    maxnum = max(numList)
    for i in range(0, maxnum +1):
        if str(i) in spl:
            binary.append('1')
        else:
            binary.append('0')
    binary_str = (''.join(map(str, binary)))
    return binary_str

def connetToCafeDb(schema):
    db = mysql.connector.connect(host='172.16.168.95', database=schema, user='dsops', password='!MyGeNeRiC1!')
    return db

def checkDataValidity(curRegId, newRegId):
    if re.search('[a-zA-Z]', curRegId):
        print ('cur region ID \'' + curRegId + '\' is Invalid!  Verify data and try again.')
        sys.exit()
    if re.search('[a-zA-Z]', newRegId):
        print ('new region ID \'' + newRegId + '\' is Invalid!  Verify data and try again.')
        sys.exit()

class shuffleFrequencies:
    def __init__(self):
        self.cli = parseCommandLine()
        self.all_uniqueness = []
        self.old_footprintMask = ''
        self.new_footprintMask = ''
        self.diff_footprintMask = ''
        self.current_uniqueness = ''
        self.SSR_LI = []
        self.SSR_LIPK = []
        self.SSR_NJ = []
        self.SSR_NJPK = []
        self.SSR_LI_ERR =[]
        self.SSR_NJ_ERR = []
        self.li = ''
        self.lipk = ''
        self.nj = ''
        self.njpk = ''

        self.cli.oldFr = (self.cli.oldFr + '0000')
        self.cli.newFr = (self.cli.newFr + '0000')

        if not len(sys.argv) > 1:
            print('No arguments provided.. Please provide arguments and try again')
            sys.exit()
        else:
            curR = self.cli.curRegId
            newR = self.cli.newRegId
            checkDataValidity(curR, newR)
        try:
            #check if db is empty
            conn = connetToCafeDb(self.cli.strSvr)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(DELIVERY_NUM) FROM ' + self.cli.strSvr + '.OUT_STREAM_DELIVERY WHERE OUT_STREAM_ID = ' + self.cli.outStr + ' AND FOOTPRINT_MASK <> 0')
            for count in cursor:
                if count[0] == 0:
                   print('Outstream ID \"' + self.cli.outStr + '\" missing from  \"' + self.cli.strSvr + '\" schema on CafeDev. Please verify that database is updated and try again.')
                   cursor.close()
                   sys.exit()
        except Error as e:
            print(e)

        try:
            #used for to get all uniquenesses
            conn = connetToCafeDb(self.cli.strSvr)
            cursor = conn.cursor()
            cursor.execute('SELECT DELIVERY_NUM FROM ' + self.cli.strSvr + '.OUT_STREAM_DELIVERY WHERE OUT_STREAM_ID = ' + self.cli.outStr + ' AND FOOTPRINT_MASK <> 0')

            #get all uniqueness (will be used to create new uniqueness)
            for count in cursor:
                self.all_uniqueness.append(count[0])
            self.highestUniqueness = max(self.all_uniqueness)
            self.new_uniqueness = self.highestUniqueness + 1
            cursor.close()
            print ('new uniqueness: ' + str(self.new_uniqueness))
        except Error as e:
            print(e)

        try:
            #current uniqueness
            conn = connetToCafeDb(self.cli.strSvr)
            cursor = conn.cursor()
            cursor.execute('SELECT DELIVERY_NUM FROM ' + self.cli.strSvr + '.OUT_STREAM_DELIVERY WHERE OUT_STREAM_ID = ' + self.cli.outStr + ' AND FREQUENCY = ' + self.cli.oldFr + ' AND FOOTPRINT_MASK <> 0')
            result = cursor.fetchone()
            if result is None:
                print('current uniqueness:  null')
            else:
                self.current_uniqueness = result[0]
                print('current uniqueness:' + str(self.current_uniqueness))
            cursor.close()
        except Error as e:
            print (e)

        try:
            #Check whether I need to use for loop instead of 'fetchone()' method to get the contents of cursor
            conn = connetToCafeDb(self.cli.strSvr)
            cursor = conn.cursor()
            cursor.execute('SELECT FOOTPRINT_MASK FROM ' + self.cli.strSvr + '.OUT_STREAM_DELIVERY WHERE OUT_STREAM_ID = ' + self.cli.outStr + ' AND FREQUENCY = ' + self.cli.oldFr + ' AND FOOTPRINT_MASK <> 0')
            result = cursor.fetchone()
            if result is None:
                print('old footprint_mask:  null')
            else:
                self.old_footprintMask = result[0]
                print('old_footprint mask:' + str(self.old_footprintMask))
            cursor.close()
        except Error as e:
            print (e)

        try:
            #get new footprint mask
            binary = create_bin(self.cli.curRegId) #binary conversion
            conn = connetToCafeDb(self.cli.strSvr)
            cursor = conn.cursor()
            cursor.execute('SELECT CONV(REVERSE(' + binary + '), 2, 10) as FM')
            result = cursor.fetchone()
            self.new_footprintMask = result[0]
            cursor.close()
            print('new_footprint mask: ' + self.new_footprintMask)
        except Error as e:
            print(e)
        try:
            # get diff footprint mask
            binary2 = create_bin(self.cli.diffRegId) #binary conversion
            conn = connetToCafeDb(self.cli.strSvr)
            cursor = conn.cursor()
            cursor.execute('SELECT CONV(REVERSE(' + binary2 + '), 2, 10) as FM')
            result = cursor.fetchone()
            self.diff_footprintMask = result[0]
            print('diff_footprint mask: ' + self.diff_footprintMask)
            cursor.close()
        except Error as e:
            print(e)
        ###############################################################################################################
        #verify why I checked for 'self.exists'... also.. if this script is looped, do I need to clear 'self.exists' after each pass?
        #Note:  If frequency or transport did not exist prior, INSERT SSR.OUT_STREAM_DELIVERY (<fields>) VALUES (<fields prior>, OUT_STREAM_ID=$out_str_id,
        #FREQUENCY=$pad_old_freq, DELIVERY_NUM = $uniqueness WHERE OUT_STREAM_ID =  $out_str_id and DELIVERY_NUM=$out_str_id, <fields post>)...
        #else UPDATE SSR.OUT_STREAM_DELIVERY SET OUT_STREAM_ID=$out_str_id, FREQUENCY=$pad_old_freq  WHERE OUT_STREAM_ID =  $out_str_id and
        #DELIVERY_NUM=$new_uniqueness;...  Note:  check if I must clear self.exists after pass

        try:
            conn = connetToCafeDb(self.cli.strSvr)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM ' + self.cli.strSvr + '.OUT_STREAM_DELIVERY WHERE OUT_STREAM_ID = ' + self.cli.outStr + ' OR FREQUENCY = ' + self.cli.oldFr)
            result = cursor.fetchone()
            self.exists = result[0]
            print('LI & NJ freq/outstream count: ' + str(self.exists))
        except Error as e:
            print(e)

        def preamble():
            pre = []
            pre.append("set colsep ','")
            pre.append("set linesize 1024")
            pre.append("set pagesize 1024")
            pre.append("set sqlprompt ''")
            pre.append("set trimspool on")
            pre.append("set headsep off")
            pre.append("set heading off")
            pre.append("set feedback off;")
            return pre

        def shuffLegacy(cli_ssr,SSR):
            if cli_ssr_ is 'SSR_NJ' or cli_ssr is 'SSR_LI':
                if self.current_uniqueness is not '' or self.old_footprintMask is not '':
                   if self.exists == 0:
                       SSR.append("INSERT INTO SSR.OUT_STREAM_DELIVERY (OUT_STREAM_ID, SI_OUT_STREAM_ID, DELIVERY_NUM, DELIVERY_TYPE, REGION_ID, FOOTPRINT_MASK, FREQUENCY, FEC_OUTER, MODULATI    ON, SYMBOL_RATE, FEC_INNER, ORBIT_POSITION, WEST_EAST_FLAG, POLARISATION, BANDWIDTH, CONSTELLATION, HIERARCHY, CODE_RATE_HP, CODE_RATE_LP, GUARD_INTERVAL, TRANSMISSION_MODE, OTHER_FREQUENCY, NOTES, SCTE_TX_SYSTEM, SCTE_SPLIT_MODE, ROLL_OFF, PLP_ID, T2_SYSTEM_ID, SISO_MISO_FLAG) VALUES (" + '\'' + self.cli.outStr + '\'' + ", '-1' , " + '\'' + str(self.new_uniqueness) + '\'' + ", '5', 'null', " + '\'' + self.diff_footprintMask + '\'' + ", " + '\'' + self.cli.newFr + '\'' + ", 'null', '16', '5360537', '3', 'null', 'null', 'null', 'null', 'null', 'null', 'null', 'null', 'null', 'null', 'null', 'null', '2', '0', '0', 'null', 'null', 'null');")
                       SSR.append("commit;")
                       SSR.append("exit")
                   else:
                       SSR.append('UPDATE SSR.OUT_STREAM_DELIVERY SET FREQUENCY=' + self.cli.oldFr + ', DELIVERY_NUM = $uniqueness WHERE OUT_STREAM_ID = ' + self.cli.outStr + ';')
                       SSR.append("commit;")
                       SSR.append("exit")
                else:
                    SSR_ERR.append(self.cli.strSvr,self.cli.outStr,self.cli.oldFr,self.cli.curRegId)
            return SSR

        def shuffPowerKey(cli_ssr,SSR):
            SSR = []
            if cli_ssr in 'SSR_LIPK' or cli_ssr in 'SSR_NJPK':
                SSR.append("UPDATE SSR.OUT_STREAM_DELIVERY SET FOOTPRINT_MASK = " + self.new_footprintMask + ", FREQUENCY=" + self.cli.oldFr + ", DELIVERY_NUM = " + str(self.current_uniqueness) + " WHERE FOOTPRINT_MASK = " + str(self.old_footprintMask) + " AND OUT_STREAM_ID =  " + self.cli.outStr + ";")
                SSR.append("commit;")
                SSR.append("INSERT INTO SSR.OUT_STREAM_DELIVERY (OUT_STREAM_ID, SI_OUT_STREAM_ID, DELIVERY_NUM, DELIVERY_TYPE, REGION_ID, FOOTPRINT_MASK, FREQUENCY, FEC_OUTER, MODULATI    ON, SYMBOL_RATE, FEC_INNER, ORBIT_POSITION, WEST_EAST_FLAG, POLARISATION, BANDWIDTH, CONSTELLATION, HIERARCHY, CODE_RATE_HP, CODE_RATE_LP, GUARD_INTERVAL, TRANSMISSION_MODE, OTHER_FREQUENCY, NOTES, SCTE_TX_SYSTEM, SCTE_SPLIT_MODE, ROLL_OFF, PLP_ID, T2_SYSTEM_ID, SISO_MISO_FLAG) VALUES (" + '\'' + self.cli.outStr + '\'' + ", '-1' , " + '\'' + str(self.new_uniqueness) + '\'' + ", '5', 'null', " + '\'' + self.diff_footprintMask + '\'' + ", " + '\'' + self.cli.newFr + '\'' + ", 'null', '16', '5360537', '3', 'null', 'null', 'null', 'null', 'null', 'null', 'null', 'null', 'null', 'null', 'null', 'null', '2', '0', '0', 'null', 'null', 'null');")
                SSR.append("commit;")
                SSR.append("exit")
            return SSR

        ##-LI
        if self.cli.strSvr in 'SSR_LI':
            header = preamble()
            self.li = shuffLegacy(self.cli.strSvr,'SSR_LI')
            sql_shuffle_stmt = header + self.lipk

        ##-LIPK
        if self.cli.strSvr in 'SSR_LIPK':
           header = preamble()
           self.lipk = shuffPowerKey(self.cli.strSvr,'SSR_LIPK')
           sql_shuffle_stmt = header + self.lipk

        ##-NJ
        if self.cli.strSvr in 'SSR_NJ':
            header = preamble()
            self.nj = shuffLegacy(self.cli.strSvr,'SSR_NJ')
            sql_shuffle_stmt = header + self.lipk

        ##-NJPK
        if self.cli.strSvr in 'SSR_NJPK':
            header = preamble()
            self.njpk = shuffPowerKey(self.cli.strSvr,'SSR_NJPK')
            sql_shuffle_stmt = header + self.lipk

        child = applyChangesToSSR(sql_shuffle_stmt)

class applyChangesToSSR:
    def __init__(self, host, sql_shuffle_stmt):
        self.port = 22
        self.username = 'root'
        self.password = 'get2know'
        self.client = host
        self.timeout = 3
        #for i in sql_shuffle_stmt:
            #print(i)

    def prepSsr(self, host):
        try:
            self.client = paramiko.SSHClient()
            self.client.connect(hostname=self.host, port=self.port, username=self.username, password=self.password, timeout=self.timeout, allow_agent=False, look_for_keys=False)
        except paramiko.SSHException as sshException:
            print(sshException)
        except socket.timeout as e:
            print "Connection timed out"







shuffleFrequencies()
