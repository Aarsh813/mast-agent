import os
from typing import Any
from langchain_core.language_models.chat_models import BaseChatModel

class LLMFactory:
    @staticmethod
    def create(provider: str, model: str, temperature: float = 0.0) -> BaseChatModel:
        provider = provider.lower()
        if provider == "groq":
            try:
                from langchain_groq import ChatGroq
                return ChatGroq(model=model, temperature=temperature)
            except ImportError:
                raise ImportError("langchain-groq not installed")
        elif provider == "openai":
            try:
                from langchain_openai import ChatOpenAI
                return ChatOpenAI(model=model, temperature=temperature)
            except ImportError:
                raise ImportError("langchain-openai not installed")
        elif provider == "anthropic":
            try:
                from langchain_anthropic import ChatAnthropic
                return ChatAnthropic(model=model, temperature=temperature)
            except ImportError:
                raise ImportError("langchain-anthropic not installed")
        elif provider == "google":
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                return ChatGoogleGenerativeAI(model=model, temperature=temperature)
            except ImportError:
                raise ImportError("langchain-google-genai not installed")
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")
