import sys
import json
import base64
import os
import time
import sys


IS_PY3 = sys.version_info.major == 3
if IS_PY3:
    from urllib.request import urlopen
    from urllib.request import Request
    from urllib.error import URLError
    from urllib.parse import urlencode
    from urllib.parse import quote_plus
else:
    import urllib2
    from urllib import quote_plus
    from urllib2 import urlopen
    from urllib2 import Request
    from urllib2 import URLError
    from urllib import urlencode


import ssl
ssl._create_default_https_context = ssl._create_unverified_context

## AK and SK can be fetched at Baidu AI platform
API_KEY = 'RWc91IhdOXqihgOkmcytEEA3'

SECRET_KEY = 'aee7nzuSwx3Nc9LdhXj6xUEtQdVHczVi'


TEXT_CENSOR = "https://aip.baidubce.com/rest/2.0/solution/v1/text_censor/v2/user_defined";


TOKEN_URL = 'https://aip.baidubce.com/oauth/2.0/token'



def fetch_token():
    params = {'grant_type': 'client_credentials',
              'client_id': API_KEY,
              'client_secret': SECRET_KEY}
    post_data = urlencode(params)
    if (IS_PY3):
        post_data = post_data.encode('utf-8')
    req = Request(TOKEN_URL, post_data)
    try:
        f = urlopen(req, timeout=5)
        result_str = f.read()
    except URLError as err:
        print(err)
    if (IS_PY3):
        result_str = result_str.decode()


    result = json.loads(result_str)

    if ('access_token' in result.keys() and 'scope' in result.keys()):
        if not 'brain_all_scope' in result['scope'].split(' '):
            print ('please ensure has check the  ability')
            exit()
        return result['access_token']
    else:
        print ('please overwrite the correct API_KEY and SECRET_KEY')
        exit()



def request(url, data):
    req = Request(url, data.encode('utf-8'))
    has_error = False
    try:
        f = urlopen(req)
        result_str = f.read()
        if (IS_PY3):
            result_str = result_str.decode()
        return result_str
    except  URLError as err:
        print(err)


def text_cencor(text):
    ## conclusion:审核结果类型，可取值1.合规，2.不合规，3.疑似，4.审核失败
    ## words:违规的词语
    ## type:审核主类型，11：百度官方违禁词库、12：文本反作弊、13:自定义文本黑名单、14:自定义文本白名单
    ## subType:审核子类型，此字段需参照type主类型字段决定其含义：
        # 当type=11时subType取值含义：
        # 0:百度官方默认违禁词库
        # 当type=12时subType取值含义：
        # 0:低质灌水、1:暴恐违禁、2:文本色情、3:政治敏感、4:恶意推广、5:低俗辱骂 6:恶意推广-联系方式、7:恶意推广-软文推广、8:广告法审核
        # 当type=13时subType取值含义：
        # 0:自定义文本黑名单
        # 当type=14时subType取值含义：
        # 0:自定义文本白名单
    assert type(text) == str, 'Input text must be of string type '

    token = fetch_token()
    text_url = TEXT_CENSOR + "?access_token=" + token
    result = json.loads(request(text_url, urlencode({'text': text})))
    output = {}
    
    if 'error_code' in result.keys():
        result['conclusionType'] = 1
        
    if result['conclusionType'] == 1:
        output['conclusionType'] = result['conclusionType']
        return output

    else:
        output['conclusionType'] = result['conclusionType']
        output['words'] = [[subsubdata['words'] for subsubdata in subdata['hits']] for subdata in result['data']]
        output['type'] = [subdata['type'] for subdata in result['data']]
        output['subType'] = [subdata['subType'] for subdata in result['data']]
        return output
    
def text_censor(sent):
    """对小骢实现的text_cencor进行封装，只返回True或False。"""
    output = text_cencor(sent)
    # print(output)
    if output['conclusionType'] == 1:
        return True
    # elif output['conclusionType'] == 2:
    #     return False
    elif output['conclusionType'] in [2,3]:
        if 'subType' in output:
            bad_sub_types = [3]
            for bad_st in bad_sub_types:
                if bad_st in output['subType']:
                    return False
        return True
    return True

if __name__ == '__main__':
    print(text_censor('光州事件 民主运动'))