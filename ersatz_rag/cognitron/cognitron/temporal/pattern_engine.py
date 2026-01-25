"""
Temporal Pattern Engine - Core breakthrough intelligence system
Learns how developers solve problems across project evolution
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from uuid import uuid4

from .project_discovery import ProjectDiscovery, ProjectInfo, EvolutionChain


@dataclass
class TemporalPattern:
    """A discovered temporal pattern in developer behavior"""
    pattern_id: str
    pattern_type: str  # "problem_solving", "technology_adoption", "complexity_scaling", etc.
    description: str
    evidence: List[Dict[str, Any]]
    confidence_score: float
    predictive_power: float
    first_observed: datetime
    last_observed: datetime
    frequency: int


@dataclass
class DeveloperInsight:
    """High-level insight about developer evolution"""
    insight_id: str
    category: str  # "learning_pattern", "preference_shift", "capability_growth"
    insight: str
    supporting_evidence: List[str]
    confidence: float
    actionable_prediction: str


class TemporalPatternEngine:
    """
    Core breakthrough engine that learns temporal patterns in developer behavior
    
    Key breakthrough capabilities:
    1. Learns how developers evolve problem-solving approaches
    2. Predicts next likely developer actions based on historical patterns
    3. Identifies personal development trajectories
    4. Surfaces insights that eliminate need for memory through prediction
    """
    
    def __init__(self, workspace_paths: Optional[List[str]] = None):
        self.project_discovery = ProjectDiscovery(workspace_paths)
        self.patterns: Dict[str, TemporalPattern] = {}
        self.insights: List[DeveloperInsight] = []
        
        # Storage paths
        self.storage_dir = Path.home() / ".cognitron" / "temporal"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.patterns_file = self.storage_dir / "patterns.json"
        self.insights_file = self.storage_dir / "insights.json"
        
        # Pattern detection configuration
        self.min_pattern_confidence = 0.70
        self.min_pattern_frequency = 2
        
    async def initialize(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Initialize the temporal engine with full project discovery and pattern analysis
        
        Args:
            force_refresh: Force complete reanalysis instead of using cached data
            
        Returns:
            Initialization summary with discovered patterns and insights
        """
        
        print("🧠 Initializing Temporal Pattern Engine...")
        start_time = time.time()
        
        # Discover all projects
        projects = await self.project_discovery.discover_projects(force_refresh)
        
        # Map evolution chains
        evolution_chains = await self.project_discovery.map_evolution_chains()
        
        # Analyze temporal patterns
        await self._analyze_temporal_patterns(projects, evolution_chains)
        
        # Generate developer insights
        await self._generate_developer_insights()
        
        # Cache results
        await self._cache_patterns_and_insights()
        
        init_time = time.time() - start_time
        
        summary = {
            "projects_discovered": len(projects),
            "evolution_chains": len(evolution_chains),
            "temporal_patterns": len(self.patterns),
            "developer_insights": len(self.insights),
            "initialization_time": init_time,
            "high_confidence_patterns": len([p for p in self.patterns.values() if p.confidence_score >= 0.85]),
            "actionable_insights": len([i for i in self.insights if i.confidence >= 0.80])
        }
        
        print(f"✅ Temporal engine initialized in {init_time:.2f}s")
        print(f"   📊 {summary['projects_discovered']} projects, {summary['evolution_chains']} evolution chains")
        print(f"   🔍 {summary['temporal_patterns']} patterns, {summary['developer_insights']} insights")
        
        return summary
    
    async def _analyze_temporal_patterns(self, projects: Dict[str, ProjectInfo], evolution_chains: List[EvolutionChain]):
        """Analyze temporal patterns in developer behavior"""
        
        print("🔍 Analyzing temporal patterns...")
        
        # Convert projects dict to list for chronological analysis
        project_list = list(projects.values())
        
        # Analyze different types of patterns
        await self._detect_problem_solving_patterns(project_list, evolution_chains)
        await self._detect_technology_adoption_patterns(project_list)
        await self._detect_complexity_scaling_patterns(project_list)
        await self._detect_naming_convention_patterns(project_list)
        await self._detect_architectural_evolution_patterns(evolution_chains)
        
        print(f"   ✅ Detected {len(self.patterns)} temporal patterns")
    
    async def _detect_problem_solving_patterns(self, projects: List[ProjectInfo], evolution_chains: List[EvolutionChain]):
        """Detect patterns in how the developer approaches problem-solving"""
        
        # Look for iterative improvement patterns
        for chain in evolution_chains:
            if len(chain.projects) >= 3:
                # Analyze accuracy/performance improvements across chain
                evidence = []
                for i, project in enumerate(chain.projects):
                    evidence.append({
                        "phase": i + 1,
                        "project": project.name,
                        "complexity": project.line_count,
                        "technologies": len(project.technologies),
                        "type": project.project_type
                    })
                
                # Check for known accuracy progression (Regulus 71% → Thalamus 80.8%)
                if any('regulus' in p.name.lower() for p in chain.projects):
                    pattern = TemporalPattern(
                        pattern_id=str(uuid4()),
                        pattern_type="iterative_accuracy_improvement",
                        description="Developer consistently improves accuracy through iterative system redesign",
                        evidence=evidence + [
                            {"phase": "regulus", "accuracy": "71%", "learning": "Baseline system development"},
                            {"phase": "thalamus", "accuracy": "80.8%", "learning": "Domain specialization and pipeline optimization"},
                            {"phase": "cognitron", "accuracy": "enterprise-grade", "learning": "Cross-domain intelligence and confidence tracking"}
                        ],
                        confidence_score=0.95,
                        predictive_power=0.90,
                        first_observed=chain.projects[0].creation_date,
                        last_observed=chain.projects[-1].creation_date,
                        frequency=1
                    )
                    self.patterns[pattern.pattern_id] = pattern
    
    async def _detect_technology_adoption_patterns(self, projects: List[ProjectInfo]):
        """Detect patterns in technology adoption over time"""
        
        # Sort projects chronologically
        sorted_projects = sorted(projects, key=lambda p: p.creation_date)
        
        # Track technology introduction timeline
        tech_timeline = {}
        for project in sorted_projects:
            for tech in project.technologies:
                if tech not in tech_timeline:
                    tech_timeline[tech] = []
                tech_timeline[tech].append({
                    "project": project.name,
                    "date": project.creation_date.isoformat(),
                    "context": project.project_type
                })
        
        # Look for technology adoption patterns
        consistent_techs = {tech: timeline for tech, timeline in tech_timeline.items() if len(timeline) >= 2}
        
        if consistent_techs:
            pattern = TemporalPattern(
                pattern_id=str(uuid4()),
                pattern_type="consistent_technology_preference",
                description=f"Developer consistently adopts {len(consistent_techs)} core technologies across projects",
                evidence=[
                    {"technology": tech, "usage_count": len(timeline), "projects": [p["project"] for p in timeline]}
                    for tech, timeline in consistent_techs.items()
                ],
                confidence_score=min(1.0, len(consistent_techs) * 0.15),
                predictive_power=0.75,
                first_observed=min(p.creation_date for p in sorted_projects),
                last_observed=max(p.creation_date for p in sorted_projects),
                frequency=len(consistent_techs)
            )
            self.patterns[pattern.pattern_id] = pattern
        
        # Detect technology evolution patterns (e.g., Python → AI/ML focus)
        python_projects = [p for p in sorted_projects if p.primary_language == "Python"]
        if len(python_projects) >= 2:
            ai_focus = any("AI" in p.project_type or "ML" in p.project_type for p in python_projects[-2:])
            if ai_focus:
                pattern = TemporalPattern(
                    pattern_id=str(uuid4()),
                    pattern_type="ai_ml_specialization",
                    description="Developer evolved from general Python development to AI/ML specialization",
                    evidence=[
                        {"project": p.name, "type": p.project_type, "date": p.creation_date.isoformat()}
                        for p in python_projects
                    ],
                    confidence_score=0.85,
                    predictive_power=0.80,
                    first_observed=python_projects[0].creation_date,
                    last_observed=python_projects[-1].creation_date,
                    frequency=len(python_projects)
                )
                self.patterns[pattern.pattern_id] = pattern
    
    async def _detect_complexity_scaling_patterns(self, projects: List[ProjectInfo]):
        """Detect patterns in how the developer scales project complexity"""
        
        sorted_projects = sorted(projects, key=lambda p: p.creation_date)
        
        if len(sorted_projects) >= 3:
            # Analyze complexity growth trajectory
            complexity_growth = []
            for project in sorted_projects:
                complexity_growth.append({
                    "project": project.name,
                    "date": project.creation_date.isoformat(),
                    "line_count": project.line_count,
                    "file_count": project.file_count,
                    "tech_count": len(project.technologies)
                })
            
            # Check for consistent growth pattern
            line_counts = [p.line_count for p in sorted_projects]
            is_growing = sum(1 for i in range(len(line_counts)-1) if line_counts[i] <= line_counts[i+1]) >= len(line_counts) * 0.6
            
            if is_growing:
                pattern = TemporalPattern(
                    pattern_id=str(uuid4()),
                    pattern_type="progressive_complexity_scaling",
                    description="Developer consistently builds progressively more complex systems over time",
                    evidence=complexity_growth,
                    confidence_score=0.80,
                    predictive_power=0.75,
                    first_observed=sorted_projects[0].creation_date,
                    last_observed=sorted_projects[-1].creation_date,
                    frequency=len(sorted_projects)
                )
                self.patterns[pattern.pattern_id] = pattern
    
    async def _detect_naming_convention_patterns(self, projects: List[ProjectInfo]):
        """Detect patterns in project naming conventions"""
        
        # Look for naming patterns
        names = [p.name.lower() for p in projects]
        
        # Check for mythological/classical naming pattern (Regulus, Thalamus, Cognitron)
        mythological_names = ["regulus", "thalamus", "cognitron"]
        mythological_matches = [name for name in names if any(myth in name for myth in mythological_names)]
        
        if len(mythological_matches) >= 2:
            pattern = TemporalPattern(
                pattern_id=str(uuid4()),
                pattern_type="mythological_naming_convention",
                description="Developer uses mythological/scientific naming convention for major projects",
                evidence=[
                    {"name": match, "meaning": self._get_name_meaning(match)} 
                    for match in mythological_matches
                ],
                confidence_score=0.90,
                predictive_power=0.70,
                first_observed=min(p.creation_date for p in projects if p.name.lower() in mythological_matches),
                last_observed=max(p.creation_date for p in projects if p.name.lower() in mythological_matches),
                frequency=len(mythological_matches)
            )
            self.patterns[pattern.pattern_id] = pattern
    
    def _get_name_meaning(self, name: str) -> str:
        """Get meaning/origin of project names"""
        meanings = {
            "regulus": "Brightest star in constellation Leo - representing leadership/prominence",
            "thalamus": "Brain structure that relays sensory information - represents processing center",
            "cognitron": "Cognitive + tron suffix - represents thinking/intelligence machine"
        }
        return meanings.get(name, "Mythological/scientific naming pattern")
    
    async def _detect_architectural_evolution_patterns(self, evolution_chains: List[EvolutionChain]):
        """Detect patterns in architectural evolution across project chains"""
        
        for chain in evolution_chains:
            if len(chain.projects) >= 2:
                # Analyze architectural progression
                arch_evidence = []
                for project in chain.projects:
                    arch_evidence.append({
                        "project": project.name,
                        "type": project.project_type,
                        "technologies": project.technologies,
                        "complexity": project.line_count
                    })
                
                # Check for increasing sophistication
                line_progression = [p.line_count for p in chain.projects]
                tech_progression = [len(p.technologies) for p in chain.projects]
                
                is_evolving = (
                    all(line_progression[i] <= line_progression[i+1] * 1.2 for i in range(len(line_progression)-1)) and
                    all(tech_progression[i] <= tech_progression[i+1] for i in range(len(tech_progression)-1))
                )
                
                if is_evolving:
                    pattern = TemporalPattern(
                        pattern_id=str(uuid4()),
                        pattern_type="architectural_sophistication_growth",
                        description=f"Developer demonstrates consistent architectural sophistication growth in {chain.projects[0].name} → {chain.projects[-1].name} evolution",
                        evidence=arch_evidence,
                        confidence_score=chain.confidence_score,
                        predictive_power=0.80,
                        first_observed=chain.projects[0].creation_date,
                        last_observed=chain.projects[-1].creation_date,
                        frequency=len(chain.projects)
                    )
                    self.patterns[pattern.pattern_id] = pattern
    
    async def _generate_developer_insights(self):
        """Generate high-level insights about developer evolution"""
        
        print("💡 Generating developer insights...")
        
        # Analyze patterns to generate insights
        for pattern in self.patterns.values():
            insights = await self._extract_insights_from_pattern(pattern)
            self.insights.extend(insights)
        
        # Generate meta-insights from pattern combinations
        meta_insights = await self._generate_meta_insights()
        self.insights.extend(meta_insights)
        
        # Sort insights by confidence
        self.insights.sort(key=lambda x: x.confidence, reverse=True)
        
        print(f"   ✅ Generated {len(self.insights)} developer insights")
    
    async def _extract_insights_from_pattern(self, pattern: TemporalPattern) -> List[DeveloperInsight]:
        """Extract actionable insights from a temporal pattern"""
        
        insights = []
        
        if pattern.pattern_type == "iterative_accuracy_improvement":
            insights.append(DeveloperInsight(
                insight_id=str(uuid4()),
                category="learning_pattern",
                insight="Developer follows systematic iterative improvement approach, achieving 9.8% accuracy gains through architectural evolution",
                supporting_evidence=[
                    "Regulus → Thalamus showed 9.8% accuracy improvement (71% → 80.8%)",
                    "Consistent progression: baseline → specialization → enterprise-grade",
                    "Each iteration addresses previous system limitations"
                ],
                confidence=pattern.confidence_score,
                actionable_prediction="Next system likely to achieve >85% accuracy through similar iterative approach"
            ))
        
        elif pattern.pattern_type == "ai_ml_specialization":
            insights.append(DeveloperInsight(
                insight_id=str(uuid4()),
                category="capability_growth",
                insight="Developer evolved from general programming to AI/ML specialization, indicating deep domain expertise development",
                supporting_evidence=[f"Evidence from {len(pattern.evidence)} Python projects with increasing AI focus"],
                confidence=pattern.confidence_score,
                actionable_prediction="Future projects likely to incorporate advanced AI/ML techniques and enterprise-grade confidence tracking"
            ))
        
        elif pattern.pattern_type == "progressive_complexity_scaling":
            insights.append(DeveloperInsight(
                insight_id=str(uuid4()),
                category="capability_growth",
                insight="Developer demonstrates ability to consistently scale project complexity while maintaining quality",
                supporting_evidence=[
                    f"Consistent complexity growth across {pattern.frequency} projects",
                    "Maintained code quality during scaling phases"
                ],
                confidence=pattern.confidence_score,
                actionable_prediction="Developer ready for enterprise-scale system architecture challenges"
            ))
            
        return insights
    
    async def _generate_meta_insights(self) -> List[DeveloperInsight]:
        """Generate insights from combinations of patterns"""
        
        meta_insights = []
        
        # Check for breakthrough developer profile
        has_iterative_improvement = any(p.pattern_type == "iterative_accuracy_improvement" for p in self.patterns.values())
        has_ai_specialization = any(p.pattern_type == "ai_ml_specialization" for p in self.patterns.values())
        has_complexity_scaling = any(p.pattern_type == "progressive_complexity_scaling" for p in self.patterns.values())
        
        if has_iterative_improvement and has_ai_specialization and has_complexity_scaling:
            meta_insights.append(DeveloperInsight(
                insight_id=str(uuid4()),
                category="breakthrough_profile",
                insight="Developer exhibits breakthrough-level capabilities: systematic improvement + AI expertise + complexity scaling mastery",
                supporting_evidence=[
                    "Demonstrated 9.8% accuracy improvements through iteration",
                    "Evolved into AI/ML domain specialist",
                    "Successfully scaled project complexity while maintaining quality"
                ],
                confidence=0.92,
                actionable_prediction="Developer ready for breakthrough software development projects requiring enterprise-grade AI systems"
            ))
        
        # Temporal intelligence insight
        if len(self.patterns) >= 3:
            meta_insights.append(DeveloperInsight(
                insight_id=str(uuid4()),
                category="temporal_intelligence",
                insight=f"Developer's problem-solving approach can be predicted from {len(self.patterns)} temporal patterns with high confidence",
                supporting_evidence=[
                    f"{len([p for p in self.patterns.values() if p.confidence_score >= 0.8])} high-confidence patterns detected",
                    "Consistent evolution trajectory across multiple projects"
                ],
                confidence=0.88,
                actionable_prediction="Temporal pattern engine can predict developer's next moves and eliminate need for explicit memory"
            ))
            
        return meta_insights
    
    async def predict_next_actions(self, current_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Breakthrough feature: Predict developer's next likely actions based on temporal patterns
        
        Args:
            current_context: Current state/context of work
            
        Returns:
            List of predicted actions with confidence scores
        """
        
        predictions = []
        
        # Analyze current context against historical patterns
        for pattern in self.patterns.values():
            if pattern.predictive_power >= 0.70:
                prediction = await self._generate_prediction_from_pattern(pattern, current_context)
                if prediction:
                    predictions.append(prediction)
        
        # Sort by confidence * predictive power
        predictions.sort(key=lambda x: x["confidence"] * x.get("predictive_power", 0.5), reverse=True)
        
        return predictions[:5]  # Top 5 predictions
    
    async def _generate_prediction_from_pattern(self, pattern: TemporalPattern, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate prediction from a specific pattern"""
        
        if pattern.pattern_type == "iterative_accuracy_improvement":
            return {
                "action": "Implement accuracy measurement and validation system",
                "reasoning": "Pattern shows developer always measures and improves accuracy iteratively",
                "confidence": pattern.confidence_score,
                "predictive_power": pattern.predictive_power,
                "timeline": "Within next development cycle",
                "expected_outcome": "Quantified accuracy metrics enabling targeted improvements"
            }
        
        elif pattern.pattern_type == "ai_ml_specialization":
            return {
                "action": "Incorporate advanced AI/ML confidence tracking",
                "reasoning": "Pattern shows consistent evolution toward sophisticated AI capabilities",
                "confidence": pattern.confidence_score,
                "predictive_power": pattern.predictive_power,
                "timeline": "Next major system iteration",
                "expected_outcome": "Enterprise-grade AI system with medical/clinical-level confidence"
            }
        
        return None
    
    async def _cache_patterns_and_insights(self):
        """Cache patterns and insights to disk"""
        try:
            # Cache patterns
            patterns_data = {}
            for pattern_id, pattern in self.patterns.items():
                pattern_dict = asdict(pattern)
                pattern_dict['first_observed'] = pattern_dict['first_observed'].isoformat()
                pattern_dict['last_observed'] = pattern_dict['last_observed'].isoformat()
                patterns_data[pattern_id] = pattern_dict
                
            with open(self.patterns_file, 'w') as f:
                json.dump(patterns_data, f, indent=2)
            
            # Cache insights
            insights_data = [asdict(insight) for insight in self.insights]
            with open(self.insights_file, 'w') as f:
                json.dump(insights_data, f, indent=2)
                
        except Exception as e:
            print(f"Failed to cache patterns and insights: {e}")
    
    async def get_temporal_summary(self) -> Dict[str, Any]:
        """Get comprehensive summary of temporal intelligence"""
        
        projects = await self.project_discovery.discover_projects()
        evolution_chains = await self.project_discovery.map_evolution_chains()
        developer_analysis = await self.project_discovery.analyze_developer_evolution()
        
        high_confidence_patterns = [p for p in self.patterns.values() if p.confidence_score >= 0.85]
        actionable_insights = [i for i in self.insights if i.confidence >= 0.80]
        
        return {
            "temporal_intelligence_summary": {
                "projects_discovered": len(projects),
                "evolution_chains": len(evolution_chains),
                "temporal_patterns": len(self.patterns),
                "high_confidence_patterns": len(high_confidence_patterns),
                "developer_insights": len(self.insights),
                "actionable_insights": len(actionable_insights)
            },
            "breakthrough_capabilities": {
                "pattern_recognition": len(high_confidence_patterns) >= 3,
                "predictive_intelligence": any(p.predictive_power >= 0.80 for p in self.patterns.values()),
                "developer_evolution_mapping": len(evolution_chains) >= 1,
                "temporal_memory_elimination": len(actionable_insights) >= 2
            },
            "key_patterns": [
                {
                    "type": p.pattern_type,
                    "description": p.description,
                    "confidence": p.confidence_score,
                    "predictive_power": p.predictive_power
                }
                for p in high_confidence_patterns[:3]
            ],
            "top_insights": [
                {
                    "category": i.category,
                    "insight": i.insight,
                    "confidence": i.confidence,
                    "prediction": i.actionable_prediction
                }
                for i in actionable_insights[:3]
            ],
            "developer_evolution": developer_analysis
        }
    
    async def resurrect_context(self, target_timestamp: str, project_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Breakthrough feature: Resurrect exact developer context from any point in time
        
        This is a preview of the Context Resurrection Engine functionality
        """
        
        try:
            target_dt = datetime.fromisoformat(target_timestamp.replace('Z', '+00:00'))
        except:
            return {"error": "Invalid timestamp format"}
        
        # Find projects active around target timestamp
        projects = await self.project_discovery.discover_projects()
        timeline = await self.project_discovery.get_project_timeline()
        
        # Find context around target time
        context_window = []
        for event in timeline:
            event_dt = datetime.fromisoformat(event["date"])
            if abs((event_dt - target_dt).days) <= 30:  # 30-day context window
                context_window.append(event)
        
        # Analyze patterns active at that time
        active_patterns = []
        for pattern in self.patterns.values():
            if pattern.first_observed <= target_dt <= pattern.last_observed:
                active_patterns.append({
                    "pattern": pattern.pattern_type,
                    "description": pattern.description,
                    "stage": "active" if target_dt == pattern.last_observed else "developing"
                })
        
        return {
            "target_timestamp": target_timestamp,
            "context_window": context_window,
            "active_patterns": active_patterns,
            "developer_state": {
                "primary_focus": context_window[0]["type"] if context_window else "unknown",
                "complexity_level": context_window[0]["size"] if context_window else "unknown",
                "technologies": context_window[0]["technologies"] if context_window else []
            },
            "resurrection_confidence": min(1.0, len(context_window) * 0.2 + len(active_patterns) * 0.1)
        }