import threading
import json
import requests
import time
import random

class MyThread(threading.Thread):
    def __init__(self,func,args,name=''):
        threading.Thread.__init__(self)
        self.func = func
        self.name = name
        self.args = args

    def run(self):
        self.res = self.func(*self.args)

    def get_result(self):
        return self.res

class APICall:
    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.lock = threading.Lock()
    def call_api(self, data):
        """调用模型的API，返回response"""
        print(f'api[{self.name}] Start at {time.time()}')
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
        print(f'api[{self.name}] End at {time.time()}')
        return ret
            
    def _call_api(self, data):
        pyload = {"user_post": data['user_post']}
        # print(f'payload: {pyload}')
        response = requests.post(self.url, data=pyload).text
        return response

class MultiAPIs:
    def __init__(self, config_path="./api_config.json"):
        """根据配置文件，建立多个模型的APICall对象"""
        config = json.load(open(config_path))
        self.apis = {}
        for name in config.keys():
            self.apis[name] = APICall(name, config[name]['url'])
        self.bot_names = list(self.apis.keys())
        self.bot_info = config
    
    def call_api_by_name(self, name, data):
        """基于当前的结果去修改API"""
        api = self.apis[name]
        return api.call_api(data)

    def call_all_apis(self, data):
        responses = {}
        for name in self.bot_names:
            responses[name] = self.call_api_by_name(name, data)
        return responses

    def call_all_apis_multithreading(self, data):
        """用多线程非阻塞的方式发送post请求，目前还未实现"""
        threads = []
        for name in self.bot_names:
            threads.append(MyThread(func=self.apis[name].call_api, args=(data,)))
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        responses = {}
        for i in range(len(self.bot_names)):
            responses[self.bot_names[i]] = threads[i].get_result()
        return responses

    def call_api_by_rank(self, data):
        """调用排序模块，返回多模型中的一个回复"""
        responses = self.call_all_apis(data)
        # 排序算法
        target_name = random.choice(self.bot_names)
        ret = {
            'bot_name': target_name,
            'responses': responses,
            'response': responses[target_name]['response'],
        }
        return ret

    def get_bot_names(self):
        """返回所有模型的name"""
        return self.bot_names