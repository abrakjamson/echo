#!/usr/bin/env python3
"""Test the deployed A2A endpoint."""

import requests
import json
import uuid

base_url = 'https://echo.azurewebsites.net/api/a2a'

print('=== Testing Deployed A2A Endpoint ===\n')

# Test 1: Simple message echo
print('Test 1: A2A Message with text')
payload = {
    'messageId': str(uuid.uuid4()),
    'role': 'user',
    'parts': [{'text': 'Hello from deployed A2A endpoint!'}],
    'metadata': {'source': 'test-client', 'timestamp': '2026-03-15T00:42:14Z'}
}
print(f'Request: {json.dumps(payload, indent=2)}')

try:
    resp = requests.post(base_url, json=payload, timeout=10)
    print(f'\nStatus: {resp.status_code}')
    print(f'Response:\n{json.dumps(resp.json(), indent=2)}')
    
    data = resp.json()
    assert resp.status_code == 200, f'Expected 200, got {resp.status_code}'
    assert 'messageId' in data, 'Missing messageId'
    assert data['role'] == 'agent', f"Expected role=agent, got {data.get('role')}"
    assert 'parts' in data, 'Missing parts'
    assert data['parts'][0]['text'] == 'Hello from deployed A2A endpoint!', 'Text not echoed correctly'
    print('\n✓ A2A endpoint test PASSED!')
except Exception as e:
    print(f'\n✗ Test failed: {e}')
