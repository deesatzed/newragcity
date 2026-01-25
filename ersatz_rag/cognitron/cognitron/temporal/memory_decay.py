"""
Memory Decay Algorithm - Breakthrough intelligent forgetting system
Makes the system MORE valuable over time by forgetting specifics while preserving wisdom
"""

import json
import math
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from uuid import uuid4
from enum import Enum

class MemoryType(str, Enum):
    """Types of memory that can decay at different rates"""
    TACTICAL = "tactical"          # Short-term decisions, temporary workarounds
    PROCEDURAL = "procedural"      # How things were done, specific steps  
    FACTUAL = "factual"           # Specific facts, data points, measurements
    STRATEGIC = "strategic"        # High-level decisions, architectural choices
    WISDOM = "wisdom"             # Patterns, principles, lessons learned
    BREAKTHROUGH = "breakthrough"  # Major insights that changed everything


class DecayFunction(str, Enum):
    """Mathematical decay functions for different memory types"""
    EXPONENTIAL = "exponential"    # Rapid initial decay, then leveling (tactical)
    LINEAR = "linear"             # Steady decay rate (procedural)
    LOGARITHMIC = "logarithmic"   # Slow decay that preserves long-term (wisdom)
    ASYMPTOTIC = "asymptotic"     # Approaches but never reaches zero (breakthrough)


@dataclass
class MemoryItem:
    """Individual memory item with decay characteristics"""
    memory_id: str
    content: str
    memory_type: MemoryType
    decay_function: DecayFunction
    
    # Temporal information
    created_at: datetime
    last_accessed: datetime
    access_count: int
    
    # Decay parameters
    initial_importance: float  # 0.0 - 1.0
    current_importance: float  # Calculated with decay
    decay_rate: float         # How fast it decays
    half_life_days: float     # Half-life in days
    
    # Preservation factors
    reinforcement_count: int  # How many times it was reinforced
    wisdom_extraction_score: float  # How much wisdom was extracted
    crystallization_potential: float  # Potential for pattern crystallization
    
    # Relationships
    related_memories: List[str]  # Related memory IDs
    breakthrough_marker: bool    # Marked as breakthrough insight
    
    # Context
    project_context: str
    developer_context: Dict[str, Any]


@dataclass
class WisdomExtraction:
    """Extracted wisdom from decaying memories"""
    wisdom_id: str
    extracted_from: List[str]  # Source memory IDs
    wisdom_content: str
    confidence_score: float
    generalization_level: float  # How broadly applicable
    preservation_priority: float  # How important to preserve
    created_at: datetime


@dataclass
class DecayReport:
    """Report on memory decay process"""
    report_id: str
    decay_cycle_timestamp: datetime
    memories_processed: int
    memories_decayed: int
    memories_forgotten: int
    wisdom_extracted: int
    storage_saved_mb: float
    system_efficiency_gain: float
    breakthrough_insights_preserved: int


