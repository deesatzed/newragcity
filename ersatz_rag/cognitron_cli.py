#!/opt/homebrew/anaconda3/envs/helix13/bin/python
"""
Cognitron CLI - Personal Knowledge Assistant
Integrates with ERSATZ RAG microservices for enhanced knowledge management
"""

import json
import sys
from pathlib import Path
from typing import List, Optional
import requests
from datetime import datetime, timezone
import mimetypes
import os
import uuid

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint

# Initialize Rich console
console = Console()
app = typer.Typer(
    name="cognitron",
    help="🧠 Cognitron: Personal Knowledge Assistant with ERSATZ RAG Integration",
    rich_markup_mode="rich"
)

# Service endpoints
SERVICES = {
    'pageindex': 'http://localhost:8000',
    'leann': 'http://localhost:8001',
    'deepconf': 'http://localhost:8002',
    'thalamus': 'http://localhost:8003',
    'qdrant': 'http://localhost:6333',
    'memproxy': 'http://localhost:8010',
}

def check_service_health(service_name: str) -> dict:
    """Check health of a specific service"""
    try:
        if service_name == 'qdrant':
            # Qdrant exposes readiness on /readyz
            url = f"{SERVICES[service_name]}/readyz"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return {"status": "healthy", "details": {"status": response.text.strip()}}
            else:
                return {"status": "unhealthy", "details": {"status_code": response.status_code}}
        else:
            url = f"{SERVICES[service_name]}/health"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                # Some services return JSON, others might not
                try:
                    return {"status": "healthy", "details": response.json()}
                except Exception:
                    return {"status": "healthy", "details": {"status": response.text.strip()}}
            else:
                return {"status": "unhealthy", "details": {"status_code": response.status_code}}
    except Exception as e:
        return {"status": "offline", "details": {"error": str(e)}}

def check_all_services() -> dict:
    """Check health of all services"""
    results = {}
    for service_name in SERVICES.keys():
        results[service_name] = check_service_health(service_name)
    return results

@app.command()
def status():
    """
    📊 Check system status and service health

    Displays the current operational status of all ERSATZ RAG services
    and provides system metrics.
    """

    console.print("\n🧠 [bold blue]Cognitron System Status[/bold blue]")
    console.print("   Integrated with ERSATZ RAG microservices")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:

        task = progress.add_task("Checking service health...", total=None)

        # Check all services
        health_results = check_all_services()

        progress.update(task, completed=True)

    # Display results
    table = Table(title="Service Health Status")
    table.add_column("Service", style="cyan", no_wrap=True)
    table.add_column("Status", style="magenta")
    table.add_column("Details", style="green")

    healthy_count = 0
    for service_name, health in health_results.items():
        status = health['status']
        if status == 'healthy':
            healthy_count += 1
            status_display = "[green]✅ Healthy[/green]"
        elif status == 'unhealthy':
            status_display = "[yellow]⚠️ Unhealthy[/yellow]"
        else:
            status_display = "[red]❌ Offline[/red]"

        details = ""
        if 'details' in health:
            if isinstance(health['details'], dict):
                if 'status' in health['details']:
                    details = f"Status: {health['details']['status']}"
                elif 'status_code' in health['details']:
                    details = f"HTTP {health['details']['status_code']}"
                elif 'error' in health['details']:
                    details = f"Error: {health['details']['error']}"

        table.add_row(service_name.title(), status_display, details)

    console.print(table)
    console.print(f"\n📈 [bold]System Overview:[/bold]")
    console.print(f"   Services Online: {healthy_count}/{len(SERVICES)}")
    console.print(f"   System Health: {'Good' if healthy_count >= 4 else 'Needs Attention'}")

