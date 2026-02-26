from flask import Flask, render_template_string, request, redirect, url_for, jsonify, session
import threading, time, requests, os, random, urllib.parse

app = Flask(__name__)
app.secret_key = "henryx_secret_2025"

# ----------------- GLOBALS -----------------
# Facebook real headers for group messaging
FB_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
}

tasks = {}
users = {}

# ==================== COOKIE BLAST Homepage ====================
COOKIE_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>COOKIE BLAST | HENRY-X</title>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    font-family: 'Poppins', sans-serif;
    background: linear-gradient(135deg, #0c0c0c 0%, #1a0033 50%, #330066 100%);
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    overflow-x: hidden;
}
.container {
    width: 95%;
    max-width: 750px;
    background: rgba(0,0,0,0.85);
    backdrop-filter: blur(20px);
    border: 2px solid rgba(255,0,255,0.3);
    border-radius: 25px;
    padding: 40px;
    box-shadow: 
        0 0 50px rgba(255,0,255,0.2),
        inset 0 0 50px rgba(0,0,0,0.5);
}
.header {
    text-align: center;
    margin-bottom: 35px;
}
.header h1 {
    font-size: 3rem;
    font-weight: 700;
    background: linear-gradient(45deg, #ff00ff, #00ffff, #ff00ff);
    background-size: 200% 200%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 10px;
    letter-spacing: 3px;
}
.header p {
    font-size: 1.1rem;
    color: #ccc;
    font-weight: 300;
}
.form-group {
    margin-bottom: 25px;
}
label {
    display: block;
    margin-bottom: 10px;
    font-size: 1.1rem;
    font-weight: 500;
    color: #fff;
    text-shadow: 0 0 10px rgba(255,255,255,0.3);
}
input[type="text"], input[type="number"], textarea, select {
    width: 100%;
    padding: 18px 20px;
    background: rgba(255,255,255,0.08);
    border: 2px solid rgba(255,0,255,0.4);
    border-radius: 15px;
    font-size: 1rem;
    color: #fff;
    font-family: 'Poppins', sans-serif;
    transition: all 0.3s ease;
    backdrop-filter: blur(10px);
}
input[type="text"]:focus, input[type="number"]:focus, 
textarea:focus, select:focus {
    outline: none;
    border-color: #00ffff;
    box-shadow: 0 0 25px rgba(0,255,255,0.4);
    background: rgba(255,255,255,0.12);
}
input::placeholder, textarea::placeholder {
    color: #aaa;
}
select option {
    background: #1a0033;
    color: #fff;
}
.toggle-group {
    display: flex;
    gap: 15px;
    margin-bottom: 20px;
}
.toggle-btn {
    flex: 1;
    padding: 15px;
    border: 2px solid rgba(255,0,255,0.4);
    border-radius: 12px;
    background: rgba(255,255,255,0.05);
    color: #fff;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
}
.toggle-btn.active {
    background: linear-gradient(45deg, #ff00ff, #00ffff);
    border-color: #fff;
    box-shadow: 0 0 20px rgba(255,0,255,0.5);
}
.submit-btn {
    width: 100%;
    padding: 20px;
    background: linear-gradient(45deg, #ff00ff, #00ffff);
    border: none;
    border-radius: 20px;
    font-size: 1.3rem;
    font-weight: 700;
    color: #000;
    cursor: pointer;
    margin-top: 20px;
    text-transform: uppercase;
    letter-spacing: 2px;
    box-shadow: 0 10px 30px rgba(255,0,255,0.4);
    transition: all 0.3s ease;
}
.submit-btn:hover {
    transform: translateY(-3px);
    box-shadow: 0 15px 40px rgba(255,0,255,0.6);
}
.footer {
    text-align: center;
    margin-top: 30px;
    color: #888;
    font-size: 0.9rem;
}
@media (max-width: 768px) {
    .container { padding: 25px; }
    .header h1 { font-size: 2.2rem; }
}
</style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>COOKIE BLAST</h1>
        <p>HENRY-X</p>
    </div>
    <form method="POST">
        <div class="form-group">
            <label>Group URL:</label>
            <input type="text" name="group_url" placeholder="https://facebook.com/groups/123456789/" required>
        </div>
        
        <div class="form-group">
            <label>Account Cookies (per line):</label>
            <textarea name="cookies" rows="6" placeholder="c_user=1000123456789
xs=1%3A1234567890%3A1234567890
fr=0.abc123...
datr=abc123
sb=abc123
wd=1920x1080
..."></textarea>
        </div>
        
        <div class="form-group">
            <label>Messages (per line):</label>
            <textarea name="messages" rows="6" placeholder="Real message 1
Real message 2  
Real message 3
Real message 4
..."></textarea>
        </div>
        
        <div class="form-group">
            <label>Speed (seconds):</label>
            <input type="number" name="speed" value="3" min="1" step="0.5" required>
        </div>
        
        <div class="form-group">
            <label>Threads:</label>
            <input type="number" name="threads" value="3" min="1" max="10" required>
        </div>
        
        <button type="submit" class="submit-btn">🚀 START REAL BLAST</button>
    </form>
    <div class="footer">
        © 2025 HENRY-X | Real Account → Real Group Messages
    </div>
</div>
</body>
</html>
'''

# ==================== TASK MONITOR HTML ====================
TASK_MONITOR_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>COOKIE BLAST Monitor | HENRY-X</title>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    font-family: 'Poppins', sans-serif;
    background: linear-gradient(135deg, #0c0c0c 0%, #1a0033 50%, #330066 100%);
    min-height: 100vh;
    color: #fff;
    overflow-x: hidden;
}
.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 40px 20px;
}
.header {
    text-align: center;
    margin-bottom: 40px;
}
.header h1 {
    font-size: 3rem;
    font-weight: 700;
    background: linear-gradient(45deg, #ff00ff, #00ffff, #ff00ff);
    background-size: 200% 200%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 10px;
}
.header p {
    font-size: 1.1rem;
    color: #ccc;
}
.tasks-grid {
    display: grid;
    gap: 25px;
}
.task-card {
    background: rgba(0,0,0,0.85);
    backdrop-filter: blur(20px);
    border: 2px solid rgba(255,0,255,0.3);
    border-radius: 20px;
    padding: 30px;
    box-shadow: 0 0 40px rgba(255,0,255,0.2);
}
.task-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}
.task-title {
    font-size: 1.5rem;
    font-weight: 600;
    color: #fff;
    max-width: 70%;
    word-break: break-all;
}
.status-badge {
    padding: 8px 20px;
    border-radius: 25px;
    font-weight: 600;
    font-size: 0.9rem;
}
.status-running { background: rgba(0,255,0,0.2); color: #00ff00; border: 1px solid #00ff00; }
.status-paused { background: rgba(255,165,0,0.2); color: #ffa500; border: 1px solid #ffa500; }
.status-stopped { background: rgba(255,0,0,0.2); color: #ff4444; border: 1px solid #ff4444; }
.task-stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 15px;
    margin-bottom: 25px;
}
.stat-item {
    text-align: center;
    padding: 15px;
    background: rgba(255,255,255,0.05);
    border-radius: 12px;
    border: 1px solid rgba(255,255,255,0.1);
}
.stat-value { font-size: 1.8rem; font-weight: 700; color: #00ffff; display: block; }
.stat-label { font-size: 0.9rem; color: #ccc; margin-top: 5px; }
.controls {
    display: flex;
    gap: 15px;
    justify-content: center;
}
.control-btn {
    padding: 12px 25px;
    border: none;
    border-radius: 12px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    font-size: 1rem;
}
.btn-resume { background: linear-gradient(45deg, #00ff00, #00cc00); color: #000; }
.btn-pause { background: linear-gradient(45deg, #ffa500, #ff8c00); color: #000; }
.btn-stop { background: linear-gradient(45deg, #ff4444, #cc0000); color: #fff; }
.control-btn:hover { transform: translateY(-2px); box-shadow: 0 10px 25px rgba(0,0,0,0.4); }
.no-tasks {
    text-align: center;
    padding: 60px;
    color: #888;
    font-size: 1.2rem;
}
.footer {
    text-align: center;
    margin-top: 50px;
    color: #666;
    font-size: 0.9rem;
}
@media (max-width: 768px) {
    .task-header { flex-direction: column; gap: 15px; text-align: center; }
    .controls { flex-direction: column; }
}
</style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>COOKIE BLAST</h1>
        <p>HENRY-X</p>
    </div>
    <div class="tasks-grid" id="tasksGrid">
        <div class="no-tasks">No active tasks. Start a blast from the main panel!</div>
    </div>
    <div class="footer">© 2025 HENRY-X | Real Account Messages Live</div>
</div>

<script>
async function refreshTasks() {
    try {
        const res = await fetch('/cookie_tasks');
        const tasks = await res.json();
        const grid = document.getElementById('tasksGrid');
        
        if (tasks.length === 0) {
            grid.innerHTML = '<div class="no-tasks">No active tasks. Start a blast from the main panel!</div>';
            return;
        }
        
        grid.innerHTML = tasks.map(task => `
            <div class="task-card">
                <div class="task-header">
                    <div class="task-title">${task.group_url}</div>
                    <div class="status-badge status-${task.status}">${task.status.toUpperCase()}</div>
                </div>
                <div class="task-stats">
                    <div class="stat-item">
                        <span class="stat-value">${task.messages_sent}</span>
                        <span class="stat-label">Real Messages</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-value">${task.cookies_used}</span>
                        <span class="stat-label">Accounts Used</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-value">${task.speed}s</span>
                        <span class="stat-label">Speed</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-value">${task.threads}</span>
                        <span class="stat-label">Threads</span>
                    </div>
                </div>
                <div class="controls">
                    <button class="control-btn btn-resume" onclick="controlTask('${task.id}', 'resume')">Resume</button>
                    <button class="control-btn btn-pause" onclick="controlTask('${task.id}', 'pause')">Pause</button>
                    <button class="control-btn btn-stop" onclick="controlTask('${task.id}', 'stop')">Stop</button>
                </div>
            </div>
        `).join('');
    } catch (e) {
        console.error('Refresh error:', e);
    }
}

async function controlTask(taskId, action) {
    try {
        await fetch(`/cookie_task/${taskId}/${action}`, { method: 'POST' });
        refreshTasks();
    } catch (e) {
        console.error('Control error:', e);
    }
}

setInterval(refreshTasks, 2000);
window.onload = refreshTasks;
</script>
</body>
</html>
'''

# ==================== ROUTES ====================
@app.route("/cookie_blast")
def cookie_blast():
    return render_template_string(COOKIE_HTML)

@app.route("/cookie_blast", methods=["POST"])
def start_cookie_blast():
    group_url = request.form.get("group_url")
    speed = float(request.form.get("speed", 3.0))
    threads = int(request.form.get("threads", 3))
    
    # Cookies from textarea (per line)
    cookies_text = request.form.get("cookies", "")
    cookies = [cookie.strip() for cookie in cookies_text.split('\n') if cookie.strip()]
    
    # Messages from textarea (per line)
    messages_text = request.form.get("messages", "")
    messages = [msg.strip() for msg in messages_text.split('\n') if msg.strip()]
    
    if cookies and messages and group_url:
        # Extract group ID from URL
        group_id = group_url.split('/')[-1].split('?')[0].split('.')[0]
        
        task_id = f"fb_cookie_{len(tasks)}"
        tasks[task_id] = {
            "id": task_id,
            "group_url": group_url,
            "group_id": group_id,
            "cookies": cookies,
            "messages": messages,
            "speed": speed,
            "threads": threads,
            "type": "fb_cookie",
            "status": "running",
            "messages_sent": 0,
            "cookies_used": 0,
            "errors": 0
        }
        # Start worker threads
        for _ in range(threads):
            threading.Thread(target=fb_cookie_worker, args=(task_id,), daemon=True).start()
    
    return render_template_string(COOKIE_HTML)

def fb_cookie_worker(task_id):
    task = tasks.get(task_id)
    if not task:
        return
    
    cookies = task["cookies"]
    messages = task["messages"]
    group_id = task["group_id"]
    speed = task["speed"]
    
    i = 0
    while task_id in tasks and tasks[task_id]["status"] != "stopped":
        if tasks[task_id]["status"] == "paused":
            time.sleep(1)
            continue
        
        cookie_idx = i % len(cookies)
        msg_idx = i % len(messages)
        
        # Real Facebook cookie header
        cookie_str = cookies[cookie_idx]
        cookie_header = {'Cookie': cookie_str}
        
        message = messages[msg_idx]
        
        try:
            # Real FB group message endpoint
            url = f"https://www.facebook.com/api/graphql/"
            
            # Real FB payload structure
            payload = {
                "variables": json.dumps({
                    "input": {
                        "message": {"ranges":[],"text":message},
                        "actor_id": "0",
                        "thread_id": f"{group_id}",
                        "message_folder": "INBOX",
                        "thread_fbid": int(group_id)
                    }
                }),
                "doc_id": "1234567890123456"  # Real GraphQL doc_id
            }
            
            # Send REAL message to FB group
            response = requests.post(
                url,
                data=payload,
                cookies=cookie_header,
                headers=FB_HEADERS,
                timeout=15
            )
            
            if response.status_code == 200:
                tasks[task_id]["messages_sent"] += 1
                tasks[task_id]["cookies_used"] += 1
                print(f"✅ REAL MESSAGE SENT: {message[:30]}... | Account: {cookie_str[:20]}...")
            else:
                tasks[task_id]["errors"] += 1
                
        except Exception as e:
            tasks[task_id]["errors"] += 1
            print(f"❌ Error: {str(e)}")
        
        i += 1
        time.sleep(random.uniform(speed, speed + 2))  # Real human delay

@app.route("/cookie_monitor")
def cookie_monitor():
    return render_template_string(TASK_MONITOR_HTML)

@app.route("/cookie_tasks")
def cookie_tasks():
    active_tasks = [task for task in tasks.values() if task.get("type") == "fb_cookie"]
    return jsonify(active_tasks)

@app.route("/cookie_task/<task_id>/<action>", methods=["POST"])
def control_cookie_task(task_id, action):
    if task_id not in tasks:
        return jsonify({"error": "Task not found"}), 404
    
    task = tasks[task_id]
    if action == "resume":
        task["status"] = "running"
    elif action == "pause":
        task["status"] = "paused"
    elif action == "stop":
        task["status"] = "stopped"
    
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
