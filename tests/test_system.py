"""
系統測試和驗證模組
確保所有組件正常運作
"""

import os
import sys
import json
import time
import logging
import unittest
from datetime import datetime
from typing import Dict, List, Optional
import pytest

# 添加src目錄到Python路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.chat.medinote_processor import MediNoteProcessor
from src.phi_processing.phi_anonymizer import PHIAnonymizer
from src.hipaa_compliance.hipaa_manager import HIPAAComplianceManager
from src.elderly_interface.elderly_interface import ElderlyInterface
from src.prompt_testing.prompt_tester import PromptTester

logger = logging.getLogger(__name__)

class SystemHealthChecker:
    """系統健康檢查器"""
    
    def __init__(self):
        self.check_results = []
        self.start_time = datetime.now()
        
    def check_all_components(self) -> Dict:
        """
        檢查所有系統組件
        
        Returns:
            健康檢查報告
        """
        logger.info("開始系統健康檢查...")
        
        # 檢查各個組件
        checks = [
            ('PHI去識別化', self.check_phi_anonymizer),
            ('HIPAA合規', self.check_hipaa_compliance),
            ('對話處理器', self.check_medinote_processor),
            ('老年人介面', self.check_elderly_interface),
            ('Prompt測試', self.check_prompt_tester),
            ('系統整合', self.check_system_integration)
        ]
        
        for check_name, check_func in checks:
            try:
                result = check_func()
                self.check_results.append({
                    'component': check_name,
                    'status': 'healthy' if result['healthy'] else 'unhealthy',
                    'details': result['details'],
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f"檢查 {check_name} 失敗: {e}")
                self.check_results.append({
                    'component': check_name,
                    'status': 'error',
                    'details': str(e),
                    'timestamp': datetime.now().isoformat()
                })
        
        # 生成總體報告
        return self._generate_health_report()
    
    def check_phi_anonymizer(self) -> Dict:
        """檢查PHI去識別化組件"""
        try:
            anonymizer = PHIAnonymizer()
            
            # 測試基本功能
            test_text = "我的電話是0912345678，住在台北市大安區"
            anonymized_text, entities = anonymizer.anonymize_text(test_text)
            
            is_healthy = len(entities) > 0 and '[PHONE_' in anonymized_text
            
            return {
                'healthy': is_healthy,
                'details': {
                    'test_result': f"原始: {test_text} -> 去識別化: {anonymized_text}",
                    'entities_found': len(entities),
                    'component_status': 'operational'
                }
            }
        except Exception as e:
            return {
                'healthy': False,
                'details': f"PHI去識別化組件錯誤: {str(e)}"
            }
    
    def check_hipaa_compliance(self) -> Dict:
        """檢查HIPAA合規組件"""
        try:
            hipaa_manager = HIPAAComplianceManager()
            
            # 測試加密功能
            test_data = "敏感醫療資訊測試"
            encrypted = hipaa_manager.encrypt_phi_data(test_data)
            decrypted = hipaa_manager.decrypt_phi_data(encrypted)
            
            is_healthy = decrypted == test_data
            
            return {
                'healthy': is_healthy,
                'details': {
                    'encryption_test': 'passed' if is_healthy else 'failed',
                    'audit_logging': 'enabled',
                    'data_retention': hipaa_manager.hipaa_settings['data_retention_days']
                }
            }
        except Exception as e:
            return {
                'healthy': False,
                'details': f"HIPAA合規組件錯誤: {str(e)}"
            }
    
    def check_medinote_processor(self) -> Dict:
        """檢查對話處理器"""
        try:
            processor = MediNoteProcessor()
            
            # 測試基本對話處理
            test_message = "我今天感覺還可以"
            response = processor.process_message(test_message)
            
            is_healthy = len(response) > 0 and '醫療助手' in response
            
            return {
                'healthy': is_healthy,
                'details': {
                    'test_message': test_message,
                    'ai_response': response[:100] + '...' if len(response) > 100 else response,
                    'model_version': processor.model_version
                }
            }
        except Exception as e:
            return {
                'healthy': False,
                'details': f"對話處理器錯誤: {str(e)}"
            }
    
    def check_elderly_interface(self) -> Dict:
        """檢查老年人介面"""
        try:
            elderly_interface = ElderlyInterface()
            
            # 測試介面設定
            settings = elderly_interface.get_interface_settings()
            
            is_healthy = ('display' in settings and 'features' in settings and
                       settings['features'].get('voice_input') is not None)
            
            return {
                'healthy': is_healthy,
                'details': {
                    'interface_features': list(settings['features'].keys()),
                    'font_size': settings['display']['font_size'],
                    'emergency_contacts': len(settings['emergency_contacts'])
                }
            }
        except Exception as e:
            return {
                'healthy': False,
                'details': f"老年人介面錯誤: {str(e)}"
            }
    
    def check_prompt_tester(self) -> Dict:
        """檢查Prompt測試框架"""
        try:
            prompt_tester = PromptTester()
            
            # 測試基本功能
            test_cases = prompt_tester.test_cases
            
            is_healthy = len(test_cases) > 0
            
            return {
                'healthy': is_healthy,
                'details': {
                    'test_cases_loaded': len(test_cases),
                    'categories': list(set(tc.category for tc in test_cases)),
                    'framework_status': 'ready'
                }
            }
        except Exception as e:
            return {
                'healthy': False,
                'details': f"Prompt測試框架錯誤: {str(e)}"
            }
    
    def check_system_integration(self) -> Dict:
        """檢查系統整合"""
        try:
            # 測試完整的對話流程
            processor = MediNoteProcessor()
            anonymizer = PHIAnonymizer()
            hipaa_manager = HIPAAComplianceManager()
            
            # 模擬完整流程
            user_message = "我的胸口有點痛，電話是0912345678"
            
            # 1. PHI去識別化
            anonymized_message, phi_entities = anonymizer.anonymize_text(user_message)
            
            # 2. HIPAA審計記錄
            hipaa_manager.log_message_access(
                user_id="test_user",
                message_type="user_input",
                message_hash=hash(user_message)
            )
            
            # 3. AI處理
            ai_response = processor.process_message(anonymized_message)
            
            # 4. 評估緊急程度
            emergency_level = processor.assess_emergency_level(user_message, ai_response)
            
            is_healthy = (
                len(phi_entities) > 0 and  # PHI檢測成功
                len(ai_response) > 0 and   # AI回應成功
                emergency_level > 0      # 緊急評估成功
            )
            
            return {
                'healthy': is_healthy,
                'details': {
                    'phi_entities_detected': len(phi_entities),
                    'ai_response_generated': len(ai_response) > 0,
                    'emergency_level': emergency_level,
                    'integration_flow': 'completed'
                }
            }
        except Exception as e:
            return {
                'healthy': False,
                'details': f"系統整合錯誤: {str(e)}"
            }
    
    def _generate_health_report(self) -> Dict:
        """生成健康報告"""
        healthy_components = sum(1 for result in self.check_results if result['status'] == 'healthy')
        total_components = len(self.check_results)
        
        overall_health = healthy_components == total_components
        
        # 計算檢查時間
        check_duration = (datetime.now() - self.start_time).total_seconds()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy' if overall_health else 'unhealthy',
            'summary': {
                'total_components': total_components,
                'healthy_components': healthy_components,
                'unhealthy_components': total_components - healthy_components,
                'check_duration_seconds': check_duration
            },
            'component_details': self.check_results,
            'recommendations': self._generate_health_recommendations()
        }
        
        return report
    
    def _generate_health_recommendations(self) -> List[str]:
        """生成健康建議"""
        recommendations = []
        
        unhealthy_components = [
            result for result in self.check_results 
            if result['status'] != 'healthy'
        ]
        
        for component in unhealthy_components:
            component_name = component['component']
            if component['status'] == 'unhealthy':
                recommendations.append(f"{component_name} 需要檢修，請檢查相關配置和依賴服務")
            elif component['status'] == 'error':
                recommendations.append(f"{component_name} 發生錯誤，請查看日誌了解詳細資訊")
        
        if not recommendations:
            recommendations.append("所有組件運作正常，建議定期進行健康檢查")
        
        return recommendations