@app.command()
def ask(
    query: str = typer.Argument(..., help="Your question or knowledge request"),
    confidence_threshold: float = typer.Option(0.7, "--confidence", "-c", help="Minimum confidence threshold"),
    detailed: bool = typer.Option(False, "--detailed", "-d", help="Show detailed reasoning"),
    mem_agent: bool = typer.Option(False, "--mem-agent", help="Enable Mem-Agent clarify/note integration via mem-proxy"),
    mem_mode: str = typer.Option("clarify", "--mem-mode", help="Mem-Agent mode: clarify|note|both"),
    mem_proxy_url: str = typer.Option("", "--mem-proxy-url", help="Mem-Proxy base URL (default: env MEM_PROXY_URL or http://localhost:8010)"),
    mem_timeout_ms: int = typer.Option(3000, "--mem-timeout-ms", help="Timeout for mem-proxy calls in milliseconds")
):
    """
    ❓ Ask questions using integrated knowledge base

    Queries the ERSATZ RAG system for answers with confidence tracking.
    Uses Thalamus for orchestration of PageIndex, LEANN, and deepConf services.
    """

    console.print(f"\n🧠 [bold blue]Cognitron Query[/bold blue]")
    console.print(f"   Question: {query}")
    console.print(f"   Confidence threshold: {confidence_threshold}")

    # Resolve mem-proxy configuration (feature-flagged and non-destructive by default)
    env_enabled = os.getenv("MEM_AGENT_ENABLED", "0").lower() in {"1", "true", "yes"}
    mem_enabled = mem_agent or env_enabled
    env_mode = os.getenv("MEM_AGENT_MODE")
    effective_mode = (env_mode or mem_mode or "clarify").lower()
    proxy_url = (mem_proxy_url or os.getenv("MEM_PROXY_URL") or SERVICES.get("memproxy", "http://localhost:8010")).rstrip("/")
    try:
        mem_timeout = int(os.getenv("MEM_AGENT_TIMEOUT_MS", str(mem_timeout_ms)))
    except Exception:
        mem_timeout = mem_timeout_ms

    # Optional clarify pre-step
    effective_query = query
    session_id = uuid.uuid4().hex
    if mem_enabled and effective_mode in ("clarify", "both"):
        try:
            clarify_payload = {"query": query, "context": {"session_id": session_id}}
            resp = requests.post(f"{proxy_url}/clarify", json=clarify_payload, timeout=mem_timeout / 1000.0)
            if resp.status_code == 200:
                cj = resp.json()
                cquery = cj.get("clarified_query")
                if isinstance(cquery, str) and cquery.strip():
                    effective_query = cquery.strip()
                console.print(f"   Using clarified query: {effective_query}")
            else:
                console.print(f"   ℹ️ mem-proxy clarify unavailable (HTTP {resp.status_code}); continuing with original query")
        except Exception as ce:
            console.print(f"   ℹ️ mem-proxy clarify error: {ce}; continuing with original query")

    # Check service health first
    thalamus_health = check_service_health('thalamus')
    if thalamus_health['status'] != 'healthy':
        console.print("❌ [red]Thalamus service is not available[/red]")
        console.print("   Please ensure ERSATZ RAG services are running")
        return

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:

        task = progress.add_task("Processing query with ERSATZ RAG...", total=None)

        try:
            # Send query to Thalamus
            payload = {
                "question": effective_query,
                "confidence_threshold": confidence_threshold,
                "detailed": detailed
            }

            response = requests.post(
                f"{SERVICES['thalamus']}/process_pipeline",
                json=payload,
                timeout=30
            )

            progress.update(task, completed=True)

            if response.status_code == 200:
                result = response.json()

                # Display results
                console.print("\n📋 [bold green]Answer:[/bold green]")
                console.print(f"   {result.get('answer', 'No answer provided')}")

                if 'confidence' in result:
                    confidence_raw = result.get('confidence')
                    try:
                        confidence = float(confidence_raw)
                        if confidence >= confidence_threshold:
                            console.print(f"\n🎯 [bold green]Confidence: {confidence:.1%} (Above threshold)[/bold green]")
                        else:
                            console.print(f"\n⚠️ [bold yellow]Confidence: {confidence:.1%} (Below threshold)[/bold yellow]")
                    except (TypeError, ValueError):
                        console.print("\nℹ️ Confidence: N/A")

                if detailed and 'citations' in result:
                    console.print(f"\n📚 [bold]Sources:[/bold]")
                    for citation in result['citations']:
                        console.print(f"   • {citation}")

                # Optional note post-step (best-effort; never blocks)
                if mem_enabled and effective_mode in ("note", "both"):
                    try:
                        note_title = f"Answer: {effective_query[:60]}" if effective_query else "Answer"
                        answer_text = result.get('answer', '') or ''
                        citations = result.get('citations', []) or []
                        note_body = (
                            f"## Question\n\n{effective_query}\n\n"
                            f"## Answer\n\n{answer_text}\n\n"
                        )
                        if citations:
                            note_body += "## Citations\n\n" + "\n".join(f"- {c}" for c in citations) + "\n"
                        note_payload = {
                            "title": note_title,
                            "body_md": note_body,
                            "tags": ["cognitron", "qa"],
                            "context": {"session_id": session_id, "ts": datetime.now(timezone.utc).isoformat()}
                        }
                        nresp = requests.post(f"{proxy_url}/note", json=note_payload, timeout=mem_timeout / 1000.0)
                        if nresp.status_code == 200:
                            nres = nresp.json()
                            console.print(f"\n📝 Note saved: {nres.get('path', '<unknown>')}")
                        else:
                            console.print(f"\nℹ️ mem-proxy note failed (HTTP {nresp.status_code})")
                    except Exception as ne:
                        console.print(f"\nℹ️ mem-proxy note error: {ne}")

            else:
                console.print(f"❌ [red]Query failed with status code: {response.status_code}[/red]")
                console.print(f"   Response: {response.text}")

        except Exception as e:
            progress.update(task, completed=True)
            console.print(f"❌ [red]Query failed: {str(e)}[/red]")

