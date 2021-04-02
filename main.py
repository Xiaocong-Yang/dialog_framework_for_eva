from flask import Flask, session, redirect, render_template, flash, request, url_for
from flask import g
import threading

app = Flask(__name__)
app.secret_key = 'large scale pre-training project'
apicall_lock = threading.Lock()
names = []
test_number = 0

@app.route('/')
def index():
	user = session.get('username')
	if user:
		flash('Message: Welcome')
		return redirect(url_for('home'))
	else:
		flash('Message: Please login.')
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

if __name__ == '__main__':
   app.run(debug=True, threaded=True)
