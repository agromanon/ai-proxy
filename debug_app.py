#!/usr/bin/env python3
"""
Debug script to compare app initialization
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=== Debug App Initialization ===")

# Import the main app
try:
    from app import app
    print("✓ Main app imported successfully")
except Exception as e:
    print(f"✗ Error importing main app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n=== Registered Routes ===")
for rule in app.url_map.iter_rules():
    print(f"  {rule.rule} -> {rule.endpoint}")

print("\n=== Testing Routes ===")
with app.test_client() as client:
    # Test main route
    response = client.get('/')
    print(f"GET / -> Status: {response.status_code}")
    
    # Test login route
    response = client.get('/login')
    print(f"GET /login -> Status: {response.status_code}")
    
    # Test health route
    response = client.get('/health')
    print(f"GET /health -> Status: {response.status_code}")

print("\n=== Debug Complete ===")