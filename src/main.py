#!/usr/bin/env python3
"""
MediNote-AI 老年人安全醫療對話框架
主程式入口點
"""

import os
import sys
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from flask_session import Session
import redis

# 添加當前目錄到Python路徑（確保能導入模組）
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from chat.medinote_processor import MediNoteProcessor
from phi_processing.simple_phi_anonymizer import SimplePHIAnonymizer
from hipaa_compliance.hipaa_manager import HIPAAComplianceManager
from elderly_interface.simple_elderly_interface import SimpleElderlyInterface
from prompt_testing.prompt_tester import PromptTester

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/medinote-ai-elderly.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 創建Flask應用
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

# 簡化會話管理（不使用Redis）
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = '/tmp/flask_session'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True

# 初始化擴展
CORS(app)
Session(app)

# 初始化核心組件
try:
    medinote_processor = MediNoteProcessor()
    phi_anonymizer = SimplePHIAnonymizer()
    hipaa_manager = HIPAAComplianceManager()
    elderly_interface = SimpleElderlyInterface()
    prompt_tester = PromptTester()
    logger.info("所有核心組件初始化成功")
except Exception as e:
    logger.error(f"初始化核心組件失敗: {e}")
    sys.exit(1)

@app.route('/')
def index():
    """主頁面 - 老年人友善介面"""
    try:
        # 檢查使用者是否已登入
        if 'user_id' not in session:
            return render_template('login.html')
        
        # 獲取老年人介面設定
        interface_settings = elderly_interface.get_interface_settings()
        return render_template('chat.html', 
                           interface_settings=interface_settings,
                           username=session.get('username'))
    except Exception as e:
        logger.error(f"載入主頁面失敗: {e}")
        return render_template('error.html', error=str(e)), 500

@app.route('/chat')
def chat_page():
    """聊天頁面 - 重定向到主頁面"""
    return index()

@app.route('/api/chat', methods=['POST'])
def chat():
    """處理對話請求"""
    try:
        # 簡化會話驗證 - 開發模式下允許測試
        if 'user_id' not in session:
            # 為測試目的創建一個預設用戶
            session['user_id'] = 'test_user_001'
            session['username'] = 'testuser'
            session['user_profile'] = {
                'age': 75,
                'medical_conditions': ['diabetes', 'hypertension'],
                'emergency_contacts': ['+886900000000']
            }
        
        data = request.get_json()
        user_message = data.get('message', '')
        conversation_context = data.get('context', {})
        
        if not user_message:
            return jsonify({'error': '訊息不能為空'}), 400
        
        # 記錄原始訊息（HIPAA審計）
        hipaa_manager.log_message_access(
            user_id=session['user_id'],
            message_type='user_input',
            message_hash=hash(user_message)
        )
        
        # PHI去識別化處理
        anonymized_message, phi_entities = phi_anonymizer.anonymize_text(user_message)
        
        # 使用MediNote-AI處理對話
        ai_response = medinote_processor.process_message(
            message=anonymized_message,
            context=conversation_context,
            user_profile=session.get('user_profile', {})
        )
        
        # 使用匿名化回應（保持去識別化以保護隱私）
        final_response = ai_response
        
        # 檢查是否需要緊急處理
        emergency_level = medinote_processor.assess_emergency_level(user_message, ai_response)
        if emergency_level > 0.7:
            elderly_interface.trigger_emergency_alert(session['user_id'], user_message)
        
        # 記錄AI回應（HIPAA審計）
        hipaa_manager.log_message_access(
            user_id=session['user_id'],
            message_type='ai_response',
            message_hash=hash(final_response)
        )
        
        return jsonify({
            'response': final_response,
            'emergency_level': emergency_level,
            'phi_detected': len(phi_entities) > 0,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"處理對話請求失敗: {e}")
        return jsonify({'error': '處理請求時發生錯誤'}), 500

@app.route('/api/voice-input', methods=['POST'])
def voice_input():
    """處理語音輸入"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': '未授權的請求'}), 401
        
        audio_file = request.files.get('audio')
        if not audio_file:
            return jsonify({'error': '未提供音訊檔案'}), 400
        
        # 使用語音轉文字服務
        text_result = elderly_interface.process_voice_input(audio_file)
        
        return jsonify({
            'text': text_result,
            'confidence': 0.85,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"處理語音輸入失敗: {e}")
        return jsonify({'error': '語音辨識失敗'}), 500

@app.route('/api/emergency-contact', methods=['POST'])
def emergency_contact():
    """緊急聯繫功能"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': '未授權的請求'}), 401
        
        data = request.get_json()
        emergency_type = data.get('type', 'general')
        location = data.get('location', {})
        
        # 記錄緊急事件
        hipaa_manager.log_emergency_event(
            user_id=session['user_id'],
            emergency_type=emergency_type,
            location=location
        )
        
        # 觸發緊急聯繫
        result = elderly_interface.emergency_contact(
            user_id=session['user_id'],
            emergency_type=emergency_type,
            location=location
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"緊急聯繫功能失敗: {e}")
        return jsonify({'error': '緊急聯繫功能暫時無法使用'}), 500

@app.route('/api/prompt-test', methods=['POST'])
def prompt_test():
    """Prompt測試端點"""
    try:
        if 'user_id' not in session or not session.get('is_admin'):
            return jsonify({'error': '需要管理員權限'}), 403
        
        data = request.get_json()
        test_scenarios = data.get('scenarios', [])
        
        results = prompt_tester.run_tests(test_scenarios)
        
        return jsonify({
            'test_results': results,
            'summary': prompt_tester.generate_summary(results),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Prompt測試失敗: {e}")
        return jsonify({'error': '測試執行失敗'}), 500

@app.route('/api/health')
def health_check():
    """健康檢查端點"""
    try:
        # 檢查各組件狀態
        components_status = {
            'medinote_processor': medinote_processor.is_healthy(),
            'phi_anonymizer': phi_anonymizer.is_healthy(),
            'hipaa_manager': hipaa_manager.is_healthy(),
            'elderly_interface': elderly_interface.is_healthy()
        }
        
        all_healthy = all(components_status.values())
        
        return jsonify({
            'status': 'healthy' if all_healthy else 'unhealthy',
            'components': components_status,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"健康檢查失敗: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/login', methods=['POST'])
def login():
    """登入端點"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        # 這裡應該連接到實際的使用者認證系統
        # 現在只是示範版本
        if username and password:
            session['user_id'] = hash(username)
            session['username'] = username
            session['user_profile'] = {
                'age': 75,
                'medical_conditions': ['diabetes', 'hypertension'],
                'emergency_contacts': ['+886900000000']
            }
            
            logger.info(f"使用者登入成功: {username}")
            return jsonify({'success': True, 'username': username})
        else:
            return jsonify({'error': '無效的使用者憑證'}), 401
            
    except Exception as e:
        logger.error(f"登入失敗: {e}")
        return jsonify({'error': '登入過程發生錯誤'}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    """登出端點"""
    try:
        username = session.get('username')
        session.clear()
        logger.info(f"使用者登出: {username}")
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"登出失敗: {e}")
        return jsonify({'error': '登出過程發生錯誤'}), 500

if __name__ == '__main__':
    # 確保日誌目錄存在
    os.makedirs('logs', exist_ok=True)
    
    # 啟動應用
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"啟動 MediNote-AI 老年人安全醫療對話框架 (port: {port})")
    app.run(host='0.0.0.0', port=port, debug=debug)