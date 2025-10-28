"""
MediNote-AI 對話處理器
整合自然語言處理和醫療知識庫
"""

import os
import json
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class ConversationContext:
    """對話上下文"""
    user_id: str
    session_id: str
    previous_messages: List[Dict]
    user_profile: Dict
    emergency_contacts: List[str]
    medical_conditions: List[str]
    current_medications: List[str]

class MediNoteProcessor:
    """
    MediNote-AI 對話處理器
    專門處理老年人醫療對話的智慧AI系統
    """
    
    def __init__(self):
        self.model_version = os.environ.get('MEDINOTE_MODEL_VERSION', '1.0')
        self.confidence_threshold = float(os.environ.get('MEDINOTE_CONFIDENCE_THRESHOLD', '0.8'))
        self.max_context_length = int(os.environ.get('MEDINOTE_MAX_CONTEXT_LENGTH', '2000'))
        
        # 載入醫療知識庫
        self.medical_knowledge = self._load_medical_knowledge()
        self.emergency_keywords = self._load_emergency_keywords()
        self.medication_database = self._load_medication_database()
        
        # 老年人特定的語言模式
        self.elderly_patterns = {
            'pain_description': [
                '痛', '疼痛', '不舒服', '難受', '痠痛', '刺痛', '抽痛'
            ],
            'emergency_indicators': [
                '救命', '快死了', '喘不過氣', '胸痛', '暈倒', '昏迷', '大量出血'
            ],
            'medication_queries': [
                '藥', '吃藥', '用藥', '劑量', '副作用', '忘記吃藥'
            ],
            'appointment_related': [
                '回診', '預約', '看診', '門診', '複診'
            ]
        }
        
        logger.info(f"MediNote-AI 對話處理器 v{self.model_version} 初始化完成")
    
    def _load_medical_knowledge(self) -> Dict:
        """載入醫療知識庫"""
        # 這裡應該連接到真正的醫療知識庫
        # 現在返回模擬資料
        return {
            'common_conditions': {
                'diabetes': {
                    'name': '糖尿病',
                    'symptoms': ['口渴', '頻尿', '疲倦', '視力模糊'],
                    'diet_advice': '控制糖分攝取，多吃蔬菜，適度運動',
                    'emergency_signs': ['昏迷', '呼吸困難', '嚴重脫水']
                },
                'hypertension': {
                    'name': '高血壓',
                    'symptoms': ['頭暈', '頭痛', '心悸', '耳鳴'],
                    'diet_advice': '低鈉飲食，多吃蔬果，限制酒精',
                    'emergency_signs': ['劇烈頭痛', '胸痛', '呼吸困難', '意識模糊']
                },
                'heart_disease': {
                    'name': '心臟病',
                    'symptoms': ['胸痛', '呼吸困難', '心悸', '疲勞'],
                    'diet_advice': '低鹽低脂，多吃魚類，適度運動',
                    'emergency_signs': ['劇烈胸痛', '呼吸困難', '昏厥', '心跳異常']
                }
            },
            'general_advice': {
                'healthy_lifestyle': '規律作息、均衡飲食、適度運動、定期體檢',
                'medication_compliance': '按時服藥，不要自行調整劑量，有疑問諮詢醫師',
                'emergency_response': '出現緊急症狀立即就醫或撥打119'
            }
        }
    
    def _load_emergency_keywords(self) -> Dict:
        """載入緊急關鍵詞"""
        return {
            'high_priority': [
                '心臟病發作', '中風', '昏迷', '呼吸停止', '心跳停止',
                '大出血', '嚴重外傷', '服毒', '上吊', '溺水'
            ],
            'medium_priority': [
                '胸痛', '呼吸困難', '嚴重頭痛', '高燒', '昏厥',
                '抽搐', '劇烈腹痛', '嘔血', '便血', '意識模糊'
            ],
            'low_priority': [
                '輕微疼痛', '小傷口', '皮膚癢', '輕微發燒', '頭暈',
                '食慾不振', '失眠', '便秘', '腹瀉', '噁心'
            ]
        }
    
    def _load_medication_database(self) -> Dict:
        """載入藥物資料庫"""
        return {
            'common_medications': {
                'metformin': {
                    'name': '二甲雙胍',
                    'usage': '降血糖藥物',
                    'common_side_effects': ['胃腸不適', '腹瀉', '噁心'],
                    'contraindications': ['腎功能不全', '嚴重感染'],
                    'elderly_notes': '老年人需監測腎功能'
                },
                'lisinopril': {
                    'name': '賴諾普利',
                    'usage': '降血壓藥物',
                    'common_side_effects': ['乾咳', '頭暈', '高血鉀'],
                    'contraindications': ['懷孕', '血管水腫病史'],
                    'elderly_notes': '需監測血壓和腎功能'
                },
                'atorvastatin': {
                    'name': '阿托伐他汀',
                    'usage': '降血脂藥物',
                    'common_side_effects': ['肌肉疼痛', '肝功能異常'],
                    'contraindications': ['活動性肝病', '懷孕'],
                    'elderly_notes': '定期檢查肝功能和肌肉酵素'
                }
            }
        }
    
    def process_message(self, message: str, context: Optional[Dict] = None, 
                     user_profile: Optional[Dict] = None) -> str:
        """
        處理使用者訊息
        
        Args:
            message: 使用者訊息
            context: 對話上下文
            user_profile: 使用者檔案
            
        Returns:
            AI回應
        """
        try:
            logger.info(f"處理訊息: {message[:50]}...")
            
            # 建立對話上下文
            conversation_context = self._build_context(context, user_profile)
            
            # 分析訊息意圖
            intent, confidence = self._analyze_intent(message, conversation_context)
            
            # 根據意圖生成回應
            response = self._generate_response(message, intent, confidence, conversation_context)
            
            logger.info(f"意圖: {intent}, 信心: {confidence}")
            
            return response
            
        except Exception as e:
            logger.error(f"處理訊息失敗: {e}")
            return "抱歉，我現在無法處理您的訊息。請稍後再試，或聯繫醫護人員。"
    
    def _build_context(self, context_data: Optional[Dict], user_profile: Optional[Dict]) -> ConversationContext:
        """建立對話上下文"""
        return ConversationContext(
            user_id=context_data.get('user_id', 'unknown') if context_data else 'unknown',
            session_id=context_data.get('session_id', 'unknown') if context_data else 'unknown',
            previous_messages=context_data.get('previous_messages', []) if context_data else [],
            user_profile=user_profile or {},
            emergency_contacts=user_profile.get('emergency_contacts', []) if user_profile else [],
            medical_conditions=user_profile.get('medical_conditions', []) if user_profile else [],
            current_medications=user_profile.get('current_medications', []) if user_profile else []
        )
    
    def _analyze_intent(self, message: str, context: ConversationContext) -> Tuple[str, float]:
        """
        分析訊息意圖
        
        Returns:
            Tuple[意圖類型, 信心分數]
        """
        message_lower = message.lower()
        
        # 檢查緊急情況
        for keyword in self.elderly_patterns['emergency_indicators']:
            if keyword in message_lower:
                return 'emergency', 0.95
        
        # 檢查疼痛描述
        for keyword in self.elderly_patterns['pain_description']:
            if keyword in message_lower:
                return 'pain_report', 0.85
        
        # 檢查藥物相關
        for keyword in self.elderly_patterns['medication_queries']:
            if keyword in message_lower:
                return 'medication', 0.8
        
        # 檢查預約相關
        for keyword in self.elderly_patterns['appointment_related']:
            if keyword in message_lower:
                return 'appointment', 0.75
        
        # 一般健康諮詢
        if any(word in message_lower for word in ['健康', '身體', '感覺', '症狀']):
            return 'health_inquiry', 0.7
        
        # 預設為一般對話
        return 'general_conversation', 0.5
    
    def _generate_response(self, message: str, intent: str, confidence: float, 
                        context: ConversationContext) -> str:
        """根據意圖生成回應"""
        
        if confidence < self.confidence_threshold:
            return "我不是很確定您的意思。您可以再說明一下嗎？如果這是緊急情況，請立即聯繫醫護人員或撥打119。"
        
        response_generators = {
            'emergency': self._handle_emergency,
            'pain_report': self._handle_pain_report,
            'medication': self._handle_medication,
            'appointment': self._handle_appointment,
            'health_inquiry': self._handle_health_inquiry,
            'general_conversation': self._handle_general_conversation
        }
        
        generator = response_generators.get(intent, self._handle_general_conversation)
        return generator(message, context)
    
    def _handle_emergency(self, message: str, context: ConversationContext) -> str:
        """處理緊急情況"""
        emergency_level = self._assess_emergency_level(message)
        
        if emergency_level > 0.8:
            return """> ⚠️ **緊急警告** ⚠️
            
            根據您的描述，這可能是緊急醫療情況。
            
            **請立即採取行動：**
            1. 撥打119叫救護車
            2. 聯繫您的家人或照顧者
            3. 如果可能的話，讓身邊的人幫助您
            
            **不要獨自等待，立即尋求幫助！**
            """
        elif emergency_level > 0.6:
            return """> ⚠️ **注意** ⚠️
            
            您的症狀可能需要立即就醫。
            
            **建議：**
            1. 立即聯繫您的家庭醫師
            2. 前往最近的急診室
            3. 告知家人或朋友您的情況
            
            如果症狀惡化，請立即撥打119。
            """
        else:
            return """
            我注意到您提到一些令人擔心的症狀。
            
            **建議：**
            - 請盡快聯繫您的家庭醫師
            - 如果症狀持續或惡化，請立即就醫
            - 保持冷靜，避免劇烈活動
            
            需要我幫您聯繫家人嗎？
            """
    
    def _handle_pain_report(self, message: str, context: ConversationContext) -> str:
        """處理疼痛報告"""
        # 分析疼痛位置和性質
        pain_analysis = self._analyze_pain(message)
        
        response = f"""
        感謝您告訴我您的疼痛情況。
        
        **疼痛分析：**
        - 位置：{pain_analysis.get('location', '不明確')}
        - 性質：{pain_analysis.get('type', '待確認')}
        """
        
        # 檢查是否與現有疾病相關
        for condition in context.medical_conditions:
            if condition in ['diabetes', 'hypertension', 'heart_disease']:
                response += f"""
        
        **與您的{self.medical_knowledge['common_conditions'].get(condition, {}).get('name', '疾病')}相關：**
        {self.medical_knowledge['common_conditions'].get(condition, {}).get('emergency_signs', ['如症狀持續請就醫'])}
        """
        
        response += """
        
        **建議：**
        - 記錄疼痛的時間和程度
        - 如果疼痛加劇或持續，請聯繫醫師
        - 避免劇烈活動，保持休息
        """
        
        return response
    
    def _handle_medication(self, message: str, context: ConversationContext) -> str:
        """處理藥物相關查詢"""
        # 檢測藥物名稱
        medication_name = self._extract_medication_name(message)
        
        if medication_name:
            medication_info = self.medication_database['common_medications'].get(medication_name)
            if medication_info:
                return f"""
                **{medication_info['name']} 資訊：**
                
                用途：{medication_info['usage']}
                
                常見副作用：{', '.join(medication_info['common_side_effects'])}
                
                老年人注意事項：{medication_info['elderly_notes']}
                
                **重要提醒：**
                - 按時服藥，不要自行調整劑量
                - 如有副作用，請諮詢醫師
                - 定期追蹤檢查
                """
        
        # 一般藥物提醒
        return """
        **用藥安全提醒：**
        
        - 按時服藥，不要忘記或重複服用
        - 如果忘記服藥，不要一次吃兩倍劑量
        - 有任何副作用，請立即聯繫醫師
        - 定期檢查藥物存量，及時領藥
        
        需要我幫您設定用藥提醒嗎？
        """
    
    def _handle_appointment(self, message: str, context: ConversationContext) -> str:
        """處理預約相關查詢"""
        return """
        **預約提醒：**
        
        下次回診：請查看您的預約卡或聯繫診所確認
        
        **看診準備：**
        - 攜帶健保卡和身份證
        - 準備要問醫師的問題清單
        - 記錄最近的症狀和血壓/血糖值
        - 攜帶目前服用的所有藥物
        
        **提醒：**
        如果需要更改預約時間，請提前1-2天聯繫診所。
        """
    
    def _handle_health_inquiry(self, message: str, context: ConversationContext) -> str:
        """處理健康諮詢"""
        # 分析諮詢內容
        health_topic = self._analyze_health_topic(message)
        
        if health_topic in self.medical_knowledge['common_conditions']:
            condition_info = self.medical_knowledge['common_conditions'][health_topic]
            return f"""
            **{condition_info['name']} 相關資訊：**
            
            常見症狀：{', '.join(condition_info['symptoms'])}
            
            飲食建議：{condition_info['diet_advice']}
            
            **注意事項：**
            - 定期追蹤檢查
            - 按時服藥
            - 如有緊急症狀（{', '.join(condition_info['emergency_signs'])}），請立即就醫
            """
        
        # 一般健康建議
        return f"""
        **健康建議：**
        
        {self.medical_knowledge['general_advice']['healthy_lifestyle']}
        
        **提醒：**
        {self.medical_knowledge['general_advice']['emergency_response']}
        
        如有具體症狀或疑問，請諮詢您的家庭醫師。
        """
    
    def _handle_general_conversation(self, message: str, context: ConversationContext) -> str:
        """處理一般對話"""
        return """
        謝謝您的訊息。我是您的醫療助手，隨時準備為您提供幫助。
        
        **我可以協助您：**
        - 回答健康相關問題
        - 提供用藥提醒和資訊
        - 協助處理緊急情況
        - 記錄健康數據
        
        **請告訴我：**
        - 您今天感覺如何？
        - 有什麼需要特別注意的症狀嗎？
        - 需要我提醒您服藥嗎？
        
        我會確保您的所有資訊都安全保密。
        """
    
    def assess_emergency_level(self, user_message: str, ai_response: str) -> float:
        """
        評估緊急程度
        
        Returns:
            0-1之間的緊急程度分數
        """
        emergency_score = 0.0
        
        # 檢查用戶訊息中的緊急關鍵詞
        message_lower = user_message.lower()
        
        for keyword in self.emergency_keywords['high_priority']:
            if keyword in message_lower:
                emergency_score = max(emergency_score, 0.9)
        
        for keyword in self.emergency_keywords['medium_priority']:
            if keyword in message_lower:
                emergency_score = max(emergency_score, 0.6)
        
        for keyword in self.emergency_keywords['low_priority']:
            if keyword in message_lower:
                emergency_score = max(emergency_score, 0.3)
        
        # 檢查AI回應是否觸發緊急警告
        if '⚠️' in ai_response or '緊急' in ai_response:
            emergency_score = max(emergency_score, 0.8)
        
        return min(emergency_score, 1.0)
    
    def _assess_emergency_level(self, message: str) -> float:
        """內部評估緊急程度"""
        return self.assess_emergency_level(message, "")
    
    def _analyze_pain(self, message: str) -> Dict:
        """分析疼痛描述"""
        pain_location = "不明確"
        pain_type = "待確認"
        
        # 簡單的關鍵詞匹配
        if '頭' in message:
            pain_location = "頭部"
        elif '胸' in message:
            pain_location = "胸部"
        elif '腹' in message:
            pain_location = "腹部"
        elif '背' in message:
            pain_location = "背部"
        
        if '刺痛' in message:
            pain_type = "刺痛"
        elif '抽痛' in message:
            pain_type = "抽痛"
        elif '痠痛' in message:
            pain_type = "痠痛"
        
        return {'location': pain_location, 'type': pain_type}
    
    def _extract_medication_name(self, message: str) -> Optional[str]:
        """提取藥物名稱"""
        message_lower = message.lower()
        
        for med_key, med_info in self.medication_database['common_medications'].items():
            if med_info['name'] in message:
                return med_key
        
        return None
    
    def _analyze_health_topic(self, message: str) -> Optional[str]:
        """分析健康主題"""
        message_lower = message.lower()
        
        for condition_key, condition_info in self.medical_knowledge['common_conditions'].items():
            if condition_info['name'] in message:
                return condition_key
        
        return None
    
    def is_healthy(self) -> bool:
        """檢查組件健康狀態"""
        try:
            # 測試基本功能
            test_message = "我頭有點痛"
            response = self.process_message(test_message)
            return len(response) > 0
        except Exception as e:
            logger.error(f"MediNote-AI健康檢查失敗: {e}")
            return False


# 使用示例
if __name__ == '__main__':
    # 創建對話處理器
    processor = MediNoteProcessor()
    
    # 測試訊息
    test_messages = [
        "我的胸口很痛，呼吸困難",
        "忘記吃糖尿病的藥怎麼辦？",
        "今天感覺還可以，謝謝關心"
    ]
    
    for message in test_messages:
        print(f"用戶: {message}")
        response = processor.process_message(message)
        print(f"AI: {response}")
        print("-" * 50)