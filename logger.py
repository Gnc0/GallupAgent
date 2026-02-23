"""对话记录模块 - 保存每次对话为YAML格式。"""
import os
import yaml
from datetime import datetime
from typing import Dict, Any, Optional


class ConversationLogger:
    """对话记录器，将每次对话保存为YAML文件。"""
    
    def __init__(self, log_dir: str = "conversations"):
        """初始化对话记录器。
        
        Args:
            log_dir: 保存对话记录的目录
        """
        self.log_dir = log_dir
        # 确保目录存在
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
    
    def save_conversation(
        self,
        user_input: str,
        response: str,
        themes: list,
        reasoning: str,
        theme_results: dict = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """保存单次对话记录。
        
        Args:
            user_input: 用户输入
            response: AI回复
            themes: 使用的主题列表
            reasoning: 主题选择理由
            theme_results: 每个主题的思考内容 {"theme": "content", ...}
            metadata: 额外元数据
            
        Returns:
            保存的文件路径
        """
        # 生成时间戳作为文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 构建对话记录
        conversation = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "response": response,
            "themes": themes,
            "reasoning": reasoning,
            "theme_results": theme_results or {},
            "metadata": metadata or {}
        }
        
        # 保存为YAML文件
        filename = f"conversation_{timestamp}.yaml"
        filepath = os.path.join(self.log_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(
                conversation, 
                f, 
                allow_unicode=True, 
                default_flow_style=False,
                sort_keys=False
            )
        
        return filepath
    
    def get_conversation_history(self, limit: int = 10) -> list:
        """获取最近的对话历史。
        
        Args:
            limit: 返回最近N条记录
            
        Returns:
            对话记录列表
        """
        if not os.path.exists(self.log_dir):
            return []
        
        # 获取所有YAML文件
        files = [f for f in os.listdir(self.log_dir) if f.endswith('.yaml')]
        files.sort(reverse=True)  # 按时间倒序
        
        conversations = []
        for filename in files[:limit]:
            filepath = os.path.join(self.log_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    conversation = yaml.safe_load(f)
                    conversations.append(conversation)
            except Exception:
                continue
        
        return conversations


# 全局实例
_logger: Optional[ConversationLogger] = None


def get_logger() -> ConversationLogger:
    """获取全局对话记录器实例。"""
    global _logger
    if _logger is None:
        _logger = ConversationLogger()
    return _logger


def save_conversation(
    user_input: str,
    response: str,
    themes: list,
    reasoning: str,
    theme_results: dict = None,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """保存对话记录的便捷函数。"""
    return get_logger().save_conversation(
        user_input, response, themes, reasoning, theme_results, metadata
    )
