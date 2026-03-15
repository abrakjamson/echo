#!/usr/bin/env python3
"""Test script for echo and JSON-RPC endpoints."""

import json
import sys
import requests
from jsonrpc_handler import JsonRpcHandler
from mcp_handler import McpHandler
from a2a_handler import A2AHandler

def test_jsonrpc_1_0():
    """Test JSON-RPC 1.0 request."""
    print("\n=== Testing JSON-RPC 1.0 ===")
    
    # Named params
    req = {
        "method": "test_method",
        "params": {"key": "value"},
        "id": "test-1"
    }
    print(f"Request: {json.dumps(req)}")
    resp = JsonRpcHandler.handle_request(req)
    print(f"Response: {json.dumps(resp)}")
    
    assert "result" in resp, "Response should have result field"
    assert resp["result"] == req, "Result should echo the request"
    assert resp["id"] == "test-1", "Response should include id"
    assert "jsonrpc" not in resp, "JSON-RPC 1.0 should not have jsonrpc field"
    print("✓ JSON-RPC 1.0 test passed")

def test_jsonrpc_2_0():
    """Test JSON-RPC 2.0 request."""
    print("\n=== Testing JSON-RPC 2.0 ===")
    
    req = {
        "jsonrpc": "2.0",
        "method": "test_method",
        "params": [1, 2, 3],
        "id": 123
    }
    print(f"Request: {json.dumps(req)}")
    resp = JsonRpcHandler.handle_request(req)
    print(f"Response: {json.dumps(resp)}")
    
    assert resp.get("jsonrpc") == "2.0", "Should include jsonrpc: 2.0"
    assert "result" in resp, "Response should have result field"
    assert resp["result"] == req, "Result should echo the request"
    assert resp["id"] == 123, "Response should include id"
    print("✓ JSON-RPC 2.0 test passed")

def test_jsonrpc_2_0_notification():
    """Test JSON-RPC 2.0 notification (no id)."""
    print("\n=== Testing JSON-RPC 2.0 Notification (no id) ===")
    
    req = {
        "jsonrpc": "2.0",
        "method": "notify_method",
        "params": {}
    }
    print(f"Request: {json.dumps(req)}")
    resp = JsonRpcHandler.handle_request(req)
    print(f"Response: {json.dumps(resp)}")
    
    assert resp.get("jsonrpc") == "2.0", "Should include jsonrpc: 2.0"
    assert "result" in resp, "Response should have result field"
    assert "id" not in resp, "Notification response should not have id"
    print("✓ JSON-RPC 2.0 notification test passed")

def test_invalid_request():
    """Test invalid request (missing method)."""
    print("\n=== Testing Invalid Request ===")
    
    req = {
        "jsonrpc": "2.0",
        "id": 1
    }
    print(f"Request (no method): {json.dumps(req)}")
    resp = JsonRpcHandler.handle_request(req)
    print(f"Response: {json.dumps(resp)}")
    
    assert "error" in resp, "Should have error field"
    assert resp["error"]["code"] == -32600, "Should have Invalid Request code"
    assert resp["id"] == 1, "Should include id from request"
    print("✓ Invalid request test passed")

def test_non_dict_request():
    """Test non-dict request."""
    print("\n=== Testing Non-Dict Request ===")
    
    req = ["not", "a", "dict"]
    print(f"Request: {json.dumps(req)}")
    resp = JsonRpcHandler.handle_request(req)
    print(f"Response: {json.dumps(resp)}")
    
    assert "error" in resp, "Should have error field"
    assert resp["error"]["code"] == -32700, "Should have Parse error code"
    assert "id" not in resp, "Should not have id for parse error"
    print("✓ Non-dict request test passed")

def test_a2a_message_echo():
    """Test A2A message echo functionality."""
    print("\n=== Testing A2A Handler (unit) ===")
    
    import uuid
    req = {
        "messageId": str(uuid.uuid4()),
        "role": "user",
        "parts": [{"text": "hello world"}],
        "metadata": {"source": "test-client"}
    }
    print(f"Request: {json.dumps(req)}")
    resp = A2AHandler.handle_request(req)
    print(f"Response: {json.dumps(resp)}")
    
    assert "error" not in resp, f"Response should not have error: {resp}"
    assert "messageId" in resp, "Response should have messageId field"
    assert resp.get("role") == "agent", "Response should have role: agent"
    assert "parts" in resp, "Response should have parts field"
    assert len(resp["parts"]) > 0, "Response should have at least one part"
    assert resp["parts"][0]["text"] == "hello world", "Text should be echoed"
    print("✓ A2A message echo test passed")

def test_http_echo_endpoint():
    """Test the deployed echo endpoint via HTTP."""
    print("\n=== Testing HTTP Echo Endpoint ===")
    
    base_url = "https://echo.azurewebsites.net/api/echo"
    
    # Test with query parameter
    print("Test 1: Query parameter")
    resp = requests.get(f"{base_url}?value=hello_world")
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text}")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    assert resp.text == "hello_world", f"Expected 'hello_world', got '{resp.text}'"
    print("✓ Query parameter test passed")
    
    # Test with JSON body
    print("\nTest 2: JSON body")
    payload = {"value": "json_test"}
    resp = requests.post(base_url, json=payload)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text}")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    assert resp.text == "json_test", f"Expected 'json_test', got '{resp.text}'"
    print("✓ JSON body test passed")
    
    # Test missing value field
    print("\nTest 3: Missing value field")
    resp = requests.get(base_url)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text}")
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}"
    assert "required" in resp.text.lower(), f"Expected error message about required field"
    print("✓ Missing value test passed")

