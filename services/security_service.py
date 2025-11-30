"""安全服务 - 输入验证和风险检测"""
import re
from typing import List
from utils.logger import logger

class SecurityService:
    """安全检测服务"""
    
    def __init__(self):
        # 恶意关键词模式
        self.malicious_patterns = [
            r'(?i)(system|prompt|ignore|previous|指令|提示|忽略|系统)',
            r'(?i)(role|play|act|as|a|an|角色|扮演|作为)',
            r'(?i)(hack|attack|inject|恶意|攻击|注入)',
            r'(?i)(password|token|key|secret|密码|密钥|秘钥)',
        ]
        
        # 医疗相关安全词
        self.medical_safe_words = [
            '头痛', '发烧', '咳嗽', '流鼻涕', '喉咙痛', '呕吐', '腹泻',
            '头晕', '乏力', '胸闷', '呼吸困难', '皮疹', '腹痛',
            '恶心', '想吐', '肚子痛', '胃痛', '胃疼', '反胃', '作呕',
            '胸口痛', '胸痛', '心疼', '心脏疼', '呼吸不畅', '气喘',
            '发热', '高烧', '低烧', '畏寒', '发冷', '寒战',
            '咳痰', '痰多', '干咳', '呛咳', '气喘', '哮喘',
            '鼻塞', '打喷嚏', '流涕', '鼻痒', '咽痛', '咽喉痛',
            '拉肚子', '腹泻', '便秘', '腹胀', '胃胀', '消化不良',
            '头晕目眩', '眩晕', '晕厥', '昏迷', '意识不清',
            '乏力', '疲劳', '虚弱', '没精神', '嗜睡', '失眠',
            '皮肤瘙痒', '红疹', '湿疹', '荨麻疹', '过敏',
            '疼痛', '酸痛', '胀痛', '刺痛', '绞痛', '隐痛',
            '心慌', '心悸', '心跳快', '心律不齐', '胸闷气短'
        ]
    
    async def check_safety(self, text: str) -> bool:
        """检查输入安全性"""
        try:
            # 空值检查
            if not text or len(text.strip()) < 3:
                return False
            
            # 长度检查
            if len(text) > 500:
                return False
            
            # 恶意模式检测
            for pattern in self.malicious_patterns:
                if re.search(pattern, text):
                    logger.warning(f"检测到恶意模式: {pattern} in {text}")
                    return False
            
            # 医疗关键词验证（至少包含一个医疗相关词）
            has_medical_keyword = any(word in text for word in self.medical_safe_words)
            if not has_medical_keyword:
                logger.warning(f"未检测到医疗关键词: {text}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"安全检测失败: {e}")
            return False
    
    def sanitize_input(self, text: str) -> str:
        """清理输入内容"""
        # 移除特殊字符和多余空格
        sanitized = re.sub(r'[<>\"\'\\]', '', text)
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()
        return sanitized[:300]  # 限制长度