from flask import Flask, session, redirect, render_template, flash, request, url_for
from time import sleep
import random

app = Flask(__name__)

@app.route('/bot1', methods=['POST'])
def bert_call():
    user_utterance = request.form.get('user_post')
    print(f'BEFRT get user utterance: {user_utterance}')
    # sleep(random.choice([0,1,2]))
    return {
        'response': "这是模拟BOT1模型给出的一条测试回复，是调用了系统接口得到的。",
        'confidence': 0.0,
        "name": "bot1"
    }

@app.route('/bot2', methods=['POST'])
def gpt_call():
    user_utterance = request.form.get('user_post')
    print(f'GPT get user utterance: {user_utterance}')
    # sleep(random.choice([0,1,2]))
    return {
        'response': "这是模拟BOT2模型给出的一条测试回复，是调用了系统接口得到的。",
        'confidence': 0.0,
        "name": "bot2"
    }

@app.route('/bot3', methods=['POST'])
def t5_call():
    user_utterance = request.form.get('user_post')
    print(f'T5 get user utterance: {user_utterance}')
    # sleep(random.choice([0,1,2]))
    return {
        'response': "这是模拟BOT3模型给出的一条测试回复，是调用了系统接口得到的。",
        'confidence': 0.0,
        "name": "bot3"
    }

if __name__ == '__main__':
   app.run(debug=True, threaded=False, port=5002)
