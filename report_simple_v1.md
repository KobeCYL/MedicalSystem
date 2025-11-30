# 工业级智能医疗导诊系统 - 第一版本（简易版）

## 一、项目背景 

随着"慧心健康"AI导诊项目的推进，需要快速上线一个可用的医疗导诊系统。第一版本专注于核心功能实现，使用简单的JSON文件存储，便于快速开发和测试。

## 二、第一版本目标

### 核心功能目标
1. **基础症状匹配**：根据用户输入匹配可能的疾病
2. **知识库查询**：从JSON文件查询处理指南和风险信息
3. **LLM综合建议**：使用DeepSeek模型生成个性化医疗建议
4. **安全防护**：基本的输入验证和安全检测

### 技术目标
- **快速启动**：无需复杂部署，Python直接运行
- **简化架构**：使用文件存储，避免数据库依赖
- **易于扩展**：代码结构支持第二版本升级到PostgreSQL

## 三、技术栈（第一版本）

### 基础技术栈
| 组件 | 技术选型 | 说明 |
|------|----------|------|
| **后端框架** | Flask | 轻量级Web框架 |
| **前端界面** | Streamlit | 快速构建交互界面 |
| **数据存储** | JSON文件 | 使用data目录下的JSON文件 |
| **AI模型** | DeepSeek API | 通过LangChain调用 |
| **异步处理** | asyncio | 提高并发性能 |

### 开发规范
- **代码结构**：模块化设计，便于后续升级
- **配置管理**：环境变量配置，便于切换环境
- **错误处理**：完善的异常处理和日志记录
- **安全规范**：输入验证和基本安全防护

## 四、项目结构（第一版本）

```
medical_ai_v1/
├── app.py                      # Flask主应用
├── streamlit_app.py            # Streamlit前端界面
├── requirements.txt            # 依赖文件
├── .env                       # 环境配置
├── config.py                   # 应用配置
│
├── data/                       # 数据文件目录
│   ├── symptom.json           # 症状-疾病映射
│   ├── guideline.json          # 处理指南
│   ├── disease_info.json       # 风险信息
│   └── test_data/             # 测试数据
│
├── services/                   # 服务层
│   ├── llm_service.py         # LLM服务（DeepSeek）
│   ├── file_storage_service.py # 文件存储服务
│   └── security_service.py     # 安全服务
│
├── controllers/                # 控制器层
│   ├── medical_controller.py   # 医疗逻辑控制器
│   └── api_controller.py       # API接口控制器
│
├── utils/                       # 工具类
│   ├── logger.py               # 日志工具
│   ├── config_loader.py        # 配置加载
│   └── validator.py           # 验证工具
│
└── tests/                       # 测试目录
    ├── test_medical_logic.py   # 医疗逻辑测试
    └── test_api_endpoints.py  # API接口测试
```

## 五、核心代码实现（第一版本）

### 1. 环境配置 (.env)
```bash
# DeepSeek API 配置（第一版本核心）
DEEPSEEK_API_URL=https://api.deepseek.com/v1
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_MODEL=deepseek-chat

# 应用配置
FLASK_ENV=development
PORT=5000
HOST=0.0.0.0

# LLM参数
MAX_TOKENS=200
TEMPERATURE=0.7

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=app.log

# 文件路径配置（第一版本使用文件存储）
DATA_DIR=./data
SYMPTOM_FILE=symptom.json
GUIDELINE_FILE=guideline.json
RISK_FILE=disease_info.json
```

### 2. 文件存储服务（第一版本核心）
```python
# services/file_storage_service.py
import json
import aiofiles
import os
from typing import List, Dict, Any
from utils.logger import logger

class FileStorageService:
    """第一版本文件存储服务，便于第二版本升级到数据库"""
    
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = data_dir
    
    async def load_json_file(self, filename: str) -> List[Dict]:
        """异步加载JSON文件"""
        try:
            filepath = os.path.join(self.data_dir, filename)
            async with aiofiles.open(filepath, 'r', encoding='utf-8') as f:
                content = await f.read()
                return json.loads(content)
        except Exception as e:
            logger.error(f"加载文件 {filename} 失败: {e}")
            return []
    
    async def get_symptom_data(self) -> List[Dict]:
        """获取症状数据"""
        return await self.load_json_file("symptom.json")
    
    async def get_guideline_data(self) -> List[Dict]:
        """获取处理指南数据"""
        return await self.load_json_file("guideline.json")
    
    async def get_risk_data(self) -> List[Dict]:
        """获取风险信息数据"""
        return await self.load_json_file("disease_info.json")
    
    # 第二版本可以轻松升级的方法
    async def find_by_disease_id(self, disease_id: str, data_type: str) -> Dict[str, Any]:
        """根据疾病ID查找数据（便于第二版本重写为数据库查询）"""
        if data_type == "symptom":
            data = await self.get_symptom_data()
        elif data_type == "guideline":
            data = await self.get_guideline_data()
        elif data_type == "risk":
            data = await self.get_risk_data()
        else:
            return {}
        
        for item in data:
            if item.get('disease_id') == disease_id:
                return item
        
        return {}
```

