"""
Cognitron: Project Memory Brain - Breakthrough Developer Intelligence System

The world's first local developer intelligence system that learns temporal patterns
and eliminates memory through prediction. Features breakthrough temporal intelligence
that understands how developers solve problems across project evolution.

Revolutionary Features:
- Temporal Pattern Recognition - Learns personal problem-solving evolution
- Context Resurrection - Instantly rebuilds mental state from any timepoint
- Intelligent Memory Decay - Gets smarter by forgetting wisely
- Pattern Crystallization - Extracts personal best practices as templates
- Predictive Intelligence - Predicts next actions based on learned patterns
- Local-Only Processing - Zero external sharing, competitive advantage preserved
"""

__version__ = "0.1.0"
__author__ = "Cognitron Team"
__email__ = "team@cognitron.ai"

from .core.agent import CognitronAgent
from .core.confidence import ConfidenceProfile, calculate_confidence_profile
from .core.memory import CaseMemory
from .indexing.service import IndexingService
from .topics.service import TopicService

# Breakthrough Temporal Intelligence Components
from .temporal.project_discovery import ProjectDiscovery
from .temporal.pattern_engine import TemporalPatternEngine
from .temporal.context_resurrection import ContextResurrection
from .temporal.memory_decay import MemoryDecay
from .temporal.pattern_crystallization import PatternCrystallization

__all__ = [
    "CognitronAgent",
    "ConfidenceProfile", 
    "calculate_confidence_profile",
    "CaseMemory",
    "IndexingService",
    "TopicService",
    # Breakthrough Temporal Intelligence
    "ProjectDiscovery",
    "TemporalPatternEngine",
    "ContextResurrection", 
    "MemoryDecay",
    "PatternCrystallization",
]