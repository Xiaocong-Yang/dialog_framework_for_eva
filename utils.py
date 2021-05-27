import threading
import json
import requests
import time
import random
import traceback

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
        if self.name.lower() == 'cpm':
            self.prompt = '“{}”“'
        elif self.name.lower() == 'wenhuiqadialog':
            self.prompt = '以下是一段对话：“{}”“'
        elif self.name.lower() == 'wenhuichatdialog':
            self.prompt = '以下是一段对话：“{}”“'
        self.headers = {"Content-Type": "application/json;charset=UTF-8"}
    def _response_clean(self, response):
        if self.name == 'cpm':
            idx = response.find('”')
            if idx >= 0:
                return response[:idx].strip()
            else:
                return response
        elif self.name == 'wenhuiqadialog':
            idx = response.find('”')
            if idx >= 0:
                return response[:idx].strip()
            else:
                return response
        elif self.name == 'wenhuichatdialog':
            idx = response.find('”“')
            res = response[idx+2:].strip()
            idx = res.find('”')
            if idx >= 0:
                return res[:idx].strip()
            else:
                return res
        return response

    def _user_post_process(self, user_post):
        if self.name == 'cpm':
            return self.prompt.format(user_post)
        elif self.name == 'wenhuiqadialog':
            return self.prompt.format(user_post)
        elif self.name == 'wenhuichatdialog':
            return self.prompt.format(user_post)
        return user_post

    def call_api(self, data):
        """调用模型的API，返回response"""
        print(f'api[{self.name}] Start at {time.time()}')
        ret = None
        if self.lock.acquire(timeout=5):
            try:
                ret = self._call_api(data)
                ret = json.loads(ret)
                # 处理不同的输出情况
                if self.name == 'wenhuiqa':
                    ret['response'] = ret['result']['content']
                elif self.name == 'wenhuichat':
                    ret['response'] = ret['result']
                elif self.name == 'wenhuiqadialog':
                    ret['response'] = ret['result']['content']
                elif self.name == 'wenhuichatdialog':
                    ret['response'] = ret['result']
                ret['response'] = self._response_clean(ret['response'])
            except Exception as e:
                print(f'Error: APICall.call_api(), name: {self.name}, url: {self.url}')
                traceback.print_exc()
                ret = {"response": f"这是从后台返回的一条测试语句，如果看到这一句话说明底层接口{self.name}::{self.url}调用失败。", "name": self.name}
            finally:
                self.lock.release()
        else:
            ret = {"response": f"这是从后台返回的一条测试语句，如果看到这一句话说明底层接口{self.name}::{self.url}当前在线用户过多，排队超时。", "name": self.name}
        print(f'api[{self.name}] End at {time.time()}')
        return ret
            
    def _call_api(self, data):
        ## 对输入的数据做预处理
        user_post = self._user_post_process(data['user_post'])
        pyload = {"user_post": user_post}
        # print(f'payload: {pyload}')
        if self.name == 'cpm':
            pyload['length'] = 30
        if self.name == 'wenhuiqa':
            response = requests.post(self.url, headers=self.headers, data=json.dumps({'token': 'b7680795f940de1e04e7e71e16e59d2e', "app": "qa", "content": user_post})).text
        elif self.name == 'wenhuichat':
            response = requests.post(self.url, headers=self.headers, data=json.dumps({'token': 'b7680795f940de1e04e7e71e16e59d2e', "app": "chat", "content": user_post})).text
        elif self.name == 'wenhuiqadialog':
            response = requests.post(self.url, headers=self.headers, data=json.dumps({'token': 'b7680795f940de1e04e7e71e16e59d2e', "app": "qa", "content": user_post})).text
        elif self.name == 'wenhuichatdialog':
            response = requests.post(self.url, headers=self.headers, data=json.dumps({'token': 'b7680795f940de1e04e7e71e16e59d2e', "app": "chat", "content": user_post})).text
        else:
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