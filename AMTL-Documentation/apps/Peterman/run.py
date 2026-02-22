"""
Peterman application entry point.

Usage:
    python run.py              # Development server
    python run.py --production # Production with gunicorn
"""

import os
import sys
import time
from app import create_app

# Set start time for uptime calculation
os.environ['APP_START_TIME'] = str(int(time.time()))

app = create_app()

if __name__ == '__main__':
    from app.config import config
    port = config['PORT']
    debug = config['DEBUG']
    
    print(f"Starting Peterman on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
