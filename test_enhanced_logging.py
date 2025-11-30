"""测试优化后的日志系统"""
import asyncio
import json
from datetime import datetime
from models.medical_models import (
    MedicalAdviceRequest, PatientInfo, SymptomInfo, 
    GuidelineInfo, RiskInfo, MedicalAdviceResponse
)
from services.llm_service import EnhancedLLMService
from utils.enhanced_logger import logger

async def test_enhanced_logging():
    """测试增强的日志系统"""
    print("=" * 60)
    print("开始测试增强日志系统")
    print("=" * 60)
    
    # 测试用户输入日志
    print("\n1. 测试用户输入日志记录")
    logger.log_user_input({
        "symptom_text": "头痛发烧",
        "patient_info": {"age": 25, "gender": "male"}
    }, source="test_script")
    
    # 测试LLM调用日志
    print("\n2. 测试LLM调用日志记录")
    logger.log_llm_call(
        prompt="测试提示词内容...",
        response="测试响应内容...",
        model="deepseek-chat",
        tokens_used=150,
        duration=2.5
    )
    
    # 测试流程节点日志
    print("\n3. 测试流程节点日志记录")
    logger.log_process_step("test_workflow", "started", {
        "step_name": "symptom_analysis",
        "input_data": "头痛发烧"
    })
    
    logger.log_process_step("test_workflow", "completed", {
        "step_name": "symptom_analysis", 
        "matched_symptoms": ["头痛", "发烧"],
        "processing_time": 1.2
    })
    
    # 测试错误日志
    print("\n4. 测试错误日志记录")
    try:
        raise ValueError("测试错误")
    except Exception as e:
        logger.log_error_with_context(e, {
            "function": "test_function",
            "input_data": "测试数据",
            "user_id": "test_user"
        })
    
    # 测试性能指标
    print("\n5. 测试性能指标记录")
    logger.log_performance_metrics("test_operation", {
        "total_time": 5.5,
        "llm_time": 3.2,
        "parsing_time": 1.3,
        "output_length": 200,
        "model": "deepseek-chat"
    })
    
    # 测试实际的LLM服务调用
    print("\n6. 测试实际LLM服务调用")
    try:
        llm_service = EnhancedLLMService()
        
        # 创建测试请求
        request = MedicalAdviceRequest(
            patient_info=PatientInfo(
                age=30,
                gender="female",
                special_conditions="无"
            ),
            symptom_info=SymptomInfo(
                disease_name="感冒",
                matched_symptoms=["头痛", "发烧", "咳嗽"]
            ),
            guideline_info=GuidelineInfo(
                urgency="low",
                recommended_action="多休息，多喝水"
            ),
            risk_info=RiskInfo(
                special_notes="注意休息",
                risk_groups=["一般人群"]
            )
        )
        
        logger.info("开始调用LLM服务生成建议...")
        response = await llm_service.generate_structured_advice(request)
        
        if response:
            logger.info(f"成功生成建议: {response.assessment}")
            logger.info(f"立即行动: {response.immediate_actions}")
            logger.info(f"医疗建议: {response.medical_advice}")
            logger.info(f"监测要点: {response.monitoring_points}")
        else:
            logger.warning("未生成有效的建议响应")
            
    except Exception as e:
        logger.error(f"LLM服务测试失败: {e}")
    
    print("\n" + "=" * 60)
    print("日志系统测试完成")
    print("=" * 60)
    print("\n请检查日志文件以查看详细的日志输出")
    print("日志文件位置: logs/medical_diagnosis.log")

if __name__ == "__main__":
    asyncio.run(test_enhanced_logging())