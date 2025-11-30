"""LLM服务 - DeepSeek集成和Pydantic验证"""
import os
import time
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import PromptTemplate
from models.medical_models import MedicalAdviceRequest, MedicalAdviceResponse
from utils.output_parsers import MedicalOutputParser
from utils.enhanced_logger import logger

class EnhancedLLMService:
    """增强的LLM服务，集成Pydantic验证和输出解析"""
    
    def __init__(self):
        self.model_name = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.base_url = os.getenv("DEEPSEEK_API_URL")
        self.temperature = float(os.getenv("TEMPERATURE", 0.7))
        self.max_tokens = int(os.getenv("MAX_TOKENS", 250))
        
        logger.info(f"Initializing LLM service with model: {self.model_name}")
        logger.log_process_step("llm_service_init", "started", {
            "model": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        })
        
        # 检查是否处于测试模式（无API密钥）
        self.test_mode = not bool(self.api_key)
        if self.test_mode:
            logger.warning("Running in test mode - no API key provided, will use mock responses")
            logger.log_process_step("llm_service_init", "test_mode_enabled", {
                "reason": "no_api_key"
            })
        
        try:
            if not self.test_mode:
                self.llm = ChatOpenAI(
                    model=self.model_name,
                    api_key=self.api_key,
                    base_url=self.base_url,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
            else:
                self.llm = None  # 测试模式下不使用实际的LLM
            
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
            
            logger.log_process_step("llm_service_init", "completed", {
                "model": self.model_name,
                "status": "initialized"
            })
            
        except Exception as e:
            logger.log_error_with_context(e, {
                "function": "__init__",
                "model": self.model_name,
                "base_url": self.base_url
            })
            raise
    
    async def generate_structured_advice(self, request: MedicalAdviceRequest) -> MedicalAdviceResponse:
        """生成结构化的医疗建议"""
        logger.log_process_step("generate_structured_advice", "started", {
            "has_patient_info": bool(request.patient_info.age or request.patient_info.gender),
            "disease_name": request.symptom_info.disease_name,
            "matched_symptoms_count": len(request.symptom_info.matched_symptoms)
        })
        
        try:
            # 构建Prompt
            logger.log_process_step("build_prompt", "started")
            prompt = self.prompt_template.format(
                age=request.patient_info.age or "未知",
                gender=request.patient_info.gender or "未知",
                special_conditions=request.patient_info.special_conditions or "无",
                disease_name=request.symptom_info.disease_name,
                matched_symptoms=", ".join(request.symptom_info.matched_symptoms),
                urgency=request.guideline_info.urgency.value,
                recommended_action=request.guideline_info.recommended_action,
                special_notes=request.risk_info.special_notes,
                risk_groups=", ".join(request.risk_info.risk_groups)
            )
            
            logger.log_process_step("build_prompt", "completed", {
                "prompt_length": len(prompt),
                "has_format_instructions": bool(self.output_parser.get_format_instructions())
            })
            
            # 记录完整的LLM调用信息
            logger.log_llm_call(
                prompt=prompt,
                response="",  # 将在获取响应后更新
                model=self.model_name,
                tokens_used=None,  # 将在获取响应后更新
                duration=None  # 将在获取响应后更新
            )
            
            # 开始计时
            logger.start_timer("llm_call")
            
            # 调用LLM或生成模拟响应
            if self.test_mode:
                logger.log_process_step("llm_call", "test_mode_mock", {
                    "model": self.model_name,
                    "note": "Using mock response for testing"
                })
                # 生成模拟的医疗建议响应
                llm_output = self._generate_mock_response(request)
                call_duration = logger.end_timer("llm_call")
            else:
                logger.log_process_step("llm_call", "started", {
                    "model": self.model_name,
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens
                })
                
                response = await self.llm.agenerate([
                    [
                        SystemMessage(content="你是一个专业的医疗导诊AI助手"),
                        HumanMessage(content=prompt)
                    ]
                ])
                
                # 记录调用耗时
                call_duration = logger.end_timer("llm_call")
                
                # 获取响应内容
                llm_output = response.generations[0][0].text
            
            logger.log_process_step("llm_call", "completed", {
                "response_length": len(llm_output),
                "duration": call_duration,
                "model": self.model_name
            })
            
            # 更新LLM调用日志
            logger.log_llm_call(
                prompt=prompt,
                response=llm_output,
                model=self.model_name,
                tokens_used=None if self.test_mode else (getattr(response, 'llm_output', {}).get("token_usage", {}).get("total_tokens") if hasattr(response, "llm_output") else None),
                duration=call_duration
            )
            
            # 解析并验证输出
            logger.log_process_step("parse_output", "started")
            logger.start_timer("output_parsing")
            
            parsed_advice = await self.output_parser.parse_advice(llm_output)
            
            parsing_time = logger.end_timer("output_parsing")
            
            logger.log_process_step("parse_output", "completed", {
                "parsing_time": parsing_time,
                "advice_valid": bool(parsed_advice),
                "advice_type": type(parsed_advice).__name__ if parsed_advice else "None"
            })
            
            # 记录最终生成的建议
            if parsed_advice:
                logger.info(f"Generated advice: {parsed_advice.assessment[:100]}...")
                logger.log_performance_metrics("advice_generation", {
                    "total_time": call_duration + parsing_time,
                    "llm_time": call_duration,
                    "parsing_time": parsing_time,
                    "output_length": len(llm_output),
                    "model": self.model_name
                })
            
            return parsed_advice
            
        except Exception as e:
            logger.log_error_with_context(e, {
                "function": "generate_structured_advice",
                "model": self.model_name,
                "disease_name": request.symptom_info.disease_name,
                "has_patient_info": bool(request.patient_info.age or request.patient_info.gender)
            })
            
            logger.log_process_step("generate_structured_advice", "failed", {
                "error_type": type(e).__name__,
                "error_message": str(e)
            })
            
            return self._get_fallback_response(request)
    
    def _get_fallback_response(self, request: MedicalAdviceRequest) -> MedicalAdviceResponse:
        """降级响应"""
        logger.log_process_step("fallback_response", "started", {
            "disease_name": request.symptom_info.disease_name
        })
        
        fallback_response = MedicalAdviceResponse(
            assessment=f"根据症状描述，疑似{request.symptom_info.disease_name}",
            immediate_actions=["保持冷静", "观察症状变化"],
            medical_advice=request.guideline_info.recommended_action,
            monitoring_points=["体温", "症状严重程度", "精神状态"],
            emergency_handling="如症状加重或出现紧急情况，请立即就医"
        )
        
        logger.log_process_step("fallback_response", "completed", {
            "assessment": fallback_response.assessment
        })
        
        return fallback_response
    
    def _generate_mock_response(self, request: MedicalAdviceRequest) -> str:
        """生成模拟的医疗建议响应（用于测试模式）"""
        logger.log_process_step("mock_response_generation", "started", {
            "disease_name": request.symptom_info.disease_name,
            "urgency": request.guideline_info.urgency.value
        })
        
        # 根据疾病和紧急程度生成合适的模拟响应
        if "感冒" in request.symptom_info.disease_name or "流感" in request.symptom_info.disease_name:
            mock_response = """{
                "assessment": "根据症状分析，疑似上呼吸道感染（普通感冒）",
                "immediate_actions": ["多休息", "多喝水", "监测体温"],
                "medical_advice": "建议居家观察1-2天，如症状加重或持续发热请及时就医",
                "monitoring_points": ["体温变化", "咳嗽程度", "精神状态"],
                "emergency_handling": "如出现高热不退、呼吸困难、胸痛等症状，请立即就医"
            }"""
        elif "心脏" in request.symptom_info.disease_name or "胸痛" in request.symptom_info.disease_name:
            mock_response = """{
                "assessment": "根据症状分析，疑似心血管相关疾病，需要专业评估",
                "immediate_actions": ["立即停止活动", "保持安静", "拨打120"],
                "medical_advice": "胸痛症状需要立即就医检查，不建议自行处理",
                "monitoring_points": ["胸痛程度", "是否放射至左臂", "伴随症状"],
                "emergency_handling": "胸痛是急症症状，请立即拨打120或前往最近医院急诊科"
            }"""
        else:
            # 默认响应
            mock_response = f"""{{
                "assessment": "根据症状分析，疑似{request.symptom_info.disease_name}",
                "immediate_actions": ["保持冷静", "观察症状变化", "记录症状发展"],
                "medical_advice": "{request.guideline_info.recommended_action}",
                "monitoring_points": ["症状严重程度", "是否出现新症状", "精神状态"],
                "emergency_handling": "如症状加重或出现紧急情况，请立即就医"
            }}"""
        
        logger.log_process_step("mock_response_generation", "completed", {
            "response_length": len(mock_response),
            "has_json_format": True
        })
        
        return mock_response