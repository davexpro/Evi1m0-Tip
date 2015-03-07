#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Dave'

import datetime
import json
import re
import requests
import time
from multiprocessing.dummy import Pool as ThreadPool
#from multiprocessing import Pool


# TODO
# 1. use yield to optimize the memory usage
# 2. encapsulate this code to module

# UID = sys.argv[1]
UID = "Evi1m0"
# THREAD_NUM = sys.argv[2]
THREAD_NUM = 5
BATCH_SIZE = 20

global HEADER, XSRF, HASH_ID

XSRF = ''
TOTAL = 0

HEADER = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
            (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36',
    'Host': 'www.zhihu.com',
    'Origin': 'http://www.zhihu.com',
    'Referer': 'http://www.zhihu.com/people/tiany-wang/followees',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest'
}

COOKIES = {
    '_xsrf': XSRF,
    'c_c': '',
    'q_c1': '',
    'z_c0': ''
}

# session object, keeping session
FansCount = requests.session()


def main():
    global HASH_ID
    print "The User[uid] We Are Crawling is " + UID
    HASH_ID, total = getHashIdAndFollerNum(UID)
    MALE, FEMALE, OTHER = startCatch(HASH_ID, total)

    print "============ Final ============"
    print "Male: " + str(MALE) + "  Female: " + str(FEMALE) + \
            " OTHER: " + str(OTHER)
    print "ADDUP: " + str(MALE + FEMALE + OTHER) + "  Total: " + str(total)


def getHashIdAndFollerNum(pUserID):

    _URL = 'http://www.zhihu.com/people/' + pUserID + '/followers'
    _FansCount = requests.get(_URL, cookies=COOKIES)

    _Pattern = "hash_id&quot;: &quot;(.*?)&quot"
    _tmp = re.findall(_Pattern, _FansCount.text)
    _hash_id = _tmp[0]

    _Pattern = "<strong>(.*?)</strong><label>"
    _tmp = re.findall(_Pattern, _FansCount.text)
    _FollowerNum = int(_tmp[1])

    return (_hash_id, _FollowerNum)


def startCatch(pHashID, pFollowNum):

    print "User HashId:" + pHashID
    print "User Followers Num:" + str(pFollowNum)

    _FollowTimes = (pFollowNum + BATCH_SIZE - 1) / BATCH_SIZE
    print "For Circle Times:" + str(_FollowTimes)

    offsets = [20 * i for i in xrange(_FollowTimes)]
    pool = ThreadPool(THREAD_NUM)

    m, f, o = 0, 0, 0  # male, female, other
    results = pool.map(oneTheadCatch, offsets)
    for c in results:
        m += c[0]
        f += c[1]
        o += c[2]

    return (m, f, o)


def oneTheadCatch(pOffsets):
    global XSRF, HASH_ID

    #print "Now Offsets:" + str(pOffsets)
    _Params = json.dumps({"hash_id": HASH_ID, "order_by": "created", \
        "offset": pOffsets, })
    _PostData = {
        'method': 'next',
        'params': _Params,
        '_xsrf': XSRF
    }

    try_count = 0
    while True:
        try:
            _FansCount = requests.post( \
                    "http://www.zhihu.com/node/ProfileFollowersListV2", \
                    data=_PostData, cookies=COOKIES, \
                    timeout=15 * (try_count + 1))
            try_count = 0
            print "Done oneTheadCatch:" + str(pOffsets)
            break
        except:
            print "Post Failed! Reposting...oneTheadCatch:" + str(pOffsets)
            try_count += 1
            time.sleep(3)  # sleep 3 seconds to avoid network error.

    return fansInfoAna(_FansCount.text)


def fansInfoAna(pJsonText):
    #print pJsonText
    _Pattern = 'www.zhihu.com\\\/people\\\/(.*?)\\\\'
    _Asortment = re.findall(_Pattern, pJsonText)

    r = []
    for i in range(len(_Asortment)):
        r.append(getFansSex(_Asortment[i]))

    m, f, o = 0, 0, 0
    for i in r:
        if i == 0:
            m += 1
        elif i == 1:
            f += 1
        else:
            o += 1

    return (m, f, o)


def getFansSex(pFansUID):
    global MALE, FEMALE, OTHER

    try_count = 0
    while True:
        try:
            _FansSex = requests.get("http://www.zhihu.com/people/" + \
                    pFansUID, cookies=COOKIES, timeout=15 * (try_count + 1))
            try_count = 0
            break
        except:
            print "Get Failed! Regetting...getFansSex:" + pFansUID
            try_count += 1
            time.sleep(3)  # sleep 3 seconds to avoid network error.

    _FansText = _FansSex.text
    _FansSex = _FansText.split("<span class=\"item gender\" >")

    if len(_FansSex) >= 2:
        _FansSex = _FansText.split("<span class=\"item gender\" >" \
                "<i class=\"icon icon-profile-male\"></i></span>")
        if len(_FansSex) >= 2:
            #MALE += 1
            return 0
        else:
            #FEMALE += 1
            return 1
    else:
        print pFansUID
        #print _FansText
        #OTHER += 1
        return 2


if __name__ == '__main__':
    start_time = datetime.datetime.now()
    main()
    end_time = datetime.datetime.now()
    print 'total time consumption: ' + \
            str((end_time - start_time).seconds) + 's'
