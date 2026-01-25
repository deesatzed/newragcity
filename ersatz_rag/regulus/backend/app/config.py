"""
Configuration settings for Regulus backend
"""
import os
from pathlib import Path

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/regulus")

# Embedding Model Configuration
# Primary model: IBM Granite for enterprise use
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "ibm-granite/granite-embedding-english-r2")

# Hybrid Retrieval (Option B) Configuration
HYBRID_ENABLED = os.getenv("REGULUS_HYBRID_ENABLED", "true").lower() in {"1", "true", "yes"}
HYBRID_EMBEDDING_MODEL = os.getenv("HYBRID_EMBEDDING_MODEL", "BAAI/bge-large-en-v1.5")
QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "regulus_docs")
OPENSEARCH_URL = os.getenv("OPENSEARCH_URL", "http://opensearch:9200")
OPENSEARCH_INDEX = os.getenv("OPENSEARCH_INDEX", "regulus_docs")
EMBED_BATCH_SIZE = int(os.getenv("EMBED_BATCH_SIZE", "16"))
CHUNK_PARAS = int(os.getenv("CHUNK_PARAS", "2"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "1"))

# Alternative models for compatibility with other applications:
# - "NeuML/pubmedbert-base-embeddings" for medical/research applications
# - "facebook/contriever" for general retrieval tasks
# - "sentence-transformers/all-MiniLM-L6-v2" for lightweight deployments

EMBEDDING_MODELS = {
    "granite": "ibm-granite/granite-embedding-english-r2",
    "pubmed": "NeuML/pubmedbert-base-embeddings", 
    "contriever": "facebook/contriever",
    "minilm": "sentence-transformers/all-MiniLM-L6-v2"
}

# LEANN Configuration
LEANN_BACKEND = os.getenv("LEANN_BACKEND", "hnsw")
LEANN_DIMENSIONS = 768  # Standard for most modern embedding models
LEANN_EMBEDDING_MODE = "sentence-transformers"

# Index Configuration
INDEX_PATH = os.getenv("INDEX_PATH", "/app/regulus_index.leann")
INDEX_BASE_DIR = Path(INDEX_PATH).parent

# PageIndex Configuration (API-based)
PAGEINDEX_API_KEY = os.getenv("PAGEINDEX_API_KEY") or os.getenv("CHATGPT_API_KEY")

# deepConf Configuration
DEEPCONF_ENABLED = os.getenv("DEEPCONF_ENABLED", "true").lower() == "true"
DEEPCONF_CONFIDENCE_THRESHOLD = float(os.getenv("DEEPCONF_CONFIDENCE_THRESHOLD", "0.80"))
DEEPCONF_WINDOW_SIZE = int(os.getenv("DEEPCONF_WINDOW_SIZE", "2048"))

# Document Processing Configuration
MAX_PAGES_PER_NODE = int(os.getenv("MAX_PAGES_PER_NODE", "10"))
MAX_TOKENS_PER_NODE = int(os.getenv("MAX_TOKENS_PER_NODE", "20000"))

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# Security Configuration
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

# Metadata Defaults
DEFAULT_METADATA = {
    "version": "1.0",
    "effective_date": "2024-01-01",
    "is_archived": False,
    "embedding_model": EMBEDDING_MODEL
}

def get_embedding_model(model_key: str = None) -> str:
    """
    Get embedding model by key or return default
    
    Args:
        model_key: Key from EMBEDDING_MODELS dict or direct model name
        
    Returns:
        Model name/path for sentence-transformers
    """
    if model_key is None:
        return EMBEDDING_MODEL
    
    # Check if it's a predefined key
    if model_key in EMBEDDING_MODELS:
        return EMBEDDING_MODELS[model_key]
    
    # Return as-is (assume it's a direct model name)
    return model_key

def get_index_path(suffix: str = None) -> str:
    """
    Get index path with optional suffix for different embedding models
    
    Args:
        suffix: Optional suffix to add to index name
        
    Returns:
        Full path to index file
    """
    base_path = Path(INDEX_PATH)
    
    if suffix:
        # Insert suffix before .leann extension
        stem = base_path.stem
        suffix_path = base_path.with_name(f"{stem}_{suffix}")
        return str(suffix_path)
    
    return str(base_path)

