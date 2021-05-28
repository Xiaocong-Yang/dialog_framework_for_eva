import threading
import json
import requests
import time
import random
import traceback
from text_censor import text_censor
import base64
import uuid
import copy

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
    def __init__(self, name, url, use_history=False):
        self.name = name
        self.url = url
        self.use_history = use_history
        self.lock = threading.Lock()
        if self.name.lower() == 'cpm':
            self.prompt = '以下是一段对话：“{}”“'
        elif self.name.lower() == 'wenhuiqadialog':
            self.prompt = '以下是一段对话：“{}”“'
        elif self.name.lower() == 'wenhuichatdialog':
            self.prompt = '以下是一段对话：“{}”“'
        self.headers = {"Content-Type": "application/json;charset=UTF-8"}
    def _response_clean(self, response, send_post=''):
        # print('原始输出：' + response)
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
            response = response[len(send_post):]
            idx = response.find('”')
            if idx >= 0:
                return response[:idx].strip()
            else:
                return response
        return response

    def _user_post_process(self, user_post, history=[]):
        # print('对话历史', history)
        if self.name == 'cpm':
            single_post = self.prompt.format(user_post)
            if self.use_history and len(history) > 0:
                multi_post = single_post[:8] + '“' + '”“'.join(history) + '”' + single_post[8:]
                return multi_post
            else:
                return single_post
        elif self.name == 'wenhuiqadialog':
            single_post = self.prompt.format(user_post)
            if self.use_history and len(history) > 0:
                multi_post = single_post[:8] + '“' + '”“'.join(history) + '”' + single_post[8:]
                return multi_post
            else:
                return single_post
        elif self.name == 'wenhuichatdialog':
            single_post = self.prompt.format(user_post)
            if self.use_history and len(history) > 0:
                multi_post = single_post[:8] + '“' + '”“'.join(history) + '”' + single_post[8:]
                return multi_post
            else:
                return single_post
        elif self.name == 'eva':
            single_post = user_post
            if self.use_history and len(history) > 0:
                multi_post = '\t\t'.join(history) + '\t\t' + single_post
                return multi_post
            else:
                return single_post
        return user_post

    def get_safe_response(self):
        candidate_responses = [
            '这个问题我还回答不了哦~',
            '没有听懂您的问题，可以换个说法吗？'
        ]
        return random.choice(candidate_responses)

    def call_api(self, data):
        """调用模型的API，返回response"""
        print(f'api[{self.name}] Start at {time.time()}')
        ret = None
        ## 敏感文本检测
        user_post = data['user_post']
        if not text_censor(user_post) and self.name != 'wenlan':
            print(f'拦截敏感输入【{user_post}】')
            return {'response': self.get_safe_response(), 'name': self.name}
        if self.lock.acquire(timeout=5):
            try:
                user_post = self._user_post_process(data['user_post'], history=data['history'])
                data['user_post'] = user_post
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
                elif self.name == 'wenlan':
                    ret['response'] = ret['sentence']
                ret['response'] = self._response_clean(ret['response'], user_post)
            except Exception as e:
                print(f'Error: APICall.call_api(), name: {self.name}, url: {self.url}')
                traceback.print_exc()
                # ret = {"response": f"这是从后台返回的一条测试语句，如果看到这一句话说明底层接口{self.name}::{self.url}调用失败。", "name": self.name}
                ret = {"response": self.get_safe_response(), "name": self.name}
            finally:
                self.lock.release()
        else:
            ret = {"response": f"这是从后台返回的一条测试语句，如果看到这一句话说明底层接口{self.name}::{self.url}当前在线用户过多，排队超时。", "name": self.name}
        # 对回复进行过滤
        if not text_censor(ret['response']):
            print('模型输出触发敏感词过滤', ret['response'])
            ret['response'] = self.get_safe_response()
        # 对模型的错误进行过滤
        if ret['response'].lower().strip() == 'bad input text':
            print('触发后端模型敏感词过滤')
            ret['response'] = self.get_safe_response()
        print(f'api[{self.name}] End at {time.time()}')
        return ret
            
    def _call_api(self, data):
        ## 对输入的数据做预处理
        pyload = {"user_post": data['user_post']}
        print('最终输入：' + data['user_post'])
        user_post = data['user_post']
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
        elif self.name == 'wenlan':
            base64_input = user_post
            prefixs = [
                'data:image/jpeg;base64,',
                'data:image/jpg;base64,',
                'data:image/png;base64,'
            ]
            img_type = ''
            for item in prefixs:
                if base64_input.startswith(item):
                    img_type = item.split('image/')[1].split(';')[0]
                base64_input = base64_input.replace(item, '')
            # print('image type', img_type)
            base64_input = bytes(base64_input, encoding = "utf8")
            # print(base64_input[:100])
            img_data = base64.b64decode(base64_input)
            tmp_name = get_time_stamp() + '_' + uuid.uuid4().hex + '.' + img_type
            # print('image_name', tmp_name)
            file = open('tmp/img/'+tmp_name, 'wb')  
            file.write(img_data)
            file.close()
            input_stream = open('tmp/img/'+tmp_name, 'rb')
            response = requests.post(self.url, files={'local_img':input_stream}).text
        else:
            response = requests.post(self.url, data=pyload).text
        return response

def get_time_stamp():
    return str(int(time.time()))

class MultiAPIs:
    def __init__(self, config_path="./api_config.json"):
        """根据配置文件，建立多个模型的APICall对象"""
        config = json.load(open(config_path))
        self.apis = {}
        for name in config.keys():
            self.apis[name] = APICall(name, config[name]['url'], config[name]['use_history'])
        self.bot_names = list(self.apis.keys())
        self.bot_info = config
    
    def call_api_by_name(self, name, data):
        """基于当前的结果去修改API"""
        api = self.apis[name]
        return api.call_api(copy.deepcopy(data))

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
        # target_name = random.choice(self.bot_names)
        target_name = data['response_bot_name']
        ret = {
            'bot_name': target_name,
            'responses': responses,
            'response': responses[target_name]['response'],
        }
        return ret

    def get_bot_names(self):
        """返回所有模型的name"""
        return self.bot_names