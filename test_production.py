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

def test_soap_endpoint():
    """Test the SOAP endpoint."""
    print("\n=== Testing SOAP Endpoint ===")
    url = f"{BASE_URL}/soap"
    
    try:
        req = """<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:echo="http://example.com/echo">
   <soapenv:Header/>
   <soapenv:Body>
      <echo:EchoRequest>
         <echo:Message>production_soap_test</echo:Message>
      </echo:EchoRequest>
   </soapenv:Body>
</soapenv:Envelope>"""
        resp = requests.post(url, data=req, headers={"Content-Type": "text/xml"}, timeout=10)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text[:300]}...")
        
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        assert "EchoResponse" in resp.text, "Response should have EchoResponse tag"
        assert "production_soap_test" in resp.text, "Response should echo the message"
        print("✓ SOAP endpoint test passed")
        return True
    except Exception as e:
        print(f"✗ SOAP endpoint test failed: {e}")
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
            "method": "echo",
            "params": {"test": "data"},
            "id": 42
        }
        resp = requests.post(url, json=payload, timeout=10)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text[:200]}")
        
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        data = resp.json()
        assert data.get("jsonrpc") == "2.0", "Response should have jsonrpc field"
        assert "result" in data, "Response should have result field"
        assert data["result"]["method"] == "echo", "Result should echo the method"
        assert data["result"]["params"] == {"test": "data"}, "Result should echo the params"
        print("✓ MCP endpoint test passed")
        return True
    except Exception as e:
        print(f"✗ MCP endpoint test failed: {e}")
        return False

def test_mcp_sse_endpoint():
    """Test the MCP SSE endpoint."""
    print("\n=== Testing MCP SSE Endpoint ===")
    url = f"{BASE_URL}/mcp/sse"
    
    try:
        payload = {
            "jsonrpc": "2.0",
            "method": "sse_echo",
            "params": {"data": "sse_test"},
            "id": "sse-42"
        }
        resp = requests.post(url, json=payload, timeout=10)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text[:200]}")
        
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        assert "text/event-stream" in resp.headers.get("Content-Type", ""), "Expected SSE content type"
        
        # Verify SSE format
        lines = resp.text.strip().split("\n")
        assert lines[0] == "event: message", f"Expected event: message, got {lines[0]}"
        assert lines[1].startswith("data: "), f"Expected data: line, got {lines[1]}"
        
        # Verify JSON content
        data_json = json.loads(lines[1][6:])
        assert data_json.get("jsonrpc") == "2.0", "Expected JSON-RPC 2.0"
        assert data_json["result"]["method"] == "sse_echo", "Method should match"
        
        print("✓ MCP SSE endpoint test passed")
        return True
    except Exception as e:
        print(f"✗ MCP SSE endpoint test failed: {e}")
        return False

def test_a2a_endpoint():
    """Test the A2A SendMessage endpoint (POST /a2a/message:send)."""
    print("\n=== Testing A2A SendMessage Endpoint ===")
    url = f"{BASE_URL}/a2a/message:send"

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

def test_a2a_get_task_endpoint():
    """Test the A2A GetTask endpoint (GET /a2a/tasks/{id})."""
    print("\n=== Testing A2A GetTask Endpoint ===")
    url = f"{BASE_URL}/a2a/tasks/prod-test-task-001"
    
    try:
        resp = requests.get(url, timeout=10)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text[:200]}")
        
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        data = resp.json()
        assert "id" in data, "Response should have id field"
        assert data["id"] == "prod-test-task-001", "Task id should match request"
        assert "status" in data, "Response should have status field"
        print("✓ A2A GetTask endpoint test passed")
        return True
    except Exception as e:
        print(f"✗ A2A GetTask endpoint test failed: {e}")
        return False

