"""
Confidence-gated case memory system for Cognitron
Developer-grade memory that only stores high-confidence successful cases
"""

import json
import sqlite3
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID, uuid4

import numpy as np
from sentence_transformers import SentenceTransformer

from ..models import CaseMemoryEntry, ConfidenceLevel, WorkflowTrace
from .confidence import ConfidenceProfile


class CaseMemory:
    """
    Developer-grade case memory system that learns from high-confidence successes
    Only stores cases that meet developer AI confidence standards
    """
    
    def __init__(self, db_path: Path, embedding_model: str = "all-MiniLM-L6-v2"):
        self.db_path = db_path
        self.embedding_model = SentenceTransformer(embedding_model)
        
        # Developer-grade confidence thresholds
        self.storage_threshold = 0.85  # Only store high-confidence cases
        self.critical_threshold = 0.95  # Critical enterprise-grade threshold
        self.retrieval_threshold = 0.80  # Minimum confidence for case retrieval
        
        # Database will be initialized lazily on first access
        self._db_initialized = False
        
    async def _ensure_db_initialized(self) -> None:
        """Ensure database is initialized"""
        if not self._db_initialized:
            await self._init_database()
            self._db_initialized = True
        
    async def _init_database(self) -> None:
        """Initialize SQLite database with enterprise-grade case storage schema"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Cases table with confidence tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cases (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                query TEXT NOT NULL,
                query_embedding BLOB NOT NULL,
                outcome TEXT NOT NULL,
                
                -- Confidence metrics (enterprise-grade)
                overall_confidence REAL NOT NULL,
                confidence_level TEXT NOT NULL,
                storage_confidence REAL NOT NULL,
                
                -- Workflow information
                workflow_trace_json TEXT NOT NULL,
                confidence_profile_json TEXT NOT NULL,
                
                -- Success tracking
                success BOOLEAN NOT NULL,
                execution_time REAL NOT NULL,
                retrieval_count INTEGER DEFAULT 0,
                success_rate REAL DEFAULT 1.0,
                
                -- Quality assurance
                meets_critical_threshold BOOLEAN NOT NULL,
                safe_for_production BOOLEAN NOT NULL,
                requires_human_review BOOLEAN NOT NULL,
                
                -- Metadata
                created_at TEXT NOT NULL,
                last_retrieved_at TEXT,
                
                -- Indexes for fast retrieval
                FOREIGN KEY (id) REFERENCES case_embeddings(case_id)
            )
        """)
        
        # Separate table for embeddings (for similarity search)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS case_embeddings (
                case_id TEXT PRIMARY KEY,
                embedding BLOB NOT NULL,
                FOREIGN KEY (case_id) REFERENCES cases(id)
            )
        """)
        
        # Performance tracking table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS case_performance (
                case_id TEXT NOT NULL,
                retrieval_timestamp TEXT NOT NULL,
                applied_successfully BOOLEAN NOT NULL,
                user_feedback INTEGER, -- -1, 0, 1 for negative, neutral, positive
                confidence_at_retrieval REAL NOT NULL,
                actual_outcome_confidence REAL,
                notes TEXT,
                FOREIGN KEY (case_id) REFERENCES cases(id)
            )
        """)
        
        # Indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_confidence ON cases(overall_confidence)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON cases(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_success ON cases(success)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_critical ON cases(meets_critical_threshold)")
        
        conn.commit()
        conn.close()
        
    async def add_case(
        self,
        query: str,
        outcome: str,
        workflow_trace: WorkflowTrace,
        confidence_profile: ConfidenceProfile,
        success: bool = True,
        execution_time: float = 0.0
    ) -> Optional[str]:
        """
        Add a case to memory only if it meets enterprise-grade confidence standards
        
        Returns case_id if stored, None if confidence too low
        """
        await self._ensure_db_initialized()
        
        # Only store high-confidence successful cases
        storage_confidence = min(
            confidence_profile.overall_confidence,
            workflow_trace.overall_confidence if workflow_trace else 0.0
        )
        
        if storage_confidence < self.storage_threshold:
            return None  # Don't store low-confidence cases
            
        if not success:
            return None  # Don't store failed cases
            
        case_id = str(uuid4())
        
        # Generate query embedding for similarity search
        query_embedding = self.embedding_model.encode(query)
        
        # Create case memory entry
        case_entry = CaseMemoryEntry(
            case_id=UUID(case_id),
            query=query,
            outcome=outcome,
            workflow_trace=workflow_trace,
            confidence_profile=confidence_profile.dict() if hasattr(confidence_profile, 'dict') else confidence_profile.__dict__,
            success=success,
            execution_time=execution_time,
            storage_confidence=storage_confidence,
            eligible_for_storage=True
        )
        
        # Store in database
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        try:
            # Insert case
            cursor.execute("""
                INSERT INTO cases (
                    id, timestamp, query, query_embedding, outcome,
                    overall_confidence, confidence_level, storage_confidence,
                    workflow_trace_json, confidence_profile_json,
                    success, execution_time, retrieval_count, success_rate,
                    meets_critical_threshold, safe_for_production, requires_human_review,
                    created_at, last_retrieved_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                case_id,
                datetime.now().isoformat(),
                query,
                query_embedding.tobytes(),
                outcome,
                confidence_profile.overall_confidence,
                confidence_profile.confidence_level.value,
                storage_confidence,
                json.dumps(workflow_trace.dict() if hasattr(workflow_trace, 'dict') else workflow_trace.__dict__),
                json.dumps(case_entry.confidence_profile),
                success,
                execution_time,
                0,  # retrieval_count
                1.0,  # success_rate
                confidence_profile.meets_developer_threshold,
                confidence_profile.overall_confidence >= 0.85,  # safe_for_production
                confidence_profile.overall_confidence < 0.95,  # requires_human_review
                datetime.now().isoformat(),
                None  # last_retrieved_at
            ))
            
            # Insert embedding
            cursor.execute("""
                INSERT INTO case_embeddings (case_id, embedding)
                VALUES (?, ?)
            """, (case_id, query_embedding.tobytes()))
            
            conn.commit()
            return case_id
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
            
    async def retrieve_cases(
        self,
        query: str,
        min_confidence: float = 0.80,
        max_cases: int = 5,
        similarity_threshold: float = 0.7
    ) -> List[CaseMemoryEntry]:
        """
        Retrieve similar high-confidence cases for a query
        Uses enterprise-grade confidence filtering
        """
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode(query)
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Retrieve all cases above confidence threshold
        cursor.execute("""
            SELECT c.*, e.embedding
            FROM cases c
            JOIN case_embeddings e ON c.id = e.case_id
            WHERE c.overall_confidence >= ?
            AND c.success = 1
            ORDER BY c.overall_confidence DESC, c.retrieval_count ASC
        """, (min_confidence,))
        
        rows = cursor.fetchall()
        conn.close()
        
        # Calculate similarities and filter
        similar_cases = []
        
        for row in rows:
            # Extract embedding
            case_embedding = np.frombuffer(row[-1], dtype=np.float32)
            
            # Calculate cosine similarity
            similarity = np.dot(query_embedding, case_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(case_embedding)
            )
            
            if similarity >= similarity_threshold:
                # Reconstruct case entry
                case_data = {
                    'case_id': UUID(row[0]),
                    'query': row[2],
                    'outcome': row[4],
                    'workflow_trace': json.loads(row[8]),
                    'confidence_profile': json.loads(row[9]),
                    'success': bool(row[10]),
                    'execution_time': row[11],
                    'retrieval_count': row[12],
                    'success_rate': row[13],
                    'storage_confidence': row[7],
                    'created_at': datetime.fromisoformat(row[17])
                }
                
                case_entry = CaseMemoryEntry(**case_data)
                case_entry.similarity_score = similarity
                similar_cases.append(case_entry)
                
        # Sort by confidence and similarity, return top cases
        similar_cases.sort(key=lambda x: (x.storage_confidence, x.similarity_score), reverse=True)
        
        # Update retrieval counts
        if similar_cases:
            await self._update_retrieval_counts([case.case_id for case in similar_cases[:max_cases]])
            
        return similar_cases[:max_cases]
        
    async def _update_retrieval_counts(self, case_ids: List[UUID]) -> None:
        """Update retrieval counts for retrieved cases"""
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        for case_id in case_ids:
            cursor.execute("""
                UPDATE cases 
                SET retrieval_count = retrieval_count + 1,
                    last_retrieved_at = ?
                WHERE id = ?
            """, (datetime.now().isoformat(), str(case_id)))
            
        conn.commit()
        conn.close()
        
    async def record_case_performance(
        self,
        case_id: UUID,
        applied_successfully: bool,
        user_feedback: Optional[int] = None,
        confidence_at_retrieval: float = 0.0,
        actual_outcome_confidence: Optional[float] = None,
        notes: Optional[str] = None
    ) -> None:
        """
        Record performance of a retrieved case for continuous learning
        """
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Record performance
        cursor.execute("""
            INSERT INTO case_performance (
                case_id, retrieval_timestamp, applied_successfully, user_feedback,
                confidence_at_retrieval, actual_outcome_confidence, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            str(case_id),
            datetime.now().isoformat(),
            applied_successfully,
            user_feedback,
            confidence_at_retrieval,
            actual_outcome_confidence,
            notes
        ))
        
        # Update case success rate
        cursor.execute("""
            SELECT COUNT(*), SUM(CASE WHEN applied_successfully THEN 1 ELSE 0 END)
            FROM case_performance 
            WHERE case_id = ?
        """, (str(case_id),))
        
        total_applications, successful_applications = cursor.fetchone()
        if total_applications > 0:
            success_rate = successful_applications / total_applications
            cursor.execute("""
                UPDATE cases SET success_rate = ? WHERE id = ?
            """, (success_rate, str(case_id)))
            
        conn.commit()
        conn.close()
        
    async def get_memory_stats(self) -> Dict[str, Any]:
        """Get comprehensive memory system statistics"""
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Basic stats
        cursor.execute("SELECT COUNT(*) FROM cases")
        total_cases = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM cases WHERE meets_critical_threshold = 1")
        critical_cases = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM cases WHERE safe_for_production = 1")
        production_cases = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(overall_confidence) FROM cases")
        avg_confidence = cursor.fetchone()[0] or 0.0
        
        cursor.execute("SELECT AVG(success_rate) FROM cases")
        avg_success_rate = cursor.fetchone()[0] or 0.0
        
        # Confidence distribution
        cursor.execute("""
            SELECT 
                confidence_level,
                COUNT(*) as count,
                AVG(overall_confidence) as avg_confidence
            FROM cases 
            GROUP BY confidence_level
        """)
        confidence_distribution = {row[0]: {"count": row[1], "avg_confidence": row[2]} 
                                  for row in cursor.fetchall()}
        
        # Recent activity
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        cursor.execute("SELECT COUNT(*) FROM cases WHERE created_at >= ?", (week_ago,))
        cases_last_week = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM case_performance WHERE retrieval_timestamp >= ?", (week_ago,))
        retrievals_last_week = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_cases": total_cases,
            "critical_cases": critical_cases,
            "production_ready_cases": production_cases,
            "average_confidence": avg_confidence,
            "average_success_rate": avg_success_rate,
            "confidence_distribution": confidence_distribution,
            "cases_added_last_week": cases_last_week,
            "retrievals_last_week": retrievals_last_week,
            "storage_threshold": self.storage_threshold,
            "critical_threshold": self.critical_threshold
        }
        
    async def cleanup_low_performing_cases(self, min_success_rate: float = 0.3, min_applications: int = 5) -> int:
        """
        Remove cases that consistently perform poorly
        Maintains enterprise-grade quality standards
        """
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Find low-performing cases
        cursor.execute("""
            SELECT id FROM cases 
            WHERE retrieval_count >= ? 
            AND success_rate < ?
        """, (min_applications, min_success_rate))
        
        low_performing_cases = [row[0] for row in cursor.fetchall()]
        
        if not low_performing_cases:
            conn.close()
            return 0
            
        # Delete low-performing cases
        placeholders = ','.join('?' * len(low_performing_cases))
        
        cursor.execute(f"DELETE FROM case_performance WHERE case_id IN ({placeholders})", low_performing_cases)
        cursor.execute(f"DELETE FROM case_embeddings WHERE case_id IN ({placeholders})", low_performing_cases)
        cursor.execute(f"DELETE FROM cases WHERE id IN ({placeholders})", low_performing_cases)
        
        conn.commit()
        deleted_count = cursor.rowcount
        conn.close()
        
        return deleted_count
        
    async def export_high_confidence_cases(self, output_path: Path, min_confidence: float = 0.90) -> int:
        """
        Export high-confidence cases for analysis or backup
        """
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM cases 
            WHERE overall_confidence >= ?
            ORDER BY overall_confidence DESC
        """, (min_confidence,))
        
        rows = cursor.fetchall()
        conn.close()
        
        # Convert to exportable format
        cases_data = []
        for row in rows:
            case_data = {
                "case_id": row[0],
                "timestamp": row[1],
                "query": row[2],
                "outcome": row[4],
                "overall_confidence": row[5],
                "confidence_level": row[6],
                "workflow_trace": json.loads(row[8]),
                "confidence_profile": json.loads(row[9]),
                "success": bool(row[10]),
                "execution_time": row[11],
                "retrieval_count": row[12],
                "success_rate": row[13]
            }
            cases_data.append(case_data)
            
        # Export to JSON
        with open(output_path, 'w') as f:
            json.dump(cases_data, f, indent=2, default=str)
            
        return len(cases_data)