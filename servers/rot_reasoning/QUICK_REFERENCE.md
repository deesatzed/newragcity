# RoT Reasoning Server - Quick Reference Card

**Version**: v0.2.0 | **Status**: ✅ Ready for Git/GitHub | **Updated**: Jan 24, 2026

---

## ⚡ Quick Commands

### Test Server
```bash
cd servers/rot_reasoning/src
python3 rot_reasoning.py --test
```

### Install with uv (Fastest)
```bash
cd servers/rot_reasoning
uv sync
uv run python src/rot_reasoning.py --test
```

### Install with venv
```bash
cd servers/rot_reasoning
./setup_venv.sh
source venv/bin/activate
python src/rot_reasoning.py --test
```

### Install with Docker
```bash
cd servers/rot_reasoning
docker-compose up
```

---

## 📂 File Index

| File | Purpose | Lines |
|------|---------|-------|
| **Configuration** |
| `pyproject.toml` | uv package config | ~100 |
| `requirements.txt` | pip dependencies | ~25 |
| `parameter.yaml` | Server config | ~50 |
| `.gitignore` | Git exclusions | ~100 |
| **Docker** |
| `Dockerfile` | Container image | ~60 |
| `docker-compose.yml` | Orchestration | ~50 |
| `.dockerignore` | Build exclusions | ~80 |
| **Scripts** |
| `setup_venv.sh` | Venv automation | ~120 |
| **Documentation** | **~3,900 lines total** |
| `README.md` | Overview & quick start | ~500 |
| `INSTALL.md` | Installation guide | ~400 |
| `INSTALL_CHECKLIST.md` | Step-by-step checklist | ~450 |
| `MODEL_SETUP.md` | LLM onboarding | ~650 |
| `FIXES.md` | v0.2.0 fix log | ~550 |
| `GIT_SETUP.md` | Git/GitHub guide | ~500 |
| `PRE_COMMIT_CHECKLIST.md` | Pre-commit verification | ~450 |
| `IMPLEMENTATION_STATUS.md` | Status tracking | ~400 |
| `SETUP_COMPLETE.md` | Summary | ~400 |

---

## 🎯 Installation Paths

### Path 1: uv (30-60 min)
```
1. uv sync
2. Configure parameter.yaml
3. Download models (optional)
4. uv run python src/rot_reasoning.py --test
```

### Path 2: venv (40-75 min)
```
1. ./setup_venv.sh
2. source venv/bin/activate
3. Configure parameter.yaml
4. Download models (optional)
5. python src/rot_reasoning.py --test
```

### Path 3: Docker (35-70 min)
```
1. docker build -t rot-reasoning-server .
2. Configure parameter.yaml
3. docker-compose up
```

---

## 🔍 Troubleshooting Quick Lookup

| Error | Solution |
|-------|----------|
| `ModuleNotFoundError: fastmcp` | `uv sync` or `pip install fastmcp` |
| `attempted relative import` | Already fixed in v0.2.0 |
| `No module named 'ultrarag.server'` | Check local UltraRAG at `../../src/` |
| `CUDA out of memory` | Set `device: "cpu"` in parameter.yaml |
| Large files prevent push | Check `.gitignore`, remove with `git rm --cached` |

---

## 📋 Pre-Commit Quick Check

```bash
# Run tests
python src/rot_reasoning.py --test

# Check for secrets
git diff --cached | grep -i "api_key\|token"

# Verify .gitignore
git status --ignored | grep checkpoints

# Stage and commit
git add .
git commit -m "Your message"
git push origin main
```

---

## 🎓 Documentation Navigator

| Need | Read |
|------|------|
| **First time?** | [README.md](README.md) → [INSTALL_CHECKLIST.md](INSTALL_CHECKLIST.md) |
| **Installing?** | [INSTALL_CHECKLIST.md](INSTALL_CHECKLIST.md) |
| **Models?** | [MODEL_SETUP.md](MODEL_SETUP.md) |
| **What's fixed?** | [FIXES.md](FIXES.md) |
| **Before commit?** | [PRE_COMMIT_CHECKLIST.md](PRE_COMMIT_CHECKLIST.md) |
| **Git/GitHub?** | [GIT_SETUP.md](GIT_SETUP.md) |
| **Summary?** | [SETUP_COMPLETE.md](SETUP_COMPLETE.md) |

---

## ✅ Success Checklist

- [ ] Tests pass: `python src/rot_reasoning.py --test` → "Core tests passed! ✅"
- [ ] No imports errors
- [ ] Using local UltraRAG: True
- [ ] .gitignore working (checkpoints/ ignored)
- [ ] Documentation complete (9 files)
- [ ] Ready to commit

---

## 🚀 Next Steps

1. ✅ **Setup Complete** (You are here)
2. 📋 Run [PRE_COMMIT_CHECKLIST.md](PRE_COMMIT_CHECKLIST.md)
3. 💾 Commit: Follow [GIT_SETUP.md](GIT_SETUP.md)
4. 🌐 Push to GitHub
5. 🏷️ Create release (v0.2.0-rot-server)
6. 🤖 Train models (see MODEL_SETUP.md)

---

## 📊 Status at a Glance

```
┌────────────────────────────────────┐
│ RoT Reasoning Server v0.2.0        │
├────────────────────────────────────┤
│ ✅ Code: Working                   │
│ ✅ Tests: 2/2 passing              │
│ ✅ Docs: 9 files, ~3,900 lines     │
│ ✅ uv: Configured                  │
│ ✅ venv: Scripted                  │
│ ✅ Docker: Ready                   │
│ ✅ Git: .gitignore set             │
│ ⏳ Models: Guide provided          │
│ ⏳ Training: Plan documented       │
├────────────────────────────────────┤
│ Status: READY FOR GIT/GITHUB 🚀   │
└────────────────────────────────────┘
```

---

## 💡 Key Files to Remember

| Scenario | File |
|----------|------|
| Need to install? | `INSTALL_CHECKLIST.md` |
| Need models? | `MODEL_SETUP.md` |
| Before committing? | `PRE_COMMIT_CHECKLIST.md` |
| Pushing to GitHub? | `GIT_SETUP.md` |
| What's new? | `SETUP_COMPLETE.md` |

---

**Keep this card handy! Pin to top of directory.**

```bash
# Quick access
cat QUICK_REFERENCE.md
```

---

**Version**: v0.2.0 | **Last Updated**: Jan 24, 2026
