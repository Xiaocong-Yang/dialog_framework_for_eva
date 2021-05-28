from flask import Flask, session, redirect, render_template, flash, request, url_for
from flask import g
import threading
import json
from time import sleep
import random
import requests
from utils import MultiAPIs
import time
# from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.secret_key = 'large scale pre-training project'
apicall_lock = threading.Lock()
names = []
test_number = 0
api_controller = MultiAPIs('./api_config.json')
bot_names = api_controller.get_bot_names()
# socketio = SocketIO(app, threaded=True)

@app.route('/')
def index():
	user = session.get('username')
	if user:
		return redirect(url_for('single'))
	else:
		return render_template('login.html')

@app.route('/login', methods=['POST'])
def login(): 
	global test_number, apicall_lock
	username = request.form['username']
	session['username'] = username
	session['dialog_history'] = []
	# number = 0
	# if username == '123':
	# 	number = 6
	# else:
	# 	number = 8
	# if apicall_lock.acquire():
	# 	for _ in range(100000000):
	# 		test_number += number
	# 		test_number -= number
	# apicall_lock.release()
	# print(test_number)
	print(f'user: {username} login')
	return redirect(url_for('index'))

@app.route('/logout')
def logout():
	session.pop('username')
	return redirect(url_for('index'))

@app.route('/show_test_result', methods=['POST'])
def show_test_result():
	messages = request.form['messages']
	messages = json.loads(messages)
	result = ''
	for i in range(len(messages) // 2):
		user_msg = messages[i*2]
		sys_msg = messages[i*2+1]
		turn_str = f"<tr><td>{user_msg['message']}</td><td>{sys_msg['message']}</td><td>{sys_msg['is_heshi']}</td><td>{sys_msg['is_juti']}</td></tr>"
		result += '\n' + turn_str
	result = result.strip()
	# result = '<html><body><table><tr><td>用户</td><td>系统</td><td>合适</td><td>具体</td></tr>' + result + '</table></body>'
	result = '<html><body><table>' + result + '</table></body>'
	return {
		"status": 0, 
		"message": result}

@app.route('/show_text/<content>')
def show_text(content):
	return content

@app.route('/multi')
def multi():
	user = session.get('username')
	if not user:
		return render_template('login.html')
	dialog_history = session.get('dialog_history')
	if not dialog_history:
		dialog_history = []
		session['dialog_history'] = []
	data = {
		'username': user,
		'dialog_history': dialog_history
	}
	return render_template('multi.html', data=data)

@app.route('/single')
def single():
	user = session.get('username')
	if not user:
		return render_template('login.html')
	dialog_history = session.get('dialog_history')
	if not dialog_history:
		dialog_history = []
		session['dialog_history'] = []
	data = {
		'username': user,
		'dialog_history': dialog_history
	}
	return render_template('single.html', data=data)

@app.route('/group')
def group():
	user = session.get('username')
	if not user:
		return render_template('login.html')
	dialog_history = session.get('dialog_history')
	if not dialog_history:
		dialog_history = []
		session['dialog_history'] = []
	data = {
		'username': user,
		'dialog_history': dialog_history
	}
	return render_template('group.html', data=data)


@app.route('/user_post', methods=['POST'])
def user_post():
	user_uttr = request.form['user_utterance']
	dialog_history = session['dialog_history']
	dialog_history.append(['user', user_uttr])
	dialog_history.append(['system', f'system utterance id {(len(dialog_history)+1)/2}'])
	username = session.get('username')
	session['dialog_history'] = dialog_history
	data = {
		'username': username,
		'dialog_history': dialog_history
	}
	return render_template('home.html', data=data)

@app.route('/clear_history', methods=['POST'])
def clear_history():
	session['dialog_history'] = []
	data = {
		'username': session['username'],
		'dialog_history': []
	}
	return render_template('home.html', data=data)

@app.route('/get_bot_info', methods=['POST'])
def get_bot_info():
	global api_controller, bot_names
	return {
		"status": 0, 
		"message": 123123, 
		"bot_info": api_controller.bot_info,
		"bot_names": bot_names}

@app.route('/send_message', methods=['POST'])
def send_message():
	global bot_names
	user_post = request.form['user_post']
	chat_mode = request.form['chat_mode']
	history = request.form['history']
	history = json.loads(history)
	ret = {
		"status": 0, 
		"message": 123123, 
		}
	start_time = time.time()
	post_data = {'user_post': user_post, 'history': history}
	print(f'user input: {user_post}')
	if chat_mode == 'single':
		single_bot_name = request.form['single_bot_name']
		ret['bot_name'] = single_bot_name
		ret['response'] = api_controller.call_api_by_name(single_bot_name, post_data)['response']
	elif chat_mode == 'multi':
		rank_response = api_controller.call_api_by_rank(post_data)
		ret['bot_name'] = rank_response['bot_name']
		ret['responses'] = rank_response['responses']
		ret['response'] = rank_response['response']
	else:  # group
		responses = api_controller.call_all_apis(post_data)
		# 随机选择下一个
		target_bot_name = random.choice(bot_names)
		ret['bot_name'] = target_bot_name
		ret['responses'] = responses
		ret['response'] = responses[target_bot_name]['response']
	if 'responses' in ret:
		for key in ret['responses']:
			ret['responses'][key]['label'] = ""
	print(f'total time: {time.time() - start_time}')
	return ret
	
if __name__ == '__main__':
	# socketio.run(app, debug=True, host='0.0.0.0', port=5000)
	app.run(host="0.0.0.0", port=5001, debug=True, threaded=True)
