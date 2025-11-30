# 工业级智能医疗导诊系统 - 第一版本（Pydantic增强版）

## 一、Pydantic数据模型设计

### 1. 核心数据模型
```python
# models/medical_models.py
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from enum import Enum

class UrgencyLevel(str, Enum):
    """紧急程度枚举"""
    LOW = "低"
    MEDIUM = "中"
    HIGH = "高"
    UNKNOWN = "未知"

class PatientInfo(BaseModel):
    """患者信息模型"""
    age: int = Field(..., ge=0, le=120, description="患者年龄")
    gender: str = Field(..., description="患者性别")
    special_conditions: Optional[str] = Field(None, description="特殊状况")

class SymptomInfo(BaseModel):
    """症状信息模型"""
    disease_id: str = Field(..., description="疾病ID")
    disease_name: str = Field(..., description="疾病名称")
    matched_symptoms: List[str] = Field(..., description="匹配的症状列表")
    confidence: float = Field(0.0, ge=0.0, le=1.0, description="匹配置信度")

class GuidelineInfo(BaseModel):
    """处理指南模型"""
    disease_id: str = Field(..., description="疾病ID")
    urgency: UrgencyLevel = Field(UrgencyLevel.UNKNOWN, description="紧急程度")
    recommended_action: str = Field(..., description="推荐处理方式")
    timeframe: Optional[str] = Field(None, description="建议时间范围")

class RiskInfo(BaseModel):
    """风险信息模型"""
    disease_id: str = Field(..., description="疾病ID")
    special_notes: str = Field(..., description="特殊注意事项")
    risk_groups: List[str] = Field(..., description="风险人群")
    contraindications: Optional[List[str]] = Field(None, description="禁忌事项")

class MedicalAdviceRequest(BaseModel):
    """医疗建议请求模型"""
    symptom_info: SymptomInfo
    guideline_info: GuidelineInfo
    risk_info: RiskInfo
    patient_info: PatientInfo

class MedicalAdviceResponse(BaseModel):
    """医疗建议响应模型"""
    assessment: str = Field(..., description="状况评估")
    immediate_actions: List[str] = Field(..., description="立即采取的措施")
    medical_advice: str = Field(..., description="就医建议")
    monitoring_points: List[str] = Field(..., description="观察要点")
    emergency_handling: Optional[str] = Field(None, description="紧急情况处理")
    
    @validator('immediate_actions')
    def validate_actions(cls, v):
        if not v:
            raise ValueError("至少需要提供一个立即措施")
        return v

class MedicalQueryResult(BaseModel):
    """医疗查询结果模型"""
    status: str = Field(..., description="处理状态")
    disease_name: Optional[str] = Field(None, description="疾病名称")
    advice: Optional[str] = Field(None, description="建议内容")
    urgency: UrgencyLevel = Field(UrgencyLevel.UNKNOWN, description="紧急程度")
    supplementary_info: Optional[Dict[str, Any]] = Field(None, description="补充信息")
    error_message: Optional[str] = Field(None, description="错误信息")
```

