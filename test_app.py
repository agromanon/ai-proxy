#!/usr/bin/env python3
"""
Test script to debug Flask app routing
"""

from flask import Flask
from web_admin.routes import web_admin

# Create a simple test app
app = Flask(__name__)
app.register_blueprint(web_admin)

print("Registered routes:")
for rule in app.url_map.iter_rules():
    print(f"  {rule.rule} -> {rule.endpoint}")

if __name__ == '__main__':
    app.run(debug=True, port=8001)