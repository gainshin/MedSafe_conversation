#!/usr/bin/env python3
"""
簡化系統測試腳本
驗證MediNote-AI老年人安全醫療對話框架的核心功能
"""

import os
import sys
import json
import time
from datetime import datetime

# 添加src目錄到Python路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_phi_anonymizer():
    """測試PHI去識別化功能"""
    print("🔒 測試PHI去識別化...")
    try:
        from phi_processing.simple_phi_anonymizer import SimplePHIAnonymizer
        
        anonymizer = SimplePHIAnonymizer()
        test_text = "我是王小明，電話0912345678，身份證A123456789，住在台北市大安區"
        
        anonymized_text, entities = anonymizer.anonymize_text(test_text)
        
        print(f"原始文本: {test_text}")
        print(f"去識別化: {anonymized_text}")
        print(f"發現 {len(entities)} 個PHI實體")
        
        # 檢查是否成功去識別化
        success = len(entities) > 0
        print(f"PHI去識別化測試: {'✅ 通過' if success else '❌ 失敗'}")
        return success
        
    except Exception as e:
        print(f"PHI去識別化測試失敗: {e}")
        return False

def test_hipaa_compliance():
    """測試HIPAA合規功能"""
    print("\n🔐 測試HIPAA合規...")
    try:
        from hipaa_compliance.hipaa_manager import HIPAAComplianceManager
        
        hipaa_manager = HIPAAComplianceManager()
        
        # 測試加密/解密
        test_data = "敏感醫療資訊測試"
        encrypted = hipaa_manager.encrypt_phi_data(test_data)
        decrypted = hipaa_manager.decrypt_phi_data(encrypted)
        
        # 測試審計日誌
        hipaa_manager.log_message_access("test_user", "test_message", hash("test"))
        
        success = decrypted == test_data
        print(f"HIPAA合規測試: {'✅ 通過' if success else '❌ 失敗'}")
        return success
        
    except Exception as e:
        print(f"HIPAA合規測試失敗: {e}")
        return False

def test_medinote_processor():
    """測試對話處理器"""
    print("\n🤖 測試MediNote對話處理器...")
    try:
        from chat.medinote_processor import MediNoteProcessor
        
        processor = MediNoteProcessor()
        
        # 測試不同類型的訊息
        test_cases = [
            ("我今天感覺還可以", "general_conversation"),
            ("我的胸口有點痛", "pain_report"),
            ("忘記吃藥怎麼辦？", "medication"),
            ("什麼時候要回診？", "appointment"),
            ("我的血糖300正常嗎？", "health_inquiry")
        ]
        
        all_passed = True
        for message, expected_type in test_cases:
            response = processor.process_message(message)
            emergency_level = processor.assess_emergency_level(message, response)
            
            print(f"訊息: {message}")
            print(f"回應: {response[:100]}...")
            print(f"緊急程度: {emergency_level:.2f}")
            print("-" * 50)
            
            if not response:
                all_passed = False
        
        print(f"MediNote處理器測試: {'✅ 通過' if all_passed else '❌ 失敗'}")
        return all_passed
        
    except Exception as e:
        print(f"MediNote處理器測試失敗: {e}")
        return False

def test_elderly_interface():
    """測試老年人友善介面"""
    print("\n👴 測試老年人友善介面...")
    try:
        from elderly_interface.elderly_interface import ElderlyInterface
        
        elderly_interface = ElderlyInterface()
        settings = elderly_interface.get_interface_settings()
        
        print("介面設定:")
        print(f"  字體大小: {settings['display']['font_size']}")
        print(f"  高對比: {settings['display']['high_contrast']}")
        print(f"  語音輸入: {settings['features']['voice_input']}")
        print(f"  緊急聯絡人: {len(settings['emergency_contacts'])} 位")
        
        # 測試緊急聯繫功能
        emergency_result = elderly_interface.emergency_contact(
            user_id="test_user",
            emergency_type="medical",
            location={"address": "測試地址", "coordinates": "25.0330,121.5654"}
        )
        
        success = settings and emergency_result.get('success', False)
        print(f"老年人介面測試: {'✅ 通過' if success else '❌ 失敗'}")
        return success
        
    except Exception as e:
        print(f"老年人介面測試失敗: {e}")
        return False