### 3. LLM服务（DeepSeek集成）
```python
# services/llm_service.py
import os
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from utils.logger import logger

class LLMService:
    """DeepSeek LLM服务"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=os.getenv("DEEPSEEK_MODEL"),
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url=os.getenv("DEEPSEEK_API_URL"),
            temperature=float(os.getenv("TEMPERATURE", 0.7)),
            max_tokens=int(os.getenv("MAX_TOKENS", 200))
        )
    
    async def generate_advice(self, symptom_info: Dict, guideline_info: Dict, 
                            risk_info: Dict, patient_info: Dict) -> str:
        """生成医疗建议"""
        prompt = self._build_prompt(symptom_info, guideline_info, risk_info, patient_info)
        
        try:
            response = await self.llm.agenerate([
                [
                    SystemMessage(content="你是医疗助手，提供准确安全的建议"),
                    HumanMessage(content=prompt)
                ]
            ])
            return response.generations[0][0].text
        except Exception as e:
            logger.error(f"LLM生成失败: {e}")
            return self._get_fallback_advice(guideline_info)
    
    def _build_prompt(self, symptom_info: Dict, guideline_info: Dict, 
                     risk_info: Dict, patient_info: Dict) -> str:
        """构建Prompt"""
        return f"""
请根据以下信息生成医疗建议：

患者：{patient_info.get('age', '未知')}岁，{patient_info.get('gender', '未知')}性
症状：{symptom_info.get('disease_name', '未知')} - {', '.join(symptom_info.get('matched_symptoms', []))}

处理指南：{guideline_info.get('recommended_action', '无')}
风险提示：{risk_info.get('special_notes', '无')}

请生成专业、安全的建议："""
    
    def _get_fallback_advice(self, guideline_info: Dict) -> str:
        """降级建议"""
        return guideline_info.get('recommended_action', '请及时就医')
```

### 4. 医疗逻辑控制器
```python
# controllers/medical_controller.py
import asyncio
from typing import Dict, Any
from services.file_storage_service import FileStorageService
from services.llm_service import LLMService
from services.security_service import SecurityService
from utils.logger import logger

class MedicalController:
    """医疗逻辑控制器"""
    
    def __init__(self):
        self.storage_service = FileStorageService()
        self.llm_service = LLMService()
        self.security_service = SecurityService()
    
    async def process_query(self, symptom_text: str, patient_info: Dict[str, Any]) -> Dict[str, Any]:
        """处理医疗查询"""
        try:
            # 1. 安全检测
            if not await self.security_service.check_safety(symptom_text):
                return {
                    'status': 'error',
                    'message': '输入内容不安全，请重新描述症状'
                }
            
            # 2. 症状匹配
            matched_disease = await self._match_symptoms(symptom_text)
            if not matched_disease:
                return {
                    'status': 'no_match', 
                    'message': '未找到匹配疾病，请详细描述症状'
                }
            
            # 3. 查询知识库信息
            guideline_info, risk_info = await asyncio.gather(
                self.storage_service.find_by_disease_id(matched_disease['disease_id'], 'guideline'),
                self.storage_service.find_by_disease_id(matched_disease['disease_id'], 'risk')
            )
            
            # 4. 生成建议
            advice = await self.llm_service.generate_advice(
                symptom_info=matched_disease,
                guideline_info=guideline_info,
                risk_info=risk_info,
                patient_info=patient_info
            )
            
            return {
                'status': 'success',
                'disease': matched_disease['name'],
                'advice': advice,
                'urgency': guideline_info.get('urgency', 'unknown')
            }
            
        except Exception as e:
            logger.error(f"处理查询失败: {e}")
            return {
                'status': 'error',
                'message': '系统处理失败，请稍后重试'
            }
    
    async def _match_symptoms(self, symptom_text: str) -> Dict[str, Any]:
        """症状匹配"""
        symptoms_data = await self.storage_service.get_symptom_data()
        
        # 简单关键词匹配（第一版本）
        for disease in symptoms_data:
            matched_symptoms = []
            for symptom in disease.get('related_symptoms', []):
                if symptom in symptom_text:
                    matched_symptoms.append(symptom)
            
            if matched_symptoms:
                return {
                    'disease_id': disease['disease_id'],
                    'name': disease['name'],
                    'matched_symptoms': matched_symptoms
                }
        
        return {}
```

