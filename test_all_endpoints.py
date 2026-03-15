#!/usr/bin/env python3
"""Test all deployed endpoints."""

import requests
import json

base_url = 'https://echo.azurewebsites.net/api'

tests = [
    ('Echo', 'GET', f'{base_url}/echo?value=test'),
    ('JSON-RPC 2.0', 'POST', f'{base_url}/jsonrpc', {'jsonrpc': '2.0', 'method': 'test', 'id': 1}),
    ('MCP', 'POST', f'{base_url}/mcp', {'action': 'echo', 'id': 1}),
    ('A2A', 'POST', f'{base_url}/a2a', {'messageId': 'test', 'role': 'user', 'parts': [{'text': 'msg'}]}),
]

print('=== Testing All Deployed Endpoints ===\n')
all_passed = True

for test in tests:
    name = test[0]
    method = test[1]
    url = test[2]
    payload = test[3] if len(test) > 3 else None
    
    try:
        if method == 'GET':
            resp = requests.get(url, timeout=10)
        else:
            resp = requests.post(url, json=payload, timeout=10)
        
        status_ok = resp.status_code == 200
        if status_ok:
            print(f'✓ {name:12} ({resp.status_code})')
        else:
            print(f'✗ {name:12} ({resp.status_code})')
            all_passed = False
    except Exception as e:
        print(f'✗ {name:12} - {e}')
        all_passed = False

print('\n' + ('='*40))
if all_passed:
    print('All endpoints operational! ✓')
else:
    print('Some endpoints may have failed.')
