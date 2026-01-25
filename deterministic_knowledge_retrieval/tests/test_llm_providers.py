import pytest
import os
from dotenv import load_dotenv
from src.llm_providers import create_provider, MockProvider, LLMProvider, OpenAIProvider, AnthropicProvider, OllamaProvider

# Load environment variables from .env file
load_dotenv()

class TestLLMProviders:
    """Test LLM provider functionality."""

    def test_mock_provider(self):
        """Test mock provider works."""
        provider = create_provider("mock")
        assert isinstance(provider, MockProvider)
        result = provider.generate(query="test", context="test", citations=[])
        assert "Mock answer" in result

    def test_create_provider_invalid(self):
        """Test provider factory with invalid type."""
        with pytest.raises(ValueError, match="Unknown provider"):
            create_provider("invalid_provider")

    def test_openai_provider(self):
        """Test OpenAI provider creation and generation."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            pytest.skip("OPENAI_API_KEY not found in environment.")
        
        try:
            provider = create_provider("openai", api_key=api_key)
            assert isinstance(provider, OpenAIProvider)
            # We don't call generate to avoid actual API costs in tests
        except ImportError:
            pytest.fail("OpenAI package not installed.")
        except Exception as e:
            pytest.fail(f"OpenAI provider failed to initialize with a valid key: {e}")

    def test_anthropic_provider(self):
        """Test Anthropic provider creation."""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            pytest.skip("ANTHROPIC_API_KEY not found in environment.")

        try:
            provider = create_provider("anthropic", api_key=api_key)
            assert isinstance(provider, AnthropicProvider)
        except ImportError:
            pytest.fail("Anthropic package not installed.")
        except Exception as e:
            pytest.fail(f"Anthropic provider failed to initialize with a valid key: {e}")

    def test_ollama_provider(self):
        """Test Ollama provider creation."""
        try:
            provider = create_provider("ollama")
            assert isinstance(provider, OllamaProvider)
        except ImportError:
            pytest.fail("requests package not installed for Ollama.")
        except Exception as e:
            # This will fail if Ollama server is not running, which is acceptable
            assert "Connection refused" in str(e) or isinstance(e, RuntimeError)
