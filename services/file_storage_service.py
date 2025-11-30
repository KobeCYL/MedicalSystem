"""文件存储服务 - 第一版本使用JSON文件"""
import json
import aiofiles
import os
from typing import List, Dict, Any
from utils.enhanced_logger import logger

class FileStorageService:
    """文件存储服务，便于第二版本升级到数据库"""
    
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = data_dir
        logger.log_process_step("file_storage_init", "started", {
            "data_dir": data_dir,
            "absolute_path": os.path.abspath(data_dir)
        })
        
        # 检查数据目录是否存在
        if not os.path.exists(self.data_dir):
            logger.warning(f"数据目录不存在: {self.data_dir}")
            try:
                os.makedirs(self.data_dir, exist_ok=True)
                logger.info(f"创建数据目录: {self.data_dir}")
            except Exception as e:
                logger.log_error_with_context(e, {
                    "function": "__init__",
                    "data_dir": self.data_dir
                })
        
        logger.log_process_step("file_storage_init", "completed", {
            "data_dir_exists": os.path.exists(self.data_dir)
        })
    
    async def load_json_file(self, filename: str) -> List[Dict]:
        """异步加载JSON文件"""
        logger.log_process_step("load_json_file", "started", {
            "filename": filename
        })
        
        try:
            filepath = os.path.join(self.data_dir, filename)
            logger.log_process_step("load_json_file", "checking_file", {
                "filepath": filepath,
                "file_exists": os.path.exists(filepath)
            })
            
            if not os.path.exists(filepath):
                logger.warning(f"文件不存在: {filepath}")
                return []
            
            async with aiofiles.open(filepath, 'r', encoding='utf-8') as f:
                content = await f.read()
                data = json.loads(content)
                
                logger.log_process_step("load_json_file", "completed", {
                    "filename": filename,
                    "data_length": len(data),
                    "first_item_keys": list(data[0].keys()) if data else []
                })
                
                return data
                
        except json.JSONDecodeError as e:
            logger.log_error_with_context(e, {
                "function": "load_json_file",
                "filename": filename,
                "error_type": "JSONDecodeError"
            })
            return []
        except Exception as e:
            logger.log_error_with_context(e, {
                "function": "load_json_file",
                "filename": filename
            })
            return []
    
    async def get_symptom_data(self) -> List[Dict]:
        """获取症状数据"""
        logger.log_process_step("get_symptom_data", "started")
        data = await self.load_json_file("symptom.json")
        logger.log_process_step("get_symptom_data", "completed", {
            "data_count": len(data)
        })
        return data
    
    async def get_guideline_data(self) -> List[Dict]:
        """获取处理指南数据"""
        logger.log_process_step("get_guideline_data", "started")
        data = await self.load_json_file("guideline.json")
        logger.log_process_step("get_guideline_data", "completed", {
            "data_count": len(data)
        })
        return data
    
    async def get_risk_data(self) -> List[Dict]:
        """获取风险信息数据"""
        logger.log_process_step("get_risk_data", "started")
        data = await self.load_json_file("disease_info.json")
        logger.log_process_step("get_risk_data", "completed", {
            "data_count": len(data)
        })
        return data
    
    async def find_by_disease_id(self, disease_id: str, data_type: str) -> Dict[str, Any]:
        """根据疾病ID查找数据（便于第二版本重写为数据库查询）"""
        logger.log_process_step("find_by_disease_id", "started", {
            "disease_id": disease_id,
            "data_type": data_type
        })
        
        try:
            if data_type == "symptom":
                data = await self.get_symptom_data()
            elif data_type == "guideline":
                data = await self.get_guideline_data()
            elif data_type == "risk":
                data = await self.get_risk_data()
            else:
                logger.warning(f"未知的数据类型: {data_type}")
                return {}
            
            logger.log_process_step("find_by_disease_id", "data_loaded", {
                "data_type": data_type,
                "data_count": len(data)
            })
            
            # 查找匹配的数据
            for item in data:
                if item.get('disease_id') == disease_id:
                    logger.log_process_step("find_by_disease_id", "completed", {
                        "disease_id": disease_id,
                        "data_type": data_type,
                        "found": True,
                        "item_keys": list(item.keys())
                    })
                    return item
            
            # 没有找到匹配的数据
            logger.log_process_step("find_by_disease_id", "completed", {
                "disease_id": disease_id,
                "data_type": data_type,
                "found": False
            })
            
            return {}
            
        except Exception as e:
            logger.log_error_with_context(e, {
                "function": "find_by_disease_id",
                "disease_id": disease_id,
                "data_type": data_type
            })
            return {}