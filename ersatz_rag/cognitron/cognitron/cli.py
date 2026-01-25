"""
Cognitron CLI: Developer-grade personal knowledge assistant
Command-line interface with confidence visualization and quality validation
"""

import asyncio
import sys
from pathlib import Path
from typing import List, Optional
import json

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.tree import Tree
from rich import print as rprint

from .core.agent import CognitronAgent
from .models import ConfidenceLevel

# Initialize Rich console for enterprise-grade output formatting
console = Console()
app = typer.Typer(
    name="cognitron",
    help="🧠 Cognitron: Developer-grade personal knowledge assistant with confidence tracking",
    rich_markup_mode="rich"
)

# Global configuration
DEFAULT_INDEX_PATH = Path.home() / ".cognitron" / "index"
DEFAULT_MEMORY_PATH = Path.home() / ".cognitron" / "memory.db"


def get_agent() -> CognitronAgent:
    """Initialize Cognitron agent with enterprise-grade configuration"""
    return CognitronAgent(
        index_path=DEFAULT_INDEX_PATH,
        memory_path=DEFAULT_MEMORY_PATH,
        confidence_threshold=0.85,  # Production threshold
        developer_threshold=0.95      # Developer-grade threshold
    )


@app.command()
def index(
    paths: List[str] = typer.Argument(..., help="Paths to index (files or directories)"),
    force_rebuild: bool = typer.Option(False, "--force", "-f", help="Force complete index rebuild"),
    confidence_threshold: float = typer.Option(0.85, "--confidence", "-c", help="Minimum confidence threshold"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed progress")
):
    """
    🚀 Index content with enterprise-grade quality assurance
    
    Combines PageIndex + LEANN + DeepConf architecture for multi-domain intelligence:
    - Code files: AST-aware semantic chunking
    - Documents: Structure-preserving intelligent segmentation  
    - Quality validation: Developer-grade confidence tracking
    """
    
    console.print("\n🧠 [bold blue]Cognitron Enterprise-Grade Indexing[/bold blue]")
    console.print("   Applying developer AI quality standards to personal knowledge")
    
    # Convert string paths to Path objects
    path_objects = [Path(p) for p in paths]
    
    # Validate paths
    invalid_paths = [p for p in path_objects if not p.exists()]
    if invalid_paths:
        console.print(f"❌ [red]Invalid paths found:[/red]")
        for path in invalid_paths:
            console.print(f"   • {path}")
        raise typer.Exit(1)
        
    # Initialize agent
    agent = get_agent()
    
    # Run indexing with progress tracking
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        task = progress.add_task("Indexing content with enterprise-grade validation...", total=None)
        
        # Run async indexing
        results = asyncio.run(agent.index_content(
            paths=path_objects,
            force_rebuild=force_rebuild
        ))
        
        progress.update(task, completed=True)
        
    # Display results with enterprise-grade metrics
    _display_indexing_results(results, verbose)
    
    console.print("\n✅ [bold green]Developer-grade indexing completed![/bold green]")
    console.print("   Ready for confident knowledge queries")


@app.command()
def ask(
    query: str = typer.Argument(..., help="Your knowledge question"),
    require_high_confidence: bool = typer.Option(True, "--high-confidence", help="Require high confidence for answers"),
    show_sources: bool = typer.Option(False, "--sources", "-s", help="Show source information"),
    confidence_threshold: float = typer.Option(0.85, "--threshold", "-t", help="Minimum confidence threshold"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed confidence analysis")
):
    """
    🤔 Ask questions with enterprise-grade confidence validation
    
    Features developer AI quality assurance:
    - Multi-domain intelligence (code + documents)
    - Confidence calibration with uncertainty quantification  
    - Case memory learning from high-confidence successes
    - Self-validation with quality thresholds
    """
    
    console.print(f"\n🧠 [bold blue]Processing query with enterprise-grade validation...[/bold blue]")
    console.print(f"   Query: [italic]{query}[/italic]")
    
    # Initialize agent
    agent = get_agent()
    
    # Process query with progress tracking
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        task = progress.add_task("Analyzing query with confidence tracking...", total=None)
        
        # Run async query processing
        result = asyncio.run(agent.ask(
            query=query,
            require_high_confidence=require_high_confidence
        ))
        
        progress.update(task, completed=True)
        
    # Display results with confidence visualization
    _display_query_result(result, show_sources, verbose)


@app.command()
def topics(
    show_confidence: bool = typer.Option(True, "--confidence", help="Show confidence metrics"),
    min_confidence: float = typer.Option(0.70, "--min-confidence", help="Minimum confidence to display"),
    sort_by: str = typer.Option("confidence", "--sort", help="Sort by: confidence, name, size")
):
    """
    🏷️  Show AI-generated topic clusters with confidence metrics
    
    Displays enterprise-grade topic analysis:
    - AI-powered content clustering
    - Confidence-validated topic coherence
    - Quality-assured knowledge organization
    """
    
    console.print("\n🏷️  [bold blue]AI-Generated Knowledge Topics[/bold blue]")
    
    # Initialize agent
    agent = get_agent()
    
    # Get topics with confidence tracking
    with console.status("Loading topics with confidence analysis..."):
        topics_data = asyncio.run(agent.get_topics())
        
    if not topics_data:
        console.print("📭 [yellow]No topics found. Run 'cognitron index' first to generate topics.[/yellow]")
        return
        
    # Filter by confidence
    filtered_topics = [
        topic for topic in topics_data 
        if topic.get("confidence", 0.0) >= min_confidence
    ]
    
    # Sort topics
    if sort_by == "confidence":
        filtered_topics.sort(key=lambda x: x.get("confidence", 0.0), reverse=True)
    elif sort_by == "name":
        filtered_topics.sort(key=lambda x: x.get("name", ""))
    elif sort_by == "size":
        filtered_topics.sort(key=lambda x: len(x.get("chunk_ids", [])), reverse=True)
        
    # Display topics table
    _display_topics_table(filtered_topics, show_confidence)


@app.command()
def status(
    show_memory: bool = typer.Option(True, "--memory", help="Show case memory statistics"),
    show_index: bool = typer.Option(True, "--index", help="Show index statistics"),
    show_health: bool = typer.Option(True, "--health", help="Show system health metrics")
):
    """
    📊 Show comprehensive system status with enterprise-grade metrics
    
    Displays:
    - Developer-grade confidence compliance rates
    - Case memory learning statistics  
    - Index quality and coverage metrics
    - System health and performance indicators
    """
    
    console.print("\n📊 [bold blue]Cognitron System Status[/bold blue]")
    console.print("   Developer-grade personal knowledge assistant")
    
    # Initialize agent  
    agent = get_agent()
    
    # Get system status
    with console.status("Gathering system metrics..."):
        status_data = asyncio.run(agent.get_status())
        
    # Display status sections
    if show_health:
        _display_health_metrics(status_data.get("health_metrics", {}))
        
    if show_memory:
        _display_memory_status(status_data.get("memory_system", {}))
        
    if show_index:
        _display_index_status(status_data.get("index_system", {}))
        
    # Display thresholds
    thresholds = status_data.get("developer_grade_thresholds", {})
    console.print(f"\n🎯 [bold]Enterprise-Grade Thresholds:[/bold]")
    console.print(f"   Critical Threshold: {thresholds.get('critical_threshold', 0.95):.1%}")
    console.print(f"   Production Threshold: {thresholds.get('production_threshold', 0.85):.1%}")


def _display_indexing_results(results: dict, verbose: bool = False):
    """Display indexing results with enterprise-grade metrics"""
    
    # Create results table
    table = Table(title="Indexing Results", show_header=True, header_style="bold blue")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    table.add_column("Quality Assessment", style="yellow")
    
    # Basic metrics
    table.add_row("Total Files", str(results.get("total_files", 0)), "✅")
    table.add_row("Indexed Documents", str(results.get("indexed_documents", 0)), "✅")
    table.add_row("Chunks Created", str(results.get("chunks_created", 0)), "📝")
    table.add_row("High-Confidence Chunks", str(results.get("high_confidence_chunks", 0)), "🎯")
    
    # Quality assessment
    total_chunks = results.get("chunks_created", 1)
    high_conf_chunks = results.get("high_confidence_chunks", 0)
    quality_rate = (high_conf_chunks / total_chunks) * 100 if total_chunks > 0 else 0
    
    if quality_rate >= 80:
        quality_status = "🏥 Developer Grade"
    elif quality_rate >= 70:
        quality_status = "✅ Production Ready"
    else:
        quality_status = "⚠️  Needs Improvement"
        
    table.add_row("Quality Rate", f"{quality_rate:.1f}%", quality_status)
    
    if results.get("processing_errors", 0) > 0:
        table.add_row("Processing Errors", str(results.get("processing_errors", 0)), "❌")
        
    console.print("\n")
    console.print(table)
    
    # Confidence distribution
    if verbose and "confidence_distribution" in results:
        _display_confidence_distribution(results["confidence_distribution"])


def _display_query_result(result, show_sources: bool = False, verbose: bool = False):
    """Display query result with enterprise-grade confidence visualization"""
    
    # Confidence level styling
    confidence_styles = {
        ConfidenceLevel.CRITICAL: ("🏥", "bold green"),
        ConfidenceLevel.HIGH: ("✅", "green"), 
        ConfidenceLevel.MEDIUM: ("⚠️ ", "yellow"),
        ConfidenceLevel.LOW: ("❌", "red"),
        ConfidenceLevel.INSUFFICIENT: ("🚫", "bold red")
    }
    
    icon, style = confidence_styles.get(result.confidence_level, ("❓", "white"))
    
    # Main answer panel
    confidence_text = f"{icon} {result.confidence_level.value.title()} Confidence ({result.overall_confidence:.1%})"
    
    if not result.should_display:
        console.print("\n🚫 [bold red]Response Suppressed[/bold red]")
        console.print("   Confidence below enterprise-grade threshold")
        console.print("   Consider refining your query or consulting additional sources")
        return
        
    answer_panel = Panel(
        result.answer,
        title=f"🧠 Enterprise-Grade Response - {confidence_text}",
        title_align="left",
        border_style=style
    )
    
    console.print("\n")
    console.print(answer_panel)
    
    # Confidence explanation
    if result.confidence_explanation:
        console.print(f"\n💡 [bold]Confidence Analysis:[/bold]")
        console.print(f"   {result.confidence_explanation}")
        
    # Uncertainty factors
    if result.uncertainty_factors:
        console.print(f"\n⚠️  [yellow]Uncertainty Factors:[/yellow]")
        for factor in result.uncertainty_factors:
            console.print(f"   • {factor}")
            
    # Validation requirements
    if result.requires_validation:
        console.print(f"\n🔍 [yellow]Recommendation: Human validation recommended for critical decisions[/yellow]")
        
    # Processing metrics
    if verbose:
        console.print(f"\n📊 [bold]Processing Metrics:[/bold]")
        console.print(f"   Processing Time: {result.processing_time:.2f}s")
        console.print(f"   Retrieval Confidence: {result.retrieval_confidence:.1%}")
        console.print(f"   Reasoning Confidence: {result.reasoning_confidence:.1%}")
        console.print(f"   Factual Confidence: {result.factual_confidence:.1%}")
        
    # Source information
    if show_sources and result.relevant_chunks:
        console.print(f"\n📚 [bold]Supporting Sources ({len(result.relevant_chunks)}):[/bold]")
        for i, chunk in enumerate(result.relevant_chunks[:3]):  # Show top 3 sources
            console.print(f"   {i+1}. {chunk.title} ({chunk.confidence_level.value} confidence)")


def _display_topics_table(topics: List[dict], show_confidence: bool = True):
    """Display topics in a formatted table"""
    
    if not topics:
        console.print("📭 [yellow]No topics meet the confidence threshold[/yellow]")
        return
        
    table = Table(title=f"Knowledge Topics ({len(topics)} found)", show_header=True, header_style="bold blue")
    table.add_column("Topic", style="cyan", min_width=20)
    table.add_column("Description", style="white", min_width=30)
    table.add_column("Chunks", justify="center", style="green")
    
    if show_confidence:
        table.add_column("Confidence", justify="center", style="yellow")
        table.add_column("Level", justify="center")
        
    for topic in topics:
        confidence = topic.get("confidence", 0.0)
        chunk_count = len(topic.get("chunk_ids", []))
        
        # Confidence level styling
        if confidence >= 0.95:
            conf_level = "🏥 Critical"
        elif confidence >= 0.85:
            conf_level = "✅ High"
        elif confidence >= 0.70:
            conf_level = "⚠️  Medium"
        else:
            conf_level = "❌ Low"
            
        row_data = [
            topic.get("name", "Unknown"),
            topic.get("description", "No description")[:50] + "...",
            str(chunk_count)
        ]
        
        if show_confidence:
            row_data.extend([f"{confidence:.1%}", conf_level])
            
        table.add_row(*row_data)
        
    console.print("\n")
    console.print(table)


def _display_health_metrics(health_metrics: dict):
    """Display system health metrics"""
    
    console.print(f"\n🏥 [bold green]Enterprise-Grade Compliance:[/bold green]")
    
    compliance = health_metrics.get("developer_threshold_compliance", {})
    critical_cases = compliance.get("cases_meeting_critical", 0)
    total_cases = compliance.get("total_cases", 0)
    critical_percentage = compliance.get("critical_percentage", 0.0)
    
    if critical_percentage >= 50:
        status_icon = "🏥"
        status_color = "green"
    elif critical_percentage >= 30:
        status_icon = "✅"
        status_color = "yellow"  
    else:
        status_icon = "⚠️ "
        status_color = "red"
        
    console.print(f"   {status_icon} Critical-grade cases: {critical_cases}/{total_cases} ({critical_percentage:.1f}%)", style=status_color)
    console.print(f"   📊 Average confidence: {health_metrics.get('average_confidence', 0.0):.1%}")
    
    # Recent activity
    activity = health_metrics.get("recent_activity", {})
    console.print(f"\n📈 [bold]Recent Activity:[/bold]")
    console.print(f"   Cases added (7 days): {activity.get('cases_added_last_week', 0)}")
    console.print(f"   Knowledge retrievals: {activity.get('retrievals_last_week', 0)}")


def _display_memory_status(memory_data: dict):
    """Display case memory statistics"""
    
    console.print(f"\n🧠 [bold blue]Case Memory System:[/bold blue]")
    console.print(f"   Total cases stored: {memory_data.get('total_cases', 0)}")
    console.print(f"   Critical-grade cases: {memory_data.get('critical_cases', 0)}")
    console.print(f"   Production-ready cases: {memory_data.get('production_ready_cases', 0)}")
    console.print(f"   Average success rate: {memory_data.get('average_success_rate', 0.0):.1%}")


def _display_index_status(index_data: dict):
    """Display index statistics"""
    
    console.print(f"\n📚 [bold blue]Knowledge Index:[/bold blue]")
    console.print(f"   Total chunks indexed: {index_data.get('total_chunks', 0)}")
    console.print(f"   LEANN available: {'✅' if index_data.get('leann_available') else '❌'}")
    
    # Chunk types
    chunk_types = index_data.get('chunk_types', {})
    if chunk_types:
        console.print(f"   Content types:")
        for chunk_type, count in chunk_types.items():
            console.print(f"     • {chunk_type}: {count}")


def _display_confidence_distribution(distribution: dict):
    """Display confidence distribution chart"""
    
    console.print(f"\n📊 [bold]Confidence Distribution:[/bold]")
    
    for level, count in distribution.items():
        if level == "critical":
            icon, style = "🏥", "bold green"
        elif level == "high":
            icon, style = "✅", "green"
        elif level == "medium":
            icon, style = "⚠️ ", "yellow"
        elif level == "low":
            icon, style = "❌", "red"
        else:
            icon, style = "❓", "white"
            
        bar = "█" * min(count, 20)  # Simple bar chart
        console.print(f"   {icon} {level.title():12} │{bar:20} {count}", style=style)


def main():
    """Main CLI entry point"""
    
    # Ensure config directories exist
    DEFAULT_INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # Display banner
    console.print("\n🧠 [bold blue]Cognitron[/bold blue] - Developer-grade personal knowledge assistant")
    console.print("   Breakthrough AI with production-level confidence tracking")
    
    # Run CLI app
    app()


if __name__ == "__main__":
    main()