from flask import Flask, render_template_string, request, redirect, url_for, jsonify, session
import threading
import time
import requests
import json
import random
import os

app = Flask(__name__)
app.secret_key = "henryx_cookie_blast_2025"

# Global tasks storage
tasks = {}
lock = threading.Lock()

# ==================== COOKIE BLAST MAIN PANEL ====================
@app.route("/", defaults={'path': ''})
@app.route("/cookie_blast")
@app.route("/cookie_blast/")
def cookie_blast_panel():
    return render_template_string(COOKIE_PANEL_HTML)

# ==================== COOKIE BLAST WORKER ====================
def fb_cookie_worker(task_id):
    with lock:
        if task_id not in tasks:
            return
            
        task = tasks[task_id]
        cookies = task["cookies"][:]
        messages = task["messages"][:]
    
    cookie_idx = 0
    msg_idx = 0
    
    while task_id in tasks:
        with lock:
            task_status = tasks[task_id]["status"]
            if task_status == "stopped":
                break
            if task_status == "paused":
                time.sleep(2)
                continue
        
        try:
            # Rotate through cookies and messages
            cookie_str = cookies[cookie_idx % len(cookies)]
            message = messages[msg_idx % len(messages)]
            
            # Facebook GraphQL endpoint for messaging
            url = "https://www.facebook.com/api/graphql/"
            
            payload = {
                "variables": json.dumps({
                    "input": {
                        "message": {"ranges": [], "text": message},
                        "actor_id": "0",
                        "thread_id": task["group_id"],
                        "message_folder": "INBOX"
                    }
                }),
                "doc_id": "533424368348617"
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Cookie': cookie_str,
                'Referer': 'https://www.facebook.com/',
                'Origin': 'https://www.facebook.com'
            }
            
            response = requests.post(url, data=payload, headers=headers, timeout=10)
            
            with lock:
                if response.status_code in [200, 202]:
                    tasks[task_id]["messages_sent"] += 1
                else:
                    tasks[task_id]["errors"] += 1
                
        except:
            with lock:
                tasks[task_id]["errors"] += 1
        
        cookie_idx += 1
        msg_idx += 1
        
        # Dynamic delay
        delay = random.uniform(task["speed"], task["speed"] + 1)
        time.sleep(delay)

# ==================== START BLAST ====================
@app.route("/start_blast", methods=['POST'])
def start_blast():
    try:
        group_url = request.form['group_url'].strip()
        cookies_text = request.form['cookies'].strip()
        messages_text = request.form['messages'].strip()
        speed = float(request.form.get('speed', 3.0))
        threads = int(request.form.get('threads', 3))
        
        # Parse inputs
        cookies = [c.strip() for c in cookies_text.split('\n') if c.strip()]
        messages = [m.strip() for m in messages_text.split('\n') if m.strip()]
        
        if not (cookies and messages and group_url):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Extract group ID
        group_id = group_url.split('/')[-1].split('?')[0].split('.')[0]
        
        task_id = f"blast_{int(time.time())}"
        
        with lock:
            tasks[task_id] = {
                'id': task_id,
                'group_url': group_url,
                'group_id': group_id,
                'cookies': cookies,
                'messages': messages,
                'speed': speed,
                'threads': threads,
                'status': 'running',
                'messages_sent': 0,
                'cookies_used': 0,
                'errors': 0,
                'start_time': time.time()
            }
        
        # Start threads
        for i in range(threads):
            t = threading.Thread(target=fb_cookie_worker, args=(task_id,), daemon=True)
            t.start()
        
        return jsonify({'success': True, 'task_id': task_id})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== TASK MONITOR ====================
@app.route("/monitor")
def monitor():
    return render_template_string(MONITOR_HTML)

@app.route("/api/tasks")
def api_tasks():
    with lock:
        active_tasks = [
            {
                'id': t['id'],
                'group_url': t['group_url'],
                'status': t['status'],
                'messages_sent': t['messages_sent'],
                'errors': t['errors'],
                'speed': t['speed'],
                'threads': t['threads']
            }
            for t in tasks.values()
        ]
    return jsonify(active_tasks)