@app.command()
def index(
    paths: List[str] = typer.Argument(..., help="Paths to process (files or directories)"),
    recursive: bool = typer.Option(True, "--recursive", "-r", help="Recurse into directories")
):
    """
    📚 Process documents via PageIndex

    Uploads documents to the PageIndex service `/extract_structure` endpoint and displays
    real extracted structure summaries. This does not yet persist content into LEANN.
    """

    console.print(f"\n📚 [bold blue]Document Indexing[/bold blue]")
    console.print(f"   Paths to index: {', '.join(paths)}")
    console.print(f"   Recursive: {recursive}")

    # Check service health
    pageindex_health = check_service_health('pageindex')
    if pageindex_health['status'] != 'healthy':
        console.print("❌ [red]PageIndex service is not available[/red]")
        return

    total_files = 0
    processed_files = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:

        for path_str in paths:
            path = Path(path_str)

            if path.is_file():
                files_to_process = [path]
            elif path.is_dir():
                if recursive:
                    files_to_process = list(path.rglob("*"))
                else:
                    files_to_process = list(path.glob("*"))
                files_to_process = [f for f in files_to_process if f.is_file()]
            else:
                console.print(f"❌ [red]Path not found: {path_str}[/red]")
                continue

            total_files += len(files_to_process)

            for file_path in files_to_process:
                task = progress.add_task(f"Uploading {file_path.name} to PageIndex...", total=None)

                try:
                    mime_type, _ = mimetypes.guess_type(str(file_path))
                    mime_type = mime_type or 'application/octet-stream'
                    with open(file_path, 'rb') as f:
                        files = { 'file': (file_path.name, f, mime_type) }
                        response = requests.post(
                            f"{SERVICES['pageindex']}/extract_structure",
                            files=files,
                            timeout=60
                        )

                    progress.update(task, completed=True)

                    if response.status_code == 200:
                        processed_files += 1
                        result = response.json()
                        structure = result.get('structure', {})
                        size_bytes = structure.get('size_bytes')
                        word_count = structure.get('summary', {}).get('word_count')
                        console.print(f"   ✓ Processed: {file_path.name} | Size: {size_bytes} bytes | Words: {word_count}")

                        # Upsert extracted text into LEANN for search
                        text = result.get('text', '')
                        if text:
                            try:
                                upsert_payload = {
                                    "chunks": [
                                        {
                                            "text": text,
                                            "metadata": {
                                                "title": file_path.name,
                                                "source_file": str(file_path)
                                            }
                                        }
                                    ]
                                }
                                upsert_resp = requests.post(
                                    f"{SERVICES['leann']}/upsert",
                                    json=upsert_payload,
                                    timeout=30
                                )
                                if upsert_resp.status_code == 200:
                                    console.print("      ↳ Added to LEANN index")
                                else:
                                    console.print(f"      ↳ LEANN upsert failed: HTTP {upsert_resp.status_code}")
                            except Exception as ue:
                                console.print(f"      ↳ LEANN upsert error: {ue}")
                    else:
                        console.print(f"   ❌ Failed: {file_path.name} - HTTP {response.status_code}")

                except Exception as e:
                    progress.update(task, completed=True)
                    console.print(f"   ❌ Failed: {file_path.name} - {str(e)}")

    console.print(f"\n✅ [bold green]Indexing completed![/bold green]")
    console.print(f"   Files processed: {processed_files}/{total_files}")
    console.print("   Note: Persistence to LEANN is not yet implemented via API.")

