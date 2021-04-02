import threading
import json

class APICall:
    def __init__(self, name, url):
        self.name = name
        self.queue = []
        self.lock = threading.Lock()
    def call_api(self, data):
        ret = None
        if self.lock.acquire(blocking=True):
            try:
                ret = self._call_api(data)
            except:
                print(f'Error: APICall.call_api()')
            finally:
                self.lock.release()
        return ret
            
    def _call_api(self, data):
        return f'{self.name}: This is a test case.'

class MultiAPIs:
    def __init__(self, config_path):
        config = json.load(open(config_path))
        self.apis = {}
        for name in config.keys():
            self.apis[name] = APICall(name, config[name]['url'])
    
    def call_api_by_name(self, name, data):
        api = self.apis['name']
        return api.call_api(data)