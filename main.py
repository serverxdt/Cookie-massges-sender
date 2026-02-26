from flask import Flask, render_template, request, jsonify, session
import requests
import json
import time
import threading
import random
from fake_useragent import UserAgent

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# Active sessions store
active_sessions = {}

class FacebookBot:
    def __init__(self, uid, password):
        self.uid = uid
        self.session = requests.Session()
        self.ua = UserAgent()
        self.login(uid, password)
    
    def login(self, uid, password):
        # Facebook mobile login flow
        login_url = "https://m.facebook.com/login.php"
        headers = {
            'User-Agent': self.ua.mobile
        }
        data = {
            'email': uid,
            'pass': password,
            'login': 'Log In'
        }
        resp = self.session.post(login_url, data=data, headers=headers)
        self.cookies = dict(self.session.cookies)
        return "c_user" in self.cookies
    
    def send_group_message(self, group_id, message):
        url = "https://www.facebook.com/api/graphql/"
        payload = {
            "doc_id": "4782784568232043",  # Live GraphQL ID
            "variables": json.dumps({
                "input": {
                    "target_id": group_id,
                    "message": {"text": message},
                    "actor_id": self.uid
                }
            })
        }
        headers = {'User-Agent': self.ua.random}
        resp = self.session.post(url, data=payload, headers=headers)
        return resp.status_code == 200
    
    def send_e2ee_message(self, target_uid, message):
        url = "https://www.facebook.com/messaging/send/"
        data = {
            'message_body': message,
            'thread_id': target_uid
        }
        resp = self.session.post(url, data=data)
        return resp.status_code in [200, 302]

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/login', methods=['POST'])
def fb_login():
    uid = request.form['uid']
    password = request.form['password']
    
    bot = FacebookBot(uid, password)
    if bot.login(uid, password):
        session_id = f"bot_{len(active_sessions)}"
        active_sessions[session_id] = {
            'bot': bot,
            'status': 'active',
            'type': 'group' if 'group' in request.form else 'e2ee'
        }
        return jsonify({'success': True, 'session_id': session_id})
    return jsonify({'success': False, 'error': 'Login failed'})

@app.route('/start_campaign', methods=['POST'])
def start_campaign():
    session_id = request.form['session_id']
    messages = request.form['messages'].split('\n')
    delay = int(request.form['delay'])
    target = request.form['target']
    
    if session_id not in active_sessions:
        return jsonify({'success': False})
    
    bot = active_sessions[session_id]['bot']
    
    def campaign_loop():
        for msg in messages:
            if active_sessions[session_id]['status'] == 'stopped':
                break
                
            if active_sessions[session_id]['type'] == 'group':
                success = bot.send_group_message(target, msg.strip())
            else:
                success = bot.send_e2ee_message(target, msg.strip())
            
            time.sleep(delay * random.uniform(0.8, 1.2))  # Human-like variation
    
    thread = threading.Thread(target=campaign_loop)
    thread.start()
    
    return jsonify({'success': True})

@app.route('/stop_campaign/<session_id>')
def stop_campaign(session_id):
    if session_id in active_sessions:
        active_sessions[session_id]['status'] = 'stopped'
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
