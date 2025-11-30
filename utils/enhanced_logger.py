#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
增强版日志系统 - 医疗导诊系统专用

功能：
1. 详细的用户输入日志记录
2. 大模型调用完整日志（输入输出）
3. 关键流程节点状态记录
4. 性能指标记录
5. 错误和异常详细追踪
"""

import logging
import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from functools import wraps
import traceback


class MedicalLogger:
    """医疗导诊系统专用日志记录器"""
    
    def __init__(self, name: str = "medical_system", log_level: str = "INFO"):
        """
        初始化日志记录器
        
        Args:
            name: 日志记录器名称
            log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # 避免重复添加handler
        if not self.logger.handlers:
            self._setup_handlers()
        
        self._setup_formatters()
        
        # 性能计时器
        self.performance_timers: Dict[str, float] = {}
    
    def _setup_handlers(self):
        """设置日志处理器"""
        # 创建日志目录
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # 文件处理器 - 按日期分割
        log_file = log_dir / f"medical_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        
        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def _setup_formatters(self):
        """设置日志格式"""
        # 详细格式 - 用于文件
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - '
            '[%(filename)s:%(lineno)d - %(funcName)s] - %(message)s'
        )
        
        # 简洁格式 - 用于控制台
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # 为不同的处理器设置不同的格式
        for handler in self.logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.setFormatter(detailed_formatter)
            else:
                handler.setFormatter(simple_formatter)
    
    def log_user_input(self, input_data: Dict[str, Any], source: str = "unknown"):
        """记录用户输入数据"""
        try:
            # 敏感信息脱敏
            safe_data = self._sanitize_data(input_data)
            
            log_entry = {
                "type": "user_input",
                "source": source,
                "timestamp": datetime.now().isoformat(),
                "data": safe_data,
                "data_size": len(str(input_data))
            }
            
            self.info(f"USER_INPUT: {json.dumps(log_entry, ensure_ascii=False)}")
            
        except Exception as e:
            self.error(f"Failed to log user input: {str(e)}")
    
    def log_llm_call(self, prompt: str, response: str, model: str = "unknown", 
                    tokens_used: Optional[int] = None, duration: Optional[float] = None):
        """记录大模型调用完整信息"""
        try:
            log_entry = {
                "type": "llm_call",
                "model": model,
                "timestamp": datetime.now().isoformat(),
                "prompt_length": len(prompt),
                "response_length": len(response),
                "tokens_used": tokens_used,
                "duration_seconds": duration,
                "prompt_preview": prompt[:200] + "..." if len(prompt) > 200 else prompt,
                "response_preview": response[:200] + "..." if len(response) > 200 else response
            }
            
            self.info(f"LLM_CALL: {json.dumps(log_entry, ensure_ascii=False)}")
            
        except Exception as e:
            self.error(f"Failed to log LLM call: {str(e)}")
    
    def log_process_step(self, step_name: str, status: str, details: Dict[str, Any] = None):
        """记录关键流程节点状态"""
        try:
            log_entry = {
                "type": "process_step",
                "step_name": step_name,
                "status": status,
                "timestamp": datetime.now().isoformat(),
                "details": details or {}
            }
            
            self.info(f"PROCESS_STEP: {json.dumps(log_entry, ensure_ascii=False)}")
            
        except Exception as e:
            self.error(f"Failed to log process step: {str(e)}")
    
    def start_timer(self, timer_name: str):
        """开始性能计时"""
        self.performance_timers[timer_name] = time.time()
        self.debug(f"Started timer: {timer_name}")
    
    def end_timer(self, timer_name: str) -> float:
        """结束性能计时并返回耗时"""
        if timer_name in self.performance_timers:
            duration = time.time() - self.performance_timers[timer_name]
            del self.performance_timers[timer_name]
            self.info(f"Timer {timer_name} completed in {duration:.3f} seconds")
            return duration
        else:
            self.warning(f"Timer {timer_name} not found")
            return 0.0
    
    def log_error_with_context(self, error: Exception, context: Dict[str, Any] = None):
        """记录带上下文的错误信息"""
        try:
            error_info = {
                "type": "error_with_context",
                "error_type": type(error).__name__,
                "error_message": str(error),
                "timestamp": datetime.now().isoformat(),
                "traceback": traceback.format_exc(),
                "context": context or {}
            }
            
            self.error(f"ERROR_CONTEXT: {json.dumps(error_info, ensure_ascii=False)}")
            
        except Exception as e:
            self.error(f"Failed to log error with context: {str(e)}")
    
    def log_performance_metrics(self, operation: str, metrics: Dict[str, Any]):
        """记录性能指标"""
        try:
            log_entry = {
                "type": "performance_metrics",
                "operation": operation,
                "timestamp": datetime.now().isoformat(),
                "metrics": metrics
            }
            
            self.info(f"PERFORMANCE: {json.dumps(log_entry, ensure_ascii=False)}")
            
        except Exception as e:
            self.error(f"Failed to log performance metrics: {str(e)}")
    
    def _sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """敏感信息脱敏处理"""
        # 复制数据避免修改原数据
        safe_data = data.copy()
        
        # 定义敏感字段
        sensitive_fields = [
            'password', 'secret', 'token', 'key', 'api_key', 
            'phone', 'email', 'id_card', 'bank_card'
        ]
        
        for field in sensitive_fields:
            if field in safe_data:
                safe_data[field] = "[REDACTED]"
        
        return safe_data
    
    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """记录调试信息"""
        self.logger.debug(message, extra=extra or {})
    
    def info(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """记录一般信息"""
        self.logger.info(message, extra=extra or {})
    
    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """记录警告信息"""
        self.logger.warning(message, extra=extra or {})
    
    def error(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """记录错误信息"""
        self.logger.error(message, extra=extra or {})
    
    def critical(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """记录严重错误信息"""
        self.logger.critical(message, extra=extra or {})


def log_process_step(step_name: str):
    """装饰器：记录函数执行过程"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = MedicalLogger()
            logger.log_process_step(step_name, "started", {
                "function": func.__name__,
                "args_count": len(args),
                "kwargs_count": len(kwargs)
            })
            
            try:
                result = func(*args, **kwargs)
                logger.log_process_step(step_name, "completed", {
                    "function": func.__name__
                })
                return result
            except Exception as e:
                logger.log_process_step(step_name, "failed", {
                    "function": func.__name__,
                    "error": str(e)
                })
                raise
        
        return wrapper
    return decorator


# 全局日志实例
logger = MedicalLogger()