@app.command()
def topics():
    """
    🏷️ Service metrics overview

    Shows real metrics from services. Topic clustering is not yet available via API.
    """

    console.print(f"\n🏷️ [bold blue]Service Metrics[/bold blue]")
    console.print("   Fetching live metrics from services...")

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task = progress.add_task("Collecting metrics...")
        metrics = {}
        for name, base in SERVICES.items():
            try:
                resp = requests.get(f"{base}/metrics", timeout=5)
                if resp.status_code == 200:
                    metrics[name] = resp.json()
                else:
                    metrics[name] = {"error": f"HTTP {resp.status_code}"}
            except Exception as e:
                metrics[name] = {"error": str(e)}
        progress.update(task, completed=True)

    table = Table(title="Service Metrics")
    table.add_column("Service", style="cyan")
    table.add_column("Requests", style="green")
    table.add_column("Avg ms", style="yellow")
    table.add_column("Errors", style="red")
    for name in ["pageindex", "leann", "deepconf", "thalamus", "memproxy"]:
        m = metrics.get(name, {})
        mm = m.get("metrics", {}) if isinstance(m, dict) else {}
        table.add_row(
            name,
            str(mm.get("requests", "-")),
            str(mm.get("avg_response_ms", "-")),
            str(mm.get("errors", "-"))
        )
    console.print(table)
    console.print("\nℹ️ Topic clustering is not available via API yet. Once LEANN exposes clustering endpoints, this command will surface real topics.")

@app.command()
def search(
    query: str = typer.Argument(..., help="Search query"),
    limit: int = typer.Option(10, "--limit", "-l", help="Maximum results to return"),
    include_metadata: bool = typer.Option(False, "--metadata", "-m", help="Include document metadata")
):
    """
    🔍 Search knowledge base

    Performs semantic search across indexed documents using LEANN vector search.
    Returns relevant documents with optional metadata.
    """

    console.print(f"\n🔍 [bold blue]Knowledge Search[/bold blue]")
    console.print(f"   Query: {query}")
    console.print(f"   Limit: {limit}")

    # Check LEANN service health
    leann_health = check_service_health('leann')
    if leann_health['status'] != 'healthy':
        console.print("❌ [red]LEANN service is not available[/red]")
        return

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:

        task = progress.add_task("Searching knowledge base...", total=None)

        try:
            # Query LEANN service
            payload = {
                "query": query,
                "limit": limit,
                "include_metadata": include_metadata
            }

            response = requests.post(
                f"{SERVICES['leann']}/search",
                json=payload,
                timeout=15
            )

            progress.update(task, completed=True)

            if response.status_code == 200:
                results = response.json()

                table = Table(title=f"Search Results for: '{query}'")
                table.add_column("Document", style="cyan")
                table.add_column("Relevance", style="green")
                if include_metadata:
                    table.add_column("Metadata", style="yellow")

                for result in results.get('results', []):
                    relevance = f"{result.get('score', 0):.1%}"
                    metadata = ""
                    if include_metadata and 'metadata' in result:
                        metadata = json.dumps(result['metadata'], indent=2)

                    table.add_row(
                        result.get('title', 'Unknown'),
                        relevance,
                        metadata if include_metadata else ""
                    )

                console.print(table)

            else:
                console.print(f"❌ [red]Search failed with status code: {response.status_code}[/red]")

        except Exception as e:
            progress.update(task, completed=True)
            console.print(f"❌ [red]Search failed: {str(e)}[/red]")

if __name__ == "__main__":
    app()
