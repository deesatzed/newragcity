from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
from mlx_lm import load, generate
from mlx_lm.sample_utils import make_sampler
import mlx_lm
import re

app = FastAPI(
    title="HIPAA PHI Redaction API",
    description="Hybrid regex + MLX(Qwen3) PHI redaction with prompt testing",
    version="3.1.0"
)

# ----------------- Model -----------------
MODEL_ID = "Qwen/Qwen3-4B-MLX-4bit"
model, tokenizer = load(MODEL_ID)

# ----------------- Default system prompt (21 identifiers + local MRN rule) -----------------
DEFAULT_SYSTEM_PROMPT = """
You are an expert HIPAA-compliant PHI redaction engine.

Goal: Redact ALL PHI while preserving non-PHI text. Output ONLY the redacted text (no explanations, no <think>).

Redaction tags:
- Names → [REDACTED NAME]
- Addresses below state → [REDACTED ADDRESS]
- Dates (admission/discharge/visit, etc.) → [REDACTED DATE]; if explicitly a DOB → [REDACTED DOB]
- Phone → [REDACTED PHONE]; Fax → [REDACTED FAX]
- Email → [REDACTED EMAIL]
- SSN → [REDACTED SSN]
- MRN → [REDACTED MRN]
- Health plan / insurance / account / group / certificate / license / vehicle / device IDs → [REDACTED ID]
- URLs → [REDACTED URL]; IPs → [REDACTED IP]
- Biometrics → [REDACTED BIOMETRIC]; Full-face photos → [REDACTED PHOTO]
- Employer names → [REDACTED EMPLOYER]
- DEA / NPI → [REDACTED ID]

Local institution rule:
- MRN format is an 'e' followed by 4–8 digits (e.g., e47576). Ensure these are [REDACTED MRN].

Minimize false positives:
- Do NOT redact month words alone (e.g., “May”).
- Do NOT redact city names unless clearly part of a street/city/ZIP address.
- Do NOT redact ordinary numbers unless they match an identifier format.
- Do NOT redact clinical terms, medications, or measurements.

Return ONLY the redacted text.
"""

# ----------------- Schemas -----------------
class RedactRequest(BaseModel):
    text: str
    max_tokens: int = 2048
    temperature: float = 0.1
    top_p: float = 0.9
    # Optional prompt override per request
    system_prompt: Optional[str] = None
    # Toggle regex pre-pass
    use_regex_prepass: bool = True

class RedactResponse(BaseModel):
    redacted_text: str

class BatchCase(BaseModel):
    # A single test run: optional system prompt override
    system_prompt: Optional[str] = None
    temperature: float = 0.1
    top_p: float = 0.9

class RedactBatchRequest(BaseModel):
    text: str
    max_tokens: int = 2048
    use_regex_prepass: bool = True
    cases: List[BatchCase]

class RedactBatchResult(BaseModel):
    system_prompt_used: str
    temperature: float
    top_p: float
    redacted_text: str

class RedactBatchResponse(BaseModel):
    results: List[RedactBatchResult]

class HealthResponse(BaseModel):
    status: str
    model_id: str
    mlx_version: str

# ----------------- Regex pre-pass (deterministic PHI) -----------------
PHONE_RE = re.compile(
    r"""(?ix)
    (?:\+?1[\s.-]?)?
    (?:\(?\d{3}\)?|\d{3})[\s.-]?\d{3}[\s.-]?\d{4}
    """
)
DATE_SIMPLE_RE = re.compile(
    r"""(?x)
    \b(?:0?[1-9]|1[0-2])  # month 1-12
    [/\-]
    (?:0?[1-9]|[12]\d|3[01])  # day 1-31
    [/\-]
    (?:19|20)\d{2}\b
    """
)
DATE_RANGE_RE = re.compile(
    r"""(?x)
    \b
    (?:0?[1-9]|1[0-2])[/\-](?:0?[1-9]|[12]\d|3[01])[/\-](?:19|20)\d{2}
    \s*[-–]\s*
    (?:0?[1-9]|1[0-2])[/\-](?:0?[1-9]|[12]\d|3[01])[/\-](?:19|20)\d{2}
    \b
    """
)
MRN_RE = re.compile(r"\b[eE]\d{4,8}\b")

def regex_prepass(text: str) -> str:
    # Order matters: redact ranges before single dates
    text = DATE_RANGE_RE.sub("[REDACTED DATE]", text)
    text = DATE_SIMPLE_RE.sub("[REDACTED DATE]", text)
    text = PHONE_RE.sub("[REDACTED PHONE]", text)
    text = MRN_RE.sub("[REDACTED MRN]", text)
    return text

# ----------------- Output cleaning -----------------
THINK_BLOCK_RE = re.compile(r"<think>.*?</think>", flags=re.DOTALL)

def clean_output(output: str) -> str:
    cleaned = THINK_BLOCK_RE.sub("", output)
    return cleaned.replace("<|im_end|>", "").strip()

# ----------------- Core generate helper -----------------
def run_llm(system_prompt: str, user_text: str, max_tokens: int, temperature: float, top_p: float) -> str:
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_text},
    ]
    prompt = tokenizer.apply_chat_template(messages, add_generation_prompt=True, tokenize=False)
    sampler = make_sampler(temp=temperature, top_p=top_p)
    raw = generate(model, tokenizer, prompt, sampler=sampler, max_tokens=max_tokens, verbose=False)
    return clean_output(raw)

# ----------------- Endpoints -----------------
@app.post("/redact", response_model=RedactResponse)
def redact(req: RedactRequest):
    text = regex_prepass(req.text) if req.use_regex_prepass else req.text
    system_prompt = req.system_prompt or DEFAULT_SYSTEM_PROMPT
    out = run_llm(system_prompt, text, req.max_tokens, req.temperature, req.top_p)
    return RedactResponse(redacted_text=out)

@app.post("/redact_batch", response_model=RedactBatchResponse)
def redact_batch(req: RedactBatchRequest):
    base_text = regex_prepass(req.text) if req.use_regex_prepass else req.text
    results: List[RedactBatchResult] = []
    for case in req.cases:
        sp = case.system_prompt or DEFAULT_SYSTEM_PROMPT
        out = run_llm(sp, base_text, req.max_tokens, case.temperature, case.top_p)
        results.append(RedactBatchResult(
            system_prompt_used=("default" if case.system_prompt is None else "custom"),
            temperature=case.temperature,
            top_p=case.top_p,
            redacted_text=out
        ))
    return RedactBatchResponse(results=results)

@app.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(status="ok", model_id=MODEL_ID, mlx_version=mlx_lm.__version__)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server2:app", host="0.0.0.0", port=8588, reload=False)
