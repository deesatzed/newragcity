"""
High-level wrapper for RoT compression and generation.
"""

import torch
from typing import List, Dict, Any, Optional
import logging
import sys
from pathlib import Path

# Handle both module and standalone imports
try:
    from .model_manager import RoTModelManager
except ImportError:
    # Running as standalone script
    current_dir = Path(__file__).parent
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
    from model_manager import RoTModelManager

logger = logging.getLogger(__name__)


class RoTCompressor:
    """Wrapper for RoT compression with simplified interface."""

    def __init__(self, model_manager: RoTModelManager):
        self.model_manager = model_manager
        self.model = None  # Lazy loading

    def _ensure_model_loaded(self):
        """Ensure model is loaded before use."""
        if self.model is None:
            self.model = self.model_manager.get_model()

    async def compress_and_generate(
        self,
        prompt: str,
        compressed_state: Optional[str] = None,
        max_tokens: int = 256,
        temperature: float = 0.7,
        top_p: float = 0.8,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate answer with compressed reasoning.

        Args:
            prompt: Input prompt
            compressed_state: Previous compressed reasoning (for loops)
            max_tokens: Max tokens to generate
            temperature: Sampling temperature
            top_p: Nucleus sampling threshold

        Returns:
            Dictionary with answer, compressed state, and metrics
        """
        self._ensure_model_loaded()

        # Prepare input
        input_text = prompt
        if compressed_state:
            # Incorporate previous reasoning state
            input_text = f"{compressed_state}\n{prompt}"

        # For now, since we don't have trained checkpoints yet,
        # we'll use the base model's generation
        # In production, this would use the RoT compressed generation
        logger.info(f"Generating with RoT compression (prompt length: {len(input_text)})")

        try:
            # Generate with RoT compression
            # NOTE: This is a placeholder - actual implementation depends on
            # CoTCompressorV2.generate() method signature
            with torch.no_grad():
                # Simplified generation for demo purposes
                # In production, use model.generate() with proper tokenization
                answer = f"[RoT Demo] Compressed reasoning for: {prompt[:50]}..."
                compressed_repr = f"compressed_state_{hash(prompt)}"

            # Calculate metrics (estimates for demo)
            original_tokens = self._estimate_tokens(prompt + answer) * 3  # Simulated 3× expansion for CoT
            compressed_tokens = self._estimate_tokens(prompt + answer)
            compression_ratio = original_tokens / compressed_tokens if compressed_tokens > 0 else 1.0
            tokens_saved = original_tokens - compressed_tokens

            return {
                'answer': answer,
                'compressed_state': compressed_repr,
                'compression_ratio': compression_ratio,
                'tokens_saved': tokens_saved,
                'original_tokens_estimated': original_tokens,
                'compressed_tokens': compressed_tokens
            }
        except Exception as e:
            logger.error(f"Error in compress_and_generate: {e}")
            # Fallback to simple response
            return {
                'answer': f"Error: {str(e)}. Please train RoT model first.",
                'compressed_state': '',
                'compression_ratio': 1.0,
                'tokens_saved': 0,
                'original_tokens_estimated': 0,
                'compressed_tokens': 0
            }

    async def visual_reasoning_trace(
        self,
        reasoning_steps: List[str]
    ) -> Dict[str, Any]:
        """
        Generate visual reasoning trace for debugging.

        Args:
            reasoning_steps: List of reasoning step texts

        Returns:
            Dictionary with rendered images and metadata
        """
        self._ensure_model_loaded()

        rendered_images = []
        try:
            for step in reasoning_steps:
                # Render using text_to_image
                image = self.model.text_renderer.render(step)
                rendered_images.append(image)
        except Exception as e:
            logger.error(f"Error rendering reasoning steps: {e}")

        return {
            'images': rendered_images,
            'count': len(rendered_images),
            'format': 'PIL.Image'
        }

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for text."""
        # Simple heuristic: ~4 chars per token for English
        # For production, use actual tokenizer
        return max(1, len(text) // 4)

    def get_model_info(self) -> Dict[str, Any]:
        """Get model information and status."""
        return {
            'model_loaded': self.model is not None,
            'device': str(self.model_manager.device),
            'checkpoint_path': str(self.model_manager.checkpoint_path),
            'stage1_checkpoint': str(self.model_manager.stage1_checkpoint),
            'checkpoints_exist': self.model_manager.checkpoint_path.exists() and self.model_manager.stage1_checkpoint.exists()
        }
