# Pre-Commit Checklist - RoT Reasoning Server v0.2.0

**IMPORTANT**: Complete ALL items before committing to git/GitHub

**Date**: January 24, 2026
**Version**: v0.2.0

---

## 1. Code Quality & Testing

### Tests Passing

- [ ] **Standalone test passes**
  ```bash
  cd src
  python3 rot_reasoning.py --test
  # Expected: "Core tests passed! ✅"
  ```

- [ ] **No import errors**
  ```bash
  python3 -c "
  from rot_reasoning import get_rot_compressor
  from model_manager import RoTModelManager
  from rot_compressor import RoTCompressor
  print('All imports OK ✅')
  "
  ```

- [ ] **All Python files have no syntax errors**
  ```bash
  cd ../
  python3 -m py_compile src/*.py
  ```

- [ ] **Unit tests pass** (if applicable)
  ```bash
  pytest tests/ -v
  # OK if tests don't exist yet
  ```

---

## 2. Dependencies & Environment

### uv Setup

- [ ] **pyproject.toml exists and valid**
  ```bash
  cat pyproject.toml | grep "name = \"rot-reasoning-server\""
  ```

- [ ] **uv sync works**
  ```bash
  uv sync
  # Should complete without errors
  ```

- [ ] **.python-version file exists**
  ```bash
  cat .python-version
  # Should show: 3.11
  ```

### requirements.txt

- [ ] **requirements.txt is up to date**
  ```bash
  cat requirements.txt | grep "fastmcp>=2.0.0"
  ```

### Docker

- [ ] **Dockerfile builds successfully**
  ```bash
  docker build -t rot-reasoning-server:test .
  # Optional if not using Docker
  ```

- [ ] **docker-compose.yml valid**
  ```bash
  docker-compose config
  # Optional if not using Docker
  ```

---

## 3. Documentation Complete

### Required Documentation

- [ ] **README.md** - User guide exists and up to date
  ```bash
  ls -lh README.md
  ```

- [ ] **INSTALL.md** - Installation guide complete
  ```bash
  grep "Installation Steps" INSTALL.md
  ```

- [ ] **INSTALL_CHECKLIST.md** - Step-by-step checklist
  ```bash
  grep "Installation Steps" INSTALL_CHECKLIST.md
  ```

- [ ] **MODEL_SETUP.md** - LLM onboarding guide
  ```bash
  grep "Model Requirements" MODEL_SETUP.md
  ```

- [ ] **FIXES.md** - Fix log from v0.1.0
  ```bash
  grep "Fix #1" FIXES.md
  ```

- [ ] **GIT_SETUP.md** - Git/GitHub instructions
  ```bash
  grep "Pre-Commit Checklist" GIT_SETUP.md
  ```

- [ ] **IMPLEMENTATION_STATUS.md** - Current status
  ```bash
  grep "v0.2.0" IMPLEMENTATION_STATUS.md
  ```

### Documentation Quality

- [ ] All links work (no broken references)
- [ ] Code examples are correct
- [ ] Version numbers consistent (v0.2.0)
- [ ] No TODO markers left uncommented
- [ ] Markdown formatting valid

---

## 4. Git Configuration

### .gitignore Setup

- [ ] **.gitignore exists**
  ```bash
  cat .gitignore | head -10
  ```

- [ ] **Large files excluded**
  ```bash
  git check-ignore checkpoints/test.pt
  # Should output: checkpoints/test.pt
  ```

- [ ] **Virtual environment excluded**
  ```bash
  git check-ignore venv/
  # Should output: venv/
  ```

- [ ] **Cache directories excluded**
  ```bash
  git check-ignore .cache/
  # Should output: .cache/
  ```

- [ ] **Environment files excluded**
  ```bash
  git check-ignore .env
  # Should output: .env
  ```

### Git Status Check

- [ ] **No unintended files staged**
  ```bash
  git status
  # Review all staged files carefully
  ```

- [ ] **No large files in commit** (>100MB)
  ```bash
  git diff --cached --stat | awk '{print $1}' | xargs -I {} du -h {} | sort -hr | head
  ```

- [ ] **No binary files committed** (except necessary ones)
  ```bash
  git diff --cached --numstat | grep "^-"
  ```

---

## 5. Security & Secrets

### No Secrets in Code

- [ ] **No API keys**
  ```bash
  git diff --cached | grep -i "api_key\|api-key"
  # Should return nothing
  ```

- [ ] **No tokens**
  ```bash
  git diff --cached | grep -i "token\|bearer"
  # Should return nothing
  ```

- [ ] **No passwords**
  ```bash
  git diff --cached | grep -i "password\|passwd"
  # Should return nothing
  ```

- [ ] **No HuggingFace tokens**
  ```bash
  git diff --cached | grep "hf_"
  # Should return nothing
  ```

- [ ] **.env files not committed**
  ```bash
  git ls-files | grep ".env"
  # Should return nothing
  ```

### Sensitive File Check

- [ ] No `secrets/` directory committed
- [ ] No `*.pem`, `*.key` files committed
- [ ] No `credentials.json` files committed

---

## 6. File Structure Verification

### Required Files Present

```bash
# Check all required files exist
ls -1 | grep -E "^(src|tests|examples|pyproject.toml|requirements.txt|Dockerfile|README.md|INSTALL.md)$"
```

