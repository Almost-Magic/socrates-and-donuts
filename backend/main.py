"""Socrates & Donuts Backend Entry Point"""
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Flask runs on port 5010 for Socrates & Donuts (per AMTL-SND-SPC-1.0 spec)
    app.run(host='127.0.0.1', port=5010, debug=True)
