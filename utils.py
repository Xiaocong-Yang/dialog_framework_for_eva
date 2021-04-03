import threading
import json
import requests

class APICall:
    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.lock = threading.Lock()
    def call_api(self, data):
        ret = None
        if self.lock.acquire(timeout=5):
            try:
                ret = self._call_api(data)
                ret = json.loads(ret)
            except:
                print(f'Error: APICall.call_api(), name: {self.name}, url: {self.url}')
                ret = {"response": f"这是从后台返回的一条测试语句，如果看到这一句话说明底层接口{self.name}::{self.url}调用失败。", "name": self.name}
            finally:
                self.lock.release()
        else:
            ret = {"response": f"这是从后台返回的一条测试语句，如果看到这一句话说明底层接口{self.name}::{self.url}当前在线用户过多，排队超时。", "name": self.name}
        return ret
            
    def _call_api(self, data):
        pyload = {"user_post": data['user_post']}
        # print(f'payload: {pyload}')
        response = requests.post(self.url, data=pyload).text
        return response

class MultiAPIs:
    def __init__(self, config_path):
        config = json.load(open(config_path))
        self.apis = {}
        for name in config.keys():
            self.apis[name] = APICall(name, config[name]['url'])
    
    def call_api_by_name(self, name, data):
        api = self.apis[name]
        return api.call_api(data)

    def get_bot_names(self):
        return list(self.apis.keys())