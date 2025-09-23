"""
LLM Client integrations for OpenAI, Claude (Anthropic), and Azure OpenAI
"""
import os
from typing import Optional
from abc import ABC, abstractmethod

class BaseLLMClient(ABC):
    @abstractmethod
    def get_response(self, system_prompt: str, user_prompt: str) -> str:
        pass

class OpenAIClient(BaseLLMClient):
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.model = model
        
    def get_response(self, system_prompt: str, user_prompt: str) -> str:
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key)
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            return content if content is not None else '{"command": "echo \\"Empty response from OpenAI\\""}'
            
        except Exception as e:
            return f'{{"command": "echo \\"OpenAI Error: {str(e)}\\""}}'

class AnthropicClient(BaseLLMClient):
    def __init__(self, api_key: str, model: str = "claude-3-haiku-20240307"):
        self.api_key = api_key
        self.model = model
        
    def get_response(self, system_prompt: str, user_prompt: str) -> str:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            
            response = client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=0.1,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            for block in response.content:
                if hasattr(block, 'text'):
                    return block.text # type: ignore

            return '{"command": "echo \\"No text content in response\\""}'

            
        except Exception as e:
            return f'{{"command": "echo \\"Claude Error: {str(e)}\\""}}'

class AzureOpenAIClient(BaseLLMClient):
    def __init__(self, api_key: str, endpoint: str, deployment_name: str, api_version: str = "2024-02-15-preview"):
        self.api_key = api_key
        self.endpoint = endpoint
        self.deployment_name = deployment_name
        self.api_version = api_version
        
    def get_response(self, system_prompt: str, user_prompt: str) -> str:
        try:
            from openai import AzureOpenAI
            client = AzureOpenAI(
                api_key=self.api_key,
                api_version=self.api_version,
                azure_endpoint=self.endpoint
            )
            
            response = client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            return content if content is not None else '{"command": "echo \\"Empty response from Azure\\""}'
            
        except Exception as e:
            return f'{{"command": "echo \\"Azure Error: {str(e)}\\""}}' 

class LLMClientFactory:
    @staticmethod
    def create_client() -> Optional[BaseLLMClient]:
        """Create LLM client based on environment variables"""
        
        # Try OpenAI first
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
            print(f"🤖 Using OpenAI with model: {model}")
            return OpenAIClient(openai_key, model)
        
        # Try Claude/Anthropic
        claude_key = os.getenv("ANTHROPIC_API_KEY")
        if claude_key:
            model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
            print(f"🤖 Using Claude with model: {model}")
            return AnthropicClient(claude_key, model)
        
        # Try Azure OpenAI
        azure_key = os.getenv("AZURE_OPENAI_API_KEY")
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        
        if azure_key and azure_endpoint and azure_deployment:
            api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
            print(f"🤖 Using Azure OpenAI with deployment: {azure_deployment}")
            return AzureOpenAIClient(azure_key, azure_endpoint, azure_deployment, api_version)
        
        print("❌ No LLM API keys found! Set one of:")
        print("   - OPENAI_API_KEY")
        print("   - ANTHROPIC_API_KEY") 
        print("   - AZURE_OPENAI_API_KEY + AZURE_OPENAI_ENDPOINT + AZURE_OPENAI_DEPLOYMENT_NAME")
        return None

# Convenience function
def get_llm_response(system_prompt: str, user_prompt: str) -> str:
    """Get LLM response using auto-detected provider"""
    client = LLMClientFactory.create_client()
    if not client:
        return '{"command": "echo \\"Please set up an LLM API key\\""}'
    
    return client.get_response(system_prompt, user_prompt)