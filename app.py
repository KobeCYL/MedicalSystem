"""Flask应用主入口 - 医疗导诊系统API"""
from flask import Flask, request, jsonify
import json
from controllers.medical_controller import EnhancedMedicalController
from models.medical_models import MedicalQueryResult, PatientInfo
import asyncio
import os
from dotenv import load_dotenv
from utils.logger import SystemLogger

# 加载环境变量
load_dotenv()

# 配置日志
logger = SystemLogger("medical_api")

app = Flask(__name__)
medical_controller = EnhancedMedicalController()

@app.route('/api/medical/query', methods=['POST'])
async def medical_query():
    """医疗查询API"""
    try:
        data = request.get_json()
        
        # 基本验证
        if not data or 'symptom' not in data:
            error_result = MedicalQueryResult(
                status="error",
                error_message="请求数据格式错误，缺少症状描述"
            )
            return jsonify(error_result.dict()), 400
        
        symptom_text = data.get('symptom', '')
        patient_info = data.get('patient_info', {})
        
        # 处理查询
        result = await medical_controller.process_query(symptom_text, patient_info)
        
        # 返回结构化响应
        return jsonify(result.dict())
        
    except Exception as e:
        error_result = MedicalQueryResult(
            status="error",
            error_message="服务器内部错误"
        )
        return jsonify(error_result.dict()), 500

@app.route('/api/medical/structured', methods=['POST'])
async def structured_medical_query():
    """结构化医疗查询API"""
    try:
        data = request.get_json()
        
        # 验证请求数据
        if not data or 'symptom' not in data or 'patient_info' not in data:
            error_result = MedicalQueryResult(
                status="error",
                error_message="请求数据格式错误"
            )
            return jsonify(error_result.dict()), 400
        
        # 验证患者信息
        try:
            patient_info = PatientInfo(**data.get('patient_info', {}))
        except Exception as e:
            error_result = MedicalQueryResult(
                status="error",
                error_message=f"患者信息格式错误: {str(e)}"
            )
            return jsonify(error_result.dict()), 400
        
        # 处理查询
        result = await medical_controller.process_query(
            data.get('symptom', ''),
            patient_info.dict()
        )
        
        return jsonify(result.dict())
        
    except Exception as e:
        error_result = MedicalQueryResult(
            status="error",
            error_message=f"服务器内部错误: {str(e)}"
        )
        return jsonify(error_result.dict()), 500

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查API"""
    return jsonify({
        'status': 'healthy',
        'version': 'v1.0',
        'service': 'medical-ai-system'
    })

@app.route('/api/info', methods=['GET'])
def system_info():
    """系统信息API"""
    return jsonify({
        'name': '智能医疗导诊系统',
        'version': '1.0.0',
        'description': '基于多知识库和AI的医疗导诊服务',
        'features': [
            '症状匹配',
            '医疗建议生成',
            '风险评估',
            '安全检测'
        ],
        'llm_provider': 'DeepSeek',
        'data_sources': ['symptom.json', 'guideline.json', 'disease_info.json']
    })

@app.route('/api/history', methods=['GET'])
def get_history():
    try:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs', 'query_history.json')
        if not os.path.exists(path):
            return jsonify([])
        with open(path, 'r', encoding='utf-8') as f:
            obj = json.load(f)
            return jsonify(obj if isinstance(obj, list) else [])
    except Exception:
        return jsonify([])

@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs', 'query_history.json')
        entries = []
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                obj = json.load(f)
                entries = obj if isinstance(obj, list) else []
        normal = 0
        malicious = 0
        non_medical = 0
        durations = []
        for e in entries:
            r = e.get('result', {})
            s = r.get('status')
            if s == 'success':
                normal += 1
            elif s == 'no_match':
                non_medical += 1
            elif s == 'failed' or s == 'error':
                malicious += 1
            d = e.get('duration_ms')
            if isinstance(d, (int, float)):
                durations.append(float(d))
        durations_sorted = sorted(durations)
        n = len(durations_sorted)
        avg = sum(durations_sorted) / n if n else 0.0
        p95 = durations_sorted[int(0.95 * (n - 1))] if n else 0.0
        mx = durations_sorted[-1] if n else 0.0
        return jsonify({
            'counts': {
                'normal': normal,
                'malicious_or_error': malicious,
                'non_medical': non_medical,
                'total': len(entries)
            },
            'durations_ms': {
                'count': n,
                'avg': round(avg, 2),
                'p95': round(p95, 2),
                'max': round(mx, 2)
            }
        })
    except Exception:
        return jsonify({'counts': {'normal': 0, 'malicious_or_error': 0, 'non_medical': 0, 'total': 0}, 'durations_ms': {'count': 0, 'avg': 0.0, 'p95': 0.0, 'max': 0.0}})

if __name__ == '__main__':
    # 第一版本直接运行，无需复杂部署
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    print(f"🚀 启动医疗导诊系统...")
    print(f"📍 服务地址: http://{host}:{port}")
    print(f"🔧 调试模式: {debug}")
    print(f"🤖 AI模型: {os.getenv('DEEPSEEK_MODEL')}")
    
    app.run(host=host, port=port, debug=debug)
