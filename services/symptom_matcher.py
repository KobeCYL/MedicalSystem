"""症状匹配服务 - 基于关键词和相似度匹配"""
import re
from typing import Dict, Any, List
from utils.enhanced_logger import logger

class SymptomMatcher:
    """症状匹配器"""
    
    def __init__(self):
        # 定义关键词到疾病的映射
        self.keyword_disease_map = {
            "头晕": ["D04"],  # 高血压急症风险
            "咳嗽": ["D01"],  # 普通感冒
            "发烧": ["D01"],  # 普通感冒
            "发热": ["D01"],  # 普通感冒
            "头痛": ["D04"],  # 高血压急症风险
            "胸痛": ["D05"],  # 心脏病发作风险
            "恶心": ["D03"],  # 急性肠胃炎
            "呕吐": ["D03"],  # 急性肠胃炎
            "腹泻": ["D03"],  # 急性肠胃炎
            "打喷嚏": ["D01", "D02"],  # 普通感冒或过敏性鼻炎
            "流鼻涕": ["D01", "D02"],  # 普通感冒或过敏性鼻炎
            "鼻子痒": ["D02"],  # 过敏性鼻炎
        }
        
        # 疾病详细信息
        self.disease_info = {
            "D01": {
                "name": "普通感冒",
                "confidence": 0.8,
                "matched_symptoms": []
            },
            "D02": {
                "name": "过敏性鼻炎", 
                "confidence": 0.7,
                "matched_symptoms": []
            },
            "D03": {
                "name": "急性肠胃炎",
                "confidence": 0.85,
                "matched_symptoms": []
            },
            "D04": {
                "name": "高血压急症风险",
                "confidence": 0.9,
                "matched_symptoms": []
            },
            "D05": {
                "name": "心脏病发作风险",
                "confidence": 0.95,
                "matched_symptoms": []
            }
        }
    
    async def match_symptoms(self, symptom_text: str) -> Dict[str, Any]:
        """根据症状文本匹配疾病"""
        logger.log_process_step("symptom_matching", "started", {
            "symptom_text": symptom_text[:100] + "..." if len(symptom_text) > 100 else symptom_text
        })
        
        try:
            # 提取关键词
            keywords = self._extract_keywords(symptom_text)
            logger.log_process_step("keyword_extraction", "completed", {
                "extracted_keywords": keywords,
                "keyword_count": len(keywords)
            })
            
            if not keywords:
                logger.warning("未提取到任何关键词")
                return self._get_default_result()
            
            # 匹配疾病
            matched_diseases = self._match_diseases(keywords)
            logger.log_process_step("disease_matching", "completed", {
                "matched_diseases": list(matched_diseases.keys()),
                "total_matches": len(matched_diseases)
            })
            
            if not matched_diseases:
                logger.warning("未匹配到任何疾病")
                return self._get_default_result()
            
            # 选择最佳匹配
            best_match = self._select_best_match(matched_diseases)
            logger.log_process_step("best_match_selection", "completed", {
                "best_disease": best_match["disease_id"],
                "confidence": best_match["confidence"],
                "matched_symptoms": best_match["matched_symptoms"]
            })
            
            return best_match
            
        except Exception as e:
            logger.log_error_with_context(e, {
                "function": "match_symptoms",
                "symptom_text": symptom_text[:100] + "..." if len(symptom_text) > 100 else symptom_text
            })
            return self._get_default_result()
    
    def _extract_keywords(self, text: str) -> List[str]:
        """从文本中提取关键词"""
        keywords = []
        text_lower = text.lower()
        
        for keyword in self.keyword_disease_map.keys():
            if keyword in text_lower:
                keywords.append(keyword)
        
        return keywords
    
    def _match_diseases(self, keywords: List[str]) -> Dict[str, Dict[str, Any]]:
        """根据关键词匹配疾病"""
        disease_matches = {}
        
        for keyword in keywords:
            disease_ids = self.keyword_disease_map.get(keyword, [])
            
            for disease_id in disease_ids:
                if disease_id not in disease_matches:
                    disease_matches[disease_id] = {
                        "disease_id": disease_id,
                        "disease_name": self.disease_info[disease_id]["name"],
                        "confidence": self.disease_info[disease_id]["confidence"],
                        "matched_symptoms": [keyword],
                        "match_count": 1
                    }
                else:
                    # 增加匹配计数和症状
                    disease_matches[disease_id]["matched_symptoms"].append(keyword)
                    disease_matches[disease_id]["match_count"] += 1
                    # 提高置信度（最多到0.99）
                    disease_matches[disease_id]["confidence"] = min(
                        0.99, 
                        disease_matches[disease_id]["confidence"] + 0.1
                    )
        
        return disease_matches
    
    def _select_best_match(self, matched_diseases: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """选择最佳匹配的疾病"""
        if len(matched_diseases) == 1:
            return list(matched_diseases.values())[0]
        
        # 按匹配数量和置信度排序
        sorted_diseases = sorted(
            matched_diseases.values(),
            key=lambda x: (x["match_count"], x["confidence"]),
            reverse=True
        )
        
        return sorted_diseases[0]
    
    def _get_default_result(self) -> Dict[str, Any]:
        """获取默认结果（当无法匹配时）"""
        return {
            "disease_id": "D01",  # 默认普通感冒
            "disease_name": "普通感冒",
            "confidence": 0.3,
            "matched_symptoms": ["一般不适"]
        }