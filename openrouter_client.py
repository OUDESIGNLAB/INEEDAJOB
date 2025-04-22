# OpenRouter API integration
# This file contains functions to connect to OpenRouter's API

import requests
import json
import os
from typing import Dict, List, Any, Optional

class OpenRouterClient:
    """Client for accessing OpenRouter API with OpenAI-compatible interface"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "Smart Job Application Assistant",  # Identify app to OpenRouter
        }
    
    def list_models(self) -> List[Dict[str, Any]]:
        """List available models from OpenRouter"""
        response = requests.get(
            f"{self.base_url}/models",
            headers=self.headers
        )
        
        if response.status_code == 200:
            return response.json()["data"]
        else:
            raise Exception(f"Error fetching models: {response.text}")
    
    def chat_completion(
        self, 
        model: str, 
        messages: List[Dict[str, str]], 
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """Create a chat completion using OpenRouter API"""
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
            
        if stream:
            payload["stream"] = True
        
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=self.headers,
            json=payload
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error generating completion: {response.text}")
    
    def get_top_models(self, category: str = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top models, optionally filtered by category"""
        models = self.list_models()
        
        # Filter by category if provided
        if category:
            models = [m for m in models if category.lower() in m.get("category", "").lower()]
        
        # Sort by ranking or defaults
        models.sort(key=lambda x: x.get("ranking", {}).get("ranking", 999))
        
        return models[:limit]


# Helper functions
def get_recommended_models() -> Dict[str, str]:
    """Return a curated list of recommended models for different tasks"""
    return {
        "fast": "openai/gpt-3.5-turbo",  # Fast, cheap option
        "powerful": "anthropic/claude-3.5-sonnet",  # Powerful option
        "balanced": "openai/gpt-4o-mini",  # Good balance of speed/quality
        "creative": "anthropic/claude-3-opus",  # Good for creative writing
        "analysis": "anthropic/claude-3.5-sonnet:thinking",  # Best for deep analysis
        "default": "anthropic/claude-3.5-sonnet"  # Good default option
    }

def format_model_info(models: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Format model information for display in Streamlit"""
    formatted = []
    
    for model in models:
        context_window = model.get("context_window", "Unknown")
        
        formatted.append({
            "id": model.get("id", ""),
            "name": model.get("name", "Unknown"),
            "description": model.get("description", "No description available"),
            "context_window": f"{context_window:,} tokens" if isinstance(context_window, int) else context_window,
            "pricing": f"${model.get('pricing', {}).get('input', 0):.6f}/1K input, ${model.get('pricing', {}).get('output', 0):.6f}/1K output",
        })
    
    return formatted