"""
The Workshop â€” Almost Magic Tech Lab Mission Control
Port: 5003
"""

import os
import json
import time
import logging
from datetime import datetime
from flask import Flask, render_template, jsonify, send_from_directory
import httpx

# ============================================================
# Configuration
# ============================================================

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'workshop-amtl-2026')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

PORT = int(os.getenv('PORT', 5003))
VERSION = '1.0.0'

# ============================================================
# Paths
# ============================================================

CK_BASE = os.getenv('CK_BASE', r'C:\Users\ManiPadisetti\Dropbox\Desktop DB\Books and Articles Mani\Books\Almost Magic Tech Lab AMTL\Source and Brand\CK')
SOURCE_BASE = os.getenv('SOURCE_BASE', r'C:\Users\ManiPadisetti\Dropbox\Desktop DB\Books and Articles Mani\Books\Almost Magic Tech Lab AMTL\Source and Brand')

# ============================================================
# Service Registry â€” Single source of truth
# ============================================================

SERVICES = {
    # CK Apps â€” launchable
    'Elaine':             {'name': 'Elaine',              'port': 5000,  'url': 'http://localhost:5000',  'type': 'ck',    'path': os.path.join(CK_BASE, 'Elaine'),           'cmd': 'launch-elaine.bat'},
    'costanza':           {'name': 'Costanza',            'port': 5001,  'url': 'http://localhost:5001',  'type': 'ck',    'path': os.path.join(CK_BASE, 'costanza'),          'cmd': 'launch-elaine.bat'},
    'learning-assistant': {'name': 'Learning Assistant',  'port': 5002,  'url': 'http://localhost:5002',  'type': 'ck',    'path': os.path.join(CK_BASE, 'learning-assistant'),'cmd': 'launch-elaine.bat'},
    'writer':             {'name': 'CK Writer',           'port': 5004,  'url': 'http://localhost:5004',  'type': 'ck',    'path': os.path.join(CK_BASE, 'ck-writer'),         'cmd': 'launch-elaine.bat'},
    'author-studio':      {'name': 'Author Studio',       'port': 5006,  'url': 'http://localhost:5006',  'type': 'ck',    'path': os.path.join(CK_BASE, 'author-studio'),     'cmd': 'launch-elaine.bat'},
    'peterman':           {'name': 'Peterman',            'port': 5008,  'url': 'http://localhost:5008',  'type': 'ck',    'path': os.path.join(SOURCE_BASE, 'Peterman SEO'),  'cmd': 'launch-elaine.bat', 'env': {'FLASK_DEBUG': '0', 'OLLAMA_TIMEOUT': '600'}},
    'dhamma':             {'name': 'Dhamma Mirror',       'port': 5020,  'url': 'http://localhost:5020',  'type': 'ck',    'path': os.path.join(CK_BASE, 'dhamma-mirror'),     'cmd': 'launch-elaine.bat'},
    'signal':             {'name': 'Signal',              'port': 8420,  'url': 'http://localhost:8420',  'type': 'ck',    'path': os.path.join(CK_BASE, 'signal'),            'cmd': 'launch-elaine.bat'},
    'junk-drawer':        {'name': 'The Junk Drawer',     'port': 3005,  'url': 'http://localhost:3005',  'type': 'ck',    'path': os.path.join(CK_BASE, 'Junk Drawer file management system', 'junk-drawer-app'), 'cmd': 'npm start'},
    'junk-drawer-api':    {'name': 'Junk Drawer API',     'port': 5006,  'url': 'http://localhost:5006',  'type': 'infra', 'path': os.path.join(CK_BASE, 'Junk Drawer file management system', 'junk-drawer-backend'), 'cmd': 'launch-elaine.bat'},
    'comfyui':            {'name': 'ComfyUI Studio',      'port': 8188,  'url': 'http://localhost:8188',  'type': 'ck',    'path': None, 'cmd': None},

    # Infrastructure â€” Docker services (start via docker start)
    'ollama':             {'name': 'Ollama',              'port': 11434, 'url': 'http://localhost:11434', 'type': 'infra', 'health': '/api/tags', 'docker': None, 'cmd': 'ollama serve'},
    'postgres':           {'name': 'PostgreSQL',          'port': 5433,  'url': None,                     'type': 'infra', 'docker': 'pgvector'},
    'redis':              {'name': 'Redis',               'port': 6379,  'url': None,                     'type': 'infra', 'docker': 'redis'},
    'searxng':            {'name': 'SearXNG',             'port': 8888,  'url': 'http://localhost:8888',  'type': 'infra', 'docker': 'searxng'},
    'n8n':                {'name': 'n8n',                 'port': 5678,  'url': 'http://localhost:5678',  'type': 'infra', 'docker': 'n8n'},
    'listmonk':           {'name': 'Listmonk',            'port': 9001,  'url': 'http://localhost:9001',  'type': 'infra', 'docker': 'listmonk'},
    'proof':              {'name': 'Proof',               'port': 8000,  'url': 'http://localhost:8000',  'type': 'infra', 'path': os.path.join(CK_BASE, '..', '..', '..', '..', '..', 'projects', 'proof'), 'cmd': 'python -m uvicorn main:app --host 0.0.0.0 --port 8000'},
    'supervisor':         {'name': 'The Supervisor',      'port': 9000,  'url': 'http://localhost:9000',  'type': 'infra', 'health': '/api/health', 'path': os.path.join(SOURCE_BASE, 'Supervisor'), 'cmd': 'python supervisor.py'},
}

