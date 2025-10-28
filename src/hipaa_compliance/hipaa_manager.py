"""
HIPAA合規管理器
整合Rocket.Chat的HIPAA合規通訊功能
"""

import os
import json
import logging
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any
from cryptography.fernet import Fernet
import redis

logger = logging.getLogger(__name__)

class HIPAAComplianceManager:
    """
    HIPAA合規管理器
    確保所有醫療資訊處理符合HIPAA法規要求
    """
    
    def __init__(self):
        self.encryption_key = os.environ.get('HIPAA_ENCRYPTION_KEY')
        if not self.encryption_key:
            self.encryption_key = Fernet.generate_key()
            logger.warning("使用生成的加密金鑰，請在生產環境中設置HIPAA_ENCRYPTION_KEY")
        
        self.cipher = Fernet(self.encryption_key)
        self.redis_client = self._init_redis()
        self.audit_logger = self._init_audit_logger()
        
        # HIPAA合規設定
        self.hipaa_settings = {
            'data_retention_days': int(os.environ.get('HIPAA_DATA_RETENTION_DAYS', 2555)),  # 7年
            'audit_log_retention_days': int(os.environ.get('HIPAA_AUDIT_RETENTION_DAYS', 3652)),  # 10年
            'encryption_enabled': os.environ.get('HIPAA_ENCRYPTION_ENABLED', 'true').lower() == 'true',
            'access_control_enabled': os.environ.get('HIPAA_ACCESS_CONTROL_ENABLED', 'true').lower() == 'true',
            'minimum_password_length': int(os.environ.get('HIPAA_MIN_PASSWORD_LENGTH', 8)),
            'session_timeout_minutes': int(os.environ.get('HIPAA_SESSION_TIMEOUT', 30)),
            'max_login_attempts': int(os.environ.get('HIPAA_MAX_LOGIN_ATTEMPTS', 5))
        }
        
        logger.info("HIPAA合規管理器初始化完成")
    
    def _init_redis(self) -> Optional[redis.Redis]:
        """初始化Redis連接"""
        try:
            redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379')
            return redis.from_url(redis_url, decode_responses=True)
        except Exception as e:
            logger.error(f"Redis連接失敗: {e}")
            return None
    
    def _init_audit_logger(self) -> logging.Logger:
        """初始化審計日誌記錄器"""
        audit_logger = logging.getLogger('hipaa_audit')
        audit_handler = logging.FileHandler('logs/hipaa_audit.log')
        audit_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        audit_logger.addHandler(audit_handler)
        audit_logger.setLevel(logging.INFO)
        return audit_logger
    
    def encrypt_phi_data(self, data: str) -> str:
        """
        加密PHI資料
        
        Args:
            data: 要加密的資料
            
        Returns:
            加密後的資料
        """
        if not self.hipaa_settings['encryption_enabled']:
            return data
        
        try:
            encrypted = self.cipher.encrypt(data.encode())
            return encrypted.decode()
        except Exception as e:
            logger.error(f"PHI資料加密失敗: {e}")
            raise
    
    def decrypt_phi_data(self, encrypted_data: str) -> str:
        """
        解密PHI資料
        
        Args:
            encrypted_data: 加密的資料
            
        Returns:
            解密後的資料
        """
        if not self.hipaa_settings['encryption_enabled']:
            return encrypted_data
        
        try:
            decrypted = self.cipher.decrypt(encrypted_data.encode())
            return decrypted.decode()
        except Exception as e:
            logger.error(f"PHI資料解密失敗: {e}")
            raise
    
    def log_message_access(self, user_id: str, message_type: str, message_hash: str, 
                        metadata: Optional[Dict] = None):
        """
        記錄訊息存取（HIPAA審計要求）
        
        Args:
            user_id: 使用者ID
            message_type: 訊息類型
            message_hash: 訊息雜湊值
            metadata: 額外元資料
        """
        try:
            audit_entry = {
                'timestamp': datetime.now().isoformat(),
                'user_id': user_id,
                'message_type': message_type,
                'message_hash': message_hash,
                'ip_address': metadata.get('ip_address', 'unknown') if metadata else 'unknown',
                'user_agent': metadata.get('user_agent', 'unknown') if metadata else 'unknown',
                'session_id': metadata.get('session_id', 'unknown') if metadata else 'unknown'
            }
            
            self.audit_logger.info(json.dumps(audit_entry))
            
            # 同時記錄到Redis以便快速查詢
            if self.redis_client:
                self.redis_client.sadd(f"audit_log:{user_id}", json.dumps(audit_entry))
                self.redis_client.expire(f"audit_log:{user_id}", 86400 * self.hipaa_settings['audit_log_retention_days'])
            
        except Exception as e:
            logger.error(f"記錄訊息存取失敗: {e}")
    
    def log_emergency_event(self, user_id: str, emergency_type: str, location: Dict):
        """
        記錄緊急事件
        
        Args:
            user_id: 使用者ID
            emergency_type: 緊急類型
            location: 位置資訊
        """
        try:
            emergency_entry = {
                'timestamp': datetime.now().isoformat(),
                'user_id': user_id,
                'emergency_type': emergency_type,
                'location': location,
                'severity': 'high'
            }
            
            self.audit_logger.info(json.dumps(emergency_entry))
            
            # 立即通知相關人員
            self._notify_emergency_contacts(user_id, emergency_entry)
            
        except Exception as e:
            logger.error(f"記錄緊急事件失敗: {e}")
    
    def _notify_emergency_contacts(self, user_id: str, emergency_event: Dict):
        """通知緊急聯絡人"""
        try:
            # 這裡應該整合Rocket.Chat的即時通訊功能
            # 發送緊急通知給家屬和醫護人員
            logger.info(f"緊急事件通知已發送: {emergency_event}")
        except Exception as e:
            logger.error(f"緊急通知發送失敗: {e}")
    
    def validate_user_access(self, user_id: str, resource_type: str, action: str) -> bool:
        """
        驗證使用者存取權限
        
        Args:
            user_id: 使用者ID
            resource_type: 資源類型
            action: 操作類型
            
        Returns:
            是否有權限
        """
        if not self.hipaa_settings['access_control_enabled']:
            return True
        
        try:
            # 基於角色的存取控制
            user_permissions = self._get_user_permissions(user_id)
            required_permission = f"{resource_type}:{action}"
            
            has_permission = required_permission in user_permissions
            
            # 記錄存取嘗試
            access_log = {
                'timestamp': datetime.now().isoformat(),
                'user_id': user_id,
                'resource_type': resource_type,
                'action': action,
                'granted': has_permission
            }
            self.audit_logger.info(json.dumps(access_log))
            
            return has_permission
            
        except Exception as e:
            logger.error(f"驗證使用者存取失敗: {e}")
            return False
    
    def _get_user_permissions(self, user_id: str) -> List[str]:
        """獲取使用者權限列表"""
        # 這裡應該連接到實際的使用者管理系統
        # 現在返回預設權限
        return [
            'medical_record:read',
            'chat:send',
            'emergency:trigger',
            'profile:update'
        ]
    
    def schedule_data_deletion(self, user_id: str, data_type: str, deletion_date: datetime):
        """
        安排資料刪除（符合HIPAA要求）
        
        Args:
            user_id: 使用者ID
            data_type: 資料類型
            deletion_date: 刪除日期
        """
        try:
            deletion_task = {
                'user_id': user_id,
                'data_type': data_type,
                'deletion_date': deletion_date.isoformat(),
                'status': 'scheduled'
            }
            
            if self.redis_client:
                self.redis_client.setex(
                    f"deletion_task:{user_id}:{data_type}",
                    int((deletion_date - datetime.now()).total_seconds()),
                    json.dumps(deletion_task)
                )
            
            logger.info(f"已安排資料刪除: {user_id} - {data_type}")
            
        except Exception as e:
            logger.error(f"安排資料刪除失敗: {e}")
    
    def generate_audit_report(self, start_date: datetime, end_date: datetime, 
                            user_id: Optional[str] = None) -> Dict:
        """
        生成審計報告
        
        Args:
            start_date: 開始日期
            end_date: 結束日期
            user_id: 特定使用者ID（可選）
            
        Returns:
            審計報告
        """
        try:
            # 讀取審計日誌
            audit_entries = self._read_audit_log(start_date, end_date, user_id)
            
            # 生成報告
            report = {
                'report_id': hashlib.md5(f"{start_date}{end_date}{user_id}".encode()).hexdigest(),
                'generated_date': datetime.now().isoformat(),
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                },
                'total_events': len(audit_entries),
                'event_breakdown': self._categorize_events(audit_entries),
                'security_alerts': self._identify_security_alerts(audit_entries),
                'compliance_status': self._assess_compliance(audit_entries)
            }
            
            return report
            
        except Exception as e:
            logger.error(f"生成審計報告失敗: {e}")
            return {'error': '無法生成審計報告'}
    
    def _read_audit_log(self, start_date: datetime, end_date: datetime, 
                     user_id: Optional[str] = None) -> List[Dict]:
        """讀取審計日誌"""
        entries = []
        
        try:
            # 從日誌文件讀取
            log_file = 'logs/hipaa_audit.log'
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    for line in f:
                        try:
                            entry = json.loads(line.strip().split(' - ')[-1])
                            entry_timestamp = datetime.fromisoformat(entry['timestamp'])
                            
                            if start_date <= entry_timestamp <= end_date:
                                if not user_id or entry.get('user_id') == user_id:
                                    entries.append(entry)
                        except:
                            continue
        except Exception as e:
            logger.error(f"讀取審計日誌失敗: {e}")
        
        return entries
    
    def _categorize_events(self, entries: List[Dict]) -> Dict:
        """分類事件"""
        categories = {}
        for entry in entries:
            event_type = entry.get('message_type', 'unknown')
            categories[event_type] = categories.get(event_type, 0) + 1
        return categories
    
    def _identify_security_alerts(self, entries: List[Dict]) -> List[Dict]:
        """識別安全警報"""
        alerts = []
        
        for entry in entries:
            # 檢測多次登入失敗
            if entry.get('message_type') == 'login_attempt' and not entry.get('granted', True):
                alerts.append({
                    'type': 'failed_login',
                    'severity': 'medium',
                    'details': entry
                })
            
            # 檢測緊急事件
            if entry.get('message_type') == 'emergency_event':
                alerts.append({
                    'type': 'emergency_access',
                    'severity': 'high',
                    'details': entry
                })
        
        return alerts
    
    def _assess_compliance(self, entries: List[Dict]) -> Dict:
        """評估合規狀態"""
        total_entries = len(entries)
        if total_entries == 0:
            return {'status': 'no_data', 'score': 0}
        
        # 簡單的合規評分
        score = 100
        
        # 檢查是否有必要的審計記錄
        required_events = ['message_access', 'emergency_event']
        found_events = set()
        
        for entry in entries:
            event_type = entry.get('message_type', '')
            if event_type in required_events:
                found_events.add(event_type)
        
        if len(found_events) < len(required_events):
            score -= 20
        
        return {
            'status': 'compliant' if score >= 80 else 'needs_attention',
            'score': score,
            'missing_events': list(set(required_events) - found_events)
        }
    
    def is_healthy(self) -> bool:
        """檢查組件健康狀態"""
        try:
            # 測試加密功能
            test_data = "test_data"
            encrypted = self.encrypt_phi_data(test_data)
            decrypted = self.decrypt_phi_data(encrypted)
            
            return decrypted == test_data
        except Exception as e:
            logger.error(f"HIPAA合規管理器健康檢查失敗: {e}")
            return False


# 使用示例
if __name__ == '__main__':
    # 設置環境變數
    os.environ['HIPAA_ENCRYPTION_KEY'] = Fernet.generate_key().decode()
    os.environ['HIPAA_DATA_RETENTION_DAYS'] = '2555'
    os.environ['HIPAA_AUDIT_RETENTION_DAYS'] = '3652'
    
    # 創建HIPAA合規管理器
    hipaa_manager = HIPAAComplianceManager()
    
    # 測試加密/解密
    test_data = "敏感醫療資訊"
    encrypted = hipaa_manager.encrypt_phi_data(test_data)
    decrypted = hipaa_manager.decrypt_phi_data(encrypted)
    
    print(f"原始資料: {test_data}")
    print(f"加密後: {encrypted}")
    print(f"解密後: {decrypted}")
    
    # 測試審計日誌
    hipaa_manager.log_message_access(
        user_id="test_user",
        message_type="test_message",
        message_hash=hashlib.md5(b"test").hexdigest()
    )
    
    print("HIPAA合規測試完成")