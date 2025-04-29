"""
Unified model factory for selecting and creating LLM instances.
"""
from typing import Dict, Any, Optional, Union, Type

from config import AVAILABLE_MODELS, get_api_key
from models.gemini import GeminiModel
from models.openai import OpenAIModel
from models.claude import ClaudeModel
from models.local_llm import OllamaModel, LMStudioModel

# Type for any supported model
ModelType = Union[GeminiModel, OpenAIModel, ClaudeModel, OllamaModel, LMStudioModel]

class ModelFactory:
    """Factory for creating LLM model instances."""
    
    @staticmethod
    def get_model_class(model_name: str) -> Type:
        """
        Get the model class for a given model name.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Model class
        """
        if model_name.startswith("gemini"):
            return GeminiModel
        elif model_name.startswith(("gpt", "openai")):
            return OpenAIModel
        elif model_name.startswith("claude"):
            return ClaudeModel
        elif model_name in ["llama3", "mistral", "mixtral"] or model_name.startswith("ollama"):
            return OllamaModel
        elif model_name == "custom" or model_name.startswith("lm-studio"):
            return LMStudioModel
        else:
            # Default to Gemini
            return GeminiModel
    
    @staticmethod
    def get_model_family(model_name: str) -> str:
        """
        Get the model family for a given model name.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Model family name
        """
        if model_name.startswith("gemini"):
            return "gemini"
        elif model_name.startswith(("gpt", "openai")):
            return "openai"
        elif model_name.startswith("claude"):
            return "anthropic"
        elif model_name in ["llama3", "mistral", "mixtral"] or model_name.startswith("ollama"):
            return "ollama"
        elif model_name == "custom" or model_name.startswith("lm-studio"):
            return "lm_studio"
        else:
            # Default to Gemini
            return "gemini"
    
    @staticmethod
    def create_model(model_name: str, **kwargs) -> ModelType:
        """
        Create a model instance for the given model name.
        
        Args:
            model_name: Name of the model
            **kwargs: Additional arguments to pass to the model constructor
            
        Returns:
            Model instance
        """
        model_class = ModelFactory.get_model_class(model_name)
        model_family = ModelFactory.get_model_family(model_name)
        
        # Get API key for the model family
        if model_family in ["gemini", "openai", "anthropic"]:
            api_key = kwargs.get("api_key") or get_api_key(model_family)
            return model_class(api_key=api_key, model_name=model_name, **kwargs)
        else:
            # Local models don't need API keys
            return model_class(model_name=model_name, **kwargs)
    
    @staticmethod
    def list_available_models() -> Dict[str, Any]:
        """
        List all available models.
        
        Returns:
            Dictionary of available models by family
        """
        return AVAILABLE_MODELS
    
    @staticmethod
    def is_valid_model(model_name: str) -> bool:
        """
        Check if a model name is valid.
        
        Args:
            model_name: Name of the model
            
        Returns:
            True if valid, False otherwise
        """
        model_family = ModelFactory.get_model_family(model_name)
        
        if model_family in AVAILABLE_MODELS:
            # Check if the model name is in the list of models for this family
            if model_name in AVAILABLE_MODELS[model_family]:
                return True
            
            # Also check for prefix matches (e.g., "gemini" matches "gemini-pro")
            for available_model in AVAILABLE_MODELS[model_family]:
                if available_model.startswith(model_name):
                    return True
        
        return False 