def test_a2a_list_tasks_endpoint():
    """Test the A2A ListTasks endpoint (GET /a2a/tasks)."""
    print("\n=== Testing A2A ListTasks Endpoint ===")
    url = f"{BASE_URL}/a2a/tasks"
    
    try:
        resp = requests.get(url, timeout=10)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text[:200]}")
        
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        data = resp.json()
        assert "tasks" in data, "Response should have tasks field"
        assert isinstance(data["tasks"], list), "Tasks should be a list"
        assert "nextPageToken" in data, "Response should have nextPageToken field"
        assert "pageSize" in data, "Response should have pageSize field"
        assert "totalSize" in data, "Response should have totalSize field"
        print("✓ A2A ListTasks endpoint test passed")
        return True
    except Exception as e:
        print(f"✗ A2A ListTasks endpoint test failed: {e}")
        return False

def test_a2a_cancel_task_endpoint():
    """Test the A2A CancelTask endpoint (POST /a2a/tasks/{id}:cancel)."""
    print("\n=== Testing A2A CancelTask Endpoint ===")
    url = f"{BASE_URL}/a2a/tasks/prod-test-task-cancel-001:cancel"
    
    try:
        resp = requests.post(url, timeout=10)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text[:200]}")
        
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        data = resp.json()
        assert "id" in data, "Response should have id field"
        assert data["id"] == "prod-test-task-cancel-001", "Task id should match request"
        assert data["status"] == "canceled", "Task status should be canceled"
        print("✓ A2A CancelTask endpoint test passed")
        return True
    except Exception as e:
        print(f"✗ A2A CancelTask endpoint test failed: {e}")
        return False

def test_a2a_jsonrpc_endpoint():
    """Test the A2A JSON-RPC endpoint (POST /a2a)."""
    print("\n=== Testing A2A JSON-RPC Endpoint ===")
    url = f"{BASE_URL}/a2a"

    try:
        # Use SDK to construct proper message
        message = Message(
            messageId="prod-test-a2a-jsonrpc-001",
            role=Role.user,
            parts=[TextPart(text="production test via JSON-RPC")],
            metadata={"source": "production-test"}
        )
        
        # Create JSON-RPC 2.0 request
        payload = {
            "jsonrpc": "2.0",
            "method": "a2a.SendMessage",
            "params": {
                "message": message.model_dump(exclude_none=True, by_alias=True)
            },
            "id": 1
        }
        
        resp = requests.post(url, json=payload, timeout=10)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text[:300]}...")
        
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        data = resp.json()
        
        # Verify JSON-RPC 2.0 structure
        assert data.get("jsonrpc") == "2.0", "Response should have jsonrpc: 2.0"
        assert "result" in data, "Response should have result field"
        assert data["id"] == 1, "Response should include id"
        
        # Verify result structure
        assert "message" in data["result"], "Result should have message field"
        result_msg = data["result"]["message"]
        assert result_msg.get("role") == "agent", "Response should have role: agent"
        assert "parts" in result_msg, "Response should have parts field"
        assert result_msg["parts"][0]["text"] == "production test via JSON-RPC", "Text should be echoed back"
        
        print("✓ A2A JSON-RPC endpoint test passed")
        return True
    except Exception as e:
        print(f"✗ A2A JSON-RPC endpoint test failed: {e}")
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
        assert data["endpoint"] == "https://echo.azurewebsites.net/api/a2a/message:send", f"Endpoint mismatch"
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
        "SOAP": test_soap_endpoint(),
        "JSON-RPC": test_jsonrpc_endpoint(),
        "MCP": test_mcp_endpoint(),
        "MCP SSE": test_mcp_sse_endpoint(),
        "A2A SendMessage": test_a2a_endpoint(),
        "A2A GetTask": test_a2a_get_task_endpoint(),
        "A2A ListTasks": test_a2a_list_tasks_endpoint(),
        "A2A CancelTask": test_a2a_cancel_task_endpoint(),
        "A2A JSON-RPC": test_a2a_jsonrpc_endpoint(),
        "Agent Card": test_agent_card_endpoint(),
    }
    
    print("\n" + "=" * 60)
    print("Production Endpoint Status Summary")
    print("=" * 60)
    
    all_passed = True
    for endpoint, passed in results.items():
        status = "✓" if passed else "✗"
        print(f"  {status} {endpoint:20} {'PASS' if passed else 'FAIL'}")
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