class TestRunner:
    """測試執行器"""
    
    def __init__(self):
        self.health_checker = SystemHealthChecker()
        self.test_results = []
    
    def run_comprehensive_tests(self) -> Dict:
        """
        執行全面測試
        
        Returns:
            測試報告
        """
        logger.info("開始執行全面測試...")
        
        # 1. 系統健康檢查
        health_report = self.health_checker.check_all_components()
        
        # 2. Prompt測試
        prompt_tester = PromptTester()
        prompt_results = prompt_tester.run_tests()
        prompt_summary = prompt_tester.generate_summary(prompt_results)
        
        # 3. 安全性測試
        security_tests = self.run_security_tests()
        
        # 4. 性能測試
        performance_tests = self.run_performance_tests()
        
        # 生成綜合報告
        comprehensive_report = {
            'test_timestamp': datetime.now().isoformat(),
            'health_check': health_report,
            'prompt_tests': prompt_summary,
            'security_tests': security_tests,
            'performance_tests': performance_tests,
            'overall_assessment': self._assess_overall_health(
                health_report, prompt_summary, security_tests, performance_tests
            )
        }
        
        return comprehensive_report
    
    def run_security_tests(self) -> Dict:
        """執行安全性測試"""
        try:
            # 測試PHI保護
            anonymizer = PHIAnonymizer()
            test_text = "我是王小明，電話0912345678，身份證A123456789"
            anonymized, entities = anonymizer.anonymize_text(test_text)
            
            phi_protection_score = 1.0 if len(entities) > 0 else 0.0
            
            # 測試加密功能
            hipaa_manager = HIPAAComplianceManager()
            test_data = "敏感測試資料"
            encrypted = hipaa_manager.encrypt_phi_data(test_data)
            decrypted = hipaa_manager.decrypt_phi_data(encrypted)
            
            encryption_score = 1.0 if decrypted == test_data else 0.0
            
            # 測試存取控制
            access_granted = hipaa_manager.validate_user_access(
                "test_user", "medical_record", "read"
            )
            
            access_control_score = 1.0 if access_granted else 0.0
            
            overall_security_score = (phi_protection_score + encryption_score + access_control_score) / 3
            
            return {
                'overall_score': overall_security_score,
                'phi_protection': {
                    'score': phi_protection_score,
                    'entities_detected': len(entities)
                },
                'encryption': {
                    'score': encryption_score,
                    'encryption_enabled': hipaa_manager.hipaa_settings['encryption_enabled']
                },
                'access_control': {
                    'score': access_control_score,
                    'access_control_enabled': hipaa_manager.hipaa_settings['access_control_enabled']
                }
            }
            
        except Exception as e:
            return {
                'overall_score': 0.0,
                'error': f"安全性測試失敗: {str(e)}"
            }
    
    def run_performance_tests(self) -> Dict:
        """執行性能測試"""
        try:
            processor = MediNoteProcessor()
            
            # 測試回應時間
            test_messages = [
                "我今天感覺還可以",
                "我的胸口有點痛",
                "忘記吃藥怎麼辦？",
                "什麼時候要回診？"
            ]
            
            response_times = []
            for message in test_messages:
                start_time = time.time()
                response = processor.process_message(message)
                response_time = time.time() - start_time
                response_times.append(response_time)
            
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            min_response_time = min(response_times)
            
            # 評分（目標：平均回應時間 < 1秒）
            response_time_score = max(0, 1 - (avg_response_time - 0.5))
            
            return {
                'overall_score': response_time_score,
                'response_times': {
                    'average_seconds': avg_response_time,
                    'max_seconds': max_response_time,
                    'min_seconds': min_response_time
                },
                'target_performance': {
                    'target_avg_response_time': 0.5,
                    'actual_avg_response_time': avg_response_time
                }
            }
            
        except Exception as e:
            return {
                'overall_score': 0.0,
                'error': f"性能測試失敗: {str(e)}"
            }
    
    def _assess_overall_health(self, health_report, prompt_summary, security_tests, performance_tests) -> str:
        """評估整體健康狀態"""
        scores = []
        
        # 健康檢查評分
        if health_report['overall_status'] == 'healthy':
            scores.append(1.0)
        else:
            healthy_count = health_report['summary']['healthy_components']
            total_count = health_report['summary']['total_components']
            scores.append(healthy_count / total_count if total_count > 0 else 0.0)
        
        # Prompt測試評分
        if 'pass_rate' in prompt_summary:
            scores.append(prompt_summary['pass_rate'])
        else:
            scores.append(0.0)
        
        # 安全性評分
        if 'overall_score' in security_tests:
            scores.append(security_tests['overall_score'])
        else:
            scores.append(0.0)
        
        # 性能評分
        if 'overall_score' in performance_tests:
            scores.append(performance_tests['overall_score'])
        else:
            scores.append(0.0)
        
        overall_score = sum(scores) / len(scores) if scores else 0.0
        
        if overall_score >= 0.8:
            return 'excellent'
        elif overall_score >= 0.6:
            return 'good'
        elif overall_score >= 0.4:
            return 'fair'
        else:
            return 'poor'


