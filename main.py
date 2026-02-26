from flask import Flask, render_template, request, jsonify, session
import requests
import json
import time
import threading
import random
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'fallback-secret')

# Simple UA list (no fake-useragent dependency)
USER_AGENTS = [
    'Mozilla/5.0 (Linux; Android 13; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1'
]

active_sessions = {}

class FacebookBot:
    def __init__(self, uid, password):
        self.uid = uid
        self.session = requests.Session()
        self.login(uid, password)
    
    def get_random_ua(self):
        return random.choice(USER_AGENTS)
    
    def login(self, uid, password):
        login_url = "https://m.facebook.com/login.php"
        headers = {'User-Agent': self.get_random_ua()}
        
        data = {
            'email': uid,
            'pass': password,
            'login': 'Log In'
        }
        resp = self.session.post(login_url, data=data, headers=headers, allow_redirects=True)
        self.cookies = dict(self.session.cookies)
        return "c_user" in self.cookies
    
    def send_group_post(self, group_id, message):
        # Updated working GraphQL endpoint
        url = "https://www.facebook.com/api/graphql/"
        headers = {'User-Agent': self.get_random_ua()}
        
        payload = {
            "doc_id": "4782784568232043",
            "variables": json.dumps({
                "input": {
                    "target_id": group_id,
                    "message": {"ranges":[],"text": message},
                    "actor_id": self.uid,
                    "client_mutation_id": "1"
                }
            })
        }
        try:
            resp = self.session.post(url, data=payload, headers=headers)
            return resp.status_code == 200
        except:
            return False
    
    def send_message(self, target_id, message):
        url = "https://www.facebook.com/messaging/send/"
        data = {
            'message_body': message,
            'thread_id': target_id
        }
        headers = {'User-Agent': self.get_random_ua()}
        try:
            resp = self.session.post(url, data=data, headers=headers)
            return resp.status_code in [200, 302]
        except:
            return False

# Routes same rahenge (upar wala code copy karo)
# ... [previous routes code same]

@app.route('/login', methods=['POST'])
def fb_login():
    uid = request.form['uid']
    password = request.form['password']
    
    bot = FacebookBot(uid, password)
    if "c_user" in bot.cookies:
        session_id = f"bot_{random.randint(1000,9999)}"
        active_sessions[session_id] = {
            'bot': bot,
            'status': 'active',
            'type': request.form.get('type', 'group')
        }
        return jsonify({'success': True, 'session_id': session_id})
    return jsonify({'success': False, 'error': 'Login failed'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
