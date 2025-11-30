"""输出解析器 - LangChain Pydantic集成"""
from langchain.output_parsers import PydanticOutputParser, OutputFixingParser
from langchain.chat_models import ChatOpenAI
from models.medical_models import MedicalAdviceResponse
import os
from utils.enhanced_logger import logger

class MedicalOutputParser:
    """医疗输出解析器，集成Pydantic验证和错误修复"""
    
    def __init__(self):
        logger.log_process_step("output_parser_init", "started")
        
        try:
            # 创建基础解析器
            self.base_parser = PydanticOutputParser(pydantic_object=MedicalAdviceResponse)
            
            # 获取LLM配置
            model_name = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
            api_key = os.getenv("DEEPSEEK_API_KEY")
            base_url = os.getenv("DEEPSEEK_API_URL")
            
            logger.log_process_step("output_parser_config", "loading", {
                "model": model_name,
                "has_api_key": bool(api_key),
                "has_base_url": bool(base_url)
            })
            
            if not api_key:
                logger.warning("API密钥未配置，将使用基础解析器")
                self.fixing_parser = None
            else:
                # 创建修复解析器
                self.fixing_parser = OutputFixingParser.from_llm(
                    parser=self.base_parser,
                    llm=ChatOpenAI(
                        model=model_name,
                        api_key=api_key,
                        base_url=base_url,
                        temperature=0.1,  # 低温度确保修复准确性
                        max_tokens=200
                    )
                )
                logger.log_process_step("output_parser_config", "completed", {
                    "fixing_parser_enabled": True
                })
            
            logger.log_process_step("output_parser_init", "completed")
            
        except Exception as e:
            logger.log_error_with_context(e, {
                "function": "__init__",
                "model": os.getenv("DEEPSEEK_MODEL"),
                "has_api_key": bool(os.getenv("DEEPSEEK_API_KEY"))
            })
            self.fixing_parser = None
    
    def get_format_instructions(self) -> str:
        """获取格式指令"""
        try:
            instructions = self.base_parser.get_format_instructions()
            logger.log_process_step("get_format_instructions", "completed", {
                "instructions_length": len(instructions)
            })
            return instructions
        except Exception as e:
            logger.log_error_with_context(e, {
                "function": "get_format_instructions"
            })
            return """请按照以下JSON格式输出医疗建议：
{
    "assessment": "状况评估",
    "immediate_actions": ["立即行动1", "立即行动2"],
    "medical_advice": "医疗建议",
    "monitoring_points": ["监测要点1", "监测要点2"],
    "emergency_handling": "紧急处理建议"
}"""
    
    async def parse_advice(self, llm_output: str) -> MedicalAdviceResponse:
        """解析LLM输出，自动修复格式错误"""
        logger.log_process_step("parse_advice", "started", {
            "output_length": len(llm_output),
            "output_preview": llm_output[:200] + "..." if len(llm_output) > 200 else llm_output
        })
        
        try:
            # 首先尝试基础解析
            logger.log_process_step("base_parser_attempt", "started")
            result = self.base_parser.parse(llm_output)
            logger.log_process_step("base_parser_attempt", "completed", {
                "parse_success": True,
                "result_type": type(result).__name__
            })
            
            logger.log_process_step("parse_advice", "completed", {
                "parse_method": "base_parser",
                "success": True
            })
            
            return result
            
        except Exception as e:
            logger.log_process_step("base_parser_attempt", "failed", {
                "error_type": type(e).__name__,
                "error_message": str(e)
            })
            
            if self.fixing_parser:
                logger.warning(f"LLM输出解析失败，尝试自动修复: {e}")
                try:
                    logger.log_process_step("fixing_parser_attempt", "started")
                    result = await self.fixing_parser.aparse(llm_output)
                    logger.log_process_step("fixing_parser_attempt", "completed", {
                        "parse_success": True
                    })
                    
                    logger.log_process_step("parse_advice", "completed", {
                        "parse_method": "fixing_parser",
                        "success": True
                    })
                    
                    return result
                    
                except Exception as fix_error:
                    logger.log_process_step("fixing_parser_attempt", "failed", {
                        "error_type": type(fix_error).__name__,
                        "error_message": str(fix_error)
                    })
                    logger.error(f"输出修复失败: {fix_error}")
            else:
                logger.warning("修复解析器未启用，使用降级响应")
            
            # 返回降级响应
            fallback_response = MedicalAdviceResponse(
                assessment="系统暂时无法生成详细建议",
                immediate_actions=["保持冷静", "观察症状变化"],
                medical_advice="请及时就医",
                monitoring_points=["体温", "症状严重程度", "新出现症状"],
                emergency_handling="如出现呼吸困难、意识模糊等紧急情况，立即拨打120"
            )
            
            logger.log_process_step("parse_advice", "completed", {
                "parse_method": "fallback",
                "success": False,
                "fallback_used": True
            })
            
            return fallback_response