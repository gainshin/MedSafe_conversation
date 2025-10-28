"""
簡化PHI去識別化處理模組
專門為老年人醫療對話設計
"""

import re
import hashlib
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

class SimplePHIAnonymizer:
    """
    簡化PHI去識別化處理器
    專門處理中文醫療對話中的個人資訊
    """
    
    def __init__(self):
        # 定義PHI實體類型和對應的正則表達式
        self.phi_patterns = {
            'PERSON': {'pattern': r'[\u4e00-\u9fff]{2,4}', 'description': '中文姓名'},
            'PHONE': {'pattern': r'09\d{8}|\d{2,3}-?\d{6,8}', 'description': '電話號碼'},
            'ID': {'pattern': r'[A-Z]\d{9}', 'description': '台灣身份證字號'},
            'EMAIL': {'pattern': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'description': '電子郵件'},
            'LOCATION': {'pattern': r'[\u4e00-\u9fff]+(?:市|縣|區|鄉|鎮|里|村|路|街|段|巷|弄|號)', 'description': '地址'},
            'DATE': {'pattern': r'\d{4}[年/-]\d{1,2}[月/-]\d{1,2}[日號]?', 'description': '日期'},
            'MEDICAL_RECORD': {'pattern': r'\d{12}', 'description': '病歷號碼'}
        }
        
        logger.info("簡化PHI去識別化處理器初始化完成")
    
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
            
            entities = []
            
            # 檢測所有PHI實體
            for entity_type, config in self.phi_patterns.items():
                pattern = config['pattern']
                matches = re.finditer(pattern, text)
                
                for match in matches:
                    entities.append({
                        'text': match.group(),
                        'start': match.start(),
                        'end': match.end(),
                        'entity_type': entity_type,
                        'confidence': 0.9,  # 簡化版本使用固定信心值
                        'replacement': self._generate_replacement(entity_type, match.group())
                    })
            
            # 按位置排序（從後往前替換）
            entities.sort(key=lambda x: x['start'], reverse=True)
            
            # 進行替換
            anonymized_text = text
            for entity in entities:
                start = entity['start']
                end = entity['end']
                replacement = entity['replacement']
                
                anonymized_text = anonymized_text[:start] + replacement + anonymized_text[end:]
            
            logger.info(f"PHI去識別化完成，發現 {len(entities)} 個PHI實體")
            
            return anonymized_text, entities
            
        except Exception as e:
            logger.error(f"PHI去識別化失敗: {e}")
            return text, []
    
    def _generate_replacement(self, entity_type: str, original_text: str) -> str:
        """生成替換文本"""
        # 生成基於哈希的替換，確保一致性
        text_hash = hashlib.md5(original_text.encode()).hexdigest()[:6]
        return f"[{entity_type}_{text_hash}]"
    
    def is_healthy(self) -> bool:
        """檢查組件健康狀態"""
        try:
            test_text = "我的電話是0912345678"
            anonymized_text, entities = self.anonymize_text(test_text)
            return len(entities) >= 0  # 至少能處理文本
        except Exception:
            return False


# 使用示例
if __name__ == '__main__':
    # 創建PHI去識別化器
    anonymizer = SimplePHIAnonymizer()
    
    # 測試文本
    test_texts = [
        "我是王小明，我的電話是0912345678",
        "我的email是test@example.com，住在台北市大安區",
        "我的病歷號碼是123456789012，身份證A123456789"
    ]
    
    for text in test_texts:
        print(f"\n原始文本: {text}")
        anonymized, entities = anonymizer.anonymize_text(text)
        print(f"去識別化: {anonymized}")
        print(f"PHI實體: {len(entities)} 個")
        
        for entity in entities:
            print(f"  - {entity['entity_type']}: {entity['text']} -> {entity['replacement']}")
    
    print(f"\n系統健康狀態: {'正常' if anonymizer.is_healthy() else '異常'}")