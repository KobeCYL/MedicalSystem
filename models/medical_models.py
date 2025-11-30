"""医疗数据模型 - Pydantic增强版"""
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