# Model compatibility matrix
MODEL_COMPATIBILITY = {
    "medical": ["NeuML/pubmedbert-base-embeddings", "ibm-granite/granite-embedding-english-r2"],
    "general": ["facebook/contriever", "sentence-transformers/all-MiniLM-L6-v2"],
    "enterprise": ["ibm-granite/granite-embedding-english-r2"]
}

# Transparency Infrastructure Configuration
TRANSPARENCY_ENABLED = os.getenv("TRANSPARENCY_ENABLED", "true").lower() == "true"
TRANSPARENCY_LEVEL = os.getenv("TRANSPARENCY_LEVEL", "comprehensive")  # basic, standard, comprehensive
EXPLAINABILITY_TARGET = float(os.getenv("EXPLAINABILITY_TARGET", "0.95"))  # 95% target
USER_COMPREHENSION_TARGET = float(os.getenv("USER_COMPREHENSION_TARGET", "0.80"))  # 80% target
AUDIT_COMPLETENESS_TARGET = float(os.getenv("AUDIT_COMPLETENESS_TARGET", "1.00"))  # 100% target

# Audit Logging Configuration
AUDIT_LOG_LEVEL = os.getenv("AUDIT_LOG_LEVEL", "medium")  # trace, low, medium, high, critical
AUDIT_STORAGE_BACKEND = os.getenv("AUDIT_STORAGE_BACKEND", "hybrid")  # database, file, hybrid
AUDIT_RETENTION_DAYS = int(os.getenv("AUDIT_RETENTION_DAYS", "365"))

# Session Management Configuration
SESSION_TIMEOUT_MINUTES = int(os.getenv("SESSION_TIMEOUT_MINUTES", "30"))
MAX_CONCURRENT_SESSIONS = int(os.getenv("MAX_CONCURRENT_SESSIONS", "1000"))

# Compliance Configuration
DEFAULT_COMPLIANCE_FRAMEWORKS = os.getenv("DEFAULT_COMPLIANCE_FRAMEWORKS", "GDPR,HIPAA,ISO27001").split(",")
COMPLIANCE_REPORTING_ENABLED = os.getenv("COMPLIANCE_REPORTING_ENABLED", "true").lower() == "true"
AUTO_COMPLIANCE_VALIDATION = os.getenv("AUTO_COMPLIANCE_VALIDATION", "true").lower() == "true"

# Explainable AI Configuration
DEFAULT_USER_PERSONA = os.getenv("DEFAULT_USER_PERSONA", "general_public")
DEFAULT_EXPLANATION_COMPLEXITY = os.getenv("DEFAULT_EXPLANATION_COMPLEXITY", "adaptive")
EXPLANATION_CACHING_ENABLED = os.getenv("EXPLANATION_CACHING_ENABLED", "true").lower() == "true"

# Environment-specific overrides
if os.getenv("ENVIRONMENT") == "development":
    # Use lighter model for faster development
    EMBEDDING_MODEL = EMBEDDING_MODELS["minilm"] if "EMBEDDING_MODEL" not in os.environ else EMBEDDING_MODEL
    DEEPCONF_ENABLED = False
    # Reduced transparency overhead in development
    TRANSPARENCY_LEVEL = "standard"
    AUDIT_LOG_LEVEL = "medium"

elif os.getenv("ENVIRONMENT") == "production":
    # Ensure production uses enterprise-grade model
    if EMBEDDING_MODEL not in MODEL_COMPATIBILITY["enterprise"]:
        print(f"Warning: Production should use enterprise model. Current: {EMBEDDING_MODEL}")
    
    # Full transparency in production
    TRANSPARENCY_ENABLED = True
    TRANSPARENCY_LEVEL = "comprehensive"
    AUDIT_LOG_LEVEL = "high"
    AUTO_COMPLIANCE_VALIDATION = True