@app.route("/api/task/<task_id>/<action>", methods=['POST'])
def control_task(task_id, action):
    with lock:
        if task_id not in tasks:
            return jsonify({'error': 'Task not found'}), 404
        
        if action == 'pause':
            tasks[task_id]['status'] = 'paused'
        elif action == 'resume':
            tasks[task_id]['status'] = 'running'
        elif action == 'stop':
            tasks[task_id]['status'] = 'stopped'
        
        return jsonify({'success': True})

# ==================== HTML TEMPLATES ====================
COOKIE_PANEL_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>COOKIE BLAST | HENRY-X</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0c0c0c 0%, #1a0033 50%, #330066 100%);
            min-height: 100vh;
            color: white;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: rgba(0,0,0,0.9);
            border-radius: 20px;
            padding: 30px;
            border: 1px solid #ff00ff;
            box-shadow: 0 0 50px rgba(255,0,255,0.3);
        }
        h1 {
            text-align: center;
            font-size: 2.5em;
            background: linear-gradient(45deg, #ff00ff, cyan);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 25px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
            color: #ccc;
        }
        input, textarea, select {
            width: 100%;
            padding: 15px;
            border: 2px solid #444;
            border-radius: 10px;
            background: #111;
            color: white;
            font-size: 14px;
            font-family: inherit;
        }
        textarea {
            resize: vertical;
            min-height: 120px;
        }
        input:focus, textarea:focus, select:focus {
            outline: none;
            border-color: #ff00ff;
            box-shadow: 0 0 10px rgba(255,0,255,0.5);
        }
        .controls {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 25px;
        }
        button {
            padding: 15px 25px;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
        }
        .start-btn {
            background: linear-gradient(45deg, #ff00ff, cyan);
            color: black;
            grid-column: span 2;
        }
        .start-btn:hover {
            transform: scale(1.05);
            box-shadow: 0 10px 30px rgba(255,0,255,0.6);
        }
        .status {
            text-align: center;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
        }
        .success { background: rgba(0,255,0,0.2); color: #0f0; }
        .error { background: rgba(255,0,0,0.2); color: #f00; }
        .monitor-link {
            display: block;
            text-align: center;
            margin-top: 25px;
            color: cyan;
            text-decoration: none;
            padding: 15px;
            background: rgba(0,255,255,0.1);
            border-radius: 10px;
            border: 2px solid cyan;
        }
        .monitor-link:hover {
            background: rgba(0,255,255,0.2);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 COOKIE BLAST</h1>
        <p style="text-align: center; color: #ccc; margin-bottom: 30px;">Real FB Group Messaging - HENRY-X</p>
        
        <form id="blastForm">
            <div class="form-group">
                <label>🎯 Group URL:</label>
                <input type="url" name="group_url" placeholder="https://facebook.com/groups/123456/" required>
            </div>
            
            <div class="form-group">
                <label>🍪 Account Cookies (per line):</label>
                <textarea name="cookies" placeholder="c_user=1000123456789&#10;xs=1%3A1234567890%3A1234567890&#10;fr=0.abc123..." required></textarea>
            </div>
            
            <div class="form-group">
                <label>💬 Messages (per line):</label>
                <textarea name="messages" placeholder="Real message 1&#10;Real message 2&#10;Real message 3" required></textarea>
            </div>
            
            <div class="controls">
                <div class="form-group">
                    <label>⚡ Speed (seconds):</label>
                    <input type="number" name="speed" value="3" min="1" step="0.5" required>
                </div>
                <div class="form-group">
                    <label>🔥 Threads:</label>
                    <input type="number" name="threads" value="3" min="1" max="10" required>
                </div>
            </div>
            
            <button type="submit" class="start-btn">🚀 START REAL BLAST</button>
        </form>
        
        <div id="status"></div>
        
        <a href="/monitor" class="monitor-link">📊 Live Task Monitor</a>
    </div>

    <script>
        document.getElementById('blastForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            const statusDiv = document.getElementById('status');
            
            statusDiv.innerHTML = '<div class="status">🚀 Starting blast...</div>';
            
            try {
                const response = await fetch('/start_blast', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (result.success) {
                    statusDiv.innerHTML = `
                        <div class="status success">
                            ✅ Blast started! Task ID: ${result.task_id}<br>
                            📊 Monitor live progress: <a href="/monitor" style="color: cyan;">Click here</a>
                        </div>
                    `;
                } else {
                    statusDiv.innerHTML = `<div class="status error">❌ Error: ${result.error}</div>`;
                }
            } catch (error) {
                statusDiv.innerHTML = `<div class="status error">❌ Network error: ${error.message}</div>`;
            }
        });
    </script>
</body>
</html>
'''

MONITOR_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>COOKIE BLAST Monitor | HENRY-X</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0c0c0c 0%, #1a0033 50%, #330066 100%);
            min-height: 100vh;
            color: white;
            padding: 20px;
        }
        .container { max-width: 1000px; margin: 0 auto; }
        h1 {
            text-align: center;
            font-size: 2.5em;
            background: linear-gradient(45deg, #ff00ff, cyan);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 30px;
        }
        .tasks {
            display: grid;
            gap: 20px;
        }
        .task-card {
            background: rgba(0,0,0,0.8);
            border: 2px solid #ff00ff;
            border-radius: 15px;
            padding: 25px;
        }
        .task-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        .task-url { font-weight: bold; color: cyan; }
        .status {
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 12px;
        }
        .status.running { background: rgba(0,255,0,0.2); color: #0f0; }
        .status.paused { background: rgba(255,165,0,0.2); color: orange; }
        .status.stopped { background: rgba(255,0,0,0.2); color: #f00; }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        .stat {
            text-align: center;
            padding: 15px;
            background: rgba(255,255,255,0.05);
            border-radius: 10px;
        }
        .stat-value { font-size: 24px; font-weight: bold; color: cyan; display: block; }
        .controls button {
            margin-right: 10px;
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
        }
        .btn-resume { background: #0f0; color: black; }
        .btn-pause { background: orange; color: black; }
        .btn-stop { background: #f00; color: white; }
        .no-tasks {
            text-align: center;
            padding: 60px;
            color: #888;
            font-size: 18px;
        }
        .back-link {
            display: inline-block;
            margin-bottom: 30px;
            color: cyan;
            text-decoration: none;
            padding: 12px 24px;
            border: 2px solid cyan;
            border-radius: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 COOKIE BLAST Monitor</h1>
        <a href="/" class="back-link">← Back to Blast Panel</a>
        <div class="tasks" id="tasks"></div>
    </div>

    <script>
        async function refreshTasks() {
            try {
                const res = await fetch('/api/tasks');
                const tasks = await res.json();
                const container = document.getElementById('tasks');
                
                if (tasks.length === 0) {
                    container.innerHTML = '<div class="no-tasks">No active blasts. Start from main panel!</div>';
                    return;
                }
                
                container.innerHTML = tasks.map(task => `
                    <div class="task-card">
                        <div class="task-header">
                            <div class="task-url">${task.group_url}</div>
                            <div class="status ${task.status}">${task.status.toUpperCase()}</div>
                        </div>
                        <div class="stats">
                            <div class="stat">
                                <span class="stat-value">${task.messages_sent}</span>
                                Sent
                            </div>
                            <div class="stat">
                                <span class="stat-value">${task.errors}</span>
                                Errors
                            </div>
                            <div class="stat">
                                <span class="stat-value">${task.speed}s</span>
                                Speed
                            </div>
                            <div class="stat">
                                <span class="stat-value">${task.threads}</span>
                                Threads
                            </div>
                        </div>
                        <div class="controls">
                            <button class="btn-resume" onclick="control('${task.id}', 'resume')">Resume</button>
                            <button class="btn-pause" onclick="control('${task.id}', 'pause')">Pause</button>
                            <button class="btn-stop" onclick="control('${task.id}', 'stop')">Stop</button>
                        </div>
                    </div>
                `).join('');
            } catch (e) {
                console.error('Refresh failed:', e);
            }
        }
        
        async function control(taskId, action) {
            try {
                await fetch(`/api/task/${taskId}/${action}`, { method: 'POST' });
                refreshTasks();
            } catch (e) {
                console.error('Control failed:', e);
            }
        }
        
        setInterval(refreshTasks, 2000);
        refreshTasks();
    </script>
</body>
</html>
'''

if __name__ == "__main__":
    print("🚀 HENRY-X COOKIE BLAST starting on http://localhost:5000")
    print("Press Ctrl+C to stop")
    app.run(host="0.0.0.0", port=5000, debug=False)
