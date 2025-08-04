#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple startup script for Render deployment
Fixes module import issues
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Now import the Flask app
from src.web_app import app

if __name__ == '__main__':
    # Get port from environment variable (Render sets this)
    port = int(os.environ.get('PORT', 5000))
    
    # Run the Flask app
    print(f"Starting Cafe24 Automation System on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=False)