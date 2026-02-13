"""
The Workshop â€” Almost Magic Tech Lab Mission Control
Port: 5003
"""

import os
import glob
import json
import time
import logging
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from flask import Flask, render_template, jsonify, request, send_from_directory
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
VERSION = '2.0.0'

# ============================================================
# Paths
# ============================================================

CK_BASE = os.getenv('CK_BASE', r'C:\Users\ManiPadisetti\Dropbox\Desktop DB\Books and Articles Mani\Books\Almost Magic Tech Lab AMTL\Source and Brand\CK')
SOURCE_BASE = os.getenv('SOURCE_BASE', r'C:\Users\ManiPadisetti\Dropbox\Desktop DB\Books and Articles Mani\Books\Almost Magic Tech Lab AMTL\Source and Brand')
DESKTOP_APPS_DIR = os.path.join(CK_BASE, 'desktop-apps')
DESKTOP_DIST_DIR = os.path.join(DESKTOP_APPS_DIR, 'dist')
SERVICES_PS1 = os.path.join(SOURCE_BASE, 'services.ps1')
ELECTRON_CMD = os.path.join(DESKTOP_APPS_DIR, 'node_modules', '.bin', 'electron.cmd')
ELECTRON_MAIN = os.path.join(DESKTOP_APPS_DIR, 'shared', 'main.js')

# ============================================================
# Desktop App Registry — maps service IDs to Electron app IDs
# and their corresponding backend service(s)
# ============================================================

DESKTOP_APPS = {
    'elaine':           {'electron_id': 'elaine',        'backend_service': 'elaine',        'name': 'Elaine'},
    'workshop':         {'electron_id': 'workshop',      'backend_service': 'workshop',      'name': 'The Workshop'},
    'ripple':           {'electron_id': 'ripple',        'backend_service': 'ripple',        'name': 'Ripple CRM'},
    'touchstone':       {'electron_id': 'touchstone',    'backend_service': 'touchstone',    'name': 'Touchstone'},
    'writer':           {'electron_id': 'writer',        'backend_service': 'writer',        'name': 'CK Writer'},
    'learning':         {'electron_id': 'learning',      'backend_service': 'learning',      'name': 'Learning Assistant'},
    'peterman':         {'electron_id': 'peterman',      'backend_service': 'peterman',      'name': 'Peterman'},
    'genie':            {'electron_id': 'genie',         'backend_service': 'genie',         'name': 'Genie'},
    'costanza':         {'electron_id': 'costanza',      'backend_service': 'costanza',      'name': 'Costanza'},
    'author-studio':    {'electron_id': 'author-studio', 'backend_service': 'authorstudio',  'name': 'Author Studio'},
    'junk-drawer':      {'electron_id': 'junk-drawer',   'backend_service': 'junkdrawer',    'name': 'Junk Drawer'},
    'supervisor':       {'electron_id': 'supervisor',    'backend_service': 'supervisor',    'name': 'Supervisor'},
}

# Backend-only services (used by "Start Backends Only")
BACKEND_SERVICES = [
    'supervisor', 'elaine', 'costanza', 'learning', 'writer',
    'authorstudio', 'peterman', 'junkdrawer', 'genie', 'ripple', 'touchstone',
]

# ============================================================
# Service Registry â€” Single source of truth
# ============================================================

LAN = '192.168.4.55'

