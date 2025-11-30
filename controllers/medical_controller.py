"""医疗控制器 - 核心业务逻辑"""
import asyncio
import json
from typing import Dict, Any
from services.file_storage_service import FileStorageService
from services.llm_service import EnhancedLLMService
from services.smart_security_service import SmartSecurityService
from services.symptom_matcher import SymptomMatcher
from models.medical_models import (
    PatientInfo, SymptomInfo, GuidelineInfo, RiskInfo,
    MedicalAdviceRequest, MedicalQueryResult, UrgencyLevel
)
from utils.enhanced_logger import logger, log_process_step

class EnhancedMedicalController:
    """增强的医疗控制器，集成Pydantic验证"""
    
    def __init__(self):
        self.storage_service = FileStorageService()
        self.llm_service = EnhancedLLMService()
        self.security_service = SmartSecurityService()
        self.symptom_matcher = SymptomMatcher()  # 新增症状匹配器
        logger.info("EnhancedMedicalController initialized successfully")
    
    async def process_query(self, symptom_text: str, patient_info: Dict[str, Any]) -> MedicalQueryResult:
        """处理医疗查询，返回结构化结果"""
        logger.log_process_step("process_query", "started", {
            "symptom_text_length": len(symptom_text),
            "patient_info_keys": list(patient_info.keys()) if patient_info else [],
            "has_patient_info": bool(patient_info)
        })
        
        try:
            # 1. 记录用户输入
            logger.log_user_input({
                "symptom_text": symptom_text,
                "patient_info": patient_info
            }, source="medical_query")
            
            # 2. 安全检查
            logger.log_process_step("security_check", "started")
            is_safe = await self.security_service.check_safety(symptom_text)
            logger.log_process_step("security_check", "completed", {
                "status": "safe" if is_safe else "unsafe"
            })
            
            if not is_safe:
                logger.warning(f"内容安全检查失败: 输入内容不符合医疗咨询要求")
                return MedicalQueryResult(
                    status="failed",
                    error_message="输入内容包含敏感信息或不符合医疗咨询要求，请重新输入"
                )
            
            # 3. 症状匹配 - 使用新的症状匹配器
            logger.log_process_step("symptom_matching", "started")
            matched_disease = await self.symptom_matcher.match_symptoms(symptom_text)
            logger.log_process_step("symptom_matching", "completed", {
                "matched_disease": matched_disease["disease_name"],
                "confidence": matched_disease["confidence"]
            })
            
            # 4. 查询知识库
            logger.log_process_step("knowledge_base_query", "started", {
                "disease_id": matched_disease['disease_id']
            })
            
            guideline_info, risk_info = await asyncio.gather(
                self.storage_service.find_by_disease_id(matched_disease['disease_id'], 'guideline'),
                self.storage_service.find_by_disease_id(matched_disease['disease_id'], 'risk')
            )
            
            logger.log_process_step("knowledge_base_query", "completed", {
                "guideline_found": bool(guideline_info),
                "risk_found": bool(risk_info)
            })
            
            # 5. 构建Pydantic请求对象
            logger.log_process_step("build_advice_request", "started")
            advice_request = self._build_advice_request(
                matched_disease, guideline_info, risk_info, patient_info
            )
            logger.log_process_step("build_advice_request", "completed", {
                "request_type": type(advice_request).__name__
            })
            
            # 6. 生成结构化建议
            logger.log_process_step("generate_advice", "started")
            structured_advice = await self.llm_service.generate_structured_advice(advice_request)
            logger.log_process_step("generate_advice", "completed", {
                "advice_generated": bool(structured_advice),
                "assessment_length": len(structured_advice.assessment) if structured_advice else 0
            })
            
            # 7. 构建最终结果
            logger.log_process_step("build_result", "started")
            result = MedicalQueryResult(
                status="success",
                disease_name=matched_disease["disease_name"],
                advice=json.dumps(structured_advice.dict()) if structured_advice else None,
                supplementary_info={
                    "confidence": matched_disease["confidence"],
                    "matched_symptoms": matched_disease.get("matched_symptoms", [])
                }
            )
            
            logger.log_process_step("build_result", "completed", {
                "status": result.status,
                "disease_name": result.disease_name,
                "has_advice": bool(result.advice)
            })
            
            logger.info(f"查询处理成功: {result.disease_name} (置信度: {result.supplementary_info.get('confidence', 0)})")
            return result
            
        except Exception as e:
            logger.log_error_with_context(e, {
                "function": "process_query",
                "symptom_text": symptom_text[:100] + "..." if len(symptom_text) > 100 else symptom_text,
                "patient_info_keys": list(patient_info.keys()) if patient_info else []
            })
            
            logger.log_process_step("process_query", "failed", {
                "error_type": type(e).__name__,
                "error_message": str(e)
            })
            
            return MedicalQueryResult(
                status="failed",
                error_message=f"处理查询时发生错误: {str(e)}"
            )
    
    def _build_advice_request(self, matched_disease: Dict[str, Any], 
                              guideline_info: Dict[str, Any], 
                              risk_info: Dict[str, Any], 
                              patient_info: Dict[str, Any]) -> MedicalAdviceRequest:
        """构建建议请求对象"""
        logger.log_process_step("_build_advice_request", "started", {
            "matched_disease": matched_disease.get("disease_name", "unknown"),
            "has_guideline": bool(guideline_info),
            "has_risk": bool(risk_info),
            "has_patient_info": bool(patient_info)
        })
        
        # 构建请求对象
        request = MedicalAdviceRequest(
            patient_info=PatientInfo(**patient_info) if patient_info else PatientInfo(),
            symptom_info=SymptomInfo(
                disease_id=matched_disease.get("disease_id", "unknown_disease"),
                disease_name=matched_disease.get("disease_name", ""),
                matched_symptoms=matched_disease.get("matched_symptoms", []),
                confidence=matched_disease.get("confidence", 0.0)
            ),
            guideline_info=GuidelineInfo(
                disease_id=matched_disease.get("disease_id", "unknown_disease"),
                urgency=guideline_info.get("urgency", "未知") if guideline_info else "未知",
                recommended_action=guideline_info.get("recommended_action", "建议就医") if guideline_info else "建议就医"
            ) if guideline_info else GuidelineInfo(
                disease_id=matched_disease.get("disease_id", "unknown_disease"),
                urgency="未知",
                recommended_action="建议就医"
            ),
            risk_info=RiskInfo(
                disease_id=matched_disease.get("disease_id", "unknown_disease"),
                special_notes=risk_info.get("special_notes", "暂无特殊注意事项") if risk_info else "暂无特殊注意事项",
                risk_groups=risk_info.get("risk_groups", ["一般人群"]) if risk_info else ["一般人群"]
            ) if risk_info else RiskInfo(
                disease_id=matched_disease.get("disease_id", "unknown_disease"),
                special_notes="暂无特殊注意事项",
                risk_groups=["一般人群"]
            )
        )
        
        logger.log_process_step("_build_advice_request", "completed", {
            "request_type": type(request).__name__,
            "has_patient_info": bool(request.patient_info.age or request.patient_info.gender)
        })
        
        return request