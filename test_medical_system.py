"""测试修复后的医疗诊断系统"""
import asyncio
import json
from datetime import datetime
from controllers.medical_controller import EnhancedMedicalController
from utils.enhanced_logger import logger

async def test_medical_system():
    """测试修复后的医疗诊断系统"""
    print("=" * 60)
    print("开始测试医疗诊断系统")
    print("=" * 60)
    
    # 创建控制器
    controller = EnhancedMedicalController()
    
    # 测试用例
    test_cases = [
        {
            "name": "头晕咳嗽",
            "symptom_text": "我有点头晕咳嗽",
            "patient_info": {"age": 25, "gender": "男", "special_conditions": ""}
        },
        {
            "name": "发烧头痛",
            "symptom_text": "我发烧了，头很痛",
            "patient_info": {"age": 30, "gender": "女", "special_conditions": "孕妇"}
        },
        {
            "name": "胸痛呼吸困难",
            "symptom_text": "胸口很痛，呼吸困难",
            "patient_info": {"age": 55, "gender": "男", "special_conditions": "高血压"}
        },
        {
            "name": "恶心呕吐",
            "symptom_text": "恶心想吐，肚子痛",
            "patient_info": {"age": 20, "gender": "女", "special_conditions": ""}
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}: {test_case['name']}")
        print(f"症状: {test_case['symptom_text']}")
        print(f"患者信息: {test_case['patient_info']}")
        print("-" * 40)
        
        try:
            result = await controller.process_query(
                test_case['symptom_text'],
                test_case['patient_info']
            )
            
            print(f"处理结果:")
            print(f"  状态: {result.status}")
            print(f"  匹配疾病: {result.disease_name}")
            print(f"  置信度: {result.supplementary_info.get('confidence', 0) if result.supplementary_info else 0}")
            
            if result.status == "success" and result.advice:
                # 解析JSON格式的建议
                import json
                try:
                    advice_data = json.loads(result.advice)
                    print(f"  评估: {advice_data.get('assessment', 'N/A')}")
                    print(f"  立即行动: {', '.join(advice_data.get('immediate_actions', []))}")
                    print(f"  医疗建议: {advice_data.get('medical_advice', 'N/A')}")
                    print(f"  监测要点: {', '.join(advice_data.get('monitoring_points', []))}")
                    print(f"  紧急处理: {advice_data.get('emergency_handling', 'N/A')}")
                except json.JSONDecodeError:
                    print(f"  建议内容: {result.advice}")
            elif result.error_message:
                print(f"  错误: {result.error_message}")
            
        except Exception as e:
            print(f"  异常: {str(e)}")
        
        print("\n")
    
    print("=" * 60)
    print("测试完成")
    print("=" * 60)
    print("\n请检查日志文件以查看详细的处理流程:")
    print("logs/medical_diagnosis.log")

if __name__ == "__main__":
    asyncio.run(test_medical_system())