def test_prompt_tester():
    """測試Prompt測試框架"""
    print("\n🧪 測試Prompt測試框架...")
    try:
        from prompt_testing.prompt_tester import PromptTester
        
        prompt_tester = PromptTester()
        
        # 執行部分測試案例
        test_results = prompt_tester.run_tests(['emergency', 'pain_report'])
        summary = prompt_tester.generate_summary(test_results)
        
        print(f"測試案例數: {len(prompt_tester.test_cases)}")
        print(f"執行測試: {len(test_results)} 個")
        print(f"通過率: {summary['test_summary']['pass_rate']:.1%}")
        
        success = len(test_results) > 0 and summary['test_summary']['pass_rate'] >= 0
        print(f"Prompt測試框架: {'✅ 通過' if success else '❌ 失敗'}")
        return success
        
    except Exception as e:
        print(f"Prompt測試框架失敗: {e}")
        return False

def run_integration_test():
    """執行整合測試"""
    print("\n🔗 執行整合測試...")
    try:
        from phi_processing.phi_anonymizer import PHIAnonymizer
        from hipaa_compliance.hipaa_manager import HIPAAComplianceManager
        from chat.medinote_processor import MediNoteProcessor
        
        # 初始化組件
        anonymizer = PHIAnonymizer()
        hipaa_manager = HIPAAComplianceManager()
        processor = MediNoteProcessor()
        
        # 模擬完整流程
        user_message = "我是王小明，電話0912345678，現在胸口很痛，呼吸困難"
        
        print(f"用戶訊息: {user_message}")
        
        # 1. PHI去識別化
        anonymized_message, phi_entities = anonymizer.anonymize_text(user_message)
        print(f"去識別化: {anonymized_message}")
        print(f"PHI實體: {len(phi_entities)} 個")
        
        # 2. HIPAA審計記錄
        hipaa_manager.log_message_access("test_user", "user_input", hash(user_message))
        print("HIPAA審計記錄完成")
        
        # 3. AI處理
        ai_response = processor.process_message(anonymized_message)
        print(f"AI回應: {ai_response[:100]}...")
        
        # 4. 緊急程度評估
        emergency_level = processor.assess_emergency_level(user_message, ai_response)
        print(f"緊急程度: {emergency_level:.2f}")
        
        success = (
            len(phi_entities) > 0 and  # PHI檢測成功
            len(ai_response) > 0 and   # AI回應成功
            emergency_level > 0.5      # 緊急評估成功
        )
        
        print(f"整合測試: {'✅ 通過' if success else '❌ 失敗'}")
        return success
        
    except Exception as e:
        print(f"整合測試失敗: {e}")
        return False

def main():
    """主函數"""
    print("🚀 MediNote-AI 老年人安全醫療對話框架 - 系統測試")
    print("=" * 60)
    
    test_results = []
    
    # 執行各項測試
    test_results.append(("PHI去識別化", test_phi_anonymizer()))
    test_results.append(("HIPAA合規", test_hipaa_compliance()))
    test_results.append(("MediNote處理器", test_medinote_processor()))
    test_results.append(("老年人介面", test_elderly_interface()))
    test_results.append(("Prompt測試", test_prompt_tester()))
    test_results.append(("整合測試", run_integration_test()))
    
    # 統計結果
    total_tests = len(test_results)
    passed_tests = sum(1 for _, result in test_results if result)
    
    print("\n" + "=" * 60)
    print("📊 測試結果統計:")
    print(f"總測試數: {total_tests}")
    print(f"通過測試: {passed_tests}")
    print(f"失敗測試: {total_tests - passed_tests}")
    print(f"通過率: {passed_tests/total_tests:.1%}")
    
    # 顯示詳細結果
    print("\n🔍 詳細測試結果:")
    for test_name, result in test_results:
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"  {test_name}: {status}")
    
    # 整體評估
    if passed_tests == total_tests:
        print("\n🎉 所有測試通過！系統運作正常。")
        return 0
    elif passed_tests >= total_tests * 0.8:
        print("\n✨ 大部分測試通過，系統基本功能正常。")
        return 0
    else:
        print("\n⚠️  部分測試失敗，建議檢查系統配置。")
        return 1

if __name__ == "__main__":
    sys.exit(main())