SERVICES = {
    # CK Apps -- launchable
    'elaine':             {'name': 'Elaine',              'port': 5000,  'url': f'http://{LAN}:5000',  'type': 'ck',    'path': os.path.join(CK_BASE, 'Elaine'),           'cmd': 'launch-elaine.bat', 'health': '/api/health'},
    'costanza':           {'name': 'Costanza',            'port': 5001,  'url': f'http://{LAN}:5001',  'type': 'ck',    'path': os.path.join(SOURCE_BASE, 'Costanza'),      'cmd': 'python app.py', 'health': '/api/health'},
    'learning-assistant': {'name': 'Learning Assistant',  'port': 5002,  'url': f'http://{LAN}:5002',  'type': 'ck',    'path': os.path.join(CK_BASE, 'learning-assistant'),'cmd': 'launch-elaine.bat'},
    'writer':             {'name': 'CK Writer',           'port': 5004,  'url': f'http://{LAN}:5004',  'type': 'ck',    'path': os.path.join(CK_BASE, 'ck-writer'),         'cmd': 'launch-elaine.bat'},
    'author-studio':      {'name': 'Author Studio',       'port': 5007,  'url': f'http://{LAN}:5007',  'type': 'ck',    'path': os.path.join(CK_BASE, 'Author Studio'),     'cmd': 'python main_flask.py'},
    'peterman':           {'name': 'Peterman',            'port': 5008,  'url': f'http://{LAN}:5008',  'type': 'ck',    'path': os.path.join(SOURCE_BASE, 'Peterman SEO'),  'cmd': 'python app.py', 'health': '/api/health', 'env': {'FLASK_DEBUG': '0', 'OLLAMA_TIMEOUT': '600'}},
    'dhamma':             {'name': 'Dhamma Mirror',       'port': 5020,  'url': f'http://{LAN}:5020',  'type': 'ck',    'path': os.path.join(CK_BASE, 'dhamma-mirror'),     'cmd': 'launch-elaine.bat'},
    'signal':             {'name': 'Signal Hunter',        'port': 8420,  'url': f'http://{LAN}:8420',  'type': 'ck',    'path': os.path.join(CK_BASE, 'signal'),            'cmd': 'python -B app.py', 'health': '/api/health'},
    'junk-drawer':        {'name': 'The Junk Drawer',     'port': 3005,  'url': f'http://{LAN}:3005',  'type': 'ck',    'path': os.path.join(CK_BASE, 'Junk Drawer file management system', 'junk-drawer-app'), 'cmd': 'npm start'},
    'junk-drawer-api':    {'name': 'Junk Drawer API',     'port': 5005,  'url': f'http://{LAN}:5005',  'type': 'infra', 'path': os.path.join(CK_BASE, 'Junk Drawer file management system', 'junk-drawer-backend'), 'cmd': 'launch-elaine.bat', 'health': '/api/health'},
    'comfyui':            {'name': 'ComfyUI Studio',      'port': 8188,  'url': f'http://{LAN}:8188',  'type': 'ck',    'path': None, 'cmd': None},
    'genie':              {'name': 'Genie',               'port': 8000,  'url': f'http://{LAN}:8000',  'type': 'ck',    'path': os.path.join(SOURCE_BASE, 'Finance App', 'Genie', 'backend'), 'cmd': 'python -m uvicorn app:app --host 0.0.0.0 --port 8000', 'health': '/api/health'},
    'genie-fe':           {'name': 'Genie Frontend',      'port': 3000,  'url': f'http://{LAN}:3000',  'type': 'ck',    'path': os.path.join(SOURCE_BASE, 'Finance App', 'Genie', 'frontend'), 'cmd': 'npm run dev'},
    'ripple':             {'name': 'Ripple CRM',          'port': 3100,  'url': f'http://{LAN}:3100',  'type': 'ck',    'path': os.path.join(SOURCE_BASE, 'Ripple CRM and Spark Marketing', 'frontend'), 'cmd': 'npx vite --host 0.0.0.0 --port 3100', 'health': '/'},
    'ripple-api':         {'name': 'Ripple CRM API',      'port': 8100,  'url': f'http://{LAN}:8100',  'type': 'ck',    'path': os.path.join(SOURCE_BASE, 'Ripple CRM and Spark Marketing', 'backend'), 'cmd': 'python -m uvicorn app.main:app --host 0.0.0.0 --port 8100', 'health': '/api/health'},
    'touchstone':         {'name': 'Touchstone',          'port': 8200,  'url': f'http://{LAN}:8200',  'type': 'ck',    'path': os.path.join(SOURCE_BASE, 'Touchstone', 'backend'), 'cmd': 'python -m uvicorn app.main:app --host 0.0.0.0 --port 8200', 'health': '/api/v1/health'},
    'touchstone-dash':    {'name': 'Touchstone Dashboard','port': 3200,  'url': f'http://{LAN}:3200',  'type': 'ck',    'path': os.path.join(SOURCE_BASE, 'Touchstone', 'dashboard'), 'cmd': 'npx vite --host 0.0.0.0 --port 3200', 'health': '/'},
    'knowyourself':       {'name': 'KnowYourself',        'port': 8300,  'url': f'http://{LAN}:8300',  'type': 'ck',    'path': os.path.join(SOURCE_BASE, 'KnowYourself', 'backend'), 'cmd': 'python -m uvicorn app.main:app --host 0.0.0.0 --port 8300', 'health': '/api/health'},
    'knowyourself-dash':  {'name': 'KnowYourself UI',     'port': 3300,  'url': f'http://{LAN}:3300',  'type': 'ck',    'path': os.path.join(SOURCE_BASE, 'KnowYourself', 'frontend'), 'cmd': 'npx vite --host 0.0.0.0 --port 3300', 'health': '/'},

    # Infrastructure -- core services
    'supervisor':         {'name': 'The Supervisor',      'port': 9000,  'url': f'http://{LAN}:9000',  'type': 'infra', 'health': '/api/health', 'path': os.path.join(SOURCE_BASE, 'Supervisor'), 'cmd': 'python supervisor.py'},
    'ollama':             {'name': 'Ollama',              'port': 11434, 'url': f'http://{LAN}:11434', 'type': 'infra', 'health': '/api/tags', 'docker': None, 'cmd': 'ollama serve'},
    'postgres':           {'name': 'PostgreSQL',          'port': 5433,  'url': None,                   'type': 'infra', 'docker': 'pgvector'},
    'redis':              {'name': 'Redis',               'port': 6379,  'url': None,                   'type': 'infra', 'docker': 'redis'},
    'n8n':                {'name': 'n8n',                 'port': 5678,  'url': f'http://{LAN}:5678',  'type': 'infra', 'docker': 'n8n'},
    'searxng':            {'name': 'SearXNG',             'port': 8888,  'url': f'http://{LAN}:8888',  'type': 'infra', 'docker': 'searxng'},
    'listmonk':           {'name': 'Listmonk',            'port': 9001,  'url': f'http://{LAN}:9001',  'type': 'infra', 'docker': 'listmonk'},
    'mailpit':            {'name': 'MailPit',             'port': 8025,  'url': f'http://{LAN}:8025',  'type': 'infra', 'docker': 'mailpit'},

    # Open Source Tools -- Tier 1 (Docker)
    'open-webui':         {'name': 'Open WebUI',          'port': 3080,  'url': f'http://{LAN}:3080',  'type': 'infra', 'docker': 'open-webui'},
    'vaultwarden':        {'name': 'Vaultwarden',         'port': 8222,  'url': f'http://{LAN}:8222',  'type': 'infra', 'docker': 'vaultwarden'},
    'formbricks':         {'name': 'Formbricks',          'port': 3015,  'url': f'http://{LAN}:3015',  'type': 'infra', 'docker': 'formbricks'},
    'matomo':             {'name': 'Matomo',              'port': 8084,  'url': f'http://{LAN}:8084',  'type': 'infra', 'docker': 'matomo'},
    'penpot':             {'name': 'Penpot',              'port': 9002,  'url': f'http://{LAN}:9002',  'type': 'infra', 'docker': 'penpot-frontend'},
    'superset':           {'name': 'Apache Superset',     'port': 8088,  'url': f'http://{LAN}:8088',  'type': 'infra', 'docker': 'superset_app'},
    'postiz':             {'name': 'Postiz',              'port': 4200,  'url': f'http://{LAN}:4200',  'type': 'infra', 'docker': 'postiz'},
    'wisdom-quotes':      {'name': 'Wisdom Quotes',       'port': 3350,  'url': f'http://{LAN}:3350',  'type': 'infra', 'health': '/api/quote/random', 'docker': 'wisdom-quotes'},

    # Linux tools (WSL2 / Docker)
    'uptime-kuma':        {'name': 'Uptime Kuma',         'port': 3001,  'url': f'http://{LAN}:3001',  'type': 'infra', 'docker': 'uptime-kuma'},
    'outline':            {'name': 'Outline',             'port': 3006,  'url': f'http://{LAN}:3006',  'type': 'infra', 'docker': 'outline'},
    'langfuse':           {'name': 'LangFuse',            'port': 3007,  'url': f'http://{LAN}:3007',  'type': 'infra', 'docker': 'langfuse-web'},
    'spiderfoot':         {'name': 'SpiderFoot',          'port': 5009,  'url': f'http://{LAN}:5009',  'type': 'infra', 'docker': 'spiderfoot'},
    'openvas':            {'name': 'OpenVAS',             'port': 9392,  'url': 'https://localhost:9392','type': 'infra', 'docker': 'greenbone-community-edition'},
    'wazuh':              {'name': 'Wazuh',               'port': 4443,  'url': 'https://localhost:4443','type': 'infra', 'docker': 'single-node-wazuh.dashboard-1'},
    'netdata':            {'name': 'Netdata',             'port': 19999, 'url': f'http://{LAN}:19999', 'type': 'infra'},

    # New tools (Docker)
    'paperless':          {'name': 'Paperless-ngx',       'port': 8010,  'url': f'http://{LAN}:8010',  'type': 'infra', 'docker': 'paperless-webserver'},
    'perplexica':         {'name': 'Perplexica',          'port': 3008,  'url': f'http://{LAN}:3008',  'type': 'infra', 'docker': 'perplexica-app'},
    'karakeep':           {'name': 'Karakeep',            'port': 3009,  'url': f'http://{LAN}:3009',  'type': 'infra', 'docker': 'karakeep'},
    'docuseal':           {'name': 'DocuSeal',            'port': 3010,  'url': f'http://{LAN}:3010',  'type': 'infra', 'docker': 'docuseal'},
    'homepage':           {'name': 'Homepage',            'port': 3011,  'url': f'http://{LAN}:3011',  'type': 'infra', 'docker': 'homepage'},
    'memos':              {'name': 'Memos',               'port': 5230,  'url': f'http://{LAN}:5230',  'type': 'infra', 'docker': 'memos'},

    # Finance & Market Data
    'fincept':            {'name': 'FinceptTerminal',     'port': None,  'url': None,                   'type': 'ck',    'path': None, 'cmd': None},
    'ghostfolio':         {'name': 'Ghostfolio',          'port': 3333,  'url': f'http://{LAN}:3333',  'type': 'infra', 'health': '/api/v1/health', 'docker': 'ghostfolio'},

    # AI Advisors — Isolated Claude AI windows
    'talaiva':            {'name': 'Talaiva',             'port': None,  'url': None,                   'type': 'advisor', 'launch': 'bat', 'bat_path': os.path.join(CK_BASE, 'ai-advisors', 'launch-talaiva.bat')},
    'guruve':             {'name': 'Guruve',              'port': None,  'url': None,                   'type': 'advisor', 'launch': 'bat', 'bat_path': os.path.join(CK_BASE, 'ai-advisors', 'launch-guruve.bat')},

    # Security & OSINT
    'tor-proxy':          {'name': 'Tor Proxy',           'port': 9050,  'url': None,                   'type': 'infra', 'docker': 'tor-socks-proxy'},
    'privoxy':            {'name': 'Privoxy',             'port': 8118,  'url': None,                   'type': 'infra', 'docker': 'privoxy'},
    'ivre':               {'name': 'IVRE',                'port': 8282,  'url': f'http://{LAN}:8282',  'type': 'infra', 'docker': 'ivreweb'},
    'hibp-checker':       {'name': 'HIBP Checker',        'port': 8284,  'url': f'http://{LAN}:8284',  'type': 'infra', 'health': '/api/health', 'docker': 'hibp-checker'},

    # OSINT CLI Tools (WSL2 — no ports, invoked via CLI)
    'amass':              {'name': 'Amass',               'port': None,  'url': None,                   'type': 'infra', 'path': None, 'cmd': None},
    'subfinder':          {'name': 'Subfinder',           'port': None,  'url': None,                   'type': 'infra', 'path': None, 'cmd': None},
    'httpx-pd':           {'name': 'httpx (ProjectDiscovery)', 'port': None, 'url': None,               'type': 'infra', 'path': None, 'cmd': None},
    'nuclei':             {'name': 'Nuclei',              'port': None,  'url': None,                   'type': 'infra', 'path': None, 'cmd': None},
    'theharvester':       {'name': 'theHarvester',        'port': None,  'url': None,                   'type': 'infra', 'path': None, 'cmd': None},
    'nmap':               {'name': 'Nmap',                'port': None,  'url': None,                   'type': 'infra', 'path': None, 'cmd': None},
    'shodan':             {'name': 'Shodan CLI',          'port': None,  'url': None,                   'type': 'infra', 'path': None, 'cmd': None},
}