# Track launched processes
launched_processes = {}


# ============================================================
# Health Check Logic
# ============================================================

def check_service(service_id, service):
    """Ping a service and return status."""
    if service.get('url') is None:
        # TCP-only services (PostgreSQL, Redis) â€” check port
        import socket
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('localhost', service['port']))
            sock.close()
            return result == 0
        except Exception:
            return False
    else:
        # HTTP services â€” check endpoint
        try:
            health_path = service.get('health', '/')
            url = f"{service['url']}{health_path}"
            resp = httpx.get(url, timeout=3.0)
            return resp.status_code < 500
        except Exception:
            return False


# ============================================================
# Routes
# ============================================================

@app.route('/')
def index():
    """Serve the Workshop dashboard."""
    return render_template('index.html')


@app.route('/api/health')
def health():
    """Workshop health check."""
    return jsonify({
        'status': 'healthy',
        'app': 'The Workshop',
        'version': VERSION,
        'timestamp': datetime.utcnow().isoformat()
    })


@app.route('/api/services')
def list_services():
    """List all registered services."""
    return jsonify(SERVICES)


@app.route('/api/services/health')
def services_health():
    """Check health of all registered services."""
    results = {}
    live_count = 0
    total = len(SERVICES)

    for sid, svc in SERVICES.items():
        is_up = check_service(sid, svc)
        results[sid] = {
            'name': svc['name'],
            'port': svc['port'],
            'type': svc['type'],
            'status': 'live' if is_up else 'stopped',
        }
        if is_up:
            live_count += 1

    return jsonify({
        'timestamp': datetime.utcnow().isoformat(),
        'summary': f'{live_count}/{total} services live',
        'live': live_count,
        'total': total,
        'services': results
    })


@app.route('/api/services/health/<service_id>')
def service_health(service_id):
    """Check health of a specific service."""
    if service_id not in SERVICES:
        return jsonify({'error': f'Unknown service: {service_id}'}), 404

    svc = SERVICES[service_id]
    is_up = check_service(service_id, svc)

    return jsonify({
        'id': service_id,
        'name': svc['name'],
        'port': svc['port'],
        'status': 'live' if is_up else 'stopped',
    })


