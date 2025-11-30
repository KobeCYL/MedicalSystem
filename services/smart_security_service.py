"""智能安全服务 - 基于语义分析的风险检测"""
import re
import jieba
from typing import List, Dict, Tuple
from utils.logger import logger
from services.llm_service import EnhancedLLMService

class SmartSecurityService:
    """智能安全检测服务 - 使用语义分析减少误判"""
    
    def __init__(self):
        # 高风险攻击模式（这些必须严格拦截）
        self.high_risk_patterns = [
            r'(?i)(system|prompt|ignore|previous|指令|提示|忽略|系统).*(?:override|覆盖|忽略|绕过)',
            r'(?i)(hack|attack|inject|恶意|攻击|注入|破解)',
            r'(?i)(password|token|key|secret|密码|密钥|秘钥).*(?:extract|获取|泄露)',
            r'<script|javascript|sql|union|select|drop|delete',  # 代码注入
            r'\$\{.*\}|\{\{.*\}\}',  # 模板注入
            r'(?i)(忘记|忘掉).*(指令|提示|系统)',  # 指令覆盖/越权尝试
        ]
        
        # 中等风险模式（需要结合上下文判断）
        self.medium_risk_patterns = [
            r'(?i)(role|play|act|as|a|an|角色|扮演|作为)',
            r'(?i)(bypass|跳过|绕过|突破)',
            r'(?i)(admin|root|superuser|管理员|超级用户)',
        ]
        
        # 医疗相关词汇（扩大覆盖范围）
        self.medical_keywords = {
            '症状描述': ['头痛', '头晕', '眩晕', '晕', '疼', '痛', '疼', '不适', '难受', '不舒服', '发烧', '发热', '高烧', '低烧', '畏寒', '发冷', '寒战'],
            '呼吸系统': ['咳嗽', '咳痰', '痰多', '干咳', '呛咳', '气喘', '哮喘', '呼吸困难', '呼吸不畅', '胸闷', '胸痛', '胸口痛', '心疼', '心脏疼', '气喘'],
            '消化系统': ['恶心', '想吐', '呕吐', '反胃', '作呕', '肚子痛', '胃痛', '胃疼', '腹痛', '拉肚子', '腹泻', '便秘', '腹胀', '胃胀', '消化不良', '没胃口', '食欲不振'],
            '全身症状': ['乏力', '疲劳', '虚弱', '没精神', '嗜睡', '失眠', '皮肤瘙痒', '红疹', '皮疹', '湿疹', '荨麻疹', '过敏', '疼痛', '酸痛', '胀痛', '刺痛', '绞痛', '隐痛'],
            '循环系统': ['心慌', '心悸', '心跳快', '心律不齐', '胸闷气短', '血压高', '血压低', '头晕目眩'],
            '五官症状': ['鼻塞', '打喷嚏', '流涕', '鼻涕', '鼻痒', '咽痛', '咽喉痛', '喉咙痛', '嗓子疼', '声音嘶哑', '耳鸣', '听力下降', '视力模糊', '眼花'],
        }
        
        # 医疗咨询常用词（合法表达）
        self.medical_phrases = [
            '怎么办', '怎么治疗', '吃什么药', '需要看医生吗', '严重吗', '是什么问题',
            '有什么建议', '需要注意什么', '会自愈吗', '要多久才好', '为什么会这样',
            '我头很晕', '我有点咳嗽', '我感觉不舒服', '我身体不舒服'
        ]
        
        # 攻击特征词（高风险）
        self.attack_keywords = [
            '忽略', '覆盖', '绕过', '突破', '破解', '注入', '攻击', '恶意', '窃取', '泄露',
            '获取', '提取', '删除', '修改', '破坏', '禁用', '关闭', '跳过', '欺骗', '伪造'
        ]
        
        # 系统相关词（中风险，需结合上下文）
        self.system_keywords = ['系统', '程序', '代码', '脚本', '数据库', '服务器', '管理员']
        try:
            self.llm_service = EnhancedLLMService()
        except Exception:
            logger.warning("LLM服务未配置，语义分析将使用本地规则")
            self.llm_service = None
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 使用jieba分词
        words = jieba.lcut(text.lower())
        # 也保留原始文本中的关键词
        original_words = []
        for category, keywords in self.medical_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    original_words.append(keyword)
        
        return list(set(words + original_words))
    
    def _calculate_risk_score(self, text: str) -> Tuple[float, Dict[str, any]]:
        """计算风险评分"""
        risk_details = {
            'high_risk_matches': [],
            'medium_risk_matches': [],
            'medical_score': 0,
            'attack_score': 0,
            'text_length': len(text),
            'has_medical_intent': False
        }
        
        text_lower = text.lower()
        
        # 1. 高风险模式检测
        for pattern in self.high_risk_patterns:
            if re.search(pattern, text_lower):
                risk_details['high_risk_matches'].append(pattern)
        
        # 2. 中等风险模式检测
        for pattern in self.medium_risk_patterns:
            if re.search(pattern, text_lower):
                risk_details['medium_risk_matches'].append(pattern)
        
        # 3. 医疗关键词评分
        medical_count = 0
        for category, keywords in self.medical_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    medical_count += 1
                    break
        
        # 4. 医疗咨询意图检测
        has_medical_intent = any(phrase in text_lower for phrase in self.medical_phrases)
        risk_details['has_medical_intent'] = has_medical_intent
        
        # 5. 攻击关键词评分
        attack_count = sum(1 for keyword in self.attack_keywords if keyword in text_lower)
        system_count = sum(1 for keyword in self.system_keywords if keyword in text_lower)
        
        # 计算综合评分
        risk_score = 0
        
        # 高风险模式直接判定为高风险
        if risk_details['high_risk_matches']:
            risk_score += 80
        
        # 中等风险模式
        risk_score += len(risk_details['medium_risk_matches']) * 20
        
        # 攻击关键词评分
        risk_score += attack_count * 15
        
        # 系统关键词（如果同时有攻击关键词，风险加倍）
        if system_count > 0 and attack_count > 0:
            risk_score += system_count * 25
        elif system_count > 0:
            risk_score += system_count * 5
        
        # 医疗关键词降低风险
        medical_score = (medical_count * 20) + (20 if has_medical_intent else 0)
        risk_score = max(0, risk_score - medical_score)
        
        # 基础文本检查
        if len(text.strip()) < 2:  # 太短
            risk_score += 30
        elif len(text) > 200:  # 太长
            risk_score += 10
        
        risk_details['medical_score'] = medical_score
        risk_details['attack_score'] = attack_count * 15 + (system_count * 25 if attack_count > 0 else system_count * 5)
        
        return min(100, risk_score), risk_details
    
    async def check_safety(self, text: str) -> bool:
        """智能安全检测"""
        try:
            if not text or not text.strip():
                return False
            
            # 基础清理
            text = text.strip()
            
            # 非医疗咨询直接拒绝
            if not self.is_medical_query(text):
                logger.warning("输入缺乏医疗症状/咨询意图，拒绝处理")
                return False
            
            # 计算风险评分
            risk_score, risk_details = self._calculate_risk_score(text)
            
            # 记录详细的风险分析
            logger.info(f"安全检测分析: 文本='{text[:50]}...', 风险评分={risk_score:.1f}, 详情={risk_details}")
            
            # 风险判定
            if risk_score >= 70:
                logger.warning(f"高风险内容被拒绝: 评分={risk_score:.1f}, 原因={risk_details}")
                return False
            
            # 调用LLM语义判定
            if self.llm_service:
                intent = await self.llm_service.assess_medical_intent(text)
                self.last_intent_assessment = intent
                conf = int(intent.get('confidence', 0) or 0)
                is_med = bool(intent.get('is_medical', False))
                logger.info(f"LLM语义判定: is_medical={is_med}, confidence={conf}, reason={intent.get('reason')}")
                if not is_med or conf < 60:
                    logger.warning("语义判定不足以继续处理，已阻断")
                    return False
            else:
                is_med = self.is_medical_query(text)
                conf = 90 if is_med else 0
                self.last_intent_assessment = {"is_medical": is_med, "confidence": conf, "reason": "本地规则判定"}
                if not is_med or conf < 60:
                    return False
            
            return True
                
        except Exception as e:
            logger.error(f"安全检测异常: {e}")
            return False  # 出现异常时默认拒绝
    
    def is_medical_query(self, text: str) -> bool:
        """判断是否为医疗咨询"""
        try:
            text_lower = text.lower()
            
            # 检查医疗关键词
            medical_count = 0
            for category, keywords in self.medical_keywords.items():
                for keyword in keywords:
                    if keyword in text_lower:
                        medical_count += 1
                        break
            
            # 检查医疗咨询短语
            has_medical_phrase = any(phrase in text_lower for phrase in self.medical_phrases)
            
            # 简单判定：有医疗关键词或医疗咨询意图
            return medical_count > 0 or has_medical_phrase
            
        except Exception:
            return False
    
    def sanitize_input(self, text: str) -> str:
        """清理输入内容"""
        # 移除潜在危险的特殊字符，但保留基本标点
        sanitized = re.sub(r'[<>\'"\\]', '', text)
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()
        return sanitized[:300]  # 限制长度
