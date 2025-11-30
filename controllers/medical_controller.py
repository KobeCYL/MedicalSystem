"""医疗控制器 - 核心业务逻辑"""
import asyncio
import json
import time
import os
from datetime import datetime
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
    
    async def process_query(self, symptom_text: str, patient_info: Dict[str, Any], client_start_ts: str = None) -> MedicalQueryResult:
        """处理医疗查询，返回结构化结果"""
        start_perf = time.perf_counter()
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
                intent = getattr(self.security_service, 'last_intent_assessment', None)
                result_model = MedicalQueryResult(
                    status="failed",
                    error_message=(
                        f"输入内容不符合医疗咨询要求：{intent.get('reason')} (置信度: {intent.get('confidence')})"
                        if intent else "输入内容不符合医疗咨询要求，请重新输入"
                    )
                )
                self._append_query_history({
                    "timestamp": datetime.now().isoformat(),
                    "symptom": symptom_text,
                    "patient_info": patient_info,
                    "result": result_model.dict(),
                    "server_duration_ms": int((time.perf_counter() - start_perf) * 1000),
                    "duration_ms": int((time.perf_counter() - start_perf) * 1000),
                    "client_start_ts": client_start_ts,
                    "total_duration_ms": self._calc_total_duration_ms(client_start_ts)
                })
                return result_model
            
            # 2.1 进一步验证是否为医疗咨询
            if not self.security_service.is_medical_query(symptom_text):
                logger.warning("缺乏有效的症状描述或医疗咨询意图")
                intent = getattr(self.security_service, 'last_intent_assessment', None)
                result_model = MedicalQueryResult(
                    status="no_match",
                    error_message=(
                        f"请用医疗症状进行描述，当前输入被判定为非病情文本：{intent.get('reason')} (置信度: {intent.get('confidence')})"
                        if intent else "请用医疗症状进行描述（如：头痛、发烧、咳嗽、胸痛等），避免角色扮演或系统指令类文本"
                    )
                )
                self._append_query_history({
                    "timestamp": datetime.now().isoformat(),
                    "symptom": symptom_text,
                    "patient_info": patient_info,
                    "result": result_model.dict(),
                    "server_duration_ms": int((time.perf_counter() - start_perf) * 1000),
                    "duration_ms": int((time.perf_counter() - start_perf) * 1000),
                    "client_start_ts": client_start_ts,
                    "total_duration_ms": self._calc_total_duration_ms(client_start_ts)
                })
                return result_model
            
            # 3. 症状匹配 - 使用新的症状匹配器
            logger.log_process_step("symptom_matching", "started")
            matched_disease = await self.symptom_matcher.match_symptoms(symptom_text)
            logger.log_process_step("symptom_matching", "completed", {
                "matched_disease": matched_disease["disease_name"],
                "confidence": matched_disease["confidence"]
            })
            candidates = matched_disease.get("candidates", [matched_disease])
            logger.log_process_step("candidate_list", "completed", {
                "count": len(candidates),
                "top_ids": [c.get("disease_id") for c in candidates[:3]],
                "top_names": [c.get("disease_name") for c in candidates[:3]],
                "top_confidences": [c.get("confidence") for c in candidates[:3]]
            })
            
            # 4. 查询知识库
            logger.log_process_step("knowledge_base_query", "started", {
                "disease_id": matched_disease['disease_id'],
                "candidate_ids": [c.get('disease_id') for c in candidates]
            })
            
            guideline_info, risk_info = await asyncio.gather(
                self.storage_service.find_by_disease_id(matched_disease['disease_id'], 'guideline'),
                self.storage_service.find_by_disease_id(matched_disease['disease_id'], 'risk')
            )
            candidate_evidence = []
            for c in candidates:
                gid = c.get('disease_id')
                gi = await self.storage_service.find_by_disease_id(gid, 'guideline')
                ri = await self.storage_service.find_by_disease_id(gid, 'risk')
                candidate_evidence.append({
                    'disease_id': gid,
                    'disease_name': c.get('disease_name'),
                    'confidence': c.get('confidence'),
                    'matched_symptoms': c.get('matched_symptoms', []),
                    'guideline': gi,
                    'risk': ri
                })
            
            logger.log_process_step("knowledge_base_query", "completed", {
                "guideline_found": bool(guideline_info),
                "risk_found": bool(risk_info),
                "candidates_queried": len(candidate_evidence)
            })
            
            # 5. 构建Pydantic请求对象
            logger.log_process_step("build_advice_request", "started")
            advice_request = self._build_advice_request(
                matched_disease, guideline_info, risk_info, patient_info
            )
            logger.log_process_step("build_advice_request", "completed", {
                "request_type": type(advice_request).__name__
            })
            composite_prompt = getattr(self.llm_service, 'build_multi_candidate_prompt', None)
            if composite_prompt:
                multi_prompt = self.llm_service.build_multi_candidate_prompt(patient_info, candidate_evidence)
                logger.log_process_step("composite_prompt", "prepared", {
                    "candidate_count": len(candidate_evidence),
                    "prompt_length": len(multi_prompt),
                    "prompt_preview": multi_prompt[:200]
                })
                logger.log_process_step("next_task", "planned", {"task": "multi_candidate_analysis"})
                multi_analysis = await self.llm_service.generate_multi_candidate_analysis(patient_info, candidate_evidence)
                logger.log_process_step("multi_candidate_analysis", "completed", {
                    "probabilities_count": len(multi_analysis.get('probabilities', []))
                })
                # 后端补充疾病名称与最佳候选
                id_to_name = {c.get('disease_id'): c.get('disease_name') for c in candidate_evidence}
                id_to_g = {c.get('disease_id'): c.get('guideline') for c in candidate_evidence}
                id_to_r = {c.get('disease_id'): c.get('risk') for c in candidate_evidence}
                probs = multi_analysis.get('probabilities') or []
                for pr in probs:
                    did = pr.get('disease_id')
                    if did and not pr.get('disease_name'):
                        pr['disease_name'] = id_to_name.get(did)
                best = None
                if probs:
                    best = sorted(probs, key=lambda x: x.get('probability', 0), reverse=True)[0]
                best_candidate = None
                if best and best.get('disease_id'):
                    did = best['disease_id']
                    best_candidate = {
                        'disease_id': did,
                        'disease_name': best.get('disease_name') or id_to_name.get(did),
                        'probability': best.get('probability', 0),
                        'guideline': id_to_g.get(did),
                        'risk': id_to_r.get(did)
                    }
                multi_analysis['probabilities'] = probs
                multi_analysis['best_candidate'] = best_candidate
            
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
                urgency=advice_request.guideline_info.urgency,
                advice=json.dumps(structured_advice.dict()) if structured_advice else None,
                supplementary_info={
                    "confidence": matched_disease["confidence"],
                    "matched_symptoms": matched_disease.get("matched_symptoms", []),
                    "candidates": candidate_evidence,
                    "multi_analysis": multi_analysis if composite_prompt else None
                }
            )
            
            logger.log_process_step("build_result", "completed", {
                "status": result.status,
                "disease_name": result.disease_name,
                "has_advice": bool(result.advice)
            })
            
            logger.info(f"查询处理成功: {result.disease_name} (置信度: {result.supplementary_info.get('confidence', 0)})")
            self._append_query_history({
                "timestamp": datetime.now().isoformat(),
                "symptom": symptom_text,
                "patient_info": patient_info,
                "result": result.dict(),
                "server_duration_ms": int((time.perf_counter() - start_perf) * 1000),
                "duration_ms": int((time.perf_counter() - start_perf) * 1000),
                "client_start_ts": client_start_ts,
                "total_duration_ms": self._calc_total_duration_ms(client_start_ts)
            })
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

    def _append_query_history(self, entry: dict):
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            logs_dir = os.path.join(project_root, "logs")
            os.makedirs(logs_dir, exist_ok=True)
            path = os.path.join(logs_dir, "query_history.json")
            tmp_path = path + ".tmp"
            data = []
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        obj = json.load(f)
                        if isinstance(obj, list):
                            data = obj
                except Exception:
                    data = []
            data.append(entry)
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            os.replace(tmp_path, path)
        except Exception as e:
            logger.warning(str(e))

    def _calc_total_duration_ms(self, client_start_ts: str):
        try:
            if not client_start_ts:
                return None
            cs = datetime.fromisoformat(client_start_ts)
            return int((datetime.now() - cs).total_seconds() * 1000)
        except Exception:
            return None