# Track launched processes
launched_processes = {}


# ============================================================
# Health Check Logic
# ============================================================

def check_service(service_id, service):
    """Ping a service and return status.
    Always probes localhost for health (apps may bind to 127.0.0.1 only).
    The service 'url' field is the LAN-accessible URL for users to click.
    """
    port = service.get('port')
    if port is None:
        return False  # CLI-only tools (no port)
    if service.get('url') is None:
        # TCP-only services (PostgreSQL, Redis)
        import socket
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            return result == 0
        except Exception:
            return False
    else:
        # HTTP services -- always check via localhost
        try:
            health_path = service.get('health', '/')
            if service['url'].startswith('https://'):
                probe_url = f"https://localhost:{port}{health_path}"
            else:
                probe_url = f"http://localhost:{port}{health_path}"
            resp = httpx.get(probe_url, timeout=3.0, verify=False)
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
    """Check health of all registered services (parallel)."""
    results = {}
    live_count = 0
    total = len(SERVICES)

    def _check(sid_svc):
        sid, svc = sid_svc
        return sid, svc, check_service(sid, svc)

    with ThreadPoolExecutor(max_workers=12) as pool:
        futures = pool.map(_check, SERVICES.items())
        for sid, svc, is_up in futures:
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


@app.route('/api/launch/<name>', methods=['POST'])
def launch_bat(name):
    """Launch a bat-based advisor window by name."""
    for sid, svc in SERVICES.items():
        if svc['name'].lower() == name.lower() and svc.get('launch') == 'bat':
            bat_path = svc.get('bat_path')
            if not bat_path or not os.path.isfile(bat_path):
                return jsonify({
                    'status': 'error',
                    'name': svc['name'],
                    'message': f"Bat file not found: {bat_path}"
                }), 404

            try:
                subprocess.Popen(
                    [bat_path],
                    cwd=os.path.dirname(bat_path),
                    shell=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
                )
                logger.info(f"Launched advisor: {svc['name']} via {bat_path}")
                return jsonify({
                    'status': 'launched',
                    'name': svc['name'],
                    'message': f"{svc['name']} window opening..."
                })
            except Exception as e:
                logger.error(f"Failed to launch {svc['name']}: {e}")
                return jsonify({
                    'status': 'error',
                    'name': svc['name'],
                    'message': str(e)
                }), 500

    return jsonify({'status': 'error', 'message': f'Unknown advisor: {name}'}), 404


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


