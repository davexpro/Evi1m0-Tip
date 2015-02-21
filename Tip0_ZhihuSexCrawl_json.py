# -*- coding: utf-8 -*-
__author__ = 'Dave'

import re
import requests
import json
import datetime
import threadpool as tp
import sys

# UID = sys.argv[1]
UID = "Evi1m0"
# THREAD_NUM = sys.argv[2]
THREAD_NUM = 20

global HEADER, MALE, FEMALE, OTHER, LASTNUM, TOTAL, XSRF

XSRF = ""
OTHER = 0
TOTAL = 0
MALE = 0
FEMALE = 0
LASTNUM = 0

HEADER = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36',
    'Host': 'www.zhihu.com',
    'Origin': 'http://www.zhihu.com',
    'Referer': 'http://www.zhihu.com/people/dave-9/followees',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest'
}

COOKIES = {
    'q_c1':'',
    'c_c':'',
    'z_c0':'',
    '_xsrf': XSRF
}

# session object, keeping session
FansCount = requests.session()

def main():
    global  MALE, FEMALE, OTHER, TOTAL
    print "The User[uid] We Are Crawling is " + UID
    getHashId(UID)

    print "============ Final ============"
    print "Male: " + str(MALE) + "  Female: " + str(FEMALE) + " OTHER: " + str(OTHER)
    print "ADDUP: " + str(MALE + FEMALE +OTHER) + "  Total: " + str(TOTAL)


def getHashId(pUserID):
    global TOTAL

    _URL = 'http://www.zhihu.com/people/' + pUserID + '/followers'
    _FansCount = requests.get(_URL, cookies=COOKIES)

    _Pattern = "hash_id&quot;: &quot;(.*?)&quot"
    _tmp = re.findall(_Pattern, _FansCount.text)
    _hash_id = _tmp[0]

    _Pattern = "<strong>(.*?)</strong><label>"
    _tmp = re.findall(_Pattern, _FansCount.text)
    _FollowerNum = int(_tmp[1])
    TOTAL = _FollowerNum

    startCatch(_hash_id, _FollowerNum)


def startCatch(pHashID, pFollowNum):
    global LASTNUM, MALE, FEMALE, OTHER

    print "User HashId:" + pHashID
    print "User Followers Num:" + str(pFollowNum)

    _LastNum = pFollowNum%20
    LASTNUM = _LastNum
    _FollowTimes = pFollowNum/20
    if _LastNum>0:
        _FollowTimes = _FollowTimes+ 1
    print "For Circle Times:" + str(_FollowTimes)

    for i in range(_FollowTimes):
        print "Current Circle " + str(i + 1) + ":"

        _Offsets = 20*i

        try:
            oneTheadCatch(pHashID,_Offsets)
        except:
            oneTheadCatch(pHashID,_Offsets)

        print "Male: " + str(MALE) + "  Female: " + str(FEMALE) + " OTHER: " + str(OTHER) +  " ADDUP: " + str(MALE + FEMALE +OTHER)


def oneTheadCatch(pHashID, pOffsets):
    global XSRF

    #print "Now Offsets:" + str(pOffsets)
    _Params = json.dumps({"hash_id": pHashID, "order_by": "created", "offset": pOffsets, })
    _PostData = {
        'method': 'next',
        'params': _Params,
        '_xsrf': XSRF
    }

    try:
        _FansCount = requests.post("http://www.zhihu.com/node/ProfileFollowersListV2", data=_PostData, cookies=COOKIES,timeout=15)
    except:
        print "Post Failed! Reposting..."
        _FansCount = requests.post("http://www.zhihu.com/node/ProfileFollowersListV2", data=_PostData, cookies=COOKIES,timeout=30)

    #print _FansCount.text

    fansInfoAna(_FansCount.text)