### 2. LangChain输出解析器集成
```python
# utils/output_parsers.py
from langchain.output_parsers import PydanticOutputParser, OutputFixingParser
from langchain.chat_models import ChatOpenAI
from models.medical_models import MedicalAdviceResponse
import os
from utils.logger import logger

class MedicalOutputParser:
    """医疗输出解析器，集成Pydantic验证和错误修复"""
    
    def __init__(self):
        # 创建基础解析器
        self.base_parser = PydanticOutputParser(pydantic_object=MedicalAdviceResponse)
        
        # 创建修复解析器
        self.fixing_parser = OutputFixingParser.from_llm(
            parser=self.base_parser,
            llm=ChatOpenAI(
                model=os.getenv("DEEPSEEK_MODEL"),
                api_key=os.getenv("DEEPSEEK_API_KEY"),
                base_url=os.getenv("DEEPSEEK_API_URL"),
                temperature=0.1,  # 低温度确保修复准确性
                max_tokens=200
            )
        )
    
    def get_format_instructions(self) -> str:
        """获取格式指令"""
        return self.base_parser.get_format_instructions()
    
    async def parse_advice(self, llm_output: str) -> MedicalAdviceResponse:
        """解析LLM输出，自动修复格式错误"""
        try:
            # 首先尝试基础解析
            return self.base_parser.parse(llm_output)
        except Exception as e:
            logger.warning(f"LLM输出解析失败，尝试自动修复: {e}")
            try:
                # 使用修复解析器
                return await self.fixing_parser.aparse(llm_output)
            except Exception as fix_error:
                logger.error(f"输出修复失败: {fix_error}")
                # 返回降级响应
                return MedicalAdviceResponse(
                    assessment="系统暂时无法生成详细建议",
                    immediate_actions=["保持冷静", "观察症状变化"],
                    medical_advice="请及时就医",
                    monitoring_points=["体温", "症状严重程度", "新出现症状"],
                    emergency_handling="如出现呼吸困难、意识模糊等紧急情况，立即拨打120"
                )
```

## 二、增强的LLM服务（集成Pydantic验证）

```python
# services/llm_service.py
import os
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import PromptTemplate
from models.medical_models import MedicalAdviceRequest, MedicalAdviceResponse
from utils.output_parsers import MedicalOutputParser
from utils.logger import logger

class EnhancedLLMService:
    """增强的LLM服务，集成Pydantic验证和输出解析"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=os.getenv("DEEPSEEK_MODEL"),
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url=os.getenv("DEEPSEEK_API_URL"),
            temperature=float(os.getenv("TEMPERATURE", 0.7)),
            max_tokens=int(os.getenv("MAX_TOKENS", 250))
        )
        self.output_parser = MedicalOutputParser()
        
        # 构建增强的Prompt模板
        self.prompt_template = PromptTemplate(
            template="""你是一个专业的医疗导诊AI助手。请根据提供的医疗信息生成准确、安全的建议。

## 格式要求
{format_instructions}

## 患者信息
- 年龄: {age}
- 性别: {gender}
- 特殊状况: {special_conditions}

## 症状信息
- 疑似疾病: {disease_name}
- 匹配症状: {matched_symptoms}

## 处理指南
- 紧急程度: {urgency}
- 建议措施: {recommended_action}

## 风险提示
- 注意事项: {special_notes}
- 风险人群: {risk_groups}

请生成专业的医疗建议：""",
            input_variables=[
                "age", "gender", "special_conditions",
                "disease_name", "matched_symptoms",
                "urgency", "recommended_action",
                "special_notes", "risk_groups"
            ],
            partial_variables={
                "format_instructions": self.output_parser.get_format_instructions()
            }
        )
    
    async def generate_structured_advice(self, request: MedicalAdviceRequest) -> MedicalAdviceResponse:
        """生成结构化的医疗建议"""
        try:
            # 构建Prompt
            prompt = self.prompt_template.format(
                age=request.patient_info.age,
                gender=request.patient_info.gender,
                special_conditions=request.patient_info.special_conditions or "无",
                disease_name=request.symptom_info.disease_name,
                matched_symptoms=", ".join(request.symptom_info.matched_symptoms),
                urgency=request.guideline_info.urgency.value,
                recommended_action=request.guideline_info.recommended_action,
                special_notes=request.risk_info.special_notes,
                risk_groups=", ".join(request.risk_info.risk_groups)
            )
            
            # 调用LLM
            response = await self.llm.agenerate([
                [
                    SystemMessage(content="你是一个专业的医疗导诊AI助手"),
                    HumanMessage(content=prompt)
                ]
            ])
            
            # 解析并验证输出
            llm_output = response.generations[0][0].text
            parsed_advice = await self.output_parser.parse_advice(llm_output)
            
            return parsed_advice
            
        except Exception as e:
            logger.error(f"生成结构化建议失败: {e}")
            return self._get_fallback_response(request)
    
    def _get_fallback_response(self, request: MedicalAdviceRequest) -> MedicalAdviceResponse:
        """降级响应"""
        return MedicalAdviceResponse(
            assessment=f"根据症状描述，疑似{request.symptom_info.disease_name}",
            immediate_actions=["保持冷静", "观察症状变化"],
            medical_advice=request.guideline_info.recommended_action,
            monitoring_points=["体温", "症状严重程度", "精神状态"],
            emergency_handling="如症状加重或出现紧急情况，请立即就医"
        )
    
    async def generate_text_advice(self, request: MedicalAdviceRequest) -> str:
        """生成文本格式的建议（兼容旧版本）"""
        structured_advice = await self.generate_structured_advice(request)
        
        # 将结构化建议转换为文本格式
        advice_text = f"""
## 状况评估
{structured_advice.assessment}

## 立即措施
{chr(10).join(f'- {action}' for action in structured_advice.immediate_actions)}

## 就医建议
{structured_advice.medical_advice}

## 观察要点
{chr(10).join(f'- {point}' for point in structured_advice.monitoring_points)}
"""
        
        if structured_advice.emergency_handling:
            advice_text += f"\n## 紧急处理\n{structured_advice.emergency_handling}"
        
        return advice_text.strip()
```