# ============================================================
# Desktop App Launch — One-Click Launch
# ============================================================

def find_desktop_exe(electron_id):
    """Find the .exe file for a desktop app in dist/."""
    dist_dir = os.path.join(DESKTOP_DIST_DIR, electron_id)
    if not os.path.isdir(dist_dir):
        return None
    # Check win-unpacked/ first (dir target output)
    unpacked_dir = os.path.join(dist_dir, 'win-unpacked')
    if os.path.isdir(unpacked_dir):
        for f in os.listdir(unpacked_dir):
            if f.endswith('.exe') and not f.startswith('Uninstall'):
                return os.path.join(unpacked_dir, f)
    # Fall back to root dist dir (portable target output)
    for f in os.listdir(dist_dir):
        if f.endswith('.exe') and not f.startswith('Uninstall'):
            return os.path.join(dist_dir, f)
    return None


def start_backend_via_services(service_key):
    """Start a backend service using services.ps1."""
    if not os.path.isfile(SERVICES_PS1):
        logger.warning(f"services.ps1 not found at {SERVICES_PS1}")
        return False
    try:
        result = subprocess.run(
            ['powershell', '-ExecutionPolicy', 'Bypass', '-File',
             SERVICES_PS1, 'start', service_key],
            capture_output=True, text=True, timeout=30,
            cwd=SOURCE_BASE
        )
        logger.info(f"services.ps1 start {service_key}: {result.stdout.strip()[:200]}")
        return True
    except Exception as e:
        logger.error(f"Failed to start {service_key} via services.ps1: {e}")
        return False


