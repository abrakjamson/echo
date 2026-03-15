#!/usr/bin/env python3
"""Production endpoint testing for https://echo.azurewebsites.net/api/"""

import json
import sys
import requests
from datetime import datetime
from a2a.types import Message, Role, TextPart

# Fix Unicode encoding on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "https://echo.azurewebsites.net/api"

def test_echo_endpoint():
    """Test the echo endpoint."""
    print("\n=== Testing Echo Endpoint ===")
    url = f"{BASE_URL}/echo?value=production_test"
    
    try:
        resp = requests.get(url, timeout=10)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")
        
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        assert resp.text == "production_test", f"Expected 'production_test', got '{resp.text}'"
        print("✓ Echo endpoint test passed")
        return True
    except Exception as e:
        print(f"✗ Echo endpoint test failed: {e}")
        return False

def test_jsonrpc_endpoint():
    """Test the JSON-RPC endpoint."""
    print("\n=== Testing JSON-RPC Endpoint ===")
    url = f"{BASE_URL}/jsonrpc"
    
    try:
        payload = {
            "jsonrpc": "2.0",
            "method": "test_method",
            "params": {"key": "value"},
            "id": 1
        }
        resp = requests.post(url, json=payload, timeout=10)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text[:200]}")
        
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        data = resp.json()
        assert "result" in data, "Response should have result field"
        assert data["result"]["method"] == "test_method", "Result should echo the request"
        print("✓ JSON-RPC endpoint test passed")
        return True
    except Exception as e:
        print(f"✗ JSON-RPC endpoint test failed: {e}")
        return False

def test_mcp_endpoint():
    """Test the MCP endpoint."""
    print("\n=== Testing MCP Endpoint ===")
    url = f"{BASE_URL}/mcp"
    
    try:
        payload = {
            "action": "echo",
            "payload": {"test": "data"},
            "id": 42
        }
        resp = requests.post(url, json=payload, timeout=10)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text[:200]}")
        
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        data = resp.json()
        assert "result" in data, "Response should have result field"
        assert data["result"]["action"] == "echo", "Result should echo the request"
        print("✓ MCP endpoint test passed")
        return True
    except Exception as e:
        print(f"✗ MCP endpoint test failed: {e}")
        return False

def test_a2a_endpoint():
    """Test the A2A SendMessage endpoint (POST /message:send)."""
    print("\n=== Testing A2A SendMessage Endpoint ===")
    url = f"{BASE_URL}/message:send"

    try:
        # Use SDK to construct proper message
        message = Message(
            messageId="prod-test-a2a-001",
            role=Role.user,
            parts=[TextPart(text="production test message")],
            metadata={"source": "production-test"}
        )
        payload = message.model_dump(exclude_none=True, by_alias=True)
        
        resp = requests.post(url, json=payload, timeout=10)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text[:200]}")
        
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        data = resp.json()
        assert "messageId" in data, "Response should have messageId field"
        assert data.get("role") == "agent", "Response should have role: agent"
        assert "parts" in data, "Response should have parts field"
        assert data["parts"][0]["text"] == "production test message", "Text should be echoed back"
        print("✓ A2A SendMessage endpoint test passed")
        return True
    except Exception as e:
        print(f"✗ A2A SendMessage endpoint test failed: {e}")
        return False

def test_agent_card_endpoint():
    """Test the agent card endpoint."""
    print("\n=== Testing Agent Card Endpoint ===")
    url = f"{BASE_URL}/.well-known/agent-card.json"
    
    try:
        resp = requests.get(url, timeout=10)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text[:300]}...")
        
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        data = resp.json()
        
        # Verify required fields
        assert "name" in data, "Agent card should have name field"
        assert "description" in data, "Agent card should have description field"
        assert "version" in data, "Agent card should have version field"
        assert "agentId" in data, "Agent card should have agentId field"
        assert "endpoint" in data, "Agent card should have endpoint field"
        assert "capabilities" in data, "Agent card should have capabilities field"
        assert "skills" in data, "Agent card should have skills field"
        
        # Verify values
        assert data["name"] == "Echo Server", f"Name should be 'Echo Server', got '{data['name']}'"
        assert data["version"] == "1.0.0", f"Version should be '1.0.0', got '{data['version']}'"
        assert data["agentId"] == "echo-server", f"Agent ID should be 'echo-server', got '{data['agentId']}'"
        assert data["endpoint"] == "https://echo.azurewebsites.net/api/a2a", f"Endpoint mismatch"
        assert data["protocolVersion"] == "1.0.0", f"Protocol version should be '1.0.0'"
        
        # Verify capabilities
        assert isinstance(data["capabilities"], dict), "Capabilities should be a dict"
        assert "streaming" in data["capabilities"], "Capabilities should have streaming field"
        assert "pushNotifications" in data["capabilities"], "Capabilities should have pushNotifications field"
        
        # Verify skills
        assert isinstance(data["skills"], list), "Skills should be a list"
        assert len(data["skills"]) > 0, "Skills should not be empty"
        skill_names = [s.get("name") for s in data["skills"]]
        assert "echo" in skill_names, "Should have 'echo' skill"
        
        print("✓ Agent card endpoint test passed")
        return True
    except Exception as e:
        print(f"✗ Agent card endpoint test failed: {e}")
        return False

def run_all_tests():
    """Run all production endpoint tests."""
    print("=" * 60)
    print(f"Production Endpoint Tests")
    print(f"Base URL: {BASE_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 60)
    
    results = {
        "Echo": test_echo_endpoint(),
        "JSON-RPC": test_jsonrpc_endpoint(),
        "MCP": test_mcp_endpoint(),
        "A2A SendMessage": test_a2a_endpoint(),
        "Agent Card": test_agent_card_endpoint(),
    }
    
    print("\n" + "=" * 60)
    print("Production Endpoint Status Summary")
    print("=" * 60)
    
    all_passed = True
    for endpoint, passed in results.items():
        status = "✓" if passed else "✗"
        print(f"  {status} {endpoint:15} {'PASS' if passed else 'FAIL'}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("✓ All production endpoints are operational!")
        print("=" * 60)
        return 0
    else:
        print("✗ Some endpoints failed!")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