## 三、增强的医疗控制器

```python
# controllers/medical_controller.py
import asyncio
from typing import Dict, Any
from services.file_storage_service import FileStorageService
from services.llm_service import EnhancedLLMService
from services.security_service import SecurityService
from models.medical_models import (
    PatientInfo, SymptomInfo, GuidelineInfo, RiskInfo,
    MedicalAdviceRequest, MedicalQueryResult, UrgencyLevel
)
from utils.logger import logger

class EnhancedMedicalController:
    """增强的医疗控制器，集成Pydantic验证"""
    
    def __init__(self):
        self.storage_service = FileStorageService()
        self.llm_service = EnhancedLLMService()
        self.security_service = SecurityService()
    
    async def process_query(self, symptom_text: str, patient_info: Dict[str, Any]) -> MedicalQueryResult:
        """处理医疗查询，返回结构化结果"""
        try:
            # 1. 安全检测
            if not await self.security_service.check_safety(symptom_text):
                return MedicalQueryResult(
                    status="error",
                    error_message="输入内容不安全，请重新描述症状"
                )
            
            # 2. 症状匹配
            matched_disease = await self._match_symptoms(symptom_text)
            if not matched_disease:
                return MedicalQueryResult(
                    status="no_match",
                    error_message="未找到匹配疾病，请详细描述症状"
                )
            
            # 3. 查询知识库信息
            guideline_info, risk_info = await asyncio.gather(
                self.storage_service.find_by_disease_id(matched_disease['disease_id'], 'guideline'),
                self.storage_service.find_by_disease_id(matched_disease['disease_id'], 'risk')
            )
            
            # 4. 构建Pydantic请求对象
            advice_request = self._build_advice_request(
                matched_disease, guideline_info, risk_info, patient_info
            )
            
            # 5. 生成结构化建议
            structured_advice = await self.llm_service.generate_structured_advice(advice_request)
            
            # 6. 转换为文本建议（兼容性）
            advice_text = await self.llm_service.generate_text_advice(advice_request)
            
            return MedicalQueryResult(
                status="success",
                disease_name=matched_disease['name'],
                advice=advice_text,
                urgency=UrgencyLevel(guideline_info.get('urgency', 'unknown')),
                supplementary_info={
                    "structured_advice": structured_advice.dict(),
                    "guideline": guideline_info,
                    "risk": risk_info
                }
            )
            
        except Exception as e:
            logger.error(f"处理查询失败: {e}")
            return MedicalQueryResult(
                status="error",
                error_message="系统处理失败，请稍后重试"
            )
    
    def _build_advice_request(self, matched_disease: Dict, guideline_info: Dict, 
                            risk_info: Dict, patient_info: Dict) -> MedicalAdviceRequest:
        """构建医疗建议请求"""
        # 转换患者信息
        patient = PatientInfo(**patient_info)
        
        # 转换症状信息
        symptom = SymptomInfo(
            disease_id=matched_disease['disease_id'],
            disease_name=matched_disease['name'],
            matched_symptoms=matched_disease['matched_symptoms'],
            confidence=matched_disease.get('confidence', 0.8)
        )
        
        # 转换指南信息
        guideline = GuidelineInfo(
            disease_id=matched_disease['disease_id'],
            urgency=UrgencyLevel(guideline_info.get('urgency', 'unknown')),
            recommended_action=guideline_info.get('recommended_action', '请及时就医'),
            timeframe=guideline_info.get('timeframe')
        )
        
        # 转换风险信息
        risk = RiskInfo(
            disease_id=matched_disease['disease_id'],
            special_notes=risk_info.get('special_notes', '无特殊注意事项'),
            risk_groups=risk_info.get('risk_groups', []),
            contraindications=risk_info.get('contraindications')
        )
        
        return MedicalAdviceRequest(
            symptom_info=symptom,
            guideline_info=guideline,
            risk_info=risk,
            patient_info=patient
        )
    
    async def _match_symptoms(self, symptom_text: str) -> Dict[str, Any]:
        """症状匹配"""
        symptoms_data = await self.storage_service.get_symptom_data()
        
        for disease in symptoms_data:
            matched_symptoms = []
            for symptom in disease.get('related_symptoms', []):
                if symptom in symptom_text:
                    matched_symptoms.append(symptom)
            
            if matched_symptoms:
                return {
                    'disease_id': disease['disease_id'],
                    'name': disease['name'],
                    'matched_symptoms': matched_symptoms,
                    'confidence': len(matched_symptoms) / len(disease.get('related_symptoms', []))
                }
        
        return {}
```