def launch_electron_app(electron_id):
    """Launch an Electron desktop app (.exe or dev mode)."""
    # Try built .exe first
    exe_path = find_desktop_exe(electron_id)
    if exe_path:
        logger.info(f"Launching desktop .exe: {exe_path}")
        subprocess.Popen(
            [exe_path],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
        )
        return {'method': 'exe', 'path': exe_path}

    # Fallback: launch via Electron dev mode
    config_path = os.path.join(DESKTOP_APPS_DIR, 'apps', electron_id, 'config.json')
    if os.path.isfile(ELECTRON_CMD) and os.path.isfile(config_path):
        logger.info(f"Launching via electron dev: {electron_id}")
        subprocess.Popen(
            [ELECTRON_CMD, ELECTRON_MAIN, f'--config={config_path}'],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            cwd=DESKTOP_APPS_DIR,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
        )
        return {'method': 'electron-dev', 'config': config_path}

    return None


@app.route('/api/desktop/launch/<app_id>', methods=['POST'])
def launch_desktop(app_id):
    """Launch a desktop app: start backend if needed, then open Electron .exe."""
    if app_id not in DESKTOP_APPS:
        return jsonify({'error': f'Unknown desktop app: {app_id}'}), 404

    desktop = DESKTOP_APPS[app_id]
    backend_key = desktop['backend_service']
    electron_id = desktop['electron_id']
    app_name = desktop['name']

    # Step 1: Check if backend is running, start if not
    backend_svc = None
    for sid, svc in SERVICES.items():
        if sid.lower().replace('-', '') == backend_key.lower().replace('-', ''):
            backend_svc = (sid, svc)
            break
    # Also try matching by name
    if not backend_svc:
        for sid, svc in SERVICES.items():
            if backend_key.lower() in sid.lower():
                backend_svc = (sid, svc)
                break

    backend_status = 'unknown'
    if backend_svc:
        sid, svc = backend_svc
        if check_service(sid, svc):
            backend_status = 'already_running'
        else:
            start_backend_via_services(backend_key)
            # Wait for backend to come up
            for _ in range(10):
                time.sleep(1.5)
                if check_service(sid, svc):
                    break
            backend_status = 'launched' if check_service(sid, svc) else 'starting'
    else:
        # No matching backend in registry — try services.ps1 anyway
        start_backend_via_services(backend_key)
        backend_status = 'started_via_script'

    # Step 2: Launch the Electron desktop app
    launch_result = launch_electron_app(electron_id)

    if launch_result:
        return jsonify({
            'id': app_id,
            'name': app_name,
            'status': 'launched',
            'backend': backend_status,
            'desktop': launch_result,
            'message': f"{app_name} desktop launched (backend: {backend_status})"
        })
    else:
        return jsonify({
            'id': app_id,
            'name': app_name,
            'status': 'no_desktop',
            'backend': backend_status,
            'message': f"Backend {backend_status} but no desktop .exe found for {app_name}. "
                       f"Run build-all.bat in CK/desktop-apps/ to create .exe files."
        }), 404


