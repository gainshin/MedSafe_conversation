#!/usr/bin/env python3
"""
測試 MediNote-AI 系統的各個組件
"""

import requests
import json

# 測試配置
BASE_URL = "http://127.0.0.1:5000"

def test_health():
    """測試健康檢查端點"""
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"健康檢查: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"系統狀態: {data['status']}")
            print(f"組件狀態: {data['components']}")
            return True
        else:
            print(f"健康檢查失敗: {response.text}")
            return False
    except Exception as e:
        print(f"健康檢查錯誤: {e}")
        return False

def test_login():
    """測試登入端點"""
    try:
        login_data = {
            "username": "testuser",
            "password": "testpass"
        }
        response = requests.post(
            f"{BASE_URL}/api/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"\n登入測試: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"登入結果: {data}")
            return True
        else:
            print(f"登入失敗: {response.text}")
            return False
    except Exception as e:
        print(f"登入錯誤: {e}")
        return False

def test_chat():
    """測試對話端點"""
    try:
        # 先登入獲取會話
        session = requests.Session()
        login_data = {
            "username": "testuser", 
            "password": "testpass"
        }
        
        # 登入
        login_response = session.post(
            f"{BASE_URL}/api/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        if login_response.status_code != 200:
            print(f"\n登入失敗，無法測試對話功能")
            return False
            
        # 測試對話
        chat_data = {
            "message": "我的胸口有點痛，請問該怎麼辦？",
            "context": {}
        }
        
        response = session.post(
            f"{BASE_URL}/api/chat",
            json=chat_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\n對話測試: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"AI回應: {data['response'][:100]}...")
            print(f"緊急程度: {data['emergency_level']}")
            return True
        else:
            print(f"對話失敗: {response.text}")
            return False
            
    except Exception as e:
        print(f"對話錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_emergency():
    """測試緊急聯繫端點"""
    try:
        session = requests.Session()
        
        # 先登入
        login_response = session.post(
            f"{BASE_URL}/api/login",
            json={"username": "testuser", "password": "testpass"},
            headers={"Content-Type": "application/json"}
        )
        
        if login_response.status_code != 200:
            print(f"\n登入失敗，無法測試緊急功能")
            return False
            
        # 測試緊急聯繫
        emergency_data = {
            "type": "medical",
            "location": {"address": "測試地址", "coordinates": "25.0330,121.5654"}
        }
        
        response = session.post(
            f"{BASE_URL}/api/emergency-contact",
            json=emergency_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\n緊急聯繫測試: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"緊急聯繫結果: {data}")
            return True
        else:
            print(f"緊急聯繫失敗: {response.text}")
            return False
            
    except Exception as e:
        print(f"緊急聯繫錯誤: {e}")
        return False

def main():
    """主測試函數"""
    print("🧪 測試 MediNote-AI 系統")
    print("=" * 50)
    
    # 測試各個端點
    health_ok = test_health()
    login_ok = test_login()
    chat_ok = False
    emergency_ok = False
    
    if login_ok:
        chat_ok = test_chat()
        emergency_ok = test_emergency()
    
    # 總結結果
    print(f"\n📊 測試結果總結:")
    print(f"健康檢查: {'✅' if health_ok else '❌'}")
    print(f"登入功能: {'✅' if login_ok else '❌'}")
    print(f"對話功能: {'✅' if chat_ok else '❌'}")
    print(f"緊急聯繫: {'✅' if emergency_ok else '❌'}")
    
    all_passed = all([health_ok, login_ok, chat_ok, emergency_ok])
    print(f"\n🎯 整體狀態: {'✅ 系統正常' if all_passed else '❌ 需要修復'}")

if __name__ == "__main__":
    main()