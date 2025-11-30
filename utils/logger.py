#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
系统日志记录组件

功能：
1. 记录系统关键操作的日志
2. 支持不同日志级别（DEBUG, INFO, WARNING, ERROR, CRITICAL）
3. 记录时间、文件名、模块、函数名等信息
4. 支持文件输出和控制台输出
5. 自动创建日志目录和文件
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any


class SystemLogger:
    """系统日志记录器"""
    
    def __init__(self, name: str = "disease_system", log_level: str = "INFO"):
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
        
        # 设置日志格式
        self._setup_formatters()
    
    def _setup_handlers(self):
        """设置日志处理器"""
        # 创建日志目录
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # 文件处理器 - 按日期分割
        log_file = log_dir / f"system_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        
        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def _setup_formatters(self):
        """设置日志格式"""
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(module)s.%(funcName)s - %(message)s'
        )
        
        for handler in self.logger.handlers:
            handler.setFormatter(formatter)
    
    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None, 
              source_file: Optional[str] = None, source_module: Optional[str] = None):
        """记录调试信息"""
        self._log(logging.DEBUG, message, extra, source_file, source_module)
    
    def info(self, message: str, extra: Optional[Dict[str, Any]] = None,
             source_file: Optional[str] = None, source_module: Optional[str] = None):
        """记录一般信息"""
        self._log(logging.INFO, message, extra, source_file, source_module)
    
    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None,
                source_file: Optional[str] = None, source_module: Optional[str] = None):
        """记录警告信息"""
        self._log(logging.WARNING, message, extra, source_file, source_module)
    
    def error(self, message: str, extra: Optional[Dict[str, Any]] = None,
              source_file: Optional[str] = None, source_module: Optional[str] = None):
        """记录错误信息"""
        self._log(logging.ERROR, message, extra, source_file, source_module)
    
    def critical(self, message: str, extra: Optional[Dict[str, Any]] = None,
                 source_file: Optional[str] = None, source_module: Optional[str] = None):
        """记录严重错误信息"""
        self._log(logging.CRITICAL, message, extra, source_file, source_module)
    
    def _log(self, level: int, message: str, extra: Optional[Dict[str, Any]],
             source_file: Optional[str], source_module: Optional[str]):
        """内部日志记录方法"""
        if extra is None:
            extra = {}
        
        # 添加额外的上下文信息
        if source_file:
            extra['source_file'] = source_file
        if source_module:
            extra['source_module'] = source_module
        
        self.logger.log(level, message, extra=extra if extra else None)
    
    def log_operation(self, operation: str, status: str, details: Optional[Dict] = None,
                      source_file: Optional[str] = None, source_module: Optional[str] = None):
        """
        记录操作日志
        
        Args:
            operation: 操作描述
            status: 操作状态 (success, failure, warning, info)
            details: 操作详细信息
            source_file: 源文件名
            source_module: 源模块名
        """
        status_levels = {
            'success': logging.INFO,
            'failure': logging.ERROR,
            'warning': logging.WARNING,
            'info': logging.INFO
        }
        
        level = status_levels.get(status.lower(), logging.INFO)
        
        log_message = f"Operation: {operation} | Status: {status}"
        if details:
            log_message += f" | Details: {details}"
        
        extra = {
            'operation': operation,
            'status': status,
            'details': details or {}
        }
        
        self._log(level, log_message, extra, source_file, source_module)
    
    def log_data_access(self, operation: str, data_type: str, data_id: Optional[str] = None,
                        success: bool = True, source_file: Optional[str] = None, 
                        source_module: Optional[str] = None):
        """
        记录数据访问日志
        
        Args:
            operation: 数据操作类型 (read, write, update, delete)
            data_type: 数据类型
            data_id: 数据ID
            success: 操作是否成功
            source_file: 源文件名
            source_module: 源模块名
        """
        status = "success" if success else "failure"
        details = {
            'data_type': data_type,
            'data_id': data_id,
            'operation': operation
        }
        
        self.log_operation(
            f"Data {operation}", 
            status, 
            details,
            source_file,
            source_module
        )
    
    def log_api_call(self, endpoint: str, method: str, status_code: Optional[int] = None,
                     response_time: Optional[float] = None, source_file: Optional[str] = None,
                     source_module: Optional[str] = None):
        """
        记录API调用日志
        
        Args:
            endpoint: API端点
            method: HTTP方法
            status_code: 状态码
            response_time: 响应时间
            source_file: 源文件名
            source_module: 源模块名
        """
        details = {
            'endpoint': endpoint,
            'method': method,
            'status_code': status_code,
            'response_time': response_time
        }
        
        status = 'success' if status_code and status_code < 400 else 'failure'
        
        self.log_operation(
            f"API Call: {method} {endpoint}",
            status,
            details,
            source_file,
            source_module
        )


# 创建全局日志记录器实例
logger = SystemLogger()


def get_logger(name: str = "disease_system", log_level: str = "INFO") -> SystemLogger:
    """
    获取日志记录器实例
    
    Args:
        name: 日志记录器名称
        log_level: 日志级别
        
    Returns:
        SystemLogger实例
    """
    return SystemLogger(name, log_level)


# 快捷方法
def log_debug(message: str, **kwargs):
    """快捷调试日志"""
    logger.debug(message, **kwargs)

def log_info(message: str, **kwargs):
    """快捷信息日志"""
    logger.info(message, **kwargs)

def log_warning(message: str, **kwargs):
    """快捷警告日志"""
    logger.warning(message, **kwargs)

def log_error(message: str, **kwargs):
    """快捷错误日志"""
    logger.error(message, **kwargs)

def log_critical(message: str, **kwargs):
    """快捷严重错误日志"""
    logger.critical(message, **kwargs)