"""
Prompt測試框架
專門針對老年人醫療對話的測試情境
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import hashlib
import time

logger = logging.getLogger(__name__)

@dataclass
class PromptTestCase:
    """Prompt測試案例"""
    test_id: str
    category: str
    description: str
    user_input: str
    expected_intent: str
    expected_emergency_level: float
    context: Dict[str, Any]
    user_profile: Dict[str, Any]
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class TestResult:
    """測試結果"""
    test_id: str
    category: str
    passed: bool
    actual_intent: str
    actual_emergency_level: float
    ai_response: str
    response_time: float
    timestamp: str
    error: Optional[str] = None

class PromptTester:
    """
    Prompt測試框架
    專門測試老年人醫療對話的各種情境
    """
    
    def __init__(self):
        self.test_cases = []
        self.test_results = []
        self.load_test_cases()
        logger.info("Prompt測試框架初始化完成")
    
    def load_test_cases(self):
        """載入測試案例"""
        self.test_cases = [
            # 緊急情況測試
            PromptTestCase(
                test_id="EMG_001",
                category="emergency",
                description="胸痛和呼吸困難 - 心臟病發作警訊",
                user_input="我的胸口好痛，呼吸困難，感覺快死了",
                expected_intent="emergency",
                expected_emergency_level=0.95,
                context={"user_id": "elderly_001", "session_id": "test_session"},
                user_profile={"age": 75, "medical_conditions": ["heart_disease", "hypertension"]}
            ),
            
            PromptTestCase(
                test_id="EMG_002",
                category="emergency",
                description="跌倒受傷",
                user_input="我剛剛跌倒撞到頭，現在頭很暈，有點想吐",
                expected_intent="emergency",
                expected_emergency_level=0.85,
                context={"user_id": "elderly_002", "session_id": "test_session"},
                user_profile={"age": 82, "medical_conditions": ["osteoporosis"]}
            ),
            
            PromptTestCase(
                test_id="EMG_003",
                category="emergency",
                description="低血糖昏迷",
                user_input="我糖尿病，現在頭暈冒冷汗，手在發抖",
                expected_intent="emergency",
                expected_emergency_level=0.8,
                context={"user_id": "elderly_003", "session_id": "test_session"},
                user_profile={"age": 78, "medical_conditions": ["diabetes"]}
            ),
            
            # 疼痛報告測試
            PromptTestCase(
                test_id="PNR_001",
                category="pain_report",
                description="關節疼痛（關節炎）",
                user_input="我的膝蓋很痛，走路很困難，特別是早上起床的時候",
                expected_intent="pain_report",
                expected_emergency_level=0.3,
                context={"user_id": "elderly_004", "session_id": "test_session"},
                user_profile={"age": 76, "medical_conditions": ["arthritis"]}
            ),
            
            PromptTestCase(
                test_id="PNR_002",
                category="pain_report",
                description="頭痛（高血壓）",
                user_input="今天頭很痛，後腦勺脹脹的，血壓好像比較高",
                expected_intent="pain_report",
                expected_emergency_level=0.4,
                context={"user_id": "elderly_005", "session_id": "test_session"},
                user_profile={"age": 73, "medical_conditions": ["hypertension"]}
            ),
            
            # 藥物相關測試
            PromptTestCase(
                test_id="MED_001",
                category="medication",
                description="忘記吃藥",
                user_input="我剛剛忘記吃降血糖的藥，現在要補吃嗎？",
                expected_intent="medication",
                expected_emergency_level=0.2,
                context={"user_id": "elderly_006", "session_id": "test_session"},
                user_profile={"age": 80, "medical_conditions": ["diabetes"], "current_medications": ["metformin"]}
            ),
            
            PromptTestCase(
                test_id="MED_002",
                category="medication",
                description="藥物副作用",
                user_input="吃了降血壓藥後一直咳嗽，是正常的嗎？",
                expected_intent="medication",
                expected_emergency_level=0.3,
                context={"user_id": "elderly_007", "session_id": "test_session"},
                user_profile={"age": 77, "medical_conditions": ["hypertension"], "current_medications": ["lisinopril"]}
            ),
            
            PromptTestCase(
                test_id="MED_003",
                category="medication",
                description="多種藥物交互作用",
                user_input="我現在有吃心臟病、高血壓、糖尿病的藥，可以一起吃嗎？",
                expected_intent="medication",
                expected_emergency_level=0.2,
                context={"user_id": "elderly_008", "session_id": "test_session"},
                user_profile={"age": 79, "medical_conditions": ["heart_disease", "hypertension", "diabetes"]}
            ),
            
            # 預約相關測試
            PromptTestCase(
                test_id="APT_001",
                category="appointment",
                description="忘記回診時間",
                user_input="我什麼時候要回診？忘記了",
                expected_intent="appointment",
                expected_emergency_level=0.1,
                context={"user_id": "elderly_009", "session_id": "test_session"},
                user_profile={"age": 81, "medical_conditions": ["diabetes", "hypertension"]}
            ),
            
            PromptTestCase(
                test_id="APT_002",
                category="appointment",
                description="準備看診",
                user_input="明天要去看診，需要準備什麼嗎？",
                expected_intent="appointment",
                expected_emergency_level=0.1,
                context={"user_id": "elderly_010", "session_id": "test_session"},
                user_profile={"age": 75, "medical_conditions": ["heart_disease"]}
            ),
            
            # 健康諮詢測試
            PromptTestCase(
                test_id="HLI_001",
                category="health_inquiry",
                description="飲食建議（糖尿病）",
                user_input="糖尿病可以吃什麼水果？",
                expected_intent="health_inquiry",
                expected_emergency_level=0.1,
                context={"user_id": "elderly_011", "session_id": "test_session"},
                user_profile={"age": 76, "medical_conditions": ["diabetes"]}
            ),
            
            PromptTestCase(
                test_id="HLI_002",
                category="health_inquiry",
                description="運動建議（心臟病）",
                user_input="有心臟病可以做什麼運動嗎？",
                expected_intent="health_inquiry",
                expected_emergency_level=0.1,
                context={"user_id": "elderly_012", "session_id": "test_session"},
                user_profile={"age": 78, "medical_conditions": ["heart_disease"]}
            ),
            
            PromptTestCase(
                test_id="HLI_003",
                category="health_inquiry",
                description="血壓監測",
                user_input="我的血壓140/90算高嗎？",
                expected_intent="health_inquiry",
                expected_emergency_level=0.2,
                context={"user_id": "elderly_013", "session_id": "test_session"},
                user_profile={"age": 74, "medical_conditions": ["hypertension"]}
            ),
            
            # 一般對話測試
            PromptTestCase(
                test_id="GEN_001",
                category="general_conversation",
                description="日常問候",
                user_input="早安，今天天氣不錯",
                expected_intent="general_conversation",
                expected_emergency_level=0.0,
                context={"user_id": "elderly_014", "session_id": "test_session"},
                user_profile={"age": 83, "medical_conditions": []}
            ),
            
            PromptTestCase(
                test_id="GEN_002",
                category="general_conversation",
                description="感謝回應",
                user_input="謝謝你的幫忙，我很感激",
                expected_intent="general_conversation",
                expected_emergency_level=0.0,
                context={"user_id": "elderly_015", "session_id": "test_session"},
                user_profile={"age": 80, "medical_conditions": ["arthritis"]}
            ),
            
            # PHI測試（包含個人資訊）
            PromptTestCase(
                test_id="PHI_001",
                category="phi_test",
                description="包含個人資訊的緊急情況",
                user_input="我是王小明，住在台北市大安區，電話是0912345678，現在胸口很痛",
                expected_intent="emergency",
                expected_emergency_level=0.9,
                context={"user_id": "elderly_016", "session_id": "test_session"},
                user_profile={"age": 77, "medical_conditions": ["heart_disease"]}
            ),
            
            PromptTestCase(
                test_id="PHI_002",
                category="phi_test",
                description="包含病歷號碼",
                user_input="我的病歷號是123456789，身份證字號A123456789，想查詢檢查報告",
                expected_intent="health_inquiry",
                expected_emergency_level=0.1,
                context={"user_id": "elderly_017", "session_id": "test_session"},
                user_profile={"age": 79, "medical_conditions": []}
            ),
            
            # 語音輸入測試
            PromptTestCase(
                test_id="VOI_001",
                category="voice_test",
                description="語音輸入 - 血糖問題",
                user_input="我的血糖今天量起來300，這樣正常嗎？",
                expected_intent="health_inquiry",
                expected_emergency_level=0.7,
                context={"user_id": "elderly_018", "session_id": "test_session", "input_method": "voice"},
                user_profile={"age": 76, "medical_conditions": ["diabetes"]}
            ),
            
            # 夜間緊急測試
            PromptTestCase(
                test_id="NTE_001",
                category="night_emergency",
                description="夜間緊急情況",
                user_input="凌晨三點，我突然呼吸困難，很害怕",
                expected_intent="emergency",
                expected_emergency_level=0.85,
                context={"user_id": "elderly_019", "session_id": "test_session", "time": "03:00"},
                user_profile={"age": 82, "medical_conditions": ["heart_disease", "hypertension"]}
            )
        ]
        
        logger.info(f"已載入 {len(self.test_cases)} 個測試案例")
    
    def run_tests(self, test_scenarios: Optional[List[str]] = None) -> List[TestResult]:
        """
        執行測試
        
        Args:
            test_scenarios: 要測試的情境類別，如果為None則測試所有
            
        Returns:
            測試結果列表
        """
        self.test_results = []
        
        # 篩選要測試的案例
        if test_scenarios:
            test_cases_to_run = [tc for tc in self.test_cases if tc.category in test_scenarios]
        else:
            test_cases_to_run = self.test_cases
        
        logger.info(f"開始執行 {len(test_cases_to_run)} 個測試案例")
        
        for test_case in test_cases_to_run:
            try:
                result = self._run_single_test(test_case)
                self.test_results.append(result)
                logger.info(f"測試 {test_case.test_id}: {'通過' if result.passed else '失敗'}")
                
                # 避免過快執行
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"測試 {test_case.test_id} 執行失敗: {e}")
                error_result = TestResult(
                    test_id=test_case.test_id,
                    category=test_case.category,
                    passed=False,
                    actual_intent="error",
                    actual_emergency_level=0.0,
                    ai_response="",
                    response_time=0.0,
                    timestamp=datetime.now().isoformat(),
                    error=str(e)
                )
                self.test_results.append(error_result)
        
        logger.info(f"測試完成，通過率: {self._calculate_pass_rate():.1%}")
        return self.test_results
    
    def _run_single_test(self, test_case: PromptTestCase) -> TestResult:
        """執行單個測試案例"""
        start_time = time.time()
        
        try:
            # 模擬AI處理（實際應該調用真正的AI處理器）
            # 這裡使用簡單的模擬邏輯
            
            # 模擬意圖識別
            actual_intent = self._simulate_intent_recognition(test_case.user_input)
            
            # 模擬緊急程度評估
            actual_emergency_level = self._simulate_emergency_assessment(test_case.user_input)
            
            # 模擬AI回應生成
            ai_response = self._simulate_ai_response(
                test_case.user_input, actual_intent, actual_emergency_level
            )
            
            # 檢查測試是否通過
            passed = self._check_test_pass(
                test_case, actual_intent, actual_emergency_level
            )
            
            response_time = time.time() - start_time
            
            return TestResult(
                test_id=test_case.test_id,
                category=test_case.category,
                passed=passed,
                actual_intent=actual_intent,
                actual_emergency_level=actual_emergency_level,
                ai_response=ai_response,
                response_time=response_time,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            return TestResult(
                test_id=test_case.test_id,
                category=test_case.category,
                passed=False,
                actual_intent="error",
                actual_emergency_level=0.0,
                ai_response="",
                response_time=response_time,
                timestamp=datetime.now().isoformat(),
                error=str(e)
            )
    
    def _simulate_intent_recognition(self, user_input: str) -> str:
        """模擬意圖識別"""
        user_input_lower = user_input.lower()
        
        # 基於關鍵詞的簡單意圖識別
        if any(word in user_input_lower for word in ['痛', '痛', '不舒服', '難受', '救命', '快死了', '喘不過氣', '胸痛', '暈倒', '昏迷']):
            return "emergency"
        elif any(word in user_input_lower for word in ['痛', '疼痛', '痠痛', '刺痛', '抽痛']):
            return "pain_report"
        elif any(word in user_input_lower for word in ['藥', '吃藥', '用藥', '劑量', '副作用', '忘記吃藥']):
            return "medication"
        elif any(word in user_input_lower for word in ['回診', '預約', '看診', '門診', '複診']):
            return "appointment"
        elif any(word in user_input_lower for word in ['健康', '身體', '感覺', '症狀', '血壓', '血糖', '運動', '飲食']):
            return "health_inquiry"
        else:
            return "general_conversation"
    
    def _simulate_emergency_assessment(self, user_input: str) -> float:
        """模擬緊急程度評估"""
        user_input_lower = user_input.lower()
        
        # 高風險關鍵詞
        high_risk_words = ['救命', '快死了', '喘不過氣', '胸痛', '暈倒', '昏迷', '大出血']
        
        # 中風險關鍵詞
        medium_risk_words = ['頭暈', '頭痛', '心悸', '高燒', '昏厥', '抽搐', '劇烈']
        
        # 低風險關鍵詞
        low_risk_words = ['輕微', '小', '有點', '還好', '普通']
        
        emergency_score = 0.0
        
        for word in high_risk_words:
            if word in user_input_lower:
                emergency_score = max(emergency_score, 0.8)
        
        for word in medium_risk_words:
            if word in user_input_lower:
                emergency_score = max(emergency_score, 0.5)
        
        for word in low_risk_words:
            if word in user_input_lower:
                emergency_score = max(emergency_score, 0.2)
        
        return min(emergency_score, 1.0)
    
    def _simulate_ai_response(self, user_input: str, intent: str, emergency_level: float) -> str:
        """模擬AI回應生成"""
        if intent == "emergency":
            if emergency_level > 0.7:
                return "⚠️ **緊急警告** ⚠️\n\n根據您的描述，這可能是緊急醫療情況。\n\n**請立即採取行動：**\n1. 撥打119叫救護車\n2. 聯繫您的家人或照顧者\n3. 如果可能的話，讓身邊的人幫助您\n\n**不要獨自等待，立即尋求幫助！**"
            else:
                return "我注意到您提到一些令人擔心的症狀。\n\n**建議：**\n- 請盡快聯繫您的家庭醫師\n- 如果症狀持續或惡化，請立即就醫\n- 保持冷靜，避免劇烈活動\n\n需要我幫您聯繫家人嗎？"
        
        elif intent == "pain_report":
            return "感謝您告訴我您的疼痛情況。\n\n**疼痛分析：**\n- 位置：待確認\n- 性質：待確認\n\n**建議：**\n- 記錄疼痛的時間和程度\n- 如果疼痛加劇或持續，請聯繫醫師\n- 避免劇烈活動，保持休息"
        
        elif intent == "medication":
            return "**用藥安全提醒：**\n\n- 按時服藥，不要忘記或重複服用\n- 如果忘記服藥，不要一次吃兩倍劑量\n- 有任何副作用，請立即聯繫醫師\n- 定期檢查藥物存量，及時領藥\n\n需要我幫您設定用藥提醒嗎？"
        
        elif intent == "appointment":
            return "**預約提醒：**\n\n下次回診：請查看您的預約卡或聯繫診所確認\n\n**看診準備：**\n- 攜帶健保卡和身份證\n- 準備要問醫師的問題清單\n- 記錄最近的症狀和血壓/血糖值\n- 攜帶目前服用的所有藥物\n\n**提醒：**\n如果需要更改預約時間，請提前1-2天聯繫診所。"
        
        elif intent == "health_inquiry":
            return "**健康建議：**\n\n規律作息、均衡飲食、適度運動、定期體檢\n\n**提醒：**\n如有具體症狀或疑問，請諮詢您的家庭醫師。"
        
        else:
            return "謝謝您的訊息。我是您的醫療助手，隨時準備為您提供幫助。\n\n**我可以協助您：**\n- 回答健康相關問題\n- 提供用藥提醒和資訊\n- 協助處理緊急情況\n- 記錄健康數據\n\n請告訴我您今天感覺如何？"
    
    def _check_test_pass(self, test_case: PromptTestCase, actual_intent: str, 
                        actual_emergency_level: float) -> bool:
        """檢查測試是否通過"""
        # 檢查意圖是否匹配
        intent_match = actual_intent == test_case.expected_intent
        
        # 檢查緊急程度是否在合理範圍內（±0.2）
        emergency_match = abs(actual_emergency_level - test_case.expected_emergency_level) <= 0.2
        
        return intent_match and emergency_match
    
    def _calculate_pass_rate(self) -> float:
        """計算通過率"""
        if not self.test_results:
            return 0.0
        
        passed_tests = sum(1 for result in self.test_results if result.passed)
        return passed_tests / len(self.test_results)
    
    def generate_summary(self, results: List[TestResult]) -> Dict:
        """
        生成測試摘要
        
        Args:
            results: 測試結果列表
            
        Returns:
            測試摘要報告
        """
        if not results:
            return {'error': '沒有測試結果可供分析'}
        
        total_tests = len(results)
        passed_tests = sum(1 for result in results if result.passed)
        failed_tests = total_tests - passed_tests
        pass_rate = passed_tests / total_tests if total_tests > 0 else 0
        
        # 按類別分組
        category_stats = {}
        for result in results:
            category = result.category
            if category not in category_stats:
                category_stats[category] = {'total': 0, 'passed': 0, 'failed': 0}
            
            category_stats[category]['total'] += 1
            if result.passed:
                category_stats[category]['passed'] += 1
            else:
                category_stats[category]['failed'] += 1
        
        # 計算平均回應時間
        avg_response_time = sum(result.response_time for result in results) / total_tests if total_tests > 0 else 0
        
        # 找出失敗的測試
        failed_test_details = [
            {
                'test_id': result.test_id,
                'category': result.category,
                'error': result.error or '測試未通過'
            }
            for result in results if not result.passed
        ]
        
        summary = {
            'test_summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': failed_tests,
                'pass_rate': pass_rate,
                'test_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            'category_breakdown': category_stats,
            'performance_metrics': {
                'average_response_time': avg_response_time,
                'max_response_time': max(result.response_time for result in results) if results else 0,
                'min_response_time': min(result.response_time for result in results) if results else 0
            },
            'failed_tests': failed_test_details,
            'recommendations': self._generate_recommendations(results)
        }
        
        return summary
    
    def _generate_recommendations(self, results: List[TestResult]) -> List[str]:
        """生成改進建議"""
        recommendations = []
        
        if not results:
            return recommendations
        
        # 分析失敗原因
        failed_results = [r for r in results if not r.passed]
        
        if failed_results:
            # 意圖識別失敗
            intent_failures = sum(1 for r in failed_results if r.actual_intent != "error")
            if intent_failures > len(failed_results) * 0.5:
                recommendations.append("建議改進意圖識別演算法，特別是區分緊急和非緊急情況")
            
            # 緊急程度評估失敗
            emergency_failures = sum(1 for r in failed_results if abs(r.actual_emergency_level - 0.5) > 0.3)
            if emergency_failures > len(failed_results) * 0.3:
                recommendations.append("建議調整緊急程度評估的敏感度")
            
            # 回應時間過長
            slow_responses = sum(1 for r in results if r.response_time > 2.0)
            if slow_responses > len(results) * 0.1:
                recommendations.append("建議優化回應速度，特別是緊急情況下的回應時間")
        
        # 一般性建議
        category_coverage = set(result.category for result in results)
        if len(category_coverage) < 5:
            recommendations.append("建議增加更多測試情境，涵蓋更廣泛的使用者情況")
        
        if not recommendations:
            recommendations.append("系統表現良好，建議定期進行測試以確保穩定性")
        
        return recommendations
    
    def export_test_report(self, results: List[TestResult], filename: str = None) -> str:
        """
        匯出測試報告
        
        Args:
            results: 測試結果列表
            filename: 輸出檔案名稱
            
        Returns:
            報告檔案路徑
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"prompt_test_report_{timestamp}.json"
        
        try:
            report_data = {
                'summary': self.generate_summary(results),
                'detailed_results': [
                    {
                        'test_id': result.test_id,
                        'category': result.category,
                        'passed': result.passed,
                        'expected_intent': next(tc.expected_intent for tc in self.test_cases if tc.test_id == result.test_id),
                        'actual_intent': result.actual_intent,
                        'expected_emergency_level': next(tc.expected_emergency_level for tc in self.test_cases if tc.test_id == result.test_id),
                        'actual_emergency_level': result.actual_emergency_level,
                        'ai_response': result.ai_response,
                        'response_time': result.response_time,
                        'timestamp': result.timestamp,
                        'error': result.error
                    }
                    for result in results
                ]
            }
            
            # 確保輸出目錄存在
            output_dir = "tests/reports"
            os.makedirs(output_dir, exist_ok=True)
            
            filepath = os.path.join(output_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"測試報告已匯出至: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"匯出測試報告失敗: {e}")
            raise


# 使用示例
if __name__ == '__main__':
    # 創建測試器
    tester = PromptTester()
    
    # 執行測試
    print("開始執行Prompt測試...")
    results = tester.run_tests()
    
    # 生成摘要
    summary = tester.generate_summary(results)
    print("\n測試摘要:")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    
    # 匯出報告
    report_path = tester.export_test_report(results)
    print(f"\n測試報告已匯出至: {report_path}")
    
    print(f"\n測試完成！通過率: {tester._calculate_pass_rate():.1%}")