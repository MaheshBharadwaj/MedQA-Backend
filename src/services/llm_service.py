from anthropic import Anthropic
from openai import OpenAI
from src.config.constants import (
    ANTHROPIC_API_KEY,
    OPENAI_API_KEY,
    ModelProvider
)
from src.utils.exceptions import ValidationError

class LLMService:
    def __init__(self):
        self.anthropic = Anthropic(api_key=ANTHROPIC_API_KEY)
        self.openai = OpenAI(api_key=OPENAI_API_KEY)

    def get_completion(self, model_type, message, context_messages=None):
        if model_type == ModelProvider.ANTHROPIC:
            return self._get_claude_completion(message, context_messages)
        elif model_type == ModelProvider.OPENAI:
            return self._get_gpt_completion(message, context_messages)
        else:
            raise ValidationError(f"Unsupported model type: {model_type}")

    def _get_claude_completion(self, message, context_messages=None):
        messages = []
        
        # Add context messages if provided
        if context_messages:
            for msg in context_messages:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        # Add the current message
        messages.append({
            "role": "user",
            "content": message
        })

        try:
            response = self.anthropic.messages.create(
                model="claude-3-opus-20240229",
                messages=messages,
                max_tokens=4096
            )
            
            return {
                'content': response.content[0].text,
                'tokens_used': response.usage.total_tokens
            }
        except Exception as e:
            raise Exception(f"Error getting completion from Claude: {str(e)}")

    def _get_gpt_completion(self, message, context_messages=None):
        messages = []
        
        # Add context messages if provided
        if context_messages:
            for msg in context_messages:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        # Add the current message
        messages.append({
            "role": "user",
            "content": message
        })

        try:
            response = self.openai.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=messages
            )
            
            return {
                'content': response.choices[0].message.content,
                'tokens_used': response.usage.total_tokens
            }
        except Exception as e:
            raise Exception(f"Error getting completion from GPT: {str(e)}")