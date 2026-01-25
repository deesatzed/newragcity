"""
Project Discovery System for Temporal Pattern Recognition
Auto-discovers developer's projects and maps evolution chains
"""

import os
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from uuid import uuid4

@dataclass
class ProjectInfo:
    """Information about a discovered project"""
    project_id: str
    name: str
    path: Path
    creation_date: datetime
    last_modified: datetime
    is_git_repo: bool
    primary_language: str
    file_count: int
    line_count: int
    technologies: List[str]
    project_type: str
    confidence_score: float

@dataclass
class EvolutionChain:
    """Represents an evolution chain between projects"""
    chain_id: str
    projects: List[ProjectInfo]
    evolution_timeline: List[Dict[str, Any]]
    confidence_score: float
    pattern_strength: float

class ProjectDiscovery:
    """
    Auto-discovers developer's projects and maps temporal evolution patterns
    
    Core breakthrough: Understanding how developers evolve their problem-solving
    approach across multiple projects over time
    """
    
    def __init__(self, workspace_paths: Optional[List[str]] = None):
        self.workspace_paths = workspace_paths or self._discover_workspace_paths()
        self.projects: Dict[str, ProjectInfo] = {}
        self.evolution_chains: List[EvolutionChain] = {}
        self.discovery_cache = Path.home() / ".cognitron" / "temporal" / "project_discovery.json"
        self.discovery_cache.parent.mkdir(parents=True, exist_ok=True)
        
    def _discover_workspace_paths(self) -> List[str]:
        """Discover common workspace paths"""
        potential_paths = [
            str(Path.home() / "Projects"),
            str(Path.home() / "Development"), 
            str(Path.home() / "Code"),
            str(Path.home() / "workspace"),
            str(Path.home() / "dev"),
            "/Volumes/WS4TB/ERSATZ_RAG",  # Current known workspace
            str(Path.cwd().parent),  # Parent of current directory
        ]
        
        existing_paths = []
        for path in potential_paths:
            if Path(path).exists() and Path(path).is_dir():
                existing_paths.append(path)
                
        return existing_paths
    
    async def discover_projects(self, force_refresh: bool = False) -> Dict[str, ProjectInfo]:
        """
        Discover all projects in workspace paths
        
        Args:
            force_refresh: Force rediscovery instead of using cache
            
        Returns:
            Dictionary of project_id -> ProjectInfo
        """
        
        if not force_refresh and self.discovery_cache.exists():
            try:
                with open(self.discovery_cache, 'r') as f:
                    cached_data = json.load(f)
                    
                # Convert cached data back to ProjectInfo objects
                for project_id, project_data in cached_data.get('projects', {}).items():
                    project_data['path'] = Path(project_data['path'])
                    project_data['creation_date'] = datetime.fromisoformat(project_data['creation_date'])
                    project_data['last_modified'] = datetime.fromisoformat(project_data['last_modified'])
                    self.projects[project_id] = ProjectInfo(**project_data)
                    
                print(f"📁 Loaded {len(self.projects)} projects from cache")
                return self.projects
            except Exception as e:
                print(f"⚠️  Cache read failed, performing fresh discovery: {e}")
        
        print("🔍 Discovering projects across workspace paths...")
        discovered_count = 0
        
        for workspace_path in self.workspace_paths:
            print(f"   Scanning: {workspace_path}")
            workspace = Path(workspace_path)
            
            if not workspace.exists():
                continue
                
            # Find potential project directories
            for item in workspace.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    try:
                        project_info = await self._analyze_project(item)
                        if project_info:
                            self.projects[project_info.project_id] = project_info
                            discovered_count += 1
                            print(f"     ✅ {project_info.name} ({project_info.project_type})")
                    except Exception as e:
                        print(f"     ❌ Failed to analyze {item.name}: {e}")
        
        # Cache the results
        await self._cache_discovery_results()
        
        print(f"🎯 Discovered {discovered_count} projects total")
        return self.projects
    
    async def _analyze_project(self, project_path: Path) -> Optional[ProjectInfo]:
        """Analyze a potential project directory"""
        
        # Skip if it's clearly not a project
        if self._should_skip_directory(project_path):
            return None
            
        try:
            # Basic file analysis
            file_count, line_count, primary_language = await self._analyze_project_files(project_path)
            
            # Skip if too small to be a meaningful project
            if file_count < 3 and line_count < 50:
                return None
            
            # Get project metadata
            creation_date = datetime.fromtimestamp(project_path.stat().st_ctime)
            last_modified = datetime.fromtimestamp(project_path.stat().st_mtime)
            
            # Check if git repository
            is_git_repo = (project_path / ".git").exists()
            
            # Detect technologies and project type
            technologies = self._detect_technologies(project_path)
            project_type = self._classify_project_type(project_path, technologies, primary_language)
            
            # Calculate confidence score based on project characteristics
            confidence_score = self._calculate_project_confidence(
                file_count, line_count, is_git_repo, technologies, project_type
            )
            
            project_info = ProjectInfo(
                project_id=str(uuid4()),
                name=project_path.name,
                path=project_path,
                creation_date=creation_date,
                last_modified=last_modified,
                is_git_repo=is_git_repo,
                primary_language=primary_language,
                file_count=file_count,
                line_count=line_count,
                technologies=technologies,
                project_type=project_type,
                confidence_score=confidence_score
            )
            
            return project_info
            
        except Exception as e:
            print(f"Error analyzing {project_path}: {e}")
            return None
    
    def _should_skip_directory(self, path: Path) -> bool:
        """Check if directory should be skipped"""
        skip_patterns = {
            'node_modules', '__pycache__', '.git', '.venv', 'venv', 
            'env', '.env', 'dist', 'build', '.cache', '.tmp',
            'temp', 'logs', '.logs', 'coverage'
        }
        
        if path.name in skip_patterns:
            return True
            
        # Skip if it looks like a cache or build directory
        if any(pattern in path.name.lower() for pattern in ['cache', 'temp', 'tmp', 'log']):
            return True
            
        return False
    
    async def _analyze_project_files(self, project_path: Path) -> Tuple[int, int, str]:
        """Analyze files in project to get counts and primary language"""
        
        file_count = 0
        line_count = 0
        language_counts = {}
        
        code_extensions = {
            '.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript',
            '.java': 'Java', '.cpp': 'C++', '.c': 'C', '.cs': 'C#',
            '.go': 'Go', '.rs': 'Rust', '.rb': 'Ruby', '.php': 'PHP',
            '.swift': 'Swift', '.kt': 'Kotlin', '.scala': 'Scala',
            '.r': 'R', '.m': 'MATLAB', '.sh': 'Shell', '.sql': 'SQL'
        }
        
        try:
            for file_path in project_path.rglob('*'):
                if file_path.is_file() and not self._should_skip_file(file_path):
                    file_count += 1
                    
                    # Count lines in code files
                    if file_path.suffix.lower() in code_extensions:
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                file_lines = sum(1 for line in f if line.strip())
                                line_count += file_lines
                                
                            # Track language distribution
                            language = code_extensions[file_path.suffix.lower()]
                            language_counts[language] = language_counts.get(language, 0) + file_lines
                        except Exception:
                            continue
                            
        except Exception as e:
            print(f"Error analyzing files in {project_path}: {e}")
        
        # Determine primary language
        primary_language = 'Unknown'
        if language_counts:
            primary_language = max(language_counts, key=language_counts.get)
            
        return file_count, line_count, primary_language
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped during analysis"""
        skip_extensions = {
            '.log', '.tmp', '.cache', '.lock', '.pid', '.swp', '.bak',
            '.pyc', '.pyo', '.o', '.obj', '.exe', '.dll', '.so',
            '.zip', '.tar', '.gz', '.rar', '.7z', 
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.ico',
            '.mp3', '.mp4', '.avi', '.mov', '.wav', '.pdf'
        }
        
        return file_path.suffix.lower() in skip_extensions
    
    def _detect_technologies(self, project_path: Path) -> List[str]:
        """Detect technologies used in the project"""
        technologies = []
        
        # Check for common framework/library indicators
        indicators = {
            'package.json': ['Node.js', 'npm'],
            'requirements.txt': ['Python', 'pip'],
            'pyproject.toml': ['Python', 'Poetry'],
            'Pipfile': ['Python', 'Pipenv'],
            'Cargo.toml': ['Rust', 'Cargo'],
            'pom.xml': ['Java', 'Maven'],
            'build.gradle': ['Java', 'Gradle'],
            'composer.json': ['PHP', 'Composer'],
            'Gemfile': ['Ruby', 'Bundler'],
            'go.mod': ['Go', 'Go Modules'],
            'CMakeLists.txt': ['C++', 'CMake'],
            'Makefile': ['Make'],
            'Dockerfile': ['Docker'],
            'docker-compose.yml': ['Docker Compose'],
            '.github': ['GitHub Actions'],
            'README.md': ['Documentation']
        }
        
        for indicator_file, techs in indicators.items():
            if (project_path / indicator_file).exists():
                technologies.extend(techs)
                
        # Check for specific framework signatures
        if (project_path / 'package.json').exists():
            try:
                with open(project_path / 'package.json', 'r') as f:
                    package_data = json.load(f)
                    deps = {**package_data.get('dependencies', {}), **package_data.get('devDependencies', {})}
                    
                    if 'react' in deps:
                        technologies.append('React')
                    if 'vue' in deps:
                        technologies.append('Vue.js')
                    if 'angular' in deps:
                        technologies.append('Angular')
                    if 'express' in deps:
                        technologies.append('Express.js')
                    if 'next' in deps:
                        technologies.append('Next.js')
            except:
                pass
                
        return list(set(technologies))  # Remove duplicates
    
    def _classify_project_type(self, project_path: Path, technologies: List[str], primary_language: str) -> str:
        """Classify the type of project"""
        
        # Check for specific project patterns
        if 'RAG' in project_path.name.upper() or 'rag' in str(project_path).lower():
            return 'AI/RAG System'
        elif 'regulus' in project_path.name.lower():
            return 'AI/ML Pipeline'  
        elif 'thalamus' in project_path.name.lower():
            return 'Medical AI System'
        elif 'cognitron' in project_path.name.lower():
            return 'Developer Intelligence System'
        elif 'React' in technologies or 'Vue.js' in technologies or 'Angular' in technologies:
            return 'Frontend Web Application'
        elif 'Express.js' in technologies or 'Flask' in technologies or 'Django' in technologies:
            return 'Backend Web Service'
        elif 'Docker' in technologies:
            return 'Containerized Application'
        elif primary_language == 'Python' and any('ml' in tech.lower() or 'ai' in tech.lower() for tech in technologies):
            return 'Machine Learning Project'
        elif primary_language == 'Python':
            return 'Python Application'
        elif primary_language == 'JavaScript' or primary_language == 'TypeScript':
            return 'JavaScript/TypeScript Application'
        elif primary_language in ['Java', 'C++', 'C#', 'Go', 'Rust']:
            return f'{primary_language} Application'
        else:
            return 'General Software Project'
    
    def _calculate_project_confidence(
        self, 
        file_count: int, 
        line_count: int, 
        is_git_repo: bool, 
        technologies: List[str], 
        project_type: str
    ) -> float:
        """Calculate confidence score for project classification"""
        
        confidence = 0.0
        
        # Base confidence from project size
        if line_count > 1000:
            confidence += 0.4
        elif line_count > 500:
            confidence += 0.3
        elif line_count > 100:
            confidence += 0.2
        else:
            confidence += 0.1
            
        # Git repository adds confidence
        if is_git_repo:
            confidence += 0.2
            
        # Technology detection adds confidence
        if len(technologies) >= 3:
            confidence += 0.3
        elif len(technologies) >= 2:
            confidence += 0.2
        elif len(technologies) >= 1:
            confidence += 0.1
            
        # Project type specificity adds confidence
        if project_type != 'General Software Project':
            confidence += 0.1
            
        return min(1.0, confidence)
    
    async def map_evolution_chains(self) -> List[EvolutionChain]:
        """
        Map evolution chains between projects based on temporal patterns
        
        This is the breakthrough feature - understanding how developers evolve
        their problem-solving approach across multiple projects
        """
        
        if not self.projects:
            await self.discover_projects()
            
        print("🔗 Mapping project evolution chains...")
        
        # Sort projects by creation date
        sorted_projects = sorted(self.projects.values(), key=lambda p: p.creation_date)
        
        # Look for evolution patterns
        evolution_chains = []
        
        # Check for known evolution chain: Regulus → Thalamus → Cognitron
        known_chain = self._find_known_evolution_chain(sorted_projects)
        if known_chain:
            evolution_chains.append(known_chain)
            
        # Detect other potential evolution chains
        other_chains = self._detect_evolution_patterns(sorted_projects)
        evolution_chains.extend(other_chains)
        
        self.evolution_chains = evolution_chains
        
        print(f"🎯 Discovered {len(evolution_chains)} evolution chains")
        for chain in evolution_chains:
            project_names = " → ".join([p.name for p in chain.projects])
            print(f"     📈 {project_names} (confidence: {chain.confidence_score:.2f})")
            
        return evolution_chains
    
    def _find_known_evolution_chain(self, sorted_projects: List[ProjectInfo]) -> Optional[EvolutionChain]:
        """Find the known Regulus → Thalamus → Cognitron evolution chain"""
        
        regulus = None
        thalamus = None
        cognitron = None
        
        for project in sorted_projects:
            name_lower = project.name.lower()
            if 'regulus' in name_lower and not regulus:
                regulus = project
            elif 'thalamus' in name_lower and not thalamus:
                thalamus = project
            elif 'cognitron' in name_lower and not cognitron:
                cognitron = project
                
        # Check if we have all three projects in chronological order
        if regulus and thalamus and cognitron:
            # Verify chronological order
            if regulus.creation_date <= thalamus.creation_date <= cognitron.creation_date:
                
                # Create evolution timeline
                timeline = [
                    {
                        "phase": "regulus",
                        "date": regulus.creation_date.isoformat(),
                        "focus": "Initial AI/ML pipeline development",
                        "accuracy": "71% baseline performance",
                        "learning": "Foundation building and data pipeline establishment"
                    },
                    {
                        "phase": "thalamus", 
                        "date": thalamus.creation_date.isoformat(),
                        "focus": "Medical-grade AI system with enhanced pipeline",
                        "accuracy": "80.8% with medical pipeline optimizations",
                        "learning": "Specialized domain focus and confidence calibration"
                    },
                    {
                        "phase": "cognitron",
                        "date": cognitron.creation_date.isoformat(), 
                        "focus": "Developer intelligence and workspace unification",
                        "accuracy": "Enterprise-grade confidence tracking",
                        "learning": "Cross-domain intelligence and temporal pattern recognition"
                    }
                ]
                
                return EvolutionChain(
                    chain_id=str(uuid4()),
                    projects=[regulus, thalamus, cognitron],
                    evolution_timeline=timeline,
                    confidence_score=0.95,  # High confidence for known chain
                    pattern_strength=0.90
                )
                
        return None
    
    def _detect_evolution_patterns(self, sorted_projects: List[ProjectInfo]) -> List[EvolutionChain]:
        """Detect other potential evolution patterns between projects"""
        
        evolution_chains = []
        
        # Group projects by technology/type similarity
        similar_groups = {}
        
        for project in sorted_projects:
            # Create a key based on primary language and technologies
            key = f"{project.primary_language}_{project.project_type}"
            if key not in similar_groups:
                similar_groups[key] = []
            similar_groups[key].append(project)
            
        # Look for chains within similar technology groups
        for group_key, group_projects in similar_groups.items():
            if len(group_projects) >= 2:
                # Sort by creation date
                group_projects.sort(key=lambda p: p.creation_date)
                
                # Check for evolutionary patterns (increasing complexity/size)
                potential_chain = []
                for i, project in enumerate(group_projects):
                    if i == 0:
                        potential_chain.append(project)
                    else:
                        prev_project = group_projects[i-1] 
                        
                        # Check if this could be an evolution (more complex/larger)
                        if (project.line_count > prev_project.line_count * 0.8 or
                            len(project.technologies) >= len(prev_project.technologies)):
                            potential_chain.append(project)
                        else:
                            # Break in evolution pattern
                            if len(potential_chain) >= 2:
                                chain = self._create_evolution_chain(potential_chain, group_key)
                                if chain:
                                    evolution_chains.append(chain)
                            potential_chain = [project]
                            
                # Check final chain
                if len(potential_chain) >= 2:
                    chain = self._create_evolution_chain(potential_chain, group_key)
                    if chain:
                        evolution_chains.append(chain)
                        
        return evolution_chains
    
    def _create_evolution_chain(self, projects: List[ProjectInfo], group_key: str) -> Optional[EvolutionChain]:
        """Create an evolution chain from a group of projects"""
        
        if len(projects) < 2:
            return None
            
        # Calculate confidence based on evolution indicators
        confidence_score = 0.0
        
        # Check for increasing complexity
        line_counts = [p.line_count for p in projects]
        if all(line_counts[i] <= line_counts[i+1] for i in range(len(line_counts)-1)):
            confidence_score += 0.3
            
        # Check for technology evolution
        tech_evolution = any(len(projects[i].technologies) <= len(projects[i+1].technologies) 
                           for i in range(len(projects)-1))
        if tech_evolution:
            confidence_score += 0.2
            
        # Check temporal spacing (not too close, not too far)
        time_diffs = [(projects[i+1].creation_date - projects[i].creation_date).days 
                      for i in range(len(projects)-1)]
        reasonable_spacing = all(7 <= diff <= 365 for diff in time_diffs)  # 1 week to 1 year
        if reasonable_spacing:
            confidence_score += 0.3
            
        # Minimum confidence threshold
        if confidence_score < 0.4:
            return None
            
        # Create timeline
        timeline = []
        for i, project in enumerate(projects):
            timeline.append({
                "phase": f"phase_{i+1}",
                "project": project.name,
                "date": project.creation_date.isoformat(),
                "focus": f"{project.project_type} development",
                "complexity": f"{project.line_count} lines, {len(project.technologies)} technologies",
                "learning": "Iterative improvement and capability expansion"
            })
            
        return EvolutionChain(
            chain_id=str(uuid4()),
            projects=projects,
            evolution_timeline=timeline,
            confidence_score=confidence_score,
            pattern_strength=confidence_score * 0.8  # Slightly lower than confidence
        )
    
    async def _cache_discovery_results(self):
        """Cache discovery results to disk"""
        try:
            # Convert ProjectInfo objects to serializable format
            cache_data = {
                "projects": {},
                "last_discovery": datetime.now().isoformat()
            }
            
            for project_id, project_info in self.projects.items():
                project_dict = asdict(project_info)
                project_dict['path'] = str(project_dict['path'])
                project_dict['creation_date'] = project_dict['creation_date'].isoformat()
                project_dict['last_modified'] = project_dict['last_modified'].isoformat()
                cache_data["projects"][project_id] = project_dict
                
            with open(self.discovery_cache, 'w') as f:
                json.dump(cache_data, f, indent=2)
                
        except Exception as e:
            print(f"Failed to cache discovery results: {e}")
    
    async def get_project_timeline(self) -> List[Dict[str, Any]]:
        """Get complete timeline of all discovered projects"""
        
        if not self.projects:
            await self.discover_projects()
            
        timeline = []
        for project in sorted(self.projects.values(), key=lambda p: p.creation_date):
            timeline.append({
                "date": project.creation_date.isoformat(),
                "project": project.name,
                "type": project.project_type,
                "language": project.primary_language,
                "size": f"{project.line_count} lines",
                "technologies": project.technologies,
                "path": str(project.path),
                "confidence": project.confidence_score
            })
            
        return timeline
    
    async def analyze_developer_evolution(self) -> Dict[str, Any]:
        """
        Analyze how the developer's approach has evolved over time
        
        This is core to the breakthrough - understanding personal development patterns
        """
        
        if not self.evolution_chains:
            await self.map_evolution_chains()
            
        analysis = {
            "total_projects": len(self.projects),
            "evolution_chains": len(self.evolution_chains),
            "primary_languages": {},
            "technology_adoption": {},
            "complexity_growth": [],
            "temporal_patterns": {}
        }
        
        # Analyze language distribution over time
        sorted_projects = sorted(self.projects.values(), key=lambda p: p.creation_date)
        for project in sorted_projects:
            lang = project.primary_language
            if lang not in analysis["primary_languages"]:
                analysis["primary_languages"][lang] = []
            analysis["primary_languages"][lang].append(project.creation_date.year)
            
        # Analyze technology adoption patterns
        for project in sorted_projects:
            year = project.creation_date.year
            for tech in project.technologies:
                if tech not in analysis["technology_adoption"]:
                    analysis["technology_adoption"][tech] = []
                analysis["technology_adoption"][tech].append(year)
                
        # Analyze complexity growth
        for project in sorted_projects:
            analysis["complexity_growth"].append({
                "date": project.creation_date.isoformat(),
                "project": project.name,
                "line_count": project.line_count,
                "file_count": project.file_count,
                "tech_count": len(project.technologies)
            })
            
        return analysis