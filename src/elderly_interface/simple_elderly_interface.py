"""
簡化老年人友善介面模組
移除語音依賴，專注於核心功能
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import requests

logger = logging.getLogger(__name__)

class SimpleElderlyInterface:
    """
    簡化老年人友善介面管理器
    專注於核心功能，移除語音等複雜功能
    """
    
    def __init__(self):
        # Rocket.Chat 設定
        self.rocket_chat_url = os.environ.get('ROCKET_CHAT_URL', 'https://demo.rocket.chat')
        self.rocket_chat_admin_user = os.environ.get('ROCKET_CHAT_ADMIN_USER', 'admin')
        self.rocket_chat_admin_password = os.environ.get('ROCKET_CHAT_ADMIN_PASSWORD', 'admin')
        self.rocket_chat_api_token = os.environ.get('ROCKET_CHAT_API_TOKEN')
        
        # 介面設定
        self.interface_settings = {
            'font_size': int(os.environ.get('ELDERLY_FONT_SIZE', '18')),
            'high_contrast': os.environ.get('ELDERLY_HIGH_CONTRAST', 'true').lower() == 'true',
            'voice_enabled': False,  # 簡化版本停用語音功能
            'large_buttons': os.environ.get('ELDERLY_LARGE_BUTTONS', 'true').lower() == 'true',
            'simplified_interface': os.environ.get('ELDERLY_SIMPLIFIED_INTERFACE', 'true').lower() == 'true',
            'emergency_hotkeys': os.environ.get('ELDERLY_EMERGENCY_HOTKEYS', 'true').lower() == 'true'
        }
        
        # 緊急聯絡人設定
        self.emergency_contacts = self._load_emergency_contacts()
        
        logger.info("簡化老年人友善介面初始化完成")
    
    def _load_emergency_contacts(self) -> List[Dict]:
        """載入緊急聯絡人"""
        return [
            {
                'name': '家庭醫師',
                'phone': '+886-2-1234-5678',
                'type': 'doctor',
                'priority': 1
            },
            {
                'name': '家人',
                'phone': '+886-900-000-000',
                'type': 'family',
                'priority': 2
            }
        ]
    
    def get_interface_settings(self) -> Dict:
        """
        獲取介面設定
        
        Returns:
            介面設定字典
        """
        return {
            'display': {
                'font_size': self.interface_settings['font_size'],
                'high_contrast': self.interface_settings['high_contrast'],
                'large_buttons': self.interface_settings['large_buttons'],
                'simplified_interface': self.interface_settings['simplified_interface']
            },
            'features': {
                'voice_input': self.interface_settings['voice_enabled'],
                'voice_output': self.interface_settings['voice_enabled'],
                'emergency_hotkeys': self.interface_settings['emergency_hotkeys']
            },
            'emergency_contacts': self.emergency_contacts
        }
    
    def emergency_contact(self, user_id: str, emergency_type: str, location: Dict) -> Dict:
        """
        緊急聯繫功能
        
        Args:
            user_id: 使用者ID
            emergency_type: 緊急類型
            location: 位置資訊
            
        Returns:
            聯繫結果
        """
        try:
            # 建立緊急訊息
            emergency_message = self._create_emergency_message(user_id, emergency_type, location)
            
            # 模擬發送緊急通知
            notification_results = []
            
            for contact in self.emergency_contacts:
                result = self._send_emergency_notification(contact, emergency_message)
                notification_results.append({
                    'contact': contact['name'],
                    'type': contact['type'],
                    'status': result['status'],
                    'timestamp': datetime.now().isoformat()
                })
            
            # 記錄緊急事件
            self._log_emergency_event(user_id, emergency_type, location, notification_results)
            
            return {
                'success': True,
                'message': '緊急聯繫已發送',
                'notifications_sent': len([r for r in notification_results if r['status'] == 'success']),
                'details': notification_results,
                'next_steps': [
                    '保持冷靜，等待回應',
                    '如果情況危急，請直接撥打119',
                    '確保門戶容易進入'
                ]
            }
            
        except Exception as e:
            logger.error(f"緊急聯繫失敗: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': '緊急聯繫功能暫時無法使用，請直接撥打119'
            }
    
    def _create_emergency_message(self, user_id: str, emergency_type: str, location: Dict) -> str:
        """建立緊急訊息"""
        emergency_types = {
            'medical': '醫療緊急情況',
            'fall': '跌倒',
            'heart_problem': '心臟問題',
            'breathing': '呼吸困難',
            'general': '緊急情況'
        }
        
        emergency_desc = emergency_types.get(emergency_type, '緊急情況')
        
        message = f"""
        🚨 **緊急通知** 🚨
        
        **使用者：** {user_id}
        **緊急類型：** {emergency_desc}
        **時間：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        if location:
            message += f"""
        **位置：**
        - 地址：{location.get('address', '未知')}
        - 座標：{location.get('coordinates', '未知')}
        """
        
        message += """
        
        **請立即採取行動：**
        1. 嘗試聯繫使用者確認情況
        2. 如果無法聯繫，考慮前往查看
        3. 必要時撥打119
        
        **系統已自動：**
        - 記錄事件時間和位置
        - 通知所有緊急聯絡人
        - 準備相關醫療資訊
        """
        
        return message
    
    def _send_emergency_notification(self, contact: Dict, message: str) -> Dict:
        """發送緊急通知"""
        try:
            # 模擬發送通知
            # 實際使用時，這裡應該整合真正的通知服務
            logger.info(f"發送緊急通知給 {contact['name']}: {contact['phone']}")
            
            return {
                'status': 'success',
                'method': 'simulated',
                'note': '實際環境中會發送簡訊或撥打電話'
            }
            
        except Exception as e:
            logger.error(f"發送緊急通知給 {contact['name']} 失敗: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'contact': contact['name']
            }
    
    def _log_emergency_event(self, user_id: str, emergency_type: str, 
                           location: Dict, notification_results: List[Dict]):
        """記錄緊急事件"""
        try:
            event_data = {
                'user_id': user_id,
                'emergency_type': emergency_type,
                'location': location,
                'timestamp': datetime.now().isoformat(),
                'notification_results': notification_results,
                'severity': 'high'
            }
            
            # 記錄到檔案
            log_file = 'logs/emergency_events.log'
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(event_data, ensure_ascii=False) + '\n')
            
            logger.info(f"緊急事件已記錄: {user_id} - {emergency_type}")
            
        except Exception as e:
            logger.error(f"記錄緊急事件失敗: {e}")
    
    def trigger_emergency_alert(self, user_id: str, message: str):
        """
        觸發緊急警報
        
        Args:
            user_id: 使用者ID
            message: 觸發警報的訊息
        """
        try:
            # 分析緊急程度
            emergency_level = self._analyze_emergency_level(message)
            
            if emergency_level > 0.7:
                # 高風險緊急情況
                self.emergency_contact(
                    user_id=user_id,
                    emergency_type='medical',
                    location={'address': '未知', 'coordinates': '未知'}
                )
                
                logger.warning(f"高風險緊急警報已觸發: {user_id}")
            
        except Exception as e:
            logger.error(f"觸發緊急警報失敗: {e}")
    
    def _analyze_emergency_level(self, message: str) -> float:
        """分析緊急程度"""
        emergency_keywords = [
            '救命', '快死了', '喘不過氣', '胸痛', '暈倒', '昏迷', '大出血',
            '心臟病', '中風', '呼吸困難', '昏厥'
        ]
        
        message_lower = message.lower()
        
        for keyword in emergency_keywords:
            if keyword in message_lower:
                return 0.9
        
        return 0.1
    
    def create_health_reminder(self, user_id: str, reminder_type: str, 
                               medication_name: str = None, time: str = None) -> str:
        """
        建立健康提醒
        
        Args:
            user_id: 使用者ID
            reminder_type: 提醒類型 (medication, appointment, checkup)
            medication_name: 藥物名稱（如果是用藥提醒）
            time: 提醒時間
            
        Returns:
            提醒訊息
        """
        if reminder_type == 'medication' and medication_name:
            reminder = f"""
            💊 **用藥提醒**
            
            時間：{time or '現在'}
            藥物：{medication_name}
            
            **用藥安全：**
            - 按時服用，不要忘記
            - 配白開水服用
            - 如有不適，立即聯繫醫師
            """
        
        elif reminder_type == 'appointment':
            reminder = f"""
            📅 **回診提醒**
            
            時間：{time or '即將到來'}
            
            **看診準備：**
            - 攜帶健保卡和身份證
            - 準備要問的問題
            - 記錄最近的症狀
            
            **注意：**
            如果需要取消，請提前聯繫診所
            """
        
        else:
            reminder = f"""
            📋 **健康提醒**
            
            時間：{time or '現在'}
            類型：{reminder_type}
            
            請按時完成相關的健康管理事項。
            如有疑問，請諮詢您的家庭醫師。
            """
        
        return reminder
    
    def is_healthy(self) -> bool:
        """檢查組件健康狀態"""
        try:
            # 測試基本功能
            settings = self.get_interface_settings()
            return len(settings) > 0
        except Exception as e:
            logger.error(f"老年人介面健康檢查失敗: {e}")
            return False


# 使用示例
if __name__ == '__main__':
    # 創建老年人介面
    elderly_interface = SimpleElderlyInterface()
    
    # 測試介面設定
    settings = elderly_interface.get_interface_settings()
    print("介面設定:")
    print(json.dumps(settings, indent=2, ensure_ascii=False))
    
    # 測試緊急聯繫
    result = elderly_interface.emergency_contact(
        user_id="test_user",
        emergency_type="medical",
        location={"address": "測試地址", "coordinates": "25.0330,121.5654"}
    )
    print("\n緊急聯繫結果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # 測試健康提醒
    reminder = elderly_interface.create_health_reminder(
        user_id="test_user",
        reminder_type="medication",
        medication_name="降血糖藥",
        time="早上8點"
    )
    print("\n健康提醒:")
    print(reminder)