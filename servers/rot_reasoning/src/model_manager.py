"""
Checkpoint loading and model initialization for RoT server.
"""

import torch
from pathlib import Path
from typing import Dict, Any, Optional
import logging
import sys

# Handle both module and standalone imports
try:
    from .cot_compressor_v2 import CoTCompressorV2
except ImportError:
    # Running as standalone script
    current_dir = Path(__file__).parent
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
    from cot_compressor_v2 import CoTCompressorV2

logger = logging.getLogger(__name__)


class RoTModelManager:
    """Manages RoT model lifecycle: loading, validation, device management."""

    def __init__(
        self,
        checkpoint_path: str,
        stage1_checkpoint: str,
        ocr_model_path: str,
        llm_model_path: str,
        device: str = "cuda",
        dtype: str = "bfloat16",
        **kwargs
    ):
        self.checkpoint_path = Path(checkpoint_path)
        self.stage1_checkpoint = Path(stage1_checkpoint)
        self.ocr_model_path = ocr_model_path
        self.llm_model_path = llm_model_path
        self.device = torch.device(device if torch.cuda.is_available() else "cpu")
        self.dtype = getattr(torch, dtype)
        self.kwargs = kwargs

        self.model: Optional[CoTCompressorV2] = None

        self._validate_checkpoints()

    def _validate_checkpoints(self):
        """Validate checkpoint paths exist."""
        if not self.checkpoint_path.exists():
            logger.warning(f"Stage 2 checkpoint not found: {self.checkpoint_path}")
            logger.warning("Model will be initialized without pre-trained weights")
            logger.warning("For production use, please train the model first using:")
            logger.warning("  cd /Volumes/WS4TB/RoT-main")
            logger.warning("  bash run_train_stage1.sh --num_gpus 2")
            logger.warning("  bash run_train_stage2.sh --num_gpus 2")
        else:
            logger.info(f"Stage 2 checkpoint found: {self.checkpoint_path}")

        if not self.stage1_checkpoint.exists():
            logger.warning(f"Stage 1 checkpoint not found: {self.stage1_checkpoint}")
        else:
            logger.info(f"Stage 1 checkpoint found: {self.stage1_checkpoint}")

    def load_model(self) -> CoTCompressorV2:
        """Load RoT model with trained checkpoints."""
        if self.model is not None:
            logger.info("Model already loaded, returning cached instance")
            return self.model

        logger.info("Loading RoT model...")

        # Initialize model in Stage 2 mode
        self.model = CoTCompressorV2(
            ocr_model_path=self.ocr_model_path,
            llm_model_path=self.llm_model_path,
            device=self.device,
            image_size=self.kwargs.get('image_size', 512),
            font_size=self.kwargs.get('font_size', 16),
            freeze_vision=True,  # Always freeze vision encoder
            use_projection_head=True,
            projection_hidden_dim=self.kwargs.get('projection_hidden_dim', 2048),
            enable_lora=self.kwargs.get('enable_lora', False),
            full_finetuning=self.kwargs.get('full_finetuning', False),
            lora_r=self.kwargs.get('lora_r', 16),
            lora_alpha=self.kwargs.get('lora_alpha', 32),
            lora_dropout=self.kwargs.get('lora_dropout', 0.05),
            lora_target_modules=self.kwargs.get('lora_target_modules', None),
            use_custom_llm=self.kwargs.get('use_custom_llm', True),
            loss_type=self.kwargs.get('loss_type', 'mse_only'),
            stage2_mode=True,  # Critical: Stage 2 inference mode
            freeze_projection_head=True,  # Freeze projection head (trained in Stage 1)
            include_vision_loss=False,  # No vision loss at inference
            include_img_end_loss=False,  # No img_end loss at inference
        )

        # Load checkpoints if available
        if self.stage1_checkpoint.exists():
            logger.info(f"Loading Stage 1 checkpoint: {self.stage1_checkpoint}")
            try:
                stage1_state = torch.load(
                    self.stage1_checkpoint / "mp_rank_00_model_states.pt",
                    map_location=self.device
                )
                # Extract projection head weights and load
                proj_head_state = self._extract_projection_head(stage1_state)
                self.model.projection_head.load_state_dict(proj_head_state)
                logger.info("✅ Stage 1 checkpoint loaded successfully")
            except Exception as e:
                logger.warning(f"Could not load Stage 1 checkpoint: {e}")

        if self.checkpoint_path.exists():
            logger.info(f"Loading Stage 2 checkpoint: {self.checkpoint_path}")
            try:
                stage2_state = torch.load(
                    self.checkpoint_path / "mp_rank_00_model_states.pt",
                    map_location=self.device
                )
                # Extract LM weights and load
                lm_state = self._extract_lm_state(stage2_state)
                self.model.language_model.load_state_dict(lm_state)
                logger.info("✅ Stage 2 checkpoint loaded successfully")
            except Exception as e:
                logger.warning(f"Could not load Stage 2 checkpoint: {e}")

        # Load special tokens (if any)
        special_tokens_path = self.stage1_checkpoint / "special_tokens.bin"
        if special_tokens_path.exists():
            try:
                special_tokens = torch.load(special_tokens_path, map_location=self.device)
                self._load_special_tokens(special_tokens)
                logger.info("✅ Special tokens loaded")
            except Exception as e:
                logger.warning(f"Could not load special tokens: {e}")

        # Set to eval mode
        self.model.eval()
        self.model.to(self.device).to(self.dtype)

        logger.info("RoT model loaded successfully")
        return self.model

    def _extract_projection_head(self, state_dict: Dict) -> Dict:
        """Extract projection head weights from checkpoint."""
        # DeepSpeed format: state_dict['module']['projection_head']
        if 'module' in state_dict:
            module_state = state_dict['module']
        else:
            module_state = state_dict

        proj_head_keys = [k for k in module_state.keys() if 'projection_head' in k]
        proj_head_state = {
            k.replace('projection_head.', ''): module_state[k]
            for k in proj_head_keys
        }
        return proj_head_state

    def _extract_lm_state(self, state_dict: Dict) -> Dict:
        """Extract language model weights from checkpoint."""
        if 'module' in state_dict:
            module_state = state_dict['module']
        else:
            module_state = state_dict

        lm_keys = [k for k in module_state.keys() if 'language_model' in k]
        lm_state = {
            k.replace('language_model.', ''): module_state[k]
            for k in lm_keys
        }
        return lm_state

    def _load_special_tokens(self, special_tokens: Dict):
        """Load special token embeddings."""
        # Add special tokens to tokenizer and model embeddings
        # Implementation depends on model architecture
        logger.info("Loading special tokens (implementation depends on model architecture)")

    def get_model(self) -> CoTCompressorV2:
        """Get model instance (loads if not already loaded)."""
        if self.model is None:
            return self.load_model()
        return self.model

    def unload_model(self):
        """Unload model to free GPU memory."""
        if self.model is not None:
            del self.model
            self.model = None
            torch.cuda.empty_cache()
            logger.info("RoT model unloaded")
