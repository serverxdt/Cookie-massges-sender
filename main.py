from flask import Flask, request, jsonify
import threading
import time
import requests
import json
import random
import re

app = Flask(__name__)
tasks = {}
task_lock = threading.Lock()

@app.route('/')
def home():
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>FB GROUP COOKIE BLAST - HENRY-X</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        *{margin:0;padding:0;box-sizing:border-box;}
        body{font-family:Arial,sans-serif;background:linear-gradient(135deg,#0c0c0c,#1a0033);color:white;min-height:100vh;padding:20px;}
        .container{max-width:900px;margin:0 auto;background:rgba(0,0,0,0.9);padding:30px;border-radius:15px;border:1px solid #00ffff;box-shadow:0 0 30px rgba(0,255,255,0.3);}
        h1{text-align:center;font-size:2.5em;background:linear-gradient(45deg,#ff00ff,#00ffff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:20px;}
        .form-group{margin-bottom:20px;}
        label{display:block;margin-bottom:8px;font-weight:bold;color:#ccc;}
        input,textarea{width:100%;padding:12px;border:2px solid #444;border-radius:8px;background:#111;color:white;font-size:14px;}
        textarea{min-height:100px;resize:vertical;}
        input:focus,textarea:focus{outline:none;border-color:#00ffff;box-shadow:0 0 10px #00ffff;}
        .row{display:grid;grid-template-columns:1fr 1fr;gap:15px;}
        button{width:100%;padding:15px;background:linear-gradient(45deg,#ff00ff,#00ffff);border:none;border-radius:10px;font-size:16px;font-weight:bold;color:black;cursor:pointer;margin-top:20px;}
        button:hover{transform:scale(1.02);}
        #status{padding:20px;margin-top:20px;border-radius:10px;text-align:center;display:none;}
        .success{background:rgba(0,255,0,0.3);color:#0f0;border:1px solid #0f0;}
        .error{background:rgba(255,0,0,0.3);color:#f00;border:1px solid #f00;}
        .monitor{margin-top:25px;padding:15px;background:rgba(0,255,255,0.2);border:2px solid #00ffff;border-radius:10px;text-align:center;}
        a{color:#00ffff;text-decoration:none;font-weight:bold;}
        .info{padding:15px;background:rgba(255,0,255,0.1);border-radius:10px;margin-bottom:20px;border-left:4px solid #ff00ff;}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 FB GROUP COOKIE BLAST</h1>
        <div class="info">
            <strong>✅ REAL FB GROUP MESSAGES:</strong><br>
            1. Copy cookies from FB (F12 → Application → Cookies)<br>
            2. Group URL: https://facebook.com/groups/XXXXX/<br>
            3. Messages will appear as REAL user messages!
        </div>
        
        <form id="form">
            <div class="form-group">
                <label>🎯 Group URL:</label>
                <input type="text" name="url" placeholder="https://facebook.com/groups/123456789/" required>
            </div>
            
            <div class="form-group">
                <label>🍪 FB Cookies (Ctrl+F12 → Application → Cookies → Copy ALL):</label>
                <textarea name="cookies" placeholder="sb=abc123; datr=xyz789; c_user=1000123456; xs=1%3A123%3A123; fr=0.ABC... (paste ALL cookies)" required></textarea>
            </div>
            
            <div class="form-group">
                <label>💬 Messages:</label>
                <textarea name="messages" placeholder="Test message 1
Test message 2
Hello group!
Real message" required></textarea>
            </div>
            
            <div class="row">
                <div>
                    <label>⚡ Delay (sec):</label>
                    <input type="number" name="delay" value="5" min="2" step="0.5">
                </div>
                <div>
                    <label>🔥 Threads:</label>
                    <input type="number" name="threads" value="2" min="1" max="5">
                </div>
            </div>
            
            <button type="submit">🚀 SEND REAL MESSAGES</button>
        </form>
        
        <div id="status"></div>
        <div class="monitor">
            <a href="/monitor">📊 LIVE MONITOR →</a>
        </div>
    </div>

    <script>
        document.getElementById('form').onsubmit = async e => {
            e.preventDefault();
            const form = new FormData(e.target);
            const status = document.getElementById('status');
            status.style.display = 'block';
            status.innerHTML = '🔄 Starting real FB messages...';
            
            try {
                const res = await fetch('/send', {method:'POST', body:form});
                const data = await res.json();
                
                if(data.ok) {
                    status.innerHTML = `✅ Started! ${data.msgs.length} messages loaded<br><a href="/monitor">📊 Watch live</a>`;
                    status.className = 'success';
                } else {
                    status.innerHTML = `❌ ${data.error}`;
                    status.className = 'error';
                }
            } catch(e) {
                status.innerHTML = `❌ Network error`;
                status.className = 'error';
            }
        }
    </script>
</body>
</html>
'''

@app.route('/send', methods=['POST'])
def send_messages():
    try:
        url = request.form['url'].strip()
        cookie_text = request.form['cookies'].strip()
        msg_text = request.form['messages'].strip()
        delay = float(request.form.get('delay', 5))
        threads = int(request.form.get('threads', 2))
        
        # Parse cookies - join all into single string
        cookies = cookie_text.replace('\n', '; ').strip()
        
        # Parse messages
        messages = [m.strip() for m in msg_text.split('\n') if m.strip()]
        
        if not messages or not cookies:
            return jsonify({'ok': False, 'error': 'No messages or cookies'})
        
        # Extract thread_id from URL
        thread_match = re.search(r'/groups/(\d+)', url)
        if not thread_match:
            return jsonify({'ok': False, 'error': 'Invalid group URL'})
        
        thread_id = thread_match.group(1)
        
        task_id = f'fb_{int(time.time())}'
        
        with task_lock:
            tasks[task_id] = {
                'id': task_id, 'thread_id': thread_id, 'cookies': cookies,
                'messages': messages, 'delay': delay, 'threads': threads,
                'status': 'running', 'sent': 0, 'errors': 0, 'url': url
            }
        
        for i in range(threads):
            t = threading.Thread(target=real_fb_sender, args=(task_id,), daemon=True)
            t.start()
        
        return jsonify({'ok': True, 'msgs': messages})
        
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)})

def real_fb_sender(task_id):
    """Real Facebook messaging via composer endpoint"""
    while task_id in tasks:
        with task_lock:
            task = tasks[task_id]
            if task['status'] != 'running':
                break
            
            cookies = task['cookies']
            messages = task['messages']
            thread_id = task['thread_id']
        
        try:
            # REAL Facebook message composer endpoint
            url = f"https://www.facebook.com/ajax/mercury/send_messages.php"
            
            # Real Facebook composer payload
            data = {
                'message_batch[0][action_type]': 'ma-type:user-generated-message',
                'message_batch[0][author]': '', 
                'message_batch[0][author_email]': '',
                'message_batch[0][body]': random.choice(messages),
                'message_batch[0][has_attachment]': 'false',
                'message_batch[0][html_body]': 'false',
                'message_batch[0][is_unread]': 'false',
                'message_batch[0][is_forward]': 'false',
                'message_batch[0][manual_retry_cnt_local]': '0',
                'message_batch[0][thread_fbid]': thread_id,
                '__user': re.search(r'c_user=(\d+)', cookies).group(1) if re.search(r'c_user=(\d+)', cookies) else '',
                '__req': 'a1',
                '__beoa': '0',
                '__pc': 'PHASED:DEFAULT'
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': 'https://www.facebook.com',
                'Referer': f'https://www.facebook.com/groups/{thread_id}/',
                'Cookie': cookies,
                'X-FB-Friendly-Name': 'MessengerComposerController',
                'X-Requested-With': 'XMLHttpRequest'
            }
            
            response = requests.post(url, data=data, headers=headers, timeout=15)
            
            with task_lock:
                if response.status_code == 200 and 'error' not in response.text.lower():
                    tasks[task_id]['sent'] += 1
                    print(f"✅ MESSAGE SENT TO GROUP {thread_id}")
                else:
                    tasks[task_id]['errors'] += 1
                    print(f"❌ Error: {response.status_code} - {response.text[:100]}")
                    
        except Exception as e:
            with task_lock:
                if task_id in tasks:
                    tasks[task_id]['errors'] += 1
        
        time.sleep(random.uniform(task['delay'], task['delay'] + 2))

@app.route('/monitor')
def monitor():
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>Monitor</title>
    <meta charset="utf-8">
    <style>*{margin:0;padding:0;box-sizing:border-box;}body{font-family:Arial,sans-serif;background:#0a0a1a;color:white;min-height:100vh;padding:20px;}.container{max-width:1000px;margin:0 auto;}h1{text-align:center;font-size:2.5em;background:linear-gradient(45deg,#ff00ff,#00ffff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}.back{margin-bottom:30px;display:inline-block;padding:12px 24px;background:rgba(0,255,255,0.2);border:2px solid #00ffff;border-radius:10px;color:#00ffff;text-decoration:none;}.tasks{display:grid;gap:20px;}.task{background:rgba(0,0,0,0.8);padding:25px;border-radius:15px;border:1px solid #00ffff;}.header{display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;}.status{padding:8px 16px;border-radius:20px;font-weight:bold;}.running{background:rgba(0,255,0,0.4);color:#0f0;}.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:15px;margin-bottom:20px;}.stat{text-align:center;padding:15px;background:rgba(255,255,255,0.05);border-radius:10px;}.stat-value{font-size:24px;color:#00ffff;display:block;font-weight:bold;}.no-tasks{text-align:center;padding:60px;color:#888;font-size:18px;}</style>
</head>
<body>
    <div class="container">
        <h1>📊 LIVE GROUP MESSAGING</h1>
        <a href="/" class="back">← New Blast</a>
        <div class="tasks" id="tasks"><div class="no-tasks">Waiting for blasts...</div></div>
    </div>
    <script>
        async function refresh(){try{const r=await fetch('/status');const tasks=await r.json();const el=document.getElementById('tasks');if(tasks.length===0){el.innerHTML='<div class="no-tasks">No active blasts</div>';return;}el.innerHTML=tasks.map(t=>`<div class="task"><div class="header"><div>${t.url}</div><div class="status running">${t.status}</div></div><div class="stats"><div class="stat"><span class="stat-value">${t.sent}</span>Sent</div><div class="stat"><span class="stat-value">${t.errors}</span>Errors</div><div class="stat"><span class="stat-value">${t.delay}s</span>Delay</div><div class="stat"><span class="stat-value">${t.threads}</span>Threads</div></div></div>`).join('');}catch(e){}}setInterval(refresh,1500);refresh();
    </script>
</body>
</html>
'''

@app.route('/status')
def status():
    with task_lock:
        return jsonify(list(tasks.values()))

if __name__ == '__main__':
    print("🚀 FB GROUP COOKIE BLAST READY")
    print("http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