# 單元測試
class TestMediNoteComponents(unittest.TestCase):
    """MediNote組件單元測試"""
    
    def setUp(self):
        """測試前置設定"""
        self.medinote_processor = MediNoteProcessor()
        self.phi_anonymizer = PHIAnonymizer()
        self.hipaa_manager = HIPAAComplianceManager()
        self.elderly_interface = ElderlyInterface()
    
    def test_phi_anonymization(self):
        """測試PHI去識別化"""
        test_text = "我是王小明，電話0912345678"
        anonymized_text, entities = self.phi_anonymizer.anonymize_text(test_text)
        
        self.assertIsInstance(entities, list)
        self.assertIn('[PHONE_', anonymized_text)
    
    def test_hipaa_encryption(self):
        """測試HIPAA加密"""
        test_data = "測試資料"
        encrypted = self.hipaa_manager.encrypt_phi_data(test_data)
        decrypted = self.hipaa_manager.decrypt_phi_data(encrypted)
        
        self.assertEqual(decrypted, test_data)
    
    def test_medinote_processing(self):
        """測試對話處理"""
        test_message = "我今天感覺還可以"
        response = self.medinote_processor.process_message(test_message)
        
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)
    
    def test_elderly_interface_settings(self):
        """測試老年人介面設定"""
        settings = self.elderly_interface.get_interface_settings()
        
        self.assertIn('display', settings)
        self.assertIn('features', settings)
        self.assertIn('emergency_contacts', settings)
    
    def test_emergency_assessment(self):
        """測試緊急程度評估"""
        emergency_message = "我的胸口很痛，呼吸困難"
        emergency_level = self.medinote_processor.assess_emergency_level(emergency_message, "")
        
        self.assertGreater(emergency_level, 0.5)


if __name__ == '__main__':
    # 設定日誌
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 執行健康檢查
    print("🔍 執行系統健康檢查...")
    health_checker = SystemHealthChecker()
    health_report = health_checker.check_all_components()
    
    print("\n📊 健康檢查報告:")
    print(json.dumps(health_report, ensure_ascii=False, indent=2))
    
    # 執行全面測試
    print("\n🧪 執行全面測試...")
    test_runner = TestRunner()
    comprehensive_report = test_runner.run_comprehensive_tests()
    
    print("\n📋 綜合測試報告:")
    print(json.dumps(comprehensive_report, ensure_ascii=False, indent=2))
    
    # 執行單元測試
    print("\n🔬 執行單元測試...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    print("\n✅ 所有測試完成！")