class MemoryDecay:
    """
    Breakthrough Memory Decay Algorithm
    
    Core breakthrough: Instead of accumulating more memory, the system becomes
    MORE intelligent by forgetting specifics while crystallizing wisdom.
    
    Key principles:
    1. Tactical details decay rapidly (they become obsolete)
    2. Procedural knowledge decays moderately (approaches change)
    3. Strategic insights decay slowly (remain relevant longer)
    4. Wisdom never fully decays (gets extracted and preserved)
    5. Breakthrough insights are immortal (preserved forever)
    """
    
    def __init__(self):
        self.memories: Dict[str, MemoryItem] = {}
        self.wisdom_extractions: Dict[str, WisdomExtraction] = {}
        self.decay_reports: List[DecayReport] = []
        
        # Storage paths
        self.storage_dir = Path.home() / ".cognitron" / "temporal" / "memory"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.memories_file = self.storage_dir / "memories.json"
        self.wisdom_file = self.storage_dir / "wisdom_extractions.json"
        self.reports_file = self.storage_dir / "decay_reports.json"
        
        # Decay configuration
        self.decay_thresholds = {
            MemoryType.TACTICAL: 0.1,        # Forget when importance < 0.1
            MemoryType.PROCEDURAL: 0.15,     # Forget when importance < 0.15
            MemoryType.FACTUAL: 0.2,         # Forget when importance < 0.2
            MemoryType.STRATEGIC: 0.3,       # Forget when importance < 0.3
            MemoryType.WISDOM: 0.5,          # Extract wisdom, never fully forget
            MemoryType.BREAKTHROUGH: 1.0     # Never decay
        }
        
        # Default half-life periods (in days)
        self.default_half_lives = {
            MemoryType.TACTICAL: 7.0,        # 1 week
            MemoryType.PROCEDURAL: 30.0,     # 1 month
            MemoryType.FACTUAL: 90.0,        # 3 months
            MemoryType.STRATEGIC: 365.0,     # 1 year
            MemoryType.WISDOM: 1825.0,       # 5 years (very slow)
            MemoryType.BREAKTHROUGH: float('inf')  # Never decays
        }
    
    async def store_memory(
        self,
        content: str,
        memory_type: MemoryType,
        importance: float = 0.8,
        context: Optional[Dict[str, Any]] = None
    ) -> MemoryItem:
        """
        Store a new memory item with decay characteristics
        
        Args:
            content: The memory content
            memory_type: Type of memory (affects decay rate)
            importance: Initial importance (0.0 - 1.0)
            context: Optional context information
            
        Returns:
            Stored memory item
        """
        
        # Determine decay function based on memory type
        decay_function = self._get_decay_function(memory_type)
        
        # Calculate decay rate based on importance and type
        half_life = self.default_half_lives[memory_type]
        if importance > 0.9:  # Very important memories decay slower
            half_life *= 2.0
        elif importance < 0.5:  # Less important memories decay faster
            half_life *= 0.5
        
        decay_rate = math.log(2) / half_life  # Lambda for exponential decay
        
        memory_item = MemoryItem(
            memory_id=str(uuid4()),
            content=content,
            memory_type=memory_type,
            decay_function=decay_function,
            
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            access_count=1,
            
            initial_importance=importance,
            current_importance=importance,
            decay_rate=decay_rate,
            half_life_days=half_life,
            
            reinforcement_count=0,
            wisdom_extraction_score=0.0,
            crystallization_potential=0.0,
            
            related_memories=[],
            breakthrough_marker=memory_type == MemoryType.BREAKTHROUGH,
            
            project_context=context.get("project", "unknown") if context else "unknown",
            developer_context=context or {}
        )
        
        self.memories[memory_item.memory_id] = memory_item
        await self._persist_memories()
        
        return memory_item
    
    def _get_decay_function(self, memory_type: MemoryType) -> DecayFunction:
        """Determine appropriate decay function for memory type"""
        
        function_mapping = {
            MemoryType.TACTICAL: DecayFunction.EXPONENTIAL,
            MemoryType.PROCEDURAL: DecayFunction.LINEAR,
            MemoryType.FACTUAL: DecayFunction.EXPONENTIAL,
            MemoryType.STRATEGIC: DecayFunction.LOGARITHMIC,
            MemoryType.WISDOM: DecayFunction.LOGARITHMIC,
            MemoryType.BREAKTHROUGH: DecayFunction.ASYMPTOTIC
        }
        
        return function_mapping.get(memory_type, DecayFunction.LINEAR)
    
    async def apply_decay_cycle(self, force_decay: bool = False) -> DecayReport:
        """
        Apply one cycle of memory decay across all stored memories
        
        Args:
            force_decay: Force decay even if not enough time has passed
            
        Returns:
            Report of decay cycle results
        """
        
        print("🧠 Starting memory decay cycle...")
        start_time = time.time()
        
        if not self.memories:
            await self._load_memories()
        
        # Calculate decay for all memories
        memories_processed = 0
        memories_decayed = 0
        memories_forgotten = 0
        wisdom_extracted = 0
        
        current_time = datetime.now()
        
        for memory_id, memory in list(self.memories.items()):
            memories_processed += 1
            
            # Calculate current importance based on decay
            old_importance = memory.current_importance
            memory.current_importance = self._calculate_current_importance(memory, current_time)
            
            if memory.current_importance != old_importance:
                memories_decayed += 1
            
            # Check if memory should be forgotten or wisdom extracted
            threshold = self.decay_thresholds[memory.memory_type]
            
            if memory.current_importance <= threshold:
                if memory.memory_type in [MemoryType.WISDOM, MemoryType.STRATEGIC]:
                    # Extract wisdom before forgetting
                    wisdom = await self._extract_wisdom_from_memory(memory)
                    if wisdom:
                        self.wisdom_extractions[wisdom.wisdom_id] = wisdom
                        wisdom_extracted += 1
                
                if memory.memory_type != MemoryType.BREAKTHROUGH:  # Never forget breakthroughs
                    del self.memories[memory_id]
                    memories_forgotten += 1
                    print(f"   🗑️  Forgot {memory.memory_type.value} memory: {memory.content[:50]}...")
        
        # Create decay report
        cycle_time = time.time() - start_time
        storage_saved = memories_forgotten * 0.1  # Rough estimate in MB
        efficiency_gain = memories_forgotten / max(memories_processed, 1) * 100
        
        report = DecayReport(
            report_id=str(uuid4()),
            decay_cycle_timestamp=current_time,
            memories_processed=memories_processed,
            memories_decayed=memories_decayed,
            memories_forgotten=memories_forgotten,
            wisdom_extracted=wisdom_extracted,
            storage_saved_mb=storage_saved,
            system_efficiency_gain=efficiency_gain,
            breakthrough_insights_preserved=len([m for m in self.memories.values() if m.breakthrough_marker])
        )
        
        self.decay_reports.append(report)
        
        # Persist changes
        await self._persist_memories()
        await self._persist_wisdom()
        await self._persist_reports()
        
        print(f"✅ Decay cycle completed in {cycle_time:.2f}s")
        print(f"   📊 Processed: {memories_processed}, Decayed: {memories_decayed}, Forgotten: {memories_forgotten}")
        print(f"   💡 Wisdom extracted: {wisdom_extracted}, Storage saved: {storage_saved:.1f}MB")
        print(f"   🧠 System efficiency gain: {efficiency_gain:.1f}%")
        
        return report
    
    def _calculate_current_importance(self, memory: MemoryItem, current_time: datetime) -> float:
        """Calculate current importance based on decay function"""
        
        # Time elapsed since creation (in days)
        time_elapsed = (current_time - memory.created_at).total_seconds() / (24 * 3600)
        
        # Time since last access (affects decay rate)
        time_since_access = (current_time - memory.last_accessed).total_seconds() / (24 * 3600)
        
        # Base decay calculation
        if memory.decay_function == DecayFunction.EXPONENTIAL:
            # Standard exponential decay: I(t) = I₀ * e^(-λt)
            importance = memory.initial_importance * math.exp(-memory.decay_rate * time_elapsed)
            
        elif memory.decay_function == DecayFunction.LINEAR:
            # Linear decay: I(t) = I₀ - (I₀ * t / half_life)
            importance = memory.initial_importance * (1 - time_elapsed / memory.half_life_days)
            
        elif memory.decay_function == DecayFunction.LOGARITHMIC:
            # Logarithmic decay (slower): I(t) = I₀ * (1 - log(1 + t/half_life))
            if time_elapsed > 0:
                importance = memory.initial_importance * (1 - math.log(1 + time_elapsed / memory.half_life_days))
            else:
                importance = memory.initial_importance
                
        elif memory.decay_function == DecayFunction.ASYMPTOTIC:
            # Asymptotic decay (approaches but never reaches zero)
            importance = memory.initial_importance / (1 + time_elapsed / memory.half_life_days)
            
        else:  # Default to exponential
            importance = memory.initial_importance * math.exp(-memory.decay_rate * time_elapsed)
        
        # Apply reinforcement factor (slows decay)
        if memory.reinforcement_count > 0:
            reinforcement_factor = 1 + (memory.reinforcement_count * 0.1)
            importance *= reinforcement_factor
        
        # Apply recency factor (recent access slows decay)
        if time_since_access < 7:  # Accessed within last week
            recency_factor = 1 + (7 - time_since_access) * 0.05
            importance *= recency_factor
        
        # Ensure importance stays within bounds
        return max(0.0, min(1.0, importance))
    
    async def _extract_wisdom_from_memory(self, memory: MemoryItem) -> Optional[WisdomExtraction]:
        """Extract generalized wisdom from a decaying memory"""
        
        # Skip if already extracted
        if memory.wisdom_extraction_score > 0:
            return None
        
        # Different wisdom extraction strategies based on memory type
        wisdom_content = ""
        confidence = 0.0
        generalization = 0.0
        
        if memory.memory_type == MemoryType.STRATEGIC:
            # Extract strategic principles
            if "architecture" in memory.content.lower():
                wisdom_content = f"Architectural principle: {self._generalize_strategic_content(memory.content)}"
                confidence = 0.8
                generalization = 0.9
            elif "decision" in memory.content.lower():
                wisdom_content = f"Decision principle: {self._generalize_decision_content(memory.content)}"
                confidence = 0.7
                generalization = 0.8
                
        elif memory.memory_type == MemoryType.WISDOM:
            # Already wisdom, just preserve essence
            wisdom_content = f"Core wisdom: {memory.content}"
            confidence = 0.9
            generalization = 1.0
            
        if not wisdom_content:
            return None
        
        wisdom = WisdomExtraction(
            wisdom_id=str(uuid4()),
            extracted_from=[memory.memory_id],
            wisdom_content=wisdom_content,
            confidence_score=confidence,
            generalization_level=generalization,
            preservation_priority=confidence * generalization,
            created_at=datetime.now()
        )
        
        # Mark memory as wisdom-extracted
        memory.wisdom_extraction_score = confidence
        
        return wisdom
    
    def _generalize_strategic_content(self, content: str) -> str:
        """Generalize strategic content into reusable principle"""
        
        # Simple heuristics for generalization (could be enhanced with NLP)
        content_lower = content.lower()
        
        if "iterative" in content_lower and "improvement" in content_lower:
            return "Use iterative improvement cycles to achieve breakthrough performance gains"
        elif "confidence" in content_lower and "tracking" in content_lower:
            return "Implement enterprise-grade confidence tracking for reliable AI systems"
        elif "temporal" in content_lower and "pattern" in content_lower:
            return "Leverage temporal patterns to predict and optimize developer workflows"
        else:
            return f"Strategic insight: {content[:100]}..."
    
    def _generalize_decision_content(self, content: str) -> str:
        """Generalize decision content into reusable principle"""
        
        content_lower = content.lower()
        
        if "accuracy" in content_lower:
            return "Prioritize measurable accuracy improvements in system iterations"
        elif "architecture" in content_lower:
            return "Choose architecture based on scalability and maintainability requirements"
        else:
            return f"Decision principle: {content[:100]}..."
    
    async def reinforce_memory(self, memory_id: str) -> bool:
        """
        Reinforce a memory to slow its decay (accessed/used again)
        
        Args:
            memory_id: ID of memory to reinforce
            
        Returns:
            True if reinforced successfully
        """
        
        if memory_id not in self.memories:
            return False
        
        memory = self.memories[memory_id]
        memory.last_accessed = datetime.now()
        memory.access_count += 1
        memory.reinforcement_count += 1
        
        # Boost current importance slightly
        memory.current_importance = min(1.0, memory.current_importance + 0.05)
        
        await self._persist_memories()
        return True
    
    async def mark_as_breakthrough(self, memory_id: str) -> bool:
        """
        Mark a memory as breakthrough insight (preserves forever)
        
        Args:
            memory_id: ID of memory to mark as breakthrough
            
        Returns:
            True if marked successfully
        """
        
        if memory_id not in self.memories:
            return False
        
        memory = self.memories[memory_id]
        memory.memory_type = MemoryType.BREAKTHROUGH
        memory.decay_function = DecayFunction.ASYMPTOTIC
        memory.breakthrough_marker = True
        memory.half_life_days = float('inf')
        
        print(f"💎 Marked as breakthrough insight: {memory.content[:50]}...")
        
        await self._persist_memories()
        return True
    
    async def get_wisdom_summary(self) -> Dict[str, Any]:
        """Get summary of extracted wisdom and system intelligence"""
        
        if not self.wisdom_extractions:
            await self._load_wisdom()
        
        high_value_wisdom = [w for w in self.wisdom_extractions.values() if w.preservation_priority >= 0.7]
        breakthrough_memories = [m for m in self.memories.values() if m.breakthrough_marker]
        
        return {
            "total_wisdom_extractions": len(self.wisdom_extractions),
            "high_value_wisdom": len(high_value_wisdom),
            "breakthrough_insights_preserved": len(breakthrough_memories),
            "system_intelligence_score": self._calculate_system_intelligence(),
            "memory_efficiency": self._calculate_memory_efficiency(),
            "decay_cycles_completed": len(self.decay_reports),
            "breakthrough_capability": {
                "intelligent_forgetting": True,
                "wisdom_crystallization": len(self.wisdom_extractions) >= 5,
                "breakthrough_preservation": len(breakthrough_memories) >= 1,
                "temporal_intelligence": self._calculate_system_intelligence() >= 0.80
            },
            "top_wisdom": [
                {
                    "wisdom": w.wisdom_content,
                    "confidence": w.confidence_score,
                    "generalization": w.generalization_level
                }
                for w in sorted(high_value_wisdom, key=lambda x: x.preservation_priority, reverse=True)[:3]
            ]
        }
    
    def _calculate_system_intelligence(self) -> float:
        """Calculate overall system intelligence score"""
        
        if not self.wisdom_extractions and not self.memories:
            return 0.0
        
        # Intelligence comes from wisdom quality and breakthrough preservation
        wisdom_quality = sum(w.confidence_score * w.generalization_level for w in self.wisdom_extractions.values())
        wisdom_quality = wisdom_quality / max(len(self.wisdom_extractions), 1)
        
        breakthrough_factor = min(1.0, len([m for m in self.memories.values() if m.breakthrough_marker]) * 0.2)
        decay_efficiency = self._calculate_memory_efficiency()
        
        intelligence_score = (wisdom_quality * 0.5) + (breakthrough_factor * 0.3) + (decay_efficiency * 0.2)
        
        return min(1.0, intelligence_score)
    
    def _calculate_memory_efficiency(self) -> float:
        """Calculate memory system efficiency"""
        
        if not self.decay_reports:
            return 0.0
        
        total_efficiency_gain = sum(r.system_efficiency_gain for r in self.decay_reports)
        avg_efficiency = total_efficiency_gain / len(self.decay_reports) / 100  # Convert percentage to 0-1
        
        return min(1.0, avg_efficiency)
    
    async def predict_future_decay(self, days_ahead: int = 30) -> Dict[str, Any]:
        """
        Predict what memories will decay in the next N days
        
        Args:
            days_ahead: Number of days to predict ahead
            
        Returns:
            Prediction of future decay patterns
        """
        
        future_time = datetime.now() + timedelta(days=days_ahead)
        predictions = {
            "prediction_horizon_days": days_ahead,
            "memories_at_risk": [],
            "wisdom_extraction_opportunities": [],
            "breakthrough_insights_safe": 0
        }
        
        for memory_id, memory in self.memories.items():
            future_importance = self._calculate_current_importance(memory, future_time)
            threshold = self.decay_thresholds[memory.memory_type]
            
            if future_importance <= threshold:
                risk_info = {
                    "memory_id": memory_id,
                    "content_preview": memory.content[:50] + "...",
                    "memory_type": memory.memory_type.value,
                    "current_importance": memory.current_importance,
                    "predicted_importance": future_importance,
                    "days_until_forgotten": days_ahead
                }
                
                if memory.memory_type in [MemoryType.WISDOM, MemoryType.STRATEGIC]:
                    predictions["wisdom_extraction_opportunities"].append(risk_info)
                else:
                    predictions["memories_at_risk"].append(risk_info)
            
            if memory.breakthrough_marker:
                predictions["breakthrough_insights_safe"] += 1
        
        return predictions
    
    async def _persist_memories(self):
        """Persist memories to disk"""
        try:
            memories_data = {}
            for memory_id, memory in self.memories.items():
                memory_dict = asdict(memory)
                memory_dict["created_at"] = memory_dict["created_at"].isoformat()
                memory_dict["last_accessed"] = memory_dict["last_accessed"].isoformat()
                memories_data[memory_id] = memory_dict
            
            with open(self.memories_file, 'w') as f:
                json.dump(memories_data, f, indent=2)
                
        except Exception as e:
            print(f"Warning: Could not persist memories: {e}")
    
    async def _persist_wisdom(self):
        """Persist wisdom extractions to disk"""
        try:
            wisdom_data = {}
            for wisdom_id, wisdom in self.wisdom_extractions.items():
                wisdom_dict = asdict(wisdom)
                wisdom_dict["created_at"] = wisdom_dict["created_at"].isoformat()
                wisdom_data[wisdom_id] = wisdom_dict
            
            with open(self.wisdom_file, 'w') as f:
                json.dump(wisdom_data, f, indent=2)
                
        except Exception as e:
            print(f"Warning: Could not persist wisdom: {e}")
    
    async def _persist_reports(self):
        """Persist decay reports to disk"""
        try:
            reports_data = []
            for report in self.decay_reports:
                report_dict = asdict(report)
                report_dict["decay_cycle_timestamp"] = report_dict["decay_cycle_timestamp"].isoformat()
                reports_data.append(report_dict)
            
            with open(self.reports_file, 'w') as f:
                json.dump(reports_data, f, indent=2)
                
        except Exception as e:
            print(f"Warning: Could not persist reports: {e}")
    
    async def _load_memories(self):
        """Load memories from disk"""
        try:
            if self.memories_file.exists():
                with open(self.memories_file, 'r') as f:
                    memories_data = json.load(f)
                
                for memory_id, memory_dict in memories_data.items():
                    memory_dict["created_at"] = datetime.fromisoformat(memory_dict["created_at"])
                    memory_dict["last_accessed"] = datetime.fromisoformat(memory_dict["last_accessed"])
                    memory_dict["memory_type"] = MemoryType(memory_dict["memory_type"])
                    memory_dict["decay_function"] = DecayFunction(memory_dict["decay_function"])
                    self.memories[memory_id] = MemoryItem(**memory_dict)
                    
        except Exception as e:
            print(f"Warning: Could not load memories: {e}")
    
    async def _load_wisdom(self):
        """Load wisdom extractions from disk"""
        try:
            if self.wisdom_file.exists():
                with open(self.wisdom_file, 'r') as f:
                    wisdom_data = json.load(f)
                
                for wisdom_id, wisdom_dict in wisdom_data.items():
                    wisdom_dict["created_at"] = datetime.fromisoformat(wisdom_dict["created_at"])
                    self.wisdom_extractions[wisdom_id] = WisdomExtraction(**wisdom_dict)
                    
        except Exception as e:
            print(f"Warning: Could not load wisdom: {e}")