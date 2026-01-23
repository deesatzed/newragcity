import os
from typing import Any, Dict, List
from openai import AsyncOpenAI
from ultrarag.server import UltraRAG_MCP_Server

app = UltraRAG_MCP_Server("local-llm-server")

client = None
model_name = "qwen2.5-14b-instruct" # Default, can be overridden

@app.tool(output="response")
async def generate(prompt: str, temperature: float = 0.7, max_tokens: int = 1024) -> str:
    """
    Generate text using the local LLM.
    
    Args:
        prompt: The full prompt string (or synthesized context).
        temperature: Sampling temperature.
        max_tokens: Max output tokens.
    """
    global client, model_name
    
    if not client:
        return "Error: Local LLM client not initialized. Run init_client first."

    app.logger.info(f"Generating with {model_name}...")
    
    try:
        # Check if prompt is a string or a serialized PromptMessage list from UltraRAG
        # UltraRAG prompt server returns PromptMessage objects, but simple string passing works too.
        messages = [{"role": "user", "content": prompt}]
        
        response = await client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except Exception as e:
        app.logger.error(f"Generation failed: {e}")
        return f"Error generating response: {str(e)}"

@app.tool(output="status")
def init_client(base_url: str, api_key: str = "EMPTY", model: str = "qwen2.5-14b-instruct") -> Dict[str, str]:
    """
    Initialize the OpenAI-compatible client.
    
    Args:
        base_url: URL of the local server (e.g., http://localhost:8000/v1)
        api_key: API Key (usually ignored for local, but required by SDK)
        model: Model name to request.
    """
    global client, model_name
    try:
        client = AsyncOpenAI(
            base_url=base_url,
            api_key=api_key
        )
        model_name = model
        app.logger.info(f"Local LLM Client initialized at {base_url} for model {model}")
        return {"status": "initialized", "url": base_url, "model": model}
    except Exception as e:
        return {"status": "failed", "error": str(e)}

if __name__ == "__main__":
    app.run(transport="stdio")
