"""
AI Provider with multi-model support (OpenAI, Gemini, Groq, Ollama)
"""
import os
import json
from abc import ABC, abstractmethod
from typing import Optional, Union, List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class BaseAIProvider(ABC):
    """Base class for AI providers"""
    
    @abstractmethod
    async def generate_text(self, prompt: Union[str, List[Dict[str, str]]], **kwargs) -> str:
        """Generate text from prompt"""
        pass
    
    @abstractmethod
    async def generate_structured(self, prompt: Union[str, List[Dict[str, str]]], schema: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Generate structured output using single LLM call"""
        pass


class OpenAIProvider(BaseAIProvider):
    """OpenAI GPT provider"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        
        if not self.api_key:
            raise ValueError("OpenAI API key not provided. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        try:
            import openai
            self.client = openai.OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("openai package not installed")
    
    async def generate_text(self, prompt: Union[str, List[Dict[str, str]]], **kwargs) -> str:
        import asyncio
        
        # Handle both string and message list formats
        if isinstance(prompt, str):
            messages = [{"role": "user", "content": prompt}]
        else:
            messages = prompt
            
        response = await asyncio.to_thread(
            self.client.chat.completions.create,
            model=self.model,
            messages=messages,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 2000)
        )
        return response.choices[0].message.content
    
    async def generate_structured(self, prompt: Union[str, List[Dict[str, str]]], schema: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        import asyncio
        
        # Handle both string and message list formats
        if isinstance(prompt, str):
            messages = [{"role": "user", "content": prompt}]
        else:
            messages = prompt
            
        # Use OpenAI's structured output feature
        response = await asyncio.to_thread(
            self.client.chat.completions.create,
            model=self.model,
            messages=messages,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 2000),
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Fallback: try to extract JSON from the response
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            raise ValueError(f"Failed to parse JSON response: {content}")


class GeminiProvider(BaseAIProvider):
    """Google Gemini provider"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.5-flash-lite"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model
        
        if not self.api_key:
            raise ValueError("Gemini API key not provided. Set GEMINI_API_KEY environment variable or pass api_key parameter.")
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel(self.model)
        except ImportError:
            raise ImportError("google-generativeai package not installed")
    
    async def generate_text(self, prompt: Union[str, List[Dict[str, str]]], **kwargs) -> str:
        # Handle both string and message list formats
        if isinstance(prompt, str):
            formatted_prompt = prompt
        else:
            # Convert message list to string format for Gemini
            formatted_prompt = "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in prompt])
        
        response = await self.client.generate_content_async(
            formatted_prompt,
            generation_config={
                "temperature": kwargs.get("temperature", 0.7),
                "max_output_tokens": kwargs.get("max_tokens", 2000)
            }
        )
        return response.text
    
    async def generate_structured(self, prompt: Union[str, List[Dict[str, str]]], schema: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        # Handle both string and message list formats
        if isinstance(prompt, str):
            formatted_prompt = prompt
        else:
            # Convert message list to string format for Gemini
            formatted_prompt = "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in prompt])
        
        # Add JSON schema instruction to the prompt
        schema_instruction = f"\n\nPlease respond with a valid JSON object that matches this schema: {json.dumps(schema, indent=2)}"
        formatted_prompt += schema_instruction
        
        response = await self.client.generate_content_async(
            formatted_prompt,
            generation_config={
                "temperature": kwargs.get("temperature", 0.7),
                "max_output_tokens": kwargs.get("max_tokens", 2000)
            }
        )
        
        content = response.text
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Fallback: try to extract JSON from the response
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            raise ValueError(f"Failed to parse JSON response: {content}")


class GroqProvider(BaseAIProvider):
    """Groq provider"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "llama-3.1-8b-instant"):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = model
        
        if not self.api_key:
            raise ValueError("Groq API key not provided. Set GROQ_API_KEY environment variable or pass api_key parameter.")
        
        try:
            from groq import Groq
            self.client = Groq(api_key=self.api_key)
        except ImportError:
            raise ImportError("groq package not installed")
    
    async def generate_text(self, prompt: Union[str, List[Dict[str, str]]], **kwargs) -> str:
        import asyncio
        
        # Handle both string and message list formats
        if isinstance(prompt, str):
            messages = [{"role": "user", "content": prompt}]
        else:
            messages = prompt
            
        response = await asyncio.to_thread(
            self.client.chat.completions.create,
            model=self.model,
            messages=messages,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 2000)
        )
        return response.choices[0].message.content
    
    async def generate_structured(self, prompt: Union[str, List[Dict[str, str]]], schema: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        import asyncio
        
        # Handle both string and message list formats
        if isinstance(prompt, str):
            messages = [{"role": "user", "content": prompt}]
        else:
            messages = prompt
            
        # Add JSON schema instruction to the prompt
        schema_instruction = f"\n\nPlease respond with a valid JSON object that matches this schema: {json.dumps(schema, indent=2)}"
        messages[-1]["content"] += schema_instruction
        
        response = await asyncio.to_thread(
            self.client.chat.completions.create,
            model=self.model,
            messages=messages,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 2000)
        )
        
        content = response.choices[0].message.content
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Fallback: try to extract JSON from the response
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            raise ValueError(f"Failed to parse JSON response: {content}")


class OllamaProvider(BaseAIProvider):
    """Ollama local provider"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.1"):
        self.base_url = base_url
        self.model = model
        try:
            import ollama
            self.client = ollama
        except ImportError:
            raise ImportError("ollama package not installed")
    
    async def generate_text(self, prompt: Union[str, List[Dict[str, str]]], **kwargs) -> str:
        import asyncio
        
        # Handle both string and message list formats
        if isinstance(prompt, str):
            messages = [{"role": "user", "content": prompt}]
        else:
            messages = prompt
            
        response = await asyncio.to_thread(
            self.client.chat,
            model=self.model,
            messages=messages,
            options={
                "temperature": kwargs.get("temperature", 0.7),
                "num_predict": kwargs.get("max_tokens", 2000)
            }
        )
        return response["message"]["content"]
    
    async def generate_structured(self, prompt: Union[str, List[Dict[str, str]]], schema: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        import asyncio
        
        # Handle both string and message list formats
        if isinstance(prompt, str):
            messages = [{"role": "user", "content": prompt}]
        else:
            messages = prompt
            
        # Add JSON schema instruction to the prompt
        schema_instruction = f"\n\nPlease respond with a valid JSON object that matches this schema: {json.dumps(schema, indent=2)}"
        messages[-1]["content"] += schema_instruction
        
        response = await asyncio.to_thread(
            self.client.chat,
            model=self.model,
            messages=messages,
            options={
                "temperature": kwargs.get("temperature", 0.7),
                "num_predict": kwargs.get("max_tokens", 2000)
            }
        )
        
        content = response["message"]["content"]
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Fallback: try to extract JSON from the response
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            raise ValueError(f"Failed to parse JSON response: {content}")


class AIProviderFactory:
    """Factory to create AI providers"""
    
    @staticmethod
    def create_provider(provider_type: str, **kwargs) -> BaseAIProvider:
        providers = {
            "openai": OpenAIProvider,
            "gemini": GeminiProvider,
            "groq": GroqProvider,
            "ollama": OllamaProvider
        }
        
        if provider_type.lower() not in providers:
            raise ValueError(f"Unknown provider: {provider_type}")
        
        provider_class = providers[provider_type.lower()]
        
        # Filter kwargs based on provider type
        if provider_type.lower() == "ollama":
            # Ollama only accepts base_url and model
            filtered_kwargs = {k: v for k, v in kwargs.items() if k in ["base_url", "model"]}
        else:
            # Other providers accept api_key, model, and other common parameters
            filtered_kwargs = {k: v for k, v in kwargs.items() if k in ["api_key", "model"]}
        
        return provider_class(**filtered_kwargs)

