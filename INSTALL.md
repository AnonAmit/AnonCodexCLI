# Installation Instructions

## Prerequisites

- Python 3.6 or higher
- Pip package manager

## Installation Methods

### Method 1: Direct Installation

1. Clone the repository:
```bash
git clone https://github.com/AnonAmit/AnonCodexCli.git
cd AnonCodexCli
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file for your API keys:
```bash
cp .env.example .env
```

4. Edit the `.env` file with your API keys.

5. Run the CLI:
```bash
python cli.py
```

### Method 2: Install as a Package

1. Clone the repository:
```bash
git clone https://github.com/AnonAmit/AnonCodexCli.git
cd AnonCodexCli
```

2. Install the package in development mode:
```bash
pip install -e .
```

3. Create a `.env` file for your API keys:
```bash
cp .env.example .env
```

4. Edit the `.env` file with your API keys.

5. Run the CLI from anywhere:
```bash
anoncodex
```

## Getting API Keys

### Google Gemini API

1. Visit the [Google AI Studio](https://ai.google.dev/)
2. Create an account or sign in
3. Navigate to "API Keys" and create a new key
4. Copy the key to your `.env` file

### OpenAI API

1. Visit [OpenAI API](https://platform.openai.com/)
2. Create an account or sign in
3. Go to "API Keys" and create a new secret key
4. Copy the key to your `.env` file

### Anthropic Claude API

1. Visit [Anthropic](https://www.anthropic.com/product)
2. Apply for API access
3. Once approved, generate an API key
4. Copy the key to your `.env` file

## Local LLM Setup

### Ollama

1. Install [Ollama](https://ollama.ai/download)
2. Run Ollama on your machine
3. Pull a model: `ollama pull llama3` (or any other model)
4. Update the `.env` file with the Ollama URL (default: `http://localhost:11434`)

### LM Studio

1. Download and install [LM Studio](https://lmstudio.ai/)
2. Launch LM Studio and set up a local server
3. Download and load a model
4. Start the server (default port is 1234)
5. Update the `.env` file with the LM Studio URL (default: `http://localhost:1234`)

## Troubleshooting

If you encounter any issues:

1. Ensure Python 3.6+ is installed and in your PATH
2. Check that all dependencies are installed correctly
3. Verify your API keys are valid and correctly formatted
4. For local LLMs, make sure the servers are running and accessible
5. Check the logs for any error messages

For more detailed help, see the [README.md](README.md) file. 