@app.route('/api/services/launch/<service_id>', methods=['POST'])
def launch_service(service_id):
    """Launch a service if it's not already running."""
    import subprocess

    if service_id not in SERVICES:
        return jsonify({'error': f'Unknown service: {service_id}'}), 404

    svc = SERVICES[service_id]

    # Already running?
    if check_service(service_id, svc):
        return jsonify({
            'id': service_id,
            'name': svc['name'],
            'status': 'already_running',
            'url': svc.get('url'),
            'message': f"{svc['name']} is already running on port {svc['port']}"
        })

    # Docker service?
    docker_name = svc.get('docker')
    if docker_name:
        try:
            subprocess.run(
                ['docker', 'start', docker_name],
                capture_output=True, text=True, timeout=15
            )
            # Wait a moment for startup
            time.sleep(3)
            is_up = check_service(service_id, svc)
            return jsonify({
                'id': service_id,
                'name': svc['name'],
                'status': 'launched' if is_up else 'starting',
                'url': svc.get('url'),
                'message': f"Docker container '{docker_name}' started"
            })
        except Exception as e:
            return jsonify({
                'id': service_id,
                'name': svc['name'],
                'status': 'error',
                'message': f"Failed to start Docker container: {str(e)}"
            }), 500

    # Python/app service?
    app_path = svc.get('path')
    app_cmd = svc.get('cmd')

    if not app_path or not app_cmd:
        return jsonify({
            'id': service_id,
            'name': svc['name'],
            'status': 'not_available',
            'message': f"{svc['name']} is not yet built or has no launch path configured"
        }), 404

    if not os.path.isdir(app_path):
        return jsonify({
            'id': service_id,
            'name': svc['name'],
            'status': 'not_found',
            'message': f"App directory not found: {app_path}"
        }), 404

    try:
        # Build environment
        env = os.environ.copy()
        extra_env = svc.get('env', {})
        env.update(extra_env)

        # Launch as detached subprocess
        process = subprocess.Popen(
            app_cmd,
            cwd=app_path,
            shell=True,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
        )

        launched_processes[service_id] = process.pid
        logger.info(f"Launched {svc['name']} (PID: {process.pid}) from {app_path}")

        # Wait for it to come up
        for i in range(10):
            time.sleep(1.5)
            if check_service(service_id, svc):
                return jsonify({
                    'id': service_id,
                    'name': svc['name'],
                    'status': 'launched',
                    'pid': process.pid,
                    'url': svc.get('url'),
                    'message': f"{svc['name']} started on port {svc['port']}"
                })

        return jsonify({
            'id': service_id,
            'name': svc['name'],
            'status': 'starting',
            'pid': process.pid,
            'url': svc.get('url'),
            'message': f"{svc['name']} is starting (PID: {process.pid}), may take a moment..."
        })

    except Exception as e:
        logger.error(f"Failed to launch {svc['name']}: {e}")
        return jsonify({
            'id': service_id,
            'name': svc['name'],
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/services/launch-all', methods=['POST'])
def launch_all():
    """Launch all services that have launch paths configured."""
    results = {}
    for sid, svc in SERVICES.items():
        if not check_service(sid, svc):
            has_launcher = svc.get('docker') or (svc.get('path') and svc.get('cmd'))
            if has_launcher:
                # Call our own launch endpoint logic
                try:
                    resp = launch_service_internal(sid)
                    results[sid] = resp
                except Exception as e:
                    results[sid] = {'status': 'error', 'message': str(e)}
            else:
                results[sid] = {'status': 'no_launcher'}
        else:
            results[sid] = {'status': 'already_running'}

    return jsonify({
        'message': 'Launch all complete',
        'results': results
    })


def launch_service_internal(service_id):
    """Internal launch logic (shared by launch and launch-all)."""
    import subprocess
    svc = SERVICES[service_id]

    docker_name = svc.get('docker')
    if docker_name:
        subprocess.run(['docker', 'start', docker_name], capture_output=True, timeout=15)
        time.sleep(2)
        return {'status': 'launched' if check_service(service_id, svc) else 'starting'}

    app_path = svc.get('path')
    app_cmd = svc.get('cmd')
    if app_path and app_cmd and os.path.isdir(app_path):
        env = os.environ.copy()
        env.update(svc.get('env', {}))
        process = subprocess.Popen(
            app_cmd, cwd=app_path, shell=True, env=env,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
        )
        launched_processes[service_id] = process.pid
        time.sleep(3)
        return {'status': 'launched', 'pid': process.pid}

    return {'status': 'no_launcher'}


@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static/favicons', 'favicon-workshop.svg', mimetype='image/svg+xml')


@app.route('/static/favicons/<path:filename>')
def serve_favicon(filename):
    return send_from_directory('static/favicons', filename)


# ============================================================
# Startup
# ============================================================

if __name__ == '__main__':
    logger.info(f'The Workshop v{VERSION} starting on port {PORT}')
    logger.info(f"  http://localhost:{PORT}  |  Services registered: {len(SERVICES)}")
    app.run(host='0.0.0.0', port=PORT, debug=False)
