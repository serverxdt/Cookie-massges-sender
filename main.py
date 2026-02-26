from flask import Flask, request, jsonify
import threading
import time
import requests
import json
import random

app = Flask(__name__)

# Simple global storage
tasks = {}
task_lock = threading.Lock()

print("🚀 Starting HENRY-X COOKIE BLAST...")

@app.route('/')
def home():
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>COOKIE BLAST - HENRY-X</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        *{margin:0;padding:0;box-sizing:border-box;}
        body{font-family:Arial,sans-serif;background:#0a0a1a;color:white;min-height:100vh;padding:20px;}
        .container{max-width:900px;margin:0 auto;background:rgba(0,0,0,0.9);padding:30px;border-radius:15px;border:1px solid #ff00ff;box-shadow:0 0 30px rgba(255,0,255,0.3);}
        h1{text-align:center;font-size:2.5em;background:linear-gradient(45deg,#ff00ff,cyan);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:30px;}
        .form-group{margin-bottom:20px;}
        label{display:block;margin-bottom:8px;font-weight:bold;color:#ccc;}
        input,textarea{width:100%;padding:12px;border:2px solid #444;border-radius:8px;background:#111;color:white;font-size:14px;}
        textarea{min-height:100px;resize:vertical;}
        input:focus,textarea:focus{outline:none;border-color:#ff00ff;box-shadow:0 0 10px #ff00ff;}
        .row{display:grid;grid-template-columns:1fr 1fr;gap:15px;}
        button{width:100%;padding:15px;background:linear-gradient(45deg,#ff00ff,cyan);border:none;border-radius:10px;font-size:16px;font-weight:bold;color:black;cursor:pointer;margin-top:20px;}
        button:hover{transform:scale(1.02);}
        #status{padding:20px;margin-top:20px;border-radius:10px;text-align:center;display:none;}
        .success{background:rgba(0,255,0,0.2);color:#0f0;border:1px solid #0f0;}
        .error{background:rgba(255,0,0,0.2);color:#f00;border:1px solid #f00;}
        .monitor{margin-top:25px;padding:15px;background:rgba(0,255,255,0.1);border:2px solid cyan;border-radius:10px;text-align:center;}
        a{color:cyan;text-decoration:none;font-weight:bold;}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 COOKIE BLAST</h1>
        <p style="text-align:center;color:#ccc;margin-bottom:30px;">Real Facebook Group Messaging</p>
        
        <form id="form">
            <div class="form-group">
                <label>🎯 Group URL:</label>
                <input type="text" name="url" placeholder="https://facebook.com/groups/123456/" required>
            </div>
            
            <div class="form-group">
                <label>🍪 Cookies (per line):</label>
                <textarea name="cookies" placeholder="c_user=1000123456789
xs=1%3A1234567890%3A1234567890
fr=0.abc123..." required></textarea>
            </div>
            
            <div class="form-group">
                <label>💬 Messages (per line):</label>
                <textarea name="messages" placeholder="Hello everyone!
This is test message
Real message 3" required></textarea>
            </div>
            
            <div class="row">
                <div class="form-group">
                    <label>⚡ Speed (sec):</label>
                    <input type="number" name="speed" value="3" min="1" step="0.5">
                </div>
                <div class="form-group">
                    <label>🔥 Threads:</label>
                    <input type="number" name="threads" value="3" min="1" max="8">
                </div>
            </div>
            
            <button type="submit">🚀 START BLAST</button>
        </form>
        
        <div id="status"></div>
        
        <div class="monitor">
            <a href="/monitor" style="font-size:18px;">📊 Live Monitor →</a>
        </div>
    </div>

    <script>
        document.getElementById('form').onsubmit = async e => {
            e.preventDefault();
            const form = new FormData(e.target);
            const status = document.getElementById('status');
            status.style.display = 'block';
            status.innerHTML = '🚀 Starting...';
            status.className = '';
            
            try {
                const res = await fetch('/start', {method:'POST', body:form});
                const data = await res.json();
                
                if(data.success) {
                    status.className = 'success';
                    status.innerHTML = `✅ Started! ID: ${data.id}<br><a href="/monitor">📊 Monitor Live</a>`;
                } else {
                    status.className = 'error';
                    status.innerHTML = `❌ ${data.error}`;
                }
            } catch(e) {
                status.className = 'error';
                status.innerHTML = `❌ Error: ${e.message}`;
            }
        }
    </script>
</body>
</html>
'''

@app.route('/start', methods=['POST'])
def start_blast():
    try:
        url = request.form['url'].strip()
        cookies = [c.strip() for c in request.form['cookies'].split('\n') if c.strip()]
        messages = [m.strip() for m in request.form['messages'].split('\n') if m.strip()]
        speed = float(request.form.get('speed', 3))
        threads = int(request.form.get('threads', 3))
        
        if len(cookies) < 1 or len(messages) < 1:
            return jsonify({'success': False, 'error': 'Need cookies & messages'})
        
        task_id = f'task_{int(time.time())}'
        
        with task_lock:
            tasks[task_id] = {
                'id': task_id,
                'url': url,
                'cookies': cookies,
                'messages': messages,
                'speed': speed,
                'threads': threads,
                'status': 'running',
                'sent': 0,
                'errors': 0
            }
        
        # Start threads
        for _ in range(threads):
            t = threading.Thread(target=worker, args=(task_id,), daemon=True)
            t.start()
        
        return jsonify({'success': True, 'id': task_id})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def worker(task_id):
    import requests
    
    while task_id in tasks:
        with task_lock:
            task = tasks.get(task_id)
            if not task or task['status'] != 'running':
                break
            
            cookie = random.choice(task['cookies'])
            message = random.choice(task['messages'])
            
        try:
            headers = {
                'Cookie': cookie,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {
                'variables': json.dumps({
                    'input': {
                        'message': {'text': message},
                        'thread_id': task['url'].split('/')[-1]
                    }
                })
            }
            
            r = requests.post('https://www.facebook.com/api/graphql/', 
                            data=data, headers=headers, timeout=10)
            
            with task_lock:
                if r.status_code == 200:
                    task['sent'] += 1
                else:
                    task['errors'] += 1
                    
        except:
            with task_lock:
                if task_id in tasks:
                    tasks[task_id]['errors'] += 1
        
        time.sleep(random.uniform(task['speed'], task['speed'] + 1))

@app.route('/monitor')
def monitor():
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>Monitor - HENRY-X</title>
    <meta charset="utf-8">
    <style>
        *{margin:0;padding:0;box-sizing:border-box;}
        body{font-family:Arial,sans-serif;background:#0a0a1a;color:white;min-height:100vh;padding:20px;}
        .container{max-width:1000px;margin:0 auto;}
        h1{text-align:center;font-size:2.5em;background:linear-gradient(45deg,#ff00ff,cyan);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
        .back{margin-bottom:30px;display:inline-block;padding:12px 24px;background:rgba(0,255,255,0.1);border:2px solid cyan;border-radius:10px;color:cyan;text-decoration:none;}
        .tasks{display:grid;gap:20px;}
        .task{background:rgba(0,0,0,0.8);padding:25px;border-radius:15px;border:1px solid #ff00ff;}
        .header{display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;}
        .status{padding:8px 16px;border-radius:20px;font-weight:bold;}
        .running{background:rgba(0,255,0,0.3);color:#0f0;}
        .stats{display:grid;grid-template-columns:repeat(4,1fr);gap:15px;margin-bottom:20px;}
        .stat{text-align:center;padding:15px;background:rgba(255,255,255,0.05);border-radius:10px;}
        .stat-value{font-size:24px;color:cyan;display:block;font-weight:bold;}
        .controls button{margin-right:10px;padding:10px 20px;border:none;border-radius:8px;cursor:pointer;font-weight:bold;}
        .no-tasks{text-align:center;padding:60px;color:#888;font-size:18px;}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Live Monitor</h1>
        <a href="/" class="back">← Back to Blast</a>
        <div class="tasks" id="tasks">
            <div class="no-tasks">No active tasks</div>
        </div>
    </div>
    <script>
        async function refresh(){
            try{
                const r=await fetch('/api/tasks');
                const tasks=await r.json();
                const el=document.getElementById('tasks');
                if(tasks.length===0){
                    el.innerHTML='<div class="no-tasks">No active tasks</div>';
                    return;
                }
                el.innerHTML=tasks.map(t=>`
                    <div class="task">
                        <div class="header">
                            <div>${t.url}</div>
                            <div class="status running">${t.status}</div>
                        </div>
                        <div class="stats">
                            <div class="stat"><span class="stat-value">${t.sent}</span>Sent</div>
                            <div class="stat"><span class="stat-value">${t.errors}</span>Errors</div>
                            <div class="stat"><span class="stat-value">${t.speed}s</span>Speed</div>
                            <div class="stat"><span class="stat-value">${t.threads}</span>Threads</div>
                        </div>
                    </div>
                `).join('');
            }catch(e){}
        }
        setInterval(refresh,2000);
        refresh();
    </script>
</body>
</html>
'''

@app.route('/api/tasks')
def api_tasks():
    with task_lock:
        return jsonify(list(tasks.values()))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