def fansInfoAna(pJsonText):
    global LASTNUM, MALE, FEMALE, OTHER

    _TmpText = pJsonText.split("<\\/a>\\n<\\/div>\\n\\n<\\/div>\\n<\\/div>")

    for i in range(len(_TmpText) - 1):
        _TmpContent = _TmpText[i]

        _Pattern = 'www.zhihu.com\\\/people\\\/(.*?)\\\\'
        _Asortment = re.findall(_Pattern, _TmpContent)
        _FansUID = _Asortment[0]

        #_Pattern = '>(.*)<\\\/button>'
        #_Asortment = re.findall(_Pattern, _TmpContent)

        _TmpFollowed = _TmpContent.split('nth-0\\">\\u53d6\\u6d88\\u5173\\u6ce8<\\/button>')
        _TmpEachFollowed = _TmpContent.split("<\\/i>\\u53d6\\u6d88\\u5173\\u6ce8\\n<\\/button>")

        if len(_TmpEachFollowed) == 2 or len(_TmpFollowed) == 2:
            getFansSex(_FansUID)
        else:
            _TmpOtherHer = _TmpContent.split(">\u5173\u6ce8\u5979<\\/button>")
            _TmpMyselfHer = _TmpContent.split("<\\/i>\\u5173\\u6ce8\\u5979\\n<\\/button>")
            if len(_TmpOtherHer) == 2 or len(_TmpMyselfHer) == 2:
                _TmpOtherHer = _TmpContent.split(">\u5173\u6ce8\u5979<\\/button>")
                _TmpMyselfHer = _TmpContent.split("<\\/i>\\u5173\\u6ce8\\u5979\\n<\\/button>")
                if len(_TmpOtherHer) == 2 or len(_TmpMyselfHer) == 2:
                    FEMALE += 1
                else:
                    getFansSex(_FansUID)
            else:
                _TmpOtherHe = _TmpContent.split('nth-0\\">\\u5173\\u6ce8\\u4ed6<\\/button>')
                _TmpMyselfHe = _TmpContent.split("<\\/i>\\u5173\\u6ce8\\u4ed6\\n<\\/button>")
                if len(_TmpOtherHe) == 2 or len(_TmpMyselfHe) == 2:
                    _TmpOtherHe = _TmpContent.split('nth-0\\">\\u5173\\u6ce8\\u4ed6<\\/button>')
                    _TmpMyselfHe = _TmpContent.split("<\\/i>\\u5173\\u6ce8\\u4ed6\\n<\\/button>")
                    if len(_TmpOtherHe) == 2 or len(_TmpMyselfHe) == 2:
                        MALE += 1
                    else:
                        getFansSex(_FansUID)
                else:
                    _TmpMyself = _TmpContent.split('data-follow=\\"m:button\\"')
                    if len(_TmpMyself) == 2:
                        print _FansUID
                        OTHER += 1
                    else:
                        getFansSex(_FansUID)



def getFansSex(pFansUID):
    global MALE, FEMALE, OTHER

    try:
        _FansSex = requests.get("http://www.zhihu.com/people/" + pFansUID,cookies=COOKIES,timeout=15)
    except:
        print "Get Failed! Regetting..."
        _FansSex = requests.get("http://www.zhihu.com/people/" + pFansUID,cookies=COOKIES,timeout=30)

    _FansText = _FansSex.text
    _FansSex = _FansText.split("icon-profile-male")

    if len(_FansSex) == 2:
        _FansSex = _FansText.split("icon-profile-male")
        if len(_FansSex) == 2:
            MALE += 1
        else:
            getFansSex(pFansUID)
    else:
        _FansSex = _FansText.split("icon-profile-female")
        if len(_FansSex) == 2:
            _FansSex = _FansText.split("icon-profile-female")
            if len(_FansSex) == 2:
                FEMALE += 1
            else:
                getFansSex(pFansU)
        else:
            print pFansUID
            OTHER += 1


if __name__ == '__main__':
    start_time = datetime.datetime.now()
    main()
    end_time = datetime.datetime.now()
    print 'total time consumption: ' + str((end_time - start_time).seconds) + 's'
