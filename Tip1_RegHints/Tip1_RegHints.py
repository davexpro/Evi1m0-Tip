#!/usr/bin/env python
# coding=utf-8

import sys
import os
import glob
import json
import requests

class FindYourHints(object):

    def importPayloads(self):
        _FileList = glob.glob(r"Reg\*.json")
        _AllFileNum = 0
        for _File in _FileList:
            _LoadFile = open(_File)
            try:
                 _Payload = _LoadFile.read()
            finally:
                 _LoadFile.close()
            self.payloadLoad(_Payload, 1, _File)
            _AllFileNum += 1

        print "============================================================"
        print "[+] Total Payload(s): " + str(_AllFileNum)

    '''
    @:param pContent fo the JSON, pType for the type 1:first loading 2:use it
    '''
    def payloadLoad(self, pContent, pType, pPath):
        '''
        The next version we will update the Fault tolerant module
        '''
        _JSON = json.loads(pContent)
        if pType == 1:
            # Init
            _Info = _JSON['Payload']
            print "[+] Site: "+ _Info['Site'] + "  Author: " + _Info['Author'] + "  Created: " +_Info['Create_Date']
        elif pType == 2:
            # Use it
            self.runTheMethod(_JSON['Reg'], _JSON['Header'], _JSON['Payload']['Site'])
        else:
            print "[-] Import Error! File: " + pPath

    def startFinding(self):
        print "[+] Please Use Double quotation marks. E.g: \"Dave\""
        self._Passport = str(input("[+] Passport: "))
        print "[+] Your Passport is " + self._Passport + ", and here we go..."
        print "============================================================"

        _FileList = glob.glob(r"Payloads\Reg\*.json")
        for _File in _FileList:
            _LoadFile = open(_File)
            try:
                 _Payload = _LoadFile.read()
            finally:
                 _LoadFile.close()
            self.payloadLoad(_Payload, 2, _File)

        print "============================================================"
        print "[+] Finished! ."

    def runTheMethod(self, pReg, pHeader, pSite):
        if pReg['Method'] == "GET":
            try:
                _Req = requests.get(pReg['Url'] + self._Passport, headers=pHeader, timeout=5)
            except:
                _Req = requests.get(pReg['Url'] + self._Passport, headers=pHeader, timeout=10)

            self.judgeTheResult(_Req.content, pReg['Judge_Yes'], pReg['Judge_No'], pSite)

        elif pReg['Method'] == "POST":
            print pReg['Payload'] + self._Passport
            try:
                _Req = requests.post(pReg['Url'], data = pReg['Payload'] + self._Passport, headers=pHeader, timeout=5)
            except:
                _Req = requests.post(pReg['Url'], data = pReg['Payload'] + self._Passport, headers=pHeader, timeout=10)

            self.judgeTheResult(_Req.content, pReg['Judge_Yes'], pReg['Judge_No'], pSite)
        else:
            print "[-] Payload Error!"

    def judgeTheResult(self, pContent, pYes, pNo, pSite):
        _Result_Yes = pContent.split(pYes)
        _Result_No = pContent.split(pNo)

        print pContent

        #√✔×✘
        if len(_Result_Yes) == 2 and len(_Result_No) == 1:
            print "[+][√] Site: " + pSite
        elif len(_Result_No) == 2 and len(_Result_Yes) == 1:
            print "[+][×] Site: " + pSite
        else:
            print "[-] Payload Error.!"

if __name__ == '__main__':
    _Wolf = FindYourHints()
    _Wolf.importPayloads()
    _Wolf.startFinding()
