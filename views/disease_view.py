from utils.logger import get_logger


class DiseaseView:
    """疾病视图类，负责显示疾病信息给用户"""
    
    def __init__(self):
        self.logger = get_logger('disease_view')
    
    def display_disease_info(self, disease_info: dict):
        """显示疾病详细信息"""
        if not disease_info:
            self.logger.warning("显示疾病信息失败: 未找到疾病信息", 
                             source_file=__file__, source_module="DiseaseView")
            print("未找到该疾病信息")
            return
        
        self.logger.info(f"显示疾病信息: {disease_info.get('disease_id', '未知')}", 
                       source_file=__file__, source_module="DiseaseView")
        
        print("\n" + "="*50)
        print(f"疾病名称: {disease_info.get('name', '未知')}")
        print(f"症候ID: {disease_info.get('disease_id', '未知')}")
        print("-" * 30)
        
        # 显示症状信息
        symptoms = disease_info.get('related_symptoms', [])
        if symptoms:
            print("关联症状:")
            for symptom in symptoms:
                print(f"  - {symptom}")
        
        # 显示指南信息
        urgency = disease_info.get('urgency')
        recommended_action = disease_info.get('recommended_action')
        
        if urgency and recommended_action:
            print("-" * 30)
            print(f"紧急程度: {urgency}")
            print(f"建议行动: {recommended_action}")
        
        # 显示附加信息
        special_notes = disease_info.get('special_notes')
        if special_notes:
            print("-" * 30)
            print("⚠️  风险提示与附加信息:")
            print(f"  {special_notes}")
        
        print("="*50 + "\n")
    
    @staticmethod
    def display_guideline_info(guideline_info: dict):
        """显示医疗指南信息"""
        if not guideline_info:
            print("未找到该疾病的医疗指南")
            return
        
        print("\n" + "="*50)
        print(f"疾病ID: {guideline_info.get('disease_id', '未知')}")
        print(f"紧急程度: {guideline_info.get('urgency', '未知')}")
        print(f"建议行动: {guideline_info.get('recommended_action', '未知')}")
        print("="*50 + "\n")
    
    @staticmethod
    def display_disease_list(diseases: list):
        """显示疾病列表"""
        if not diseases:
            print("未找到任何疾病信息")
            return
        
        print("\n" + "="*50)
        print("疾病列表:")
        print("-" * 30)
        
        for i, disease in enumerate(diseases, 1):
            print(f"{i}. {disease.get('name', '未知')} (ID: {disease.get('disease_id', '未知')})")
        
        print("="*50 + "\n")
    
    @staticmethod
    def display_search_results(diseases: list, symptom: str):
        """显示症状搜索结果"""
        if not diseases:
            print(f"未找到包含症状 '{symptom}' 的疾病")
            return
        
        print(f"\n找到 {len(diseases)} 个包含症状 '{symptom}' 的疾病:")
        print("="*50)
        
        for i, disease in enumerate(diseases, 1):
            print(f"{i}. {disease.get('name', '未知')} (ID: {disease.get('disease_id', '未知')})")
        
        print("="*50 + "\n")
    
    @staticmethod
    def display_emergency_guidelines(guidelines: list):
        """显示紧急医疗指南"""
        if not guidelines:
            print("暂无紧急医疗指南")
            return
        
        print("\n" + "="*60)
        print("⚠️  紧急医疗指南 ⚠️")
        print("="*60)
        
        for guideline in guidelines:
            print(f"\n疾病ID: {guideline.get('disease_id', '未知')}")
            print(f"紧急程度: {guideline.get('urgency', '未知')}")
            print(f"建议行动: {guideline.get('recommended_action', '未知')}")
            print("-" * 40)
        
        print("="*60 + "\n")