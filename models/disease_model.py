import json
import os
from typing import List, Dict, Optional
from utils.logger import get_logger


class DiseaseModel:
    """疾病数据模型类，负责从JSON文件读取疾病数据"""
    
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        self.logger = get_logger('disease_model')
    
    def _load_json_file(self, filename: str) -> List[Dict]:
        """加载JSON文件"""
        filepath = os.path.join(self.data_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                data = json.load(file)
                self.logger.info(f"成功加载文件: {filename}", 
                               source_file=__file__, source_module="DiseaseModel")
                return data
        except FileNotFoundError:
            self.logger.error(f"文件不存在: {filename}", 
                           source_file=__file__, source_module="DiseaseModel")
            return []
        except json.JSONDecodeError:
            self.logger.error(f"JSON格式错误: {filename}", 
                           source_file=__file__, source_module="DiseaseModel")
            return []
    
    def get_all_diseases(self) -> List[Dict]:
        """获取所有疾病信息"""
        return self._load_json_file('symptom.json')
    
    def get_disease_by_id(self, disease_id: str) -> Optional[Dict]:
        """根据疾病ID获取疾病信息"""
        diseases = self._load_json_file('symptom.json')
        for disease in diseases:
            if disease.get('disease_id') == disease_id:
                return disease
        return None
    
    def get_disease_by_name(self, name: str) -> Optional[Dict]:
        """根据疾病名称获取疾病信息"""
        diseases = self._load_json_file('symptom.json')
        for disease in diseases:
            if disease.get('name') == name:
                return disease
        return None


class GuidelineModel:
    """医疗指南数据模型类，负责从JSON文件读取医疗指南数据"""
    
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        self.logger = get_logger('guideline_model')
    
    def _load_json_file(self, filename: str) -> List[Dict]:
        """加载JSON文件"""
        filepath = os.path.join(self.data_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                data = json.load(file)
                self.logger.info(f"成功加载文件: {filename}", 
                               source_file=__file__, source_module="GuidelineModel")
                return data
        except FileNotFoundError:
            self.logger.error(f"文件不存在: {filename}", 
                           source_file=__file__, source_module="GuidelineModel")
            return []
        except json.JSONDecodeError:
            self.logger.error(f"JSON格式错误: {filename}", 
                           source_file=__file__, source_module="GuidelineModel")
            return []
    
    def get_guideline_by_id(self, disease_id: str) -> Optional[Dict]:
        """根据疾病ID获取医疗指南信息"""
        guidelines = self._load_json_file('guideline.json')
        for guideline in guidelines:
            if guideline.get('disease_id') == disease_id:
                return guideline
        return None
    
    def get_all_guidelines(self) -> List[Dict]:
        """获取所有医疗指南信息"""
        return self._load_json_file('guideline.json')
    
    def get_guidelines_by_urgency(self, urgency: str) -> List[Dict]:
        """根据紧急程度获取医疗指南信息"""
        guidelines = self._load_json_file('guideline.json')
        return [g for g in guidelines if g.get('urgency') == urgency]


class DiseaseInfoModel:
    """疾病附加信息数据模型类，负责从JSON文件读取疾病附加信息数据"""
    
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        self.logger = get_logger('disease_info_model')
    
    def _load_json_file(self, filename: str) -> List[Dict]:
        """加载JSON文件"""
        filepath = os.path.join(self.data_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                data = json.load(file)
                self.logger.info(f"成功加载文件: {filename}", 
                               source_file=__file__, source_module="DiseaseInfoModel")
                return data
        except FileNotFoundError:
            self.logger.error(f"文件不存在: {filename}", 
                           source_file=__file__, source_module="DiseaseInfoModel")
            return []
        except json.JSONDecodeError:
            self.logger.error(f"JSON格式错误: {filename}", 
                           source_file=__file__, source_module="DiseaseInfoModel")
            return []
    
    def get_disease_info_by_id(self, disease_id: str) -> Optional[Dict]:
        """根据疾病ID获取疾病附加信息"""
        disease_infos = self._load_json_file('disease_info.json')
        for disease_info in disease_infos:
            if disease_info.get('disease_id') == disease_id:
                return disease_info
        return None
    
    def get_all_disease_infos(self) -> List[Dict]:
        """获取所有疾病附加信息"""
        return self._load_json_file('disease_info.json')