@app.route('/api/desktop/launch-all', methods=['POST'])
def launch_all_desktop():
    """Launch ALL desktop apps: start all backends, then open all Electron .exes."""
    results = {}

    # Step 1: Start all backends via services.ps1
    logger.info("Launch All: starting all backends via services.ps1...")
    start_backend_via_services('all')
    time.sleep(5)  # Give backends a head start

    # Step 2: Launch each desktop app
    for app_id, desktop in DESKTOP_APPS.items():
        electron_id = desktop['electron_id']
        launch_result = launch_electron_app(electron_id)
        if launch_result:
            results[app_id] = {'status': 'launched', 'method': launch_result.get('method')}
        else:
            results[app_id] = {'status': 'no_exe'}

    launched = sum(1 for r in results.values() if r['status'] == 'launched')
    return jsonify({
        'message': f'Launch All complete: {launched}/{len(DESKTOP_APPS)} desktop apps launched',
        'results': results
    })


@app.route('/api/services/start-backends', methods=['POST'])
def start_backends_only():
    """Start all backend services without opening any desktop windows."""
    logger.info("Starting all backends only (no desktop windows)...")
    success = start_backend_via_services('all')

    # Wait and check health
    time.sleep(5)
    running = 0
    total = len(BACKEND_SERVICES)
    statuses = {}

    for key in BACKEND_SERVICES:
        for sid, svc in SERVICES.items():
            if sid.lower().replace('-', '') == key.lower().replace('-', ''):
                is_up = check_service(sid, svc)
                statuses[key] = 'running' if is_up else 'starting'
                if is_up:
                    running += 1
                break

    return jsonify({
        'message': f'Backends started: {running}/{total} responding',
        'services': statuses
    })


@app.route('/api/desktop/apps')
def list_desktop_apps():
    """List available desktop apps and their .exe status."""
    result = {}
    for app_id, desktop in DESKTOP_APPS.items():
        exe_path = find_desktop_exe(desktop['electron_id'])
        result[app_id] = {
            'name': desktop['name'],
            'electron_id': desktop['electron_id'],
            'has_exe': exe_path is not None,
            'exe_path': exe_path,
        }
    return jsonify(result)


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
