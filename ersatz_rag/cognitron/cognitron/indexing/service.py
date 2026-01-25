"""
enterprise-grade indexing service combining PageIndex + LEANN architecture
"""

import asyncio
import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

# Import LEANN for AST-aware code indexing
try:
    from leann.api import LeannBuilder, LeannSearcher
    LEANN_AVAILABLE = True
except ImportError:
    print("⚠️  LEANN not available, code indexing will use fallback")
    LEANN_AVAILABLE = False

# Import for document processing
import fitz  # PyMuPDF
from sentence_transformers import SentenceTransformer

from ..models import Chunk, ChunkType, DocumentMetadata, ConfidenceLevel


class IndexingService:
    """
    enterprise-grade indexing service with multi-domain intelligence
    
    Features:
    - LEANN AST-aware code chunking
    - PageIndex-inspired smart document chunking
    - Enterprise-grade confidence tracking
    - Quality validation at every step
    """
    
    def __init__(self, index_path: Path):
        self.index_path = index_path
        self.index_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize embedding model for semantic search
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize LEANN if available
        self.leann_available = LEANN_AVAILABLE
        if self.leann_available:
            try:
                self.leann_builder = LeannBuilder(backend_name="hnsw")
                self.leann_searcher = None
            except Exception as e:
                print(f"⚠️  LEANN initialization failed: {e}")
                self.leann_builder = None
                self.leann_searcher = None
                self.leann_available = False
        else:
            self.leann_builder = None
            self.leann_searcher = None
            
        # enterprise-grade quality thresholds
        self.confidence_threshold = 0.85
        self.chunk_min_confidence = 0.70
        
        print("🔍 Enterprise-Grade Indexing Service Initialized")
        print(f"   Index Path: {index_path}")
        print(f"   LEANN Available: {self.leann_available}")
        print(f"   Confidence Threshold: {self.confidence_threshold:.1%}")
        
    async def run_indexing(
        self,
        paths: List[Path],
        force_rebuild: bool = False,
        confidence_threshold: float = 0.85
    ) -> Dict[str, Any]:
        """
        Run enterprise-grade indexing with quality validation
        
        Args:
            paths: Paths to index (files or directories)
            force_rebuild: Force complete rebuild
            confidence_threshold: Minimum confidence for chunk storage
            
        Returns:
            Indexing results with quality metrics
        """
        
        start_time = time.time()
        
        print("📚 Starting enterprise-grade content indexing...")
        
        # Collect all files to index
        all_files = []
        for path in paths:
            if path.is_file():
                all_files.append(path)
            elif path.is_dir():
                all_files.extend(self._discover_files(path))
                
        print(f"📄 Discovered {len(all_files)} files to index")
        
        # Process files by type with confidence tracking
        indexing_results = {
            "total_files": len(all_files),
            "indexed_documents": 0,
            "chunks_created": 0,
            "high_confidence_chunks": 0,
            "processing_errors": 0,
            "confidence_distribution": {},
            "success": False
        }
        
        all_chunks = []
        
        for file_path in all_files:
            try:
                print(f"🔍 Processing: {file_path.name}")
                
                # Determine processing strategy
                strategy = self._get_strategy(file_path)
                
                # Process file with appropriate strategy
                if strategy == "code_ast":
                    chunks = await self._process_code_file(file_path)
                elif strategy == "document_structure":
                    chunks = await self._process_document_file(file_path)
                else:
                    chunks = await self._process_text_file(file_path)
                    
                # Validate chunk confidence
                high_confidence_chunks = [
                    chunk for chunk in chunks 
                    if chunk.overall_confidence >= confidence_threshold
                ]
                
                all_chunks.extend(high_confidence_chunks)
                indexing_results["chunks_created"] += len(chunks)
                indexing_results["high_confidence_chunks"] += len(high_confidence_chunks)
                indexing_results["indexed_documents"] += 1
                
                # Track confidence distribution
                for chunk in chunks:
                    conf_level = chunk.confidence_level.value
                    if conf_level not in indexing_results["confidence_distribution"]:
                        indexing_results["confidence_distribution"][conf_level] = 0
                    indexing_results["confidence_distribution"][conf_level] += 1
                    
            except Exception as e:
                print(f"❌ Error processing {file_path}: {e}")
                indexing_results["processing_errors"] += 1
                
        # Build LEANN index if available and we have chunks
        if self.leann_available and all_chunks:
            print("🧠 Building LEANN semantic index...")
            try:
                await self._build_leann_index(all_chunks)
            except Exception as e:
                print(f"⚠️  LEANN indexing failed: {e}")
                
        # Save chunk metadata
        await self._save_chunk_metadata(all_chunks)
        
        indexing_time = time.time() - start_time
        indexing_results["indexing_time"] = indexing_time
        indexing_results["success"] = indexing_results["processing_errors"] == 0
        
        print(f"✅ Indexing completed in {indexing_time:.2f}s")
        print(f"   High-confidence chunks: {indexing_results['high_confidence_chunks']}")
        print(f"   Confidence distribution: {indexing_results['confidence_distribution']}")
        
        return indexing_results
        
    def _discover_files(self, directory: Path) -> List[Path]:
        """Discover indexable files in directory"""
        
        # Supported file types
        code_extensions = {'.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.hpp', '.go', '.rs', '.rb', '.php'}
        doc_extensions = {'.md', '.txt', '.pdf', '.docx', '.rst', '.org'}
        
        supported_extensions = code_extensions | doc_extensions
        
        files = []
        for file_path in directory.rglob('*'):
            if (file_path.is_file() and 
                file_path.suffix.lower() in supported_extensions and
                not any(part.startswith('.') for part in file_path.parts[1:])):  # Skip hidden files/dirs
                files.append(file_path)
                
        return files
        
    def _get_strategy(self, file_path: Path) -> str:
        """Determine processing strategy for file"""
        
        suffix = file_path.suffix.lower()
        
        # Code files use AST-aware chunking
        code_extensions = {'.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.hpp', '.go', '.rs', '.rb', '.php'}
        if suffix in code_extensions:
            return "code_ast"
            
        # Document files use structure-aware chunking
        doc_extensions = {'.pdf', '.docx'}
        if suffix in doc_extensions:
            return "document_structure"
            
        # Plain text files
        return "plain_text"
        
    async def _process_code_file(self, file_path: Path) -> List[Chunk]:
        """Process code file with AST-aware chunking"""
        
        try:
            # Read code file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Use LEANN AST chunking if available
            if LEANN_AVAILABLE:
                chunks = await self._leann_ast_chunking(file_path, content)
            else:
                chunks = await self._fallback_code_chunking(file_path, content)
                
            # Add confidence scores based on code analysis
            for chunk in chunks:
                chunk.extraction_confidence = self._calculate_code_extraction_confidence(chunk.content)
                chunk.semantic_confidence = self._calculate_code_semantic_confidence(chunk.content)
                
            return chunks
            
        except Exception as e:
            print(f"❌ Code processing failed for {file_path}: {e}")
            return []
            
    async def _leann_ast_chunking(self, file_path: Path, content: str) -> List[Chunk]:
        """Use LEANN AST-aware chunking for code"""
        
        # Simplified LEANN-style chunking (actual implementation would use LEANN API)
        chunks = []
        
        # Split by functions/classes (simplified AST analysis)
        lines = content.split('\n')
        current_chunk = []
        chunk_title = None
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            
            # Detect function/class definitions
            if (line_stripped.startswith('def ') or 
                line_stripped.startswith('class ') or
                line_stripped.startswith('function ') or
                line_stripped.startswith('async def ')):
                
                # Save previous chunk
                if current_chunk:
                    chunk_content = '\n'.join(current_chunk)
                    if len(chunk_content.strip()) > 50:  # Minimum chunk size
                        chunk = Chunk(
                            document_id=self._get_document_id(file_path),
                            chunk_type=ChunkType.CODE_AST,
                            content=chunk_content,
                            title=chunk_title or "Code Block",
                            start_index=i - len(current_chunk),
                            end_index=i,
                            ast_node_type="function" if "def " in line_stripped else "class",
                            extraction_confidence=0.9,
                            semantic_confidence=0.8
                        )
                        chunks.append(chunk)
                        
                # Start new chunk
                current_chunk = [line]
                chunk_title = line_stripped.split('(')[0].replace('def ', '').replace('class ', '').strip()
            else:
                current_chunk.append(line)
                
        # Add final chunk
        if current_chunk:
            chunk_content = '\n'.join(current_chunk)
            if len(chunk_content.strip()) > 50:
                chunk = Chunk(
                    document_id=self._get_document_id(file_path),
                    chunk_type=ChunkType.CODE_AST,
                    content=chunk_content,
                    title=chunk_title or "Code Block",
                    start_index=len(lines) - len(current_chunk),
                    end_index=len(lines),
                    extraction_confidence=0.9,
                    semantic_confidence=0.8
                )
                chunks.append(chunk)
                
        return chunks
        
    async def _fallback_code_chunking(self, file_path: Path, content: str) -> List[Chunk]:
        """Fallback code chunking when LEANN unavailable"""
        
        # Simple line-based chunking
        lines = content.split('\n')
        chunk_size = 100  # lines per chunk
        
        chunks = []
        for i in range(0, len(lines), chunk_size):
            chunk_lines = lines[i:i + chunk_size]
            chunk_content = '\n'.join(chunk_lines)
            
            if len(chunk_content.strip()) > 50:
                chunk = Chunk(
                    document_id=self._get_document_id(file_path),
                    chunk_type=ChunkType.CODE_AST,
                    content=chunk_content,
                    title=f"Code Block {i // chunk_size + 1}",
                    start_index=i,
                    end_index=min(i + chunk_size, len(lines)),
                    extraction_confidence=0.85,
                    semantic_confidence=0.75
                )
                chunks.append(chunk)
                
        return chunks
        
    async def _process_document_file(self, file_path: Path) -> List[Chunk]:
        """Process document file with structure-aware chunking (PageIndex-inspired)"""
        
        try:
            if file_path.suffix.lower() == '.pdf':
                return await self._process_pdf_file(file_path)
            else:
                return await self._process_text_file(file_path)
                
        except Exception as e:
            print(f"❌ Document processing failed for {file_path}: {e}")
            return []
            
    async def _process_pdf_file(self, file_path: Path) -> List[Chunk]:
        """Process PDF with structure awareness"""
        
        chunks = []
        
        try:
            # Open PDF
            doc = fitz.open(file_path)
            
            current_section = None
            current_content = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # Extract text with structure information
                blocks = page.get_text("dict")["blocks"]
                
                for block in blocks:
                    if "lines" in block:
                        for line in block["lines"]:
                            for span in line["spans"]:
                                text = span["text"].strip()
                                if not text:
                                    continue
                                    
                                # Detect headings (larger font size)
                                font_size = span["size"]
                                if font_size > 14:  # Heading detection heuristic
                                    # Save previous section
                                    if current_content:
                                        section_content = '\n'.join(current_content)
                                        if len(section_content.strip()) > 100:
                                            chunk = Chunk(
                                                document_id=self._get_document_id(file_path),
                                                chunk_type=ChunkType.DOCUMENT_STRUCTURE,
                                                content=section_content,
                                                title=current_section or "Document Section",
                                                document_section=current_section,
                                                extraction_confidence=0.9,
                                                semantic_confidence=0.85
                                            )
                                            chunks.append(chunk)
                                            
                                    # Start new section
                                    current_section = text
                                    current_content = []
                                else:
                                    current_content.append(text)
                                    
            # Add final section
            if current_content:
                section_content = '\n'.join(current_content)
                if len(section_content.strip()) > 100:
                    chunk = Chunk(
                        document_id=self._get_document_id(file_path),
                        chunk_type=ChunkType.DOCUMENT_STRUCTURE,
                        content=section_content,
                        title=current_section or "Document Section",
                        document_section=current_section,
                        extraction_confidence=0.9,
                        semantic_confidence=0.85
                    )
                    chunks.append(chunk)
                    
            doc.close()
            
            # Calculate document-specific confidence
            for chunk in chunks:
                chunk.extraction_confidence = self._calculate_document_extraction_confidence(chunk.content)
                chunk.semantic_confidence = self._calculate_document_semantic_confidence(chunk.content)
                
            return chunks
            
        except Exception as e:
            print(f"❌ PDF processing failed: {e}")
            return []
            
    async def _process_text_file(self, file_path: Path) -> List[Chunk]:
        """Process text file with simple chunking"""
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Simple paragraph-based chunking
            paragraphs = content.split('\n\n')
            chunks = []
            
            current_chunk_paras = []
            current_word_count = 0
            target_chunk_size = 500  # words
            
            for para in paragraphs:
                para_words = len(para.split())
                
                if current_word_count + para_words > target_chunk_size and current_chunk_paras:
                    # Create chunk
                    chunk_content = '\n\n'.join(current_chunk_paras)
                    if len(chunk_content.strip()) > 100:
                        chunk = Chunk(
                            document_id=self._get_document_id(file_path),
                            chunk_type=ChunkType.PLAIN_TEXT,
                            content=chunk_content,
                            title=f"Text Section {len(chunks) + 1}",
                            extraction_confidence=0.8,
                            semantic_confidence=0.75
                        )
                        chunks.append(chunk)
                        
                    # Reset
                    current_chunk_paras = [para]
                    current_word_count = para_words
                else:
                    current_chunk_paras.append(para)
                    current_word_count += para_words
                    
            # Add final chunk
            if current_chunk_paras:
                chunk_content = '\n\n'.join(current_chunk_paras)
                if len(chunk_content.strip()) > 100:
                    chunk = Chunk(
                        document_id=self._get_document_id(file_path),
                        chunk_type=ChunkType.PLAIN_TEXT,
                        content=chunk_content,
                        title=f"Text Section {len(chunks) + 1}",
                        extraction_confidence=0.8,
                        semantic_confidence=0.75
                    )
                    chunks.append(chunk)
                    
            # Calculate text-specific confidence
            for chunk in chunks:
                chunk.extraction_confidence = self._calculate_text_extraction_confidence(chunk.content)
                chunk.semantic_confidence = self._calculate_text_semantic_confidence(chunk.content)
                
            return chunks
            
        except Exception as e:
            print(f"❌ Text processing failed: {e}")
            return []
            
    def _calculate_code_extraction_confidence(self, content: str) -> float:
        """Calculate extraction confidence for code content"""
        
        # Factors: syntax validity, completeness, structure
        confidence_factors = []
        
        # Basic syntax indicators
        if content.count('(') == content.count(')'):
            confidence_factors.append(0.9)
        else:
            confidence_factors.append(0.6)
            
        if content.count('{') == content.count('}'):
            confidence_factors.append(0.9)
        else:
            confidence_factors.append(0.7)
            
        # Content completeness
        word_count = len(content.split())
        if 50 <= word_count <= 500:
            confidence_factors.append(0.9)
        elif word_count < 50:
            confidence_factors.append(0.6)
        else:
            confidence_factors.append(0.8)
            
        return min(confidence_factors) if confidence_factors else 0.5
        
    def _calculate_code_semantic_confidence(self, content: str) -> float:
        """Calculate semantic confidence for code content"""
        
        # Factors: meaningful names, comments, structure
        confidence_factors = []
        
        # Comment ratio
        lines = content.split('\n')
        comment_lines = [line for line in lines if line.strip().startswith('#') or line.strip().startswith('//')]
        comment_ratio = len(comment_lines) / max(len(lines), 1)
        
        if comment_ratio > 0.1:
            confidence_factors.append(0.9)
        else:
            confidence_factors.append(0.7)
            
        # Meaningful variable names (heuristic)
        single_letter_vars = len([word for word in content.split() if len(word) == 1 and word.isalpha()])
        total_words = len(content.split())
        
        if single_letter_vars / max(total_words, 1) < 0.1:
            confidence_factors.append(0.9)
        else:
            confidence_factors.append(0.7)
            
        return min(confidence_factors) if confidence_factors else 0.8
        
    def _calculate_document_extraction_confidence(self, content: str) -> float:
        """Calculate extraction confidence for document content"""
        
        # Factors: completeness, formatting, readability
        confidence_factors = []
        
        # Length appropriateness
        word_count = len(content.split())
        if 100 <= word_count <= 1000:
            confidence_factors.append(0.95)
        elif 50 <= word_count < 100:
            confidence_factors.append(0.8)
        else:
            confidence_factors.append(0.7)
            
        # Sentence completeness
        sentences = content.split('.')
        complete_sentences = [s for s in sentences if len(s.strip()) > 10]
        completeness = len(complete_sentences) / max(len(sentences), 1)
        
        if completeness > 0.8:
            confidence_factors.append(0.9)
        else:
            confidence_factors.append(0.7)
            
        return min(confidence_factors) if confidence_factors else 0.8
        
    def _calculate_document_semantic_confidence(self, content: str) -> float:
        """Calculate semantic confidence for document content"""
        return 0.85  # Simplified for documents
        
    def _calculate_text_extraction_confidence(self, content: str) -> float:
        """Calculate extraction confidence for text content"""
        return 0.9  # Text files are usually well extracted
        
    def _calculate_text_semantic_confidence(self, content: str) -> float:
        """Calculate semantic confidence for text content"""
        return 0.8  # Moderate confidence for plain text
        
    def _get_document_id(self, file_path: Path) -> UUID:
        """Generate document ID from file path"""
        import uuid
        # Generate UUID from file path hash
        return uuid.uuid5(uuid.NAMESPACE_OID, str(file_path))
        
    async def _build_leann_index(self, chunks: List[Chunk]) -> None:
        """Build LEANN semantic index from chunks"""
        
        if not self.leann_available or not self.leann_builder:
            return
            
        try:
            # Add chunks to LEANN builder
            for chunk in chunks:
                # Add chunk content with metadata
                await asyncio.to_thread(
                    self.leann_builder.add_document,
                    doc_id=str(chunk.chunk_id),
                    content=chunk.content,
                    metadata={
                        "title": chunk.title,
                        "chunk_type": chunk.chunk_type.value,
                        "confidence": chunk.overall_confidence
                    }
                )
                
            # Build index
            index_path = self.index_path / "leann_index"
            await asyncio.to_thread(self.leann_builder.build_index, str(index_path))
            
            # Initialize searcher
            self.leann_searcher = LeannSearcher(str(index_path))
            
        except Exception as e:
            print(f"❌ LEANN index building failed: {e}")
            
    async def _save_chunk_metadata(self, chunks: List[Chunk]) -> None:
        """Save chunk metadata for retrieval"""
        
        metadata_path = self.index_path / "chunk_metadata.json"
        
        chunk_metadata = []
        for chunk in chunks:
            chunk_data = {
                "chunk_id": str(chunk.chunk_id),
                "document_id": str(chunk.document_id),
                "chunk_type": chunk.chunk_type.value,
                "title": chunk.title,
                "confidence": chunk.overall_confidence,
                "confidence_level": chunk.confidence_level.value,
                "content_preview": chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content
            }
            chunk_metadata.append(chunk_data)
            
        with open(metadata_path, 'w') as f:
            json.dump(chunk_metadata, f, indent=2)
            
    async def search_code(self, query: str, max_results: int = 10, confidence_threshold: float = 0.7) -> Dict[str, Any]:
        """Search code using LEANN if available"""
        
        if not self.leann_available or not self.leann_searcher:
            return {"chunks": [], "message": "Code search unavailable - LEANN not initialized"}
            
        try:
            # Search using LEANN
            results = await asyncio.to_thread(
                self.leann_searcher.search,
                query=query,
                top_k=max_results,
                filters={"chunk_type": "code_ast"}
            )
            
            # Filter by confidence
            high_confidence_results = [
                result for result in results
                if result.get("metadata", {}).get("confidence", 0.0) >= confidence_threshold
            ]
            
            return {
                "chunks": high_confidence_results,
                "total_found": len(results),
                "high_confidence_count": len(high_confidence_results)
            }
            
        except Exception as e:
            return {"chunks": [], "error": str(e)}
            
    async def search_documents(self, query: str, max_results: int = 10, confidence_threshold: float = 0.7) -> Dict[str, Any]:
        """Search documents using semantic similarity"""
        
        try:
            # Load chunk metadata
            metadata_path = self.index_path / "chunk_metadata.json"
            if not metadata_path.exists():
                return {"chunks": [], "message": "No indexed documents found"}
                
            with open(metadata_path, 'r') as f:
                chunks_metadata = json.load(f)
                
            # Filter document chunks
            doc_chunks = [
                chunk for chunk in chunks_metadata
                if chunk["chunk_type"] in ["document_structure", "plain_text"] and
                chunk["confidence"] >= confidence_threshold
            ]
            
            # Simple text matching (could be enhanced with embeddings)
            query_words = set(query.lower().split())
            scored_chunks = []
            
            for chunk in doc_chunks:
                content_words = set(chunk["content_preview"].lower().split())
                title_words = set(chunk["title"].lower().split())
                
                # Calculate simple relevance score
                content_overlap = len(query_words & content_words) / len(query_words)
                title_overlap = len(query_words & title_words) / len(query_words)
                relevance_score = (content_overlap * 0.7) + (title_overlap * 0.3)
                
                if relevance_score > 0:
                    chunk["relevance_score"] = relevance_score
                    scored_chunks.append(chunk)
                    
            # Sort by relevance and confidence
            scored_chunks.sort(key=lambda x: (x["relevance_score"], x["confidence"]), reverse=True)
            
            return {
                "chunks": scored_chunks[:max_results],
                "total_found": len(scored_chunks)
            }
            
        except Exception as e:
            return {"chunks": [], "error": str(e)}
            
    async def get_index_stats(self) -> Dict[str, Any]:
        """Get comprehensive index statistics"""
        
        stats = {
            "index_path": str(self.index_path),
            "leann_available": self.leann_available,
            "confidence_threshold": self.confidence_threshold
        }
        
        # Load chunk metadata if available
        metadata_path = self.index_path / "chunk_metadata.json"
        if metadata_path.exists():
            with open(metadata_path, 'r') as f:
                chunks_metadata = json.load(f)
                
            stats.update({
                "total_chunks": len(chunks_metadata),
                "chunk_types": {},
                "confidence_distribution": {}
            })
            
            for chunk in chunks_metadata:
                # Count by type
                chunk_type = chunk["chunk_type"]
                if chunk_type not in stats["chunk_types"]:
                    stats["chunk_types"][chunk_type] = 0
                stats["chunk_types"][chunk_type] += 1
                
                # Count by confidence level
                conf_level = chunk["confidence_level"]
                if conf_level not in stats["confidence_distribution"]:
                    stats["confidence_distribution"][conf_level] = 0
                stats["confidence_distribution"][conf_level] += 1
                
        return stats
        
    async def search_chunks(self, query: str, max_results: int = 5, confidence_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Search all chunks across code and documents"""
        
        try:
            # Load chunk metadata
            metadata_path = self.index_path / "chunk_metadata.json"
            if not metadata_path.exists():
                return []
                
            with open(metadata_path, 'r') as f:
                chunks_metadata = json.load(f)
                
            # Filter by confidence
            high_confidence_chunks = [
                chunk for chunk in chunks_metadata
                if chunk["confidence"] >= confidence_threshold
            ]
            
            # Simple text matching for relevance scoring
            query_words = set(query.lower().split())
            scored_chunks = []
            
            for chunk in high_confidence_chunks:
                content_words = set(chunk.get("content_preview", "").lower().split())
                title_words = set(chunk.get("title", "").lower().split())
                
                # Calculate relevance score
                content_matches = len(query_words.intersection(content_words))
                title_matches = len(query_words.intersection(title_words))
                
                relevance_score = (title_matches * 2) + content_matches
                
                if relevance_score > 0:
                    chunk["relevance_score"] = relevance_score
                    scored_chunks.append(chunk)
                    
            # Sort by relevance and confidence
            scored_chunks.sort(key=lambda x: (x["relevance_score"], x["confidence"]), reverse=True)
            
            return scored_chunks[:max_results]
            
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return []