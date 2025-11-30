from typing import Dict, Optional, List
from models.disease_model import DiseaseModel, GuidelineModel, DiseaseInfoModel
from utils.logger import get_logger


class DiseaseController:
    """疾病控制器类，负责处理疾病相关的业务逻辑"""
    
    def __init__(self):
        self.disease_model = DiseaseModel()
        self.guideline_model = GuidelineModel()
        self.disease_info_model = DiseaseInfoModel()
        self.logger = get_logger('disease_controller')
    
    def get_disease_info(self, disease_id: str) -> Optional[Dict]:
        """获取疾病完整信息（包括症状、指南和附加信息）"""
        self.logger.info(f"开始获取疾病信息: {disease_id}", 
                       source_file=__file__, source_module="DiseaseController")
        
        disease_info = self.disease_model.get_disease_by_id(disease_id)
        if not disease_info:
            self.logger.warning(f"未找到疾病信息: {disease_id}", 
                             source_file=__file__, source_module="DiseaseController")
            return None
        
        guideline_info = self.guideline_model.get_guideline_by_id(disease_id)
        disease_additional_info = self.disease_info_model.get_disease_info_by_id(disease_id)
        
        # 合并疾病信息、指南信息和附加信息
        if guideline_info:
            disease_info.update(guideline_info)
        if disease_additional_info:
            disease_info.update(disease_additional_info)
        
        self.logger.info(f"成功获取疾病信息: {disease_id}", 
                       source_file=__file__, source_module="DiseaseController")
        return disease_info
    
    def get_guideline_by_id(self, disease_id: str) -> Optional[Dict]:
        """根据疾病ID获取医疗指南"""
        self.logger.info(f"获取医疗指南: {disease_id}", 
                       source_file=__file__, source_module="DiseaseController")
        guideline = self.guideline_model.get_guideline_by_id(disease_id)
        if not guideline:
            self.logger.warning(f"未找到医疗指南: {disease_id}", 
                             source_file=__file__, source_module="DiseaseController")
        return guideline
    
    def search_diseases_by_symptom(self, symptom: str) -> List[Dict]:
        """根据症状搜索相关疾病"""
        diseases = self.disease_model.get_all_diseases()
        matching_diseases = []
        
        for disease in diseases:
            symptoms = disease.get('related_symptoms', [])
            if symptom in symptoms:
                matching_diseases.append(disease)
        
        return matching_diseases
    
    def get_emergency_guidelines(self) -> List[Dict]:
        """获取紧急情况的医疗指南"""
        return self.guideline_model.get_guidelines_by_urgency('紧急')
    
    def get_high_urgency_guidelines(self) -> List[Dict]:
        """获取高紧急程度的医疗指南"""
        return self.guideline_model.get_guidelines_by_urgency('高')
    
    def get_all_diseases_with_guidelines(self) -> List[Dict]:
        """获取所有疾病及其指南信息"""
        self.logger.info("开始获取所有疾病信息", 
                       source_file=__file__, source_module="DiseaseController")
        
        diseases = self.disease_model.get_all_diseases()
        result = []
        
        for disease in diseases:
            disease_id = disease.get('disease_id')
            if disease_id:
                guideline_info = self.guideline_model.get_guideline_by_id(disease_id)
                disease_additional_info = self.disease_info_model.get_disease_info_by_id(disease_id)
                
                # 合并信息
                if guideline_info:
                    disease.update(guideline_info)
                if disease_additional_info:
                    disease.update(disease_additional_info)
                
                result.append(disease)
        
        self.logger.info(f"成功获取 {len(result)} 个疾病信息", 
                       source_file=__file__, source_module="DiseaseController")
        return result
    
    def get_disease_info_by_id(self, disease_id: str) -> Optional[Dict]:
        """根据疾病ID获取疾病附加信息"""
        self.logger.info(f"获取疾病附加信息: {disease_id}", 
                       source_file=__file__, source_module="DiseaseController")
        disease_info = self.disease_info_model.get_disease_info_by_id(disease_id)
        if not disease_info:
            self.logger.warning(f"未找到疾病附加信息: {disease_id}", 
                             source_file=__file__, source_module="DiseaseController")
        return disease_info