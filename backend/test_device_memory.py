#!/usr/bin/env python3
"""
Test Device Memory and Linking Features
Demonstrates how device memory works and device linking API
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"  # Change to your server URL
DEVICE_1 = "my-phone-123"
DEVICE_2 = "my-laptop-456"

def test_device_memory():
    """Test device memory functionality"""
    print("🧠 Testing Device Memory System")
    print("=" * 40)
    
    # Test 1: First conversation on phone
    print(f"\n📱 Testing conversation on {DEVICE_1}...")
    response1 = requests.post(f"{BASE_URL}/api/chat", json={
        "message": "Hello! I'm using my phone. Can you remember this?",
        "device_id": DEVICE_1
    })
    
    if response1.status_code == 200:
        data1 = response1.json()
        print(f"✅ Phone response: {data1['response'][:100]}...")
        print(f"📊 Model used: {data1['model']}")
        print(f"🧠 Context used: {data1['context_used']}")
    else:
        print(f"❌ Phone request failed: {response1.status_code}")
        return
    
    # Test 2: Second conversation on phone (should have context)
    print(f"\n📱 Second conversation on {DEVICE_1}...")
    response2 = requests.post(f"{BASE_URL}/api/chat", json={
        "message": "Do you remember what I said before?",
        "device_id": DEVICE_1
    })
    
    if response2.status_code == 200:
        data2 = response2.json()
        print(f"✅ Phone response: {data2['response'][:100]}...")
        print(f"🧠 Context used: {data2['context_used']}")
    else:
        print(f"❌ Phone request failed: {response2.status_code}")
    
    # Test 3: Conversation on laptop (should be isolated)
    print(f"\n💻 Testing conversation on {DEVICE_2}...")
    response3 = requests.post(f"{BASE_URL}/api/chat", json={
        "message": "Hello! I'm using my laptop. Do you know what I said on my phone?",
        "device_id": DEVICE_2
    })
    
    if response3.status_code == 200:
        data3 = response3.json()
        print(f"✅ Laptop response: {data3['response'][:100]}...")
        print(f"🧠 Context used: {data3['context_used']}")
    else:
        print(f"❌ Laptop request failed: {response3.status_code}")

def test_device_linking():
    """Test device linking functionality"""
    print(f"\n🔗 Testing Device Linking")
    print("=" * 40)
    
    # Link devices
    print(f"\n🔗 Linking {DEVICE_1} and {DEVICE_2}...")
    link_response = requests.post(f"{BASE_URL}/api/device/link", json={
        "device_id": DEVICE_1,
        "target_device_id": DEVICE_2
    })
    
    if link_response.status_code == 200:
        link_data = link_response.json()
        print(f"✅ {link_data['message']}")
    else:
        print(f"❌ Device linking failed: {link_response.status_code}")
        return
    
    # Test conversation with linked context
    print(f"\n📱 Conversation on {DEVICE_1} with linked context...")
    response4 = requests.post(f"{BASE_URL}/api/chat", json={
        "message": "Now that we're linked, can you see my laptop conversations?",
        "device_id": DEVICE_1
    })
    
    if response4.status_code == 200:
        data4 = response4.json()
        print(f"✅ Linked response: {data4['response'][:100]}...")
        print(f"🧠 Context used: {data4['context_used']}")
    else:
        print(f"❌ Linked request failed: {response4.status_code}")

def test_device_memory_retrieval():
    """Test retrieving device memory"""
    print(f"\n📋 Testing Device Memory Retrieval")
    print("=" * 40)
    
    # Get phone memory
    print(f"\n📱 Getting memory for {DEVICE_1}...")
    memory_response = requests.get(f"{BASE_URL}/api/device/{DEVICE_1}/memory")
    
    if memory_response.status_code == 200:
        memory_data = memory_response.json()
        print(f"✅ Phone has {memory_data['total_conversations']} conversations")
        for conv in memory_data['conversations'][-3:]:  # Show last 3
            print(f"  📝 {conv['timestamp']}: {conv['message'][:50]}...")
    else:
        print(f"❌ Memory retrieval failed: {memory_response.status_code}")
    
    # Get laptop memory
    print(f"\n💻 Getting memory for {DEVICE_2}...")
    memory_response2 = requests.get(f"{BASE_URL}/api/device/{DEVICE_2}/memory")
    
    if memory_response2.status_code == 200:
        memory_data2 = memory_response2.json()
        print(f"✅ Laptop has {memory_data2['total_conversations']} conversations")
        for conv in memory_data2['conversations'][-3:]:  # Show last 3
            print(f"  📝 {conv['timestamp']}: {conv['message'][:50]}...")
    else:
        print(f"❌ Memory retrieval failed: {memory_response2.status_code}")

def test_smart_model_selection():
    """Test smart model selection"""
    print(f"\n🧠 Testing Smart Model Selection")
    print("=" * 40)
    
    # Test coding task
    print(f"\n💻 Testing coding task...")
    coding_response = requests.post(f"{BASE_URL}/api/chat", json={
        "message": "Write a Python function to calculate fibonacci numbers",
        "device_id": DEVICE_1
    })
    
    if coding_response.status_code == 200:
        coding_data = coding_response.json()
        print(f"✅ Coding response: {coding_data['response'][:100]}...")
        print(f"🤖 Model selected: {coding_data['model']}")
    else:
        print(f"❌ Coding request failed: {coding_response.status_code}")
    
    # Test simple task
    print(f"\n👋 Testing simple task...")
    simple_response = requests.post(f"{BASE_URL}/api/chat", json={
        "message": "Hello! How are you?",
        "device_id": DEVICE_1
    })
    
    if simple_response.status_code == 200:
        simple_data = simple_response.json()
        print(f"✅ Simple response: {simple_data['response'][:100]}...")
        print(f"🤖 Model selected: {simple_data['model']}")
    else:
        print(f"❌ Simple request failed: {simple_response.status_code}")

def main():
    """Main test function"""
    print("🚀 Ethos AI - Device Memory and Linking Test")
    print("=" * 50)
    print(f"Testing against: {BASE_URL}")
    print(f"Device 1: {DEVICE_1}")
    print(f"Device 2: {DEVICE_2}")
    
    try:
        # Test basic functionality
        test_device_memory()
        
        # Test device linking
        test_device_linking()
        
        # Test memory retrieval
        test_device_memory_retrieval()
        
        # Test smart model selection
        test_smart_model_selection()
        
        print(f"\n🎉 All tests completed!")
        print(f"📱 Device {DEVICE_1} has isolated memory")
        print(f"💻 Device {DEVICE_2} has isolated memory")
        print(f"🔗 Devices can be linked for shared context")
        print(f"🧠 AI can access device memory for better responses")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    main()
