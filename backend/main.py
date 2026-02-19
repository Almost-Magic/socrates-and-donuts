"""Socrates & Donuts Backend Entry Point"""
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Flask runs on port 5015 for Socrates & Donuts
    app.run(host='127.0.0.1', port=5015, debug=True)
