# coding=utf-8

import sys
import json
import base64
import os
import time
import sys

# 保证兼容python2以及python3
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

# 防止https证书校验不正确
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

API_KEY = 'RWc91IhdOXqihgOkmcytEEA3'

SECRET_KEY = 'aee7nzuSwx3Nc9LdhXj6xUEtQdVHczVi'


IMAGE_CENSOR = "https://aip.baidubce.com/rest/2.0/solution/v1/img_censor/v2/user_defined"



"""  TOKEN start """
TOKEN_URL = 'https://aip.baidubce.com/oauth/2.0/token'


"""
    获取token
"""
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

"""
    读取文件
"""
def read_file(image_path):
    f = None
    try:
        f = open(image_path, 'rb')
        return f.read()
    except:
        print('read image file fail')
        return None
    finally:
        if f:
            f.close()


"""
    调用远程服务
"""
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

def image_cencor(image_path):
    start = time.time()
    token = fetch_token()
    image_url = IMAGE_CENSOR + "?access_token=" + token
    assert os.path.exists(image_path), 'Image path does not exists. '
    file_content = read_file(image_path)
    result = json.loads(request(image_url, urlencode({'image': base64.b64encode(file_content)})))
    output = {}
    if result['conclusionType'] == 1:
        output['conclusionType'] = result['conclusionType']
        return output

    else:
        output['conclusionType'] = result['conclusionType']
        output['type'] = [subdata['type'] for subdata in result['data']]
        return output



    
    ##conclusionType:审核结果类型，可取值1、2、3、4，分别代表1：合规，2：不合规，3：疑似，4：审核失败
    ##type:结果具体命中的模型：0:百度官方违禁图库、1：色情识别、2：暴恐识别、3：恶心图识别、4:广告检测、\\
        # 5：政治敏感识别、6：图像质量检测、7：用户图像黑名单、8：用户图像白名单、10：用户头像审核、\\
            # 11：百度官方违禁词库、12：图文审核、13:自定义文本黑名单、14:自定义文本白名单、\\
                # 15:EasyDL自定义模型、16：敏感旗帜标志识别、21：不良场景识别、24：直播场景审核

if __name__ == '__main__':
    print(image_cencor('picture/political/[www.google.com][440].jpg'))