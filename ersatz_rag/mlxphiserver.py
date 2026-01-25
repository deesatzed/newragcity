from typing import List, Literal, Optional, Any
from fastapi import FastAPI
from pydantic import BaseModel
from mlx_lm import load, generate
from mlx_lm.sample_utils import make_sampler

# ── FastAPI app ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="MLX PHI Redaction API",
    description="FastAPI service using MLX + Qwen3 for PHI redaction",
    version="1.0.0"
)

# ── Model load ───────────────────────────────────────────────────────────────
MODEL_ID = "Qwen/Qwen3-4B-MLX-4bit"
model, tokenizer = load(MODEL_ID)

# ── Default PHI Redaction System Prompt ──────────────────────────────────────
DEFAULT_SYSTEM_PROMPT = """You are an expert in protecting sensitive health information. Your task is to redact specific types of Protected Health Information (PHI) from a given medical note. Carefully examine the input and replace any occurrences of personal names, dates, addresses, phone/fax numbers, email addresses, and various unique numeric or alphanumeric identifiers such as Medical Record Numbers, Social Security Numbers, and Health Plan IDs.

For each type of PHI:
- Personal Names → [REDACTED NAME]
- Geographic Data → [REDACTED ADDRESS]
- Dates → [REDACTED DATE] (use [REDACTED DOB] for DOB)
- Phone/Fax → [REDACTED PHONE] / [REDACTED FAX]
- Email → [REDACTED EMAIL]
- SSN → [REDACTED SSN]
- MRN → [REDACTED MRN]
- Other IDs (health plan, accounts, license numbers, URLs, IPs) → [REDACTED ID]

Ensure all non-PHI content remains intact. Do not explain the redactions; output only the redacted note.
"""

# ── Schemas ───────────────────────────────────────────────────────────────────
class Message(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: str
    reasoning_content: Optional[str] = None
    tool_calls: Optional[List[Any]] = None

class ChatRequest(BaseModel):
    messages: Optional[List[Message]] = None
    prompt: Optional[str] = None
    system: Optional[str] = None
    tools: Optional[List[dict]] = None
    add_generation_prompt: bool = True
    max_tokens: int = 2048
    temperature: float = 0.2
    top_p: float = 0.9

class ChatResponse(BaseModel):
    text: str
    rendered_prompt: str

class HealthResponse(BaseModel):
    status: str
    model_id: str
    mlx_version: str

# ── Utilities ────────────────────────────────────────────────────────────────
def ensure_system_prompt(msgs: List[Message], system_text: str) -> List[Message]:
    """Ensure the system prompt is always the first message."""
    if not msgs:
        return [Message(role="system", content=system_text)]
    first = msgs[0]
    if first.role != "system":
        return [Message(role="system", content=system_text)] + msgs
    if not first.content.strip():
        msgs[0] = Message(role="system", content=system_text)
    return msgs

def strip_after_im_end(text: str) -> str:
    """Trim anything after the first <|im_end|> marker (Qwen-style chat templates)."""
    end_token = "<|im_end|>"
    if end_token in text:
        return text.split(end_token, 1)[0]
    return text

# ── Routes ───────────────────────────────────────────────────────────────────
@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    # Build messages list
    if req.messages:
        messages = req.messages
    elif req.prompt:
        messages = [Message(role="user", content=req.prompt)]
    else:
        return ChatResponse(text="", rendered_prompt="")

    # Inject system prompt if not provided
    system_prompt = req.system or DEFAULT_SYSTEM_PROMPT
    messages = ensure_system_prompt(messages, system_prompt)

    # Render chat template for Qwen3 MLX
    rendered_prompt = tokenizer.apply_chat_template(
        [m.model_dump() for m in messages],
        tools=req.tools,
        add_generation_prompt=req.add_generation_prompt,
        tokenize=False
    )

    # Configure sampler dynamically per request
    sampler = make_sampler(temp=req.temperature, top_p=req.top_p)

    # Generate redacted text using MLX
    out = generate(
        model,
        tokenizer,
        rendered_prompt,
        sampler=sampler,
        max_tokens=req.max_tokens,
        verbose=False
    )

    text = strip_after_im_end(out).strip()
    return ChatResponse(text=text, rendered_prompt=rendered_prompt)

@app.get("/health", response_model=HealthResponse)
def health():
    import mlx_lm
    return HealthResponse(
        status="ok",
        model_id=MODEL_ID,
        mlx_version=mlx_lm.__version__
    )

# ── Entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("mlxphiserver:app", host="0.0.0.0", port=8598, reload=False)