### 5. Flask主应用
```python
# app.py
from flask import Flask, request, jsonify
from controllers.medical_controller import MedicalController
from utils.logger import setup_logger
import asyncio

# 配置日志
setup_logger()

app = Flask(__name__)
medical_controller = MedicalController()

@app.route('/api/medical/query', methods=['POST'])
async def medical_query():
    """医疗查询API"""
    try:
        data = request.get_json()
        symptom_text = data.get('symptom', '')
        patient_info = data.get('patient_info', {})
        
        # 处理查询
        result = await medical_controller.process_query(symptom_text, patient_info)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': '服务器内部错误'
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({'status': 'healthy', 'version': 'v1.0'})

if __name__ == '__main__':
    # 第一版本直接运行，无需复杂部署
    app.run(
        host=os.getenv('HOST', '0.0.0.0'),
        port=int(os.getenv('PORT', 5000)),
        debug=os.getenv('FLASK_ENV') == 'development'
    )
```

### 6. Streamlit前端界面
```python
# streamlit_app.py
import streamlit as st
import requests
import json

st.title("🤖 智能医疗导诊系统 - 第一版本")

# 症状输入
symptom = st.text_area("请描述您的症状:", placeholder="例如：头痛、发烧、咳嗽...")

# 患者信息
col1, col2 = st.columns(2)
with col1:
    age = st.number_input("年龄", min_value=0, max_value=120, value=25)
with col2:
    gender = st.selectbox("性别", ["男", "女", "其他"])

special_conditions = st.text_input("特殊状况（可选）", placeholder="如怀孕、慢性病等")

if st.button("获取建议"):
    if symptom.strip():
        # 调用后端API
        payload = {
            "symptom": symptom,
            "patient_info": {
                "age": age,
                "gender": gender,
                "special_conditions": special_conditions
            }
        }
        
        try:
            response = requests.post(
                "http://localhost:5000/api/medical/query",
                json=payload,
                timeout=10
            )
            
            result = response.json()
            
            if result['status'] == 'success':
                st.success(f"**诊断结果**: {result['disease']}")
                st.info(f"**紧急程度**: {result['urgency']}")
                st.write(f"**建议**: {result['advice']}")
            else:
                st.warning(result['message'])
                
        except Exception as e:
            st.error(f"系统错误: {e}")
    else:
        st.warning("请输入症状描述")
```

## 六、依赖配置（第一版本简化）

```txt
# requirements.txt
# 核心依赖
flask==2.3.3
streamlit==1.28.0
langchain==0.0.346
openai==0.28.0

# 异步处理
aiohttp==3.8.5
asyncio==3.4.3
aiofiles==23.2.1

# 工具类
python-dotenv==1.0.0
requests==2.31.0

# 开发工具（可选）
black==23.7.0
flake8==6.0.0
```

## 七、运行方式（第一版本）

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置环境变量
创建 `.env` 文件并配置DeepSeek API密钥：
```bash
DEEPSEEK_API_URL=https://api.deepseek.com/v1
DEEPSEEK_API_KEY=your_actual_api_key
DEEPSEEK_MODEL=deepseek-chat
PORT=5000
```

### 3. 启动后端服务
```bash
python app.py
```

### 4. 启动前端界面（新终端）
```bash
streamlit run streamlit_app.py
```

### 5. 访问应用
- 后端API: http://localhost:5000
- 前端界面: http://localhost:8501

## 八、第二版本升级路径

### 数据库升级准备
```python
# 第二版本只需要修改FileStorageService为DatabaseService
# services/database_service.py (V2)
class DatabaseService:
    # 保持相同的接口方法
    async def find_by_disease_id(self, disease_id: str, data_type: str) -> Dict[str, Any]:
        # 改为数据库查询
        async with self.pool.acquire() as conn:
            if data_type == "guideline":
                query = "SELECT * FROM guidelines WHERE disease_id = $1"
            elif data_type == "risk":
                query = "SELECT * FROM risks WHERE disease_id = $1"
            # ...执行数据库查询
```

### 配置升级
```bash
# .env (V2)
# 增加数据库配置
DB_HOST=localhost
DB_PORT=5432
DB_NAME=medical_ai
DB_USER=ai_user
DB_PASSWORD=ai_password

# 其他配置保持不变
```

## 九、第一版本特点

### ✅ 已完成功能
- [x] 基础症状匹配（关键词匹配）
- [x] JSON文件数据存储
- [x] DeepSeek LLM集成
- [x] Flask + Streamlit 前后端分离
- [x] 基本安全检测
- [x] 异步处理优化

### 🔄 第二版本升级内容
- [ ] PostgreSQL数据库集成
- [ ] 向量化搜索（症状语义匹配）
- [ ] Docker容器化部署
- [ ] 性能监控和日志系统
- [ ] 高级安全防护

### 🚀 快速启动优势
1. **无需数据库**：使用文件存储，零配置启动
2. **简单部署**：Python直接运行，无需Docker
3. **快速开发**：代码结构清晰，易于理解和修改
4. **便于测试**：所有数据在文件中，方便测试和调试

---

**第一版本状态**: ✅ 可立即开发部署
**升级路径**: 清晰的接口设计，便于第二版本升级