- [ ] `src/` directory with all Python files
- [ ] `tests/` directory (even if empty)
- [ ] `examples/` directory with YAML files
- [ ] `pyproject.toml`
- [ ] `requirements.txt`
- [ ] `.python-version`
- [ ] `Dockerfile`
- [ ] `docker-compose.yml`
- [ ] `.dockerignore`
- [ ] `setup_venv.sh` (executable)
- [ ] `.gitignore`
- [ ] `parameter.yaml`
- [ ] `README.md`
- [ ] `INSTALL.md`
- [ ] `INSTALL_CHECKLIST.md`
- [ ] `MODEL_SETUP.md`
- [ ] `FIXES.md`
- [ ] `GIT_SETUP.md`
- [ ] `IMPLEMENTATION_STATUS.md`
- [ ] `PRE_COMMIT_CHECKLIST.md` (this file)

### Files NOT Present (Should Be Ignored)

- [ ] No `venv/` directory
- [ ] No `__pycache__/` directories
- [ ] No `checkpoints/` with model files
- [ ] No `.cache/` directories
- [ ] No `*.pyc` files
- [ ] No `.env` files
- [ ] No large `*.pt`, `*.pth`, `*.bin` files

---

## 7. Code Quality Standards

### Python Code

- [ ] **No syntax errors**
  ```bash
  python3 -m py_compile src/*.py
  ```

- [ ] **Imports organized** (standard, third-party, local)
- [ ] **No unused imports** (run ruff if available)
  ```bash
  ruff check src/ || echo "ruff not installed (optional)"
  ```

- [ ] **Docstrings present** for public functions
- [ ] **Type hints added** where appropriate

### Code Style

- [ ] Consistent indentation (4 spaces)
- [ ] Line length ≤ 120 characters (recommended)
- [ ] No trailing whitespace
- [ ] Files end with newline

---

## 8. Functionality Verification

### Server Startup

- [ ] **Server can start**
  ```bash
  cd src
  timeout 5 python3 rot_reasoning.py --port 8000 || echo "Startup OK (timeout expected)"
  ```

### Import Chain

- [ ] **Local UltraRAG detected**
  ```bash
  python3 rot_reasoning.py --test 2>&1 | grep "Using local UltraRAG: True"
  ```

### Configuration Valid

- [ ] **parameter.yaml loads**
  ```bash
  python3 -c "
  import yaml
  with open('../parameter.yaml') as f:
      config = yaml.safe_load(f)
  assert 'checkpoint_path' in config
  print('Config valid ✅')
  "
  ```

---

## 9. Version Control

### Commit Message Ready

- [ ] Commit message drafted (descriptive, clear)
- [ ] Follows format: `<type>: <subject>`
- [ ] Includes Co-Authored-By for Claude
- [ ] References related issues (if any)

### Branch Status

- [ ] On correct branch (main or feature branch)
  ```bash
  git branch --show-current
  ```

- [ ] No uncommitted changes (after staging)
  ```bash
  git status --short
  # Should show only staged files (green)
  ```

---

## 10. Final Checks

### Build Verification

- [ ] **Fresh install works**
  ```bash
  # In a clean directory
  rm -rf venv/
  uv sync
  uv run python src/rot_reasoning.py --test
  # Should complete successfully
  ```

- [ ] **Docker build works** (if using Docker)
  ```bash
  docker build -t rot-reasoning-server:v0.2.0 .
  docker run rot-reasoning-server:v0.2.0 --test
  ```

### Documentation Links

- [ ] All internal links work (README.md → INSTALL.md, etc.)
- [ ] No broken references to files
- [ ] External links accessible (optional check)

### Team Review (Optional)

- [ ] Code reviewed by peer
- [ ] Architecture approved
- [ ] Breaking changes documented
- [ ] Migration guide provided (if needed)

---

## Commit Command

Once all checkboxes complete:

```bash
git add .
git status  # Final review

git commit -m "Add RoT Reasoning Server v0.2.0 - Fixed standalone version

- Fixed all import errors from v0.1.0
- Added uv/venv support with pyproject.toml
- Created comprehensive installation documentation
- Added Docker and docker-compose setup
- Added MODEL_SETUP.md for LLM onboarding
- Added INSTALL_CHECKLIST.md for step-by-step setup
- Server now truly standalone (no external repos needed)

Fixes:
- Missing fastmcp dependency
- Relative import errors in 5 files
- Missing cot_compressor.py
- Local UltraRAG import path
- Decorated function testing

Tests: 2/2 core tests passing
Status: Ready for production (pending model training)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

git push origin main
```

---

## Post-Commit

- [ ] Push successful
- [ ] GitHub repository updated
- [ ] Create release (v0.2.0-rot-server)
- [ ] Tag created and pushed
- [ ] CI/CD pipeline passing (if configured)
- [ ] Documentation visible on GitHub

---

## Rollback Plan (If Issues Found)

If critical issues discovered after push:

```bash
# Revert last commit (local only)
git reset --soft HEAD~1

# Revert and keep changes
git reset HEAD~1

# Force revert (if already pushed)
git revert HEAD
git push origin main
```

---

## Summary Checklist

Quick verification before commit:

- [ ] ✅ Tests pass
- [ ] ✅ No import errors
- [ ] ✅ Documentation complete
- [ ] ✅ .gitignore configured
- [ ] ✅ No secrets in code
- [ ] ✅ No large files
- [ ] ✅ All required files present
- [ ] ✅ Fresh install works
- [ ] ✅ Commit message ready

**Total items**: 100+ checks
**Estimated time**: 30-45 minutes for thorough review

---

**If ALL items checked: READY TO COMMIT! 🎉**

**If ANY items unchecked: Address before committing.**

---

**Last Updated**: January 24, 2026
**Version**: v0.2.0
**Status**: Ready for Final Review
