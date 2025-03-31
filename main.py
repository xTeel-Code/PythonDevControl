from flask import Flask, render_template, jsonify, request
import os
import psutil
import subprocess
from datetime import datetime

# Try to import git, but don't fail if it's not available
try:
    import git
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    return jsonify({
        'status': 'running',
        'version': '1.0.0'
    })

@app.route('/api/system-stats')
def get_system_stats():
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return jsonify({
        'cpu': cpu_percent,
        'memory': memory.percent,
        'disk': disk.percent
    })

@app.route('/api/processes')
def get_processes():
    processes = []
    try:
        for proc in psutil.process_iter():
            try:
                # Get process information
                pinfo = proc.as_dict(attrs=['pid', 'name', 'status'])
                pinfo['cpu'] = round(proc.cpu_percent(interval=0.1), 1)
                pinfo['memory'] = f"{round(proc.memory_percent(), 1)}%"
                processes.append(pinfo)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
    except Exception as e:
        print(f"Error getting process list: {str(e)}")
        return jsonify({'processes': []})
    
    # Sort by CPU usage
    processes.sort(key=lambda x: x['cpu'], reverse=True)
    return jsonify({'processes': processes[:20]})  # Return top 20 processes

@app.route('/api/git-status')
def get_git_status():
    if not GIT_AVAILABLE:
        return jsonify({'status': 'Git is not installed on this system'})
    try:
        repo = git.Repo(os.getcwd())
        status = repo.git.status()
        return jsonify({'status': status})
    except Exception as e:
        return jsonify({'status': f"Error: {str(e)}"})

@app.route('/api/logs')
def get_logs():
    try:
        # Get system logs (this is a simple example - you might want to customize this)
        if os.name == 'nt':  # Windows
            # Use PowerShell to get recent system events in a more readable format
            ps_command = """
            Get-WinEvent -LogName System -MaxEvents 10 | 
            Select-Object TimeCreated, LevelDisplayName, Message | 
            Format-Table -AutoSize -Wrap | 
            Out-String -Width 4096
            """
            result = subprocess.run(['powershell', '-Command', ps_command], 
                                 capture_output=True, 
                                 encoding='cp1252')  # Use Windows encoding
            logs = result.stdout
        else:  # Linux/Unix
            logs = subprocess.check_output(['journalctl', '-n', '10']).decode('utf-8')
        
        # Clean up the output and make it more readable
        logs = logs.strip().replace('\r\n', '\n')
        return jsonify({'logs': logs})
    except Exception as e:
        return jsonify({'logs': f"Error: {str(e)}"})

@app.route('/api/terminate-process/<int:pid>', methods=['POST'])
def terminate_process(pid):
    try:
        process = psutil.Process(pid)
        process.terminate()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/execute-command', methods=['POST'])
def execute_command():
    try:
        command = request.json.get('command')
        if not command:
            return jsonify({'output': 'No command provided'}), 400

        # Execute the command and capture output
        if os.name == 'nt':  # Windows
            result = subprocess.run(['powershell', '-Command', command], 
                                 capture_output=True, 
                                 text=True,
                                 encoding='cp1252',  # Use Windows encoding
                                 shell=True)
        else:  # Linux/Unix
            result = subprocess.run(['bash', '-c', command], 
                                 capture_output=True, 
                                 text=True)

        output = result.stdout if result.stdout else result.stderr
        return jsonify({'output': output or 'Command executed successfully'})
    except Exception as e:
        return jsonify({'output': f'Error: {str(e)}'}), 500

@app.route('/terminal')
def terminal():
    return render_template('terminal.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