## 四、增强的API接口

```python
# app.py
from flask import Flask, request, jsonify
from controllers.medical_controller import EnhancedMedicalController
from models.medical_models import MedicalQueryResult, PatientInfo
from utils.logger import setup_logger
import asyncio

# 配置日志
setup_logger()

app = Flask(__name__)
medical_controller = EnhancedMedicalController()

@app.route('/api/medical/query', methods=['POST'])
async def medical_query():
    """医疗查询API"""
    try:
        data = request.get_json()
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
        patient_info = PatientInfo(**data.get('patient_info', {}))
        
        # 这里可以添加更复杂的结构化查询逻辑
        result = await medical_controller.process_query(
            data.get('symptom', ''),
            patient_info.dict()
        )
        
        return jsonify(result.dict())
        
    except Exception as e:
        error_result = MedicalQueryResult(
            status="error",
            error_message=f"请求数据格式错误: {str(e)}"
        )
        return jsonify(error_result.dict()), 400
```

## 五、依赖更新

```txt
# requirements.txt
# 核心依赖
flask==2.3.3
streamlit==1.28.0
langchain==0.0.346
openai==0.28.0

# Pydantic相关
pydantic==1.10.12

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
mypy==1.5.1
```

## 六、优势总结

### ✅ Pydantic带来的好处
1. **数据验证**：自动验证输入输出数据的完整性和正确性
2. **类型安全**：完整的类型提示，减少运行时错误
3. **文档生成**：自动生成API文档和模型说明
4. **序列化**：方便的dict()和json()转换

### ✅ LangChain输出解析器的优势
1. **格式修复**：自动修复LLM输出格式错误
2. **结构保证**：确保返回数据符合预定结构
3. **错误恢复**：在解析失败时提供降级方案
4. **兼容性**：支持新旧版本数据格式

### ✅ 架构改进
1. **清晰的接口**：明确的输入输出模型
2. **更好的错误处理**：结构化的错误响应
3. **易于扩展**：新增字段只需更新模型
4. **测试友好**：模型验证简化测试编写

这个增强版本在保持第一版本简单性的同时，通过Pydantic和LangChain输出解析器大大提升了系统的健壮性和可靠性。