"""Gallup Agent Configuration Module.

支持配置LM Studio、DeepSeek和其他OpenAI兼容的API。
"""
import os
from typing import Optional
from langchain_openai import ChatOpenAI

# 加载 .env 文件
from dotenv import load_dotenv
load_dotenv()


class Config:
    """API配置类，支持灵活配置不同的LLM服务。"""

    # DeepSeek 配置（从环境变量读取）
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
    DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    
    # LM Studio 默认配置
    BASE_URL: str = os.getenv("LLM_BASE_URL", "http://localhost:1234/v1")
    API_KEY: str = os.getenv("LLM_API_KEY", "lm-studio")
    MODEL_NAME: str = os.getenv("LLM_MODEL", "qwen3-4b-instruct")
    
    # 当前使用的LLM类型: "deepseek" 或 "lmstudio"
    CURRENT_LLM: str = "deepseek"
    
    # 温度参数
    TEMPERATURE: float = 0.7
    TEMPERATURE_LOW: float = 0.3  # 用于精确推理
    
    # 最大迭代次数
    MAX_ITERATIONS: int = 10

    @classmethod
    def get_llm(cls, temperature: Optional[float] = None) -> ChatOpenAI:
        """获取LLM实例。
        
        Args:
            temperature: 温度参数，默认使用类属性
            
        Returns:
            ChatOpenAI实例
        """
        if cls.CURRENT_LLM == "deepseek":
            return ChatOpenAI(
                base_url=cls.DEEPSEEK_BASE_URL,
                api_key=cls.DEEPSEEK_API_KEY,
                model=cls.DEEPSEEK_MODEL,
                temperature=temperature if temperature is not None else cls.TEMPERATURE
            )
        else:
            # LM Studio
            return ChatOpenAI(
                base_url=cls.BASE_URL,
                api_key=cls.API_KEY,
                model=cls.MODEL_NAME,
                temperature=temperature if temperature is not None else cls.TEMPERATURE
            )

    @classmethod
    def get_supervisor_llm(cls) -> ChatOpenAI:
        """获取Supervisor使用的LLM（低温，更精确）。"""
        return cls.get_llm(temperature=cls.TEMPERATURE_LOW)

    @classmethod
    def get_worker_llm(cls) -> ChatOpenAI:
        """获取Worker使用的LLM。"""
        return cls.get_llm(temperature=cls.TEMPERATURE)

    @classmethod
    def update_config(cls, **kwargs):
        """动态更新配置。
        
        Args:
            **kwargs: 配置参数
        """
        for key, value in kwargs.items():
            if hasattr(cls, key.upper()):
                setattr(cls, key.upper(), value)