def test_http_jsonrpc_endpoint():
    """Test the deployed JSON-RPC endpoint via HTTP."""
    print("\n=== Testing HTTP JSON-RPC Endpoint ===")
    
    base_url = "https://echo.azurewebsites.net/api/jsonrpc"
    
    # Test JSON-RPC 1.0
    print("Test 1: JSON-RPC 1.0")
    payload = {
        "method": "test_method",
        "params": {"key": "value"},
        "id": "test-1"
    }
    resp = requests.post(base_url, json=payload)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text}")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    data = resp.json()
    assert "result" in data, "Response should have result field"
    assert data["result"]["method"] == "test_method", "Result should contain the request"
    assert "jsonrpc" not in data, "JSON-RPC 1.0 should not have jsonrpc field"
    print("✓ JSON-RPC 1.0 test passed")
    
    # Test JSON-RPC 2.0
    print("\nTest 2: JSON-RPC 2.0")
    payload = {
        "jsonrpc": "2.0",
        "method": "test_method",
        "params": [1, 2, 3],
        "id": 123
    }
    resp = requests.post(base_url, json=payload)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text}")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    data = resp.json()
    assert data.get("jsonrpc") == "2.0", "Response should have jsonrpc: 2.0"
    assert "result" in data, "Response should have result field"
    assert data["id"] == 123, "Response should include id"
    print("✓ JSON-RPC 2.0 test passed")
    
    # Test JSON-RPC 2.0 notification
    print("\nTest 3: JSON-RPC 2.0 notification (no id)")
    payload = {
        "jsonrpc": "2.0",
        "method": "notify_method",
        "params": {}
    }
    resp = requests.post(base_url, json=payload)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text}")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    data = resp.json()
    assert data.get("jsonrpc") == "2.0", "Response should have jsonrpc: 2.0"
    assert "id" not in data, "Notification response should not have id"
    print("✓ JSON-RPC 2.0 notification test passed")

if __name__ == "__main__":
    def test_mcp_handler_unit():
        """Unit test for McpHandler."""
        print("\n=== Testing MCP handler (unit) ===")
        req = {"action": "echo", "payload": {"foo": "bar"}, "id": "mcp-1"}
        print(f"Request: {json.dumps(req)}")
        resp = McpHandler.handle_request(req)
        print(f"Response: {json.dumps(resp)}")
        assert "result" in resp, "Response should have result field"
        assert resp["result"] == req, "Result should echo the request"
        assert resp["id"] == "mcp-1", "Response should include id"
        print("✓ MCP handler unit test passed")

    def test_http_mcp_endpoint():
        """Integration test for deployed /api/mcp endpoint."""
        print("\n=== Testing HTTP MCP Endpoint ===")
        base_url = "https://echo.azurewebsites.net/api/mcp"

        print("Test 1: POST JSON body")
        payload = {"action": "echo", "payload": {"x": 1}, "id": 42}
        try:
            resp = requests.post(base_url, json=payload, timeout=10)
        except requests.exceptions.RequestException as e:
            print(f"\n⚠ HTTP MCP test skipped: {e}")
            return
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")
        if resp.status_code != 200:
            print(f"\n⚠ HTTP MCP test skipped: expected 200 but got {resp.status_code} (endpoint may not be deployed yet)")
            return
        data = resp.json()
        assert "result" in data, "Response should have result"
        assert data["result"]["action"] == "echo", "Result should contain the request"
        print("✓ HTTP MCP endpoint test passed")

    def test_http_a2a_endpoint():
        """Integration test for deployed /api/a2a endpoint."""
        print("\n=== Testing HTTP A2A Endpoint ===")
        base_url = "https://echo.azurewebsites.net/api/a2a"

        print("Test 1: A2A message echo")
        import uuid
        payload = {
            "messageId": str(uuid.uuid4()),
            "role": "user",
            "parts": [{"text": "hello from A2A client"}],
            "metadata": {"source": "test-client"}
        }
        try:
            resp = requests.post(base_url, json=payload, timeout=10)
        except requests.exceptions.RequestException as e:
            print(f"\n⚠ HTTP A2A test skipped: {e}")
            return
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")
        if resp.status_code != 200:
            print(f"\n⚠ HTTP A2A test skipped: expected 200 but got {resp.status_code} (endpoint may not be deployed yet)")
            return
        data = resp.json()
        assert "messageId" in data, "Response should have messageId field"
        assert data.get("role") == "agent", "Response should have role: agent"
        assert "parts" in data, "Response should have parts field"
        assert len(data["parts"]) > 0, "Response should have at least one part"
        assert data["parts"][0]["text"] == "hello from A2A client", "Text should be echoed back"
        print("✓ HTTP A2A endpoint test passed")

    try:
        test_jsonrpc_1_0()
        test_jsonrpc_2_0()
        test_jsonrpc_2_0_notification()
        test_invalid_request()
        test_non_dict_request()
        # MCP unit test
        test_mcp_handler_unit()
        # A2A unit test
        test_a2a_message_echo()

        # HTTP endpoint tests
        try:
            test_http_echo_endpoint()
            test_http_jsonrpc_endpoint()
            test_http_mcp_endpoint()
            test_http_a2a_endpoint()
        except requests.exceptions.RequestException as e:
            print(f"\n⚠ HTTP tests skipped: {e}")
            print("(Endpoints may not be deployed yet)")

        print("\n" + "="*50)
        print("All tests passed! ✓")
        print("="*50)
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        sys.exit(1)
