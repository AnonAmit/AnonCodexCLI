import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(".env")
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    print("Warning: .env file not found. Using default or system environment variables.")

# LLM API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Local LLM Settings
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
LM_STUDIO_BASE_URL = os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234")

# Application Settings
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gemini-pro")
DEFAULT_MODE = os.getenv("DEFAULT_MODE", "interactive")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", 4096))
HISTORY_PATH = os.getenv("HISTORY_PATH", "./history")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# Define available models
AVAILABLE_MODELS = {
    "gemini": ["gemini-pro", "gemini-2.5-pro-exp-03-25"],
    "openai": ["gpt-3.5-turbo", "gpt-4", "gpt-4o"],
    "anthropic": [
        "claude-3-opus-20240229", 
        "claude-3-sonnet-20240229", 
        "claude-3-haiku-20240307",
        "claude-2.1",
        "claude-2.0"
    ],
    "ollama": ["llama3", "mistral", "mixtral"],
    "lm_studio": ["custom"]
}

def get_api_key(model_family):
    """Get the appropriate API key for the model family."""
    if model_family == "gemini":
        return GEMINI_API_KEY
    elif model_family == "openai":
        return OPENAI_API_KEY
    elif model_family == "anthropic":
        return ANTHROPIC_API_KEY
    else:
        return None  # Local models don't need API keys

def validate_api_keys():
    """Validate that necessary API keys are available."""
    if not GEMINI_API_KEY and "gemini" in DEFAULT_MODEL:
        print("Warning: Gemini API key not found. Gemini models will not be available.")
    if not OPENAI_API_KEY and "gpt" in DEFAULT_MODEL:
        print("Warning: OpenAI API key not found. OpenAI models will not be available.")
    if not ANTHROPIC_API_KEY and "claude" in DEFAULT_MODEL:
        print("Warning: Anthropic API key not found. Claude models will not be available.")

# Create directories if they don't exist
def create_required_directories():
    """Create necessary directories if they don't exist."""
    Path(HISTORY_PATH).mkdir(parents=True, exist_ok=True)

# Initialize settings
def initialize():
    """Initialize application settings."""
    validate_api_keys()
    create_required_directories()
    
    # Print debug information if in debug mode
    if DEBUG:
        print(f"Debug mode: ON")
        print(f"Default model: {DEFAULT_MODEL}")
        print(f"Default mode: {DEFAULT_MODE}")
        print(f"Max tokens: {MAX_TOKENS}")
        print(f"History path: {HISTORY_PATH}") 