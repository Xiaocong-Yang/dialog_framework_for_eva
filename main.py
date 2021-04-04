from flask import Flask, session, redirect, render_template, flash, request, url_for
from flask import g
import threading
import json
from time import sleep
import random
import requests
from utils import MultiAPIs
import time

app = Flask(__name__)
app.secret_key = 'large scale pre-training project'
apicall_lock = threading.Lock()
names = []
test_number = 0
api_controller = MultiAPIs('./api_config.json')
bot_names = api_controller.get_bot_names()

@app.route('/')
def index():
	user = session.get('username')
	if user:
		return redirect(url_for('home'))
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
	return redirect(url_for('index'))

@app.route('/logout')
def logout():
	session.pop('username')
	return redirect(url_for('index'))

@app.route('/home')
def home():
	user = session.get('username')
	dialog_history = session.get('dialog_history')
	if not dialog_history:
		dialog_history = []
		session['dialog_history'] = []
	data = {
		'username': user,
		'dialog_history': dialog_history
	}
	return render_template('home.html', data=data)

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

@app.route('/send_message', methods=['POST'])
def send_message():
	global bot_names
	user_post = request.form['user_post']
	ret = {
		"status": 0, 
		"message": 123123, 
		}
	# call base models
	target_bot = random.choice(bot_names)
	# print(f'bot names: {bot_names}')
	responses = {}
	start_time = time.time()
	post_data = {'user_post': user_post}
	# for name in bot_names:
	# 	responses[name] = api_controller.call_api_by_name(name, {'user_post': user_post})
	# responses = api_controller.call_all_apis({'user_post': user_post})
	# ret['response'] = responses[target_bot]['response']
	# ret['bot_name'] = target_bot
	# ret['responses'] = responses

	rank_response = api_controller.call_api_by_rank(post_data)
	ret['bot_name'] = rank_response['bot_name']
	ret['responses'] = rank_response['responses']
	ret['response'] = rank_response['response']

	print(f'total time: {time.time() - start_time}')
	return ret
	
if __name__ == '__main__':
	app.run(debug=True, threaded=True)
