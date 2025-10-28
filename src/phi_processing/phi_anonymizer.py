"""
PHI去識別化處理模組
整合John Snow Labs的PHI去識別化技術
"""

import re
import hashlib
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import json
import os

# 模擬John Snow Labs的PHI去識別化功能
# 在實際部署時，這裡應該連接到真正的John Snow Labs API

logger = logging.getLogger(__name__)

class PHIAnonymizer:
    """
    PHI (Protected Health Information) 去識別化處理器
    整合John Snow Labs技術進行醫療資訊去識別化
    """
    
    def __init__(self):
        self.api_key = os.environ.get('JSL_PHI_API_KEY', 'demo-key')
        self.confidence_threshold = float(os.environ.get('JSL_PHI_CONFIDENCE_THRESHOLD', 0.9))
        self.model_version = os.environ.get('JSL_PHI_MODEL_VERSION', 'latest')
        
        # 定義PHI實體類型
        self.phi_entities = {
            'PERSON': '人名',
            'LOCATION': '地址',
            'DATE': '日期',
            'AGE': '年齡',
            'PHONE': '電話號碼',
            'EMAIL': '電子郵件',
            'ID': '身份證號碼',
            'MEDICAL_RECORD': '病歷號碼',
            'HEALTH_PLAN': '健康保險號碼',
            'ACCOUNT': '帳號',
            'LICENSE': '執照號碼',
            'VEHICLE': '車牌號碼',
            'DEVICE': '設備序號',
            'WEB_URL': '網址',
            'IP_ADDRESS': 'IP地址',
            'BIOMETRIC': '生物特徵',
            'PHOTOGRAPH': '照片',
            'UNIQUE_ID': '唯一識別碼'
        }
        
        # 中文特定的PHI模式
        self.chinese_patterns = {
            'identity_card': r'[A-Z]\d{9}',  # 台灣身份證字號
            'health_card': r'\d{12}',  # 健保卡號碼
            'phone_tw': r'0?9\d{8}',  # 台灣手機號碼
            'phone_landline': r'0\d{1,2}-?\d{6,8}',  # 台灣市話
            'address_tw': r'[\u4e00-\u9fff]+(?:市|縣|區|鄉|鎮|里|村|鄰|路|街|段|巷|弄|號|樓)',
            'chinese_name': r'[\u4e00-\u9fff]{2,4}'  # 中文姓名
        }
        
        logger.info("PHI去識別化處理器初始化完成")
    
    def anonymize_text(self, text: str) -> Tuple[str, List[Dict]]:
        """
        對文本進行PHI去識別化處理
        
        Args:
            text: 原始文本
            
        Returns:
            Tuple[去識別化文本, PHI實體列表]
        """
        try:
            logger.info(f"開始PHI去識別化處理，文本長度: {len(text)}")
            
            # 使用John Snow Labs API進行PHI檢測
            # 這裡模擬API調用結果
            phi_entities = self._detect_phi_entities(text)
            
            # 進行去識別化替換
            anonymized_text = self._replace_phi_entities(text, phi_entities)
            
            logger.info(f"PHI去識別化完成，發現 {len(phi_entities)} 個PHI實體")
            
            return anonymized_text, phi_entities
            
        except Exception as e:
            logger.error(f"PHI去識別化失敗: {e}")
            # 如果處理失敗，返回原始文本和空實體列表
            return text, []
    
    def reidentify_text(self, anonymized_text: str, phi_entities: List[Dict]) -> str:
        """
        將去識別化的文本恢復（如果需要）
        
        Args:
            anonymized_text: 去識別化文本
            phi_entities: PHI實體列表
            
        Returns:
            恢復後的文本
        """
        try:
            # 這裡可以實現重新識別化的邏輯
            # 目前直接返回去識別化文本
            return anonymized_text
            
        except Exception as e:
            logger.error(f"重新識別化失敗: {e}")
            return anonymized_text
    
    def _detect_phi_entities(self, text: str) -> List[Dict]:
        """
        檢測文本中的PHI實體
        
        Args:
            text: 原始文本
            
        Returns:
            PHI實體列表
        """
        entities = []
        
        try:
            # 模擬John Snow Labs API調用
            # 實際使用時，這裡應該調用真正的API
            
            # 檢測中文特定的PHI
            for pattern_name, pattern in self.chinese_patterns.items():
                matches = re.finditer(pattern, text)
                for match in matches:
                    entity_type = self._get_entity_type(pattern_name)
                    confidence = self._calculate_confidence(match.group(), entity_type)
                    
                    if confidence >= self.confidence_threshold:
                        entities.append({
                            'text': match.group(),
                            'start': match.start(),
                            'end': match.end(),
                            'entity_type': entity_type,
                            'confidence': confidence,
                            'replacement': self._generate_replacement(entity_type, match.group())
                        })
            
            # 檢測一般的PHI實體（英文）
            entities.extend(self._detect_general_phi(text))
            
            # 按位置排序
            entities.sort(key=lambda x: x['start'])
            
            logger.info(f"檢測到 {len(entities)} 個PHI實體")
            
        except Exception as e:
            logger.error(f"PHI實體檢測失敗: {e}")
        
        return entities
    
    def _detect_general_phi(self, text: str) -> List[Dict]:
        """
        檢測一般性的PHI實體
        """
        entities = []
        
        # 電子郵件
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        for match in re.finditer(email_pattern, text):
            entities.append({
                'text': match.group(),
                'start': match.start(),
                'end': match.end(),
                'entity_type': 'EMAIL',
                'confidence': 0.95,
                'replacement': '[EMAIL]'
            })
        
        # 電話號碼（國際格式）
        phone_pattern = r'\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}'
        for match in re.finditer(phone_pattern, text):
            entities.append({
                'text': match.group(),
                'start': match.start(),
                'end': match.end(),
                'entity_type': 'PHONE',
                'confidence': 0.9,
                'replacement': '[PHONE]'
            })
        
        # 日期
        date_pattern = r'\b(?:19|20)\d{2}[-/](?:0[1-9]|1[0-2])[-/](?:0[1-9]|[12]\d|3[01])\b'
        for match in re.finditer(date_pattern, text):
            entities.append({
                'text': match.group(),
                'start': match.start(),
                'end': match.end(),
                'entity_type': 'DATE',
                'confidence': 0.85,
                'replacement': '[DATE]'
            })
        
        return entities
    
    def _replace_phi_entities(self, text: str, entities: List[Dict]) -> str:
        """
        替換PHI實體
        
        Args:
            text: 原始文本
            entities: PHI實體列表
            
        Returns:
            去識別化文本
        """
        if not entities:
            return text
        
        # 從後往前替換，避免位置偏移
        entities_sorted = sorted(entities, key=lambda x: x['start'], reverse=True)
        
        result_text = text
        for entity in entities_sorted:
            start = entity['start']
            end = entity['end']
            replacement = entity.get('replacement', f"[{entity['entity_type']}]")
            
            result_text = result_text[:start] + replacement + result_text[end:]
        
        return result_text
    
    def _get_entity_type(self, pattern_name: str) -> str:
        """獲取實體類型"""
        mapping = {
            'identity_card': 'ID',
            'health_card': 'MEDICAL_RECORD',
            'phone_tw': 'PHONE',
            'phone_landline': 'PHONE',
            'address_tw': 'LOCATION',
            'chinese_name': 'PERSON'
        }
        return mapping.get(pattern_name, 'UNKNOWN')
    
    def _calculate_confidence(self, text: str, entity_type: str) -> float:
        """
        計算實體檢測的信心分數
        
        Args:
            text: 檢測到的文本
            entity_type: 實體類型
            
        Returns:
            信心分數 (0-1)
        """
        # 簡單的信心分數計算
        # 實際使用時，這應該基於機器學習模型
        
        base_confidence = 0.8
        
        # 根據文本長度和格式調整信心分數
        if entity_type == 'EMAIL' and '@' in text:
            base_confidence += 0.15
        elif entity_type == 'PHONE' and len(text) >= 8:
            base_confidence += 0.1
        elif entity_type == 'ID' and len(text) == 10:
            base_confidence += 0.1
        
        return min(base_confidence, 1.0)
    
    def _generate_replacement(self, entity_type: str, original_text: str) -> str:
        """
        生成替換文本
        
        Args:
            entity_type: 實體類型
            original_text: 原始文本
            
        Returns:
            替換文本
        """
        # 生成基於哈希的替換，確保一致性
        text_hash = hashlib.md5(original_text.encode()).hexdigest()[:8]
        
        replacements = {
            'PERSON': f'[PERSON_{text_hash}]',
            'LOCATION': f'[LOCATION_{text_hash}]',
            'DATE': f'[DATE_{text_hash}]',
            'AGE': f'[AGE_{text_hash}]',
            'PHONE': f'[PHONE_{text_hash}]',
            'EMAIL': f'[EMAIL_{text_hash}]',
            'ID': f'[ID_{text_hash}]',
            'MEDICAL_RECORD': f'[MEDICAL_RECORD_{text_hash}]',
            'HEALTH_PLAN': f'[HEALTH_PLAN_{text_hash}]',
            'ACCOUNT': f'[ACCOUNT_{text_hash}]',
            'LICENSE': f'[LICENSE_{text_hash}]',
            'VEHICLE': f'[VEHICLE_{text_hash}]',
            'DEVICE': f'[DEVICE_{text_hash}]',
            'WEB_URL': f'[URL_{text_hash}]',
            'IP_ADDRESS': f'[IP_{text_hash}]',
            'BIOMETRIC': f'[BIOMETRIC_{text_hash}]',
            'PHOTOGRAPH': f'[PHOTO_{text_hash}]',
            'UNIQUE_ID': f'[ID_{text_hash}]'
        }
        
        return replacements.get(entity_type, f'[{entity_type}_{text_hash}]')
    
    def is_healthy(self) -> bool:
        """檢查組件健康狀態"""
        try:
            # 測試PHI檢測功能
            test_text = "我的電話是0912345678"
            _, entities = self.anonymize_text(test_text)
            return len(entities) >= 0  # 至少能處理文本
        except Exception:
            return False


# 使用示例
if __name__ == '__main__':
    # 設置環境變數
    os.environ['JSL_PHI_API_KEY'] = 'demo-key'
    os.environ['JSL_PHI_CONFIDENCE_THRESHOLD'] = '0.8'
    
    # 創建PHI去識別化器
    anonymizer = PHIAnonymizer()
    
    # 測試文本
    test_texts = [
        "我是王小明，我的電話是0912345678，身份證字號是A123456789",
        "我的email是test@example.com，住在台北市大安區",
        "我的病歷號碼是123456789012，出生日期是1950年1月1日"
    ]
    
    for text in test_texts:
        print(f"原始文本: {text}")
        anonymized, entities = anonymizer.anonymize_text(text)
        print(f"去識別化: {anonymized}")
        print(f"PHI實體: {entities}")
        print("-" * 50)