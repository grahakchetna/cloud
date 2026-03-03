#!/usr/bin/env python3
"""
Test script to verify all Flask endpoints are accessible
"""
import requests
import json
import sys
import time

BASE_URL = "http://localhost:5002"

# Test endpoints
ENDPOINTS = {
    "GET": [
        "/",
        "/short",
        "/long",
        "/wordpress",
        "/facebook",
        "/instagram",
        "/videos",
        "/layout-designer",
        "/settings",
        "/api/layouts",
        "/api/videos",
    ],
    "POST": [
        "/generate",  # Requires form data
        "/generate-long",  # Requires form data
        "/wordpress/post",
        "/facebook/post",
        "/instagram/post",
        "/api/layouts",
        "/upload-background",
        "/fetch_rss",
        "/rss_save_mapping",
        "/fetch_rss_post_selected",
    ]
}

def test_endpoint(method, endpoint, data=None):
    """Test a single endpoint"""
    url = BASE_URL + endpoint
    try:
        if method == "GET":
            response = requests.get(url, timeout=5)
        else:
            response = requests.post(url, data=data or {}, timeout=5)
        
        status = "✓" if response.status_code < 500 else "✗"
        return {
            "endpoint": endpoint,
            "method": method,
            "status": status,
            "code": response.status_code,
            "length": len(response.content)
        }
    except requests.exceptions.ConnectionError:
        return {
            "endpoint": endpoint,
            "method": method,
            "status": "✗",
            "error": "Connection refused - server not running"
        }
    except Exception as e:
        return {
            "endpoint": endpoint,
            "method": method,
            "status": "✗",
            "error": str(e)
        }

def main():
    print("\n" + "="*60)
    print("ENDPOINT TESTING")
    print("="*60)
    
    results = {
        "total": 0,
        "success": 0,
        "failed": 0,
        "endpoints": []
    }
    
    # Test GET endpoints
    print("\n📡 Testing GET endpoints...")
    for endpoint in ENDPOINTS["GET"]:
        result = test_endpoint("GET", endpoint)
        results["endpoints"].append(result)
        results["total"] += 1
        if result["status"] == "✓" and result["code"] < 400:
            results["success"] += 1
            print(f"  ✓ {endpoint:40} [{result['code']}]")
        else:
            results["failed"] += 1
            error = result.get("error", f"HTTP {result.get('code', '?')}")
            print(f"  ✗ {endpoint:40} [{error}]")
    
    # Test POST endpoints
    print("\n📤 Testing POST endpoints...")
    for endpoint in ENDPOINTS["POST"]:
        result = test_endpoint("POST", endpoint)
        results["endpoints"].append(result)
        results["total"] += 1
        if result["status"] == "✓" and result["code"] < 500:
            results["success"] += 1
            print(f"  ✓ {endpoint:40} [{result['code']}]")
        else:
            results["failed"] += 1
            error = result.get("error", f"HTTP {result.get('code', '?')}")
            print(f"  ✗ {endpoint:40} [{error}]")
    
    # Summary
    print("\n" + "="*60)
    print(f"SUMMARY: {results['success']}/{results['total']} endpoints accessible")
    print("="*60)
    
    # Detailed report
    print("\nDETAILED REPORT:")
    print(json.dumps(results, indent=2))
    
    return 0 if results["failed"] == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
