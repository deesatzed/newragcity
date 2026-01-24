# Execute: GitHub Update & Fresh Install Test

**Date**: January 24, 2026
**Status**: Ready to execute

---

## Quick Overview

This plan will:
1. ✅ Commit all changes to GitHub
2. ✅ Clone to fresh location
3. ✅ Test as new installation
4. ✅ Validate everything works

**Total time**: ~60-90 minutes

---

## Part 1: Commit to GitHub (15-30 minutes)

### Option A: Automated Script (Recommended)

```bash
cd /Volumes/WS4TB/newragcity/UltraRAG-main/servers/rot_reasoning

# Run automated commit script
./commit_to_github.sh

# Script will:
# 1. Run tests
# 2. Check for secrets
# 3. Stage files
# 4. Create commit
# 5. Push to GitHub
# 6. Optionally create tag
```

### Option B: Manual Commands

```bash
cd /Volumes/WS4TB/newragcity/UltraRAG-main

# 1. Run tests
cd servers/rot_reasoning/src
python3 rot_reasoning.py --test
cd ../../..

# 2. Stage files
git add servers/rot_reasoning/

# 3. Check status
git status

# 4. Commit
git commit -m "Add RoT Reasoning Server v0.2.0 - Production ready

[See commit_to_github.sh for full message]"

# 5. Push
git push origin main

# 6. Create tag (optional)
git tag -a v0.2.0-rot-server -m "RoT v0.2.0"
git push origin v0.2.0-rot-server
```

**Checkpoint**: ✅ Verify push succeeded on GitHub web interface

---

## Part 2: Fresh Clone (5 minutes)

```bash
# Create test directory (outside existing workspace)
mkdir -p ~/fresh_install_test
cd ~/fresh_install_test

# Clone from GitHub (replace YOUR_USERNAME)
git clone https://github.com/YOUR_USERNAME/UltraRAG.git fresh-ultrarag-test

# Navigate to RoT server
cd fresh-ultrarag-test/servers/rot_reasoning

# List files to verify
ls -la
# Should show: pyproject.toml, Dockerfile, *.md files, etc.
```

**Checkpoint**: ✅ All files present

---

## Part 3: Test Installation (30-60 minutes)

### Test Method 1: uv (Fastest)

```bash
# Ensure uv is installed
uv --version
# If not: curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Run tests
uv run python src/rot_reasoning.py --test

# Expected output:
# ============================================================
# Testing RoT Reasoning Server
# ============================================================
# Test 1: get_model_info()
# ✓ Model info: {...}
# Test 2: assess_complexity()
# ✓ Complexity: {...}
# Core tests passed! ✅
# ============================================================
```

**Success Criteria**:
- ✅ "Core tests passed! ✅" appears
- ✅ No import errors
- ✅ "Using local UltraRAG: True"

### Test Method 2: venv (Alternative)

```bash
# Run automated setup
./setup_venv.sh

# Activate venv
source venv/bin/activate

# Run tests
python src/rot_reasoning.py --test

# Deactivate when done
deactivate
```

### Test Method 3: Docker (Alternative)

```bash
# Build image
docker build -t rot-reasoning-server:test .

# Run tests
docker run --rm rot-reasoning-server:test
```

---

## Part 4: Document Results (10 minutes)

Create `FRESH_INSTALL_TEST_RESULTS.md` in the fresh clone:

```bash
cd ~/fresh_install_test/fresh-ultrarag-test/servers/rot_reasoning

cat > FRESH_INSTALL_TEST_RESULTS.md << 'EOF'
# Fresh Install Test Results

**Date**: $(date +%Y-%m-%d)
**Commit**: $(git rev-parse --short HEAD)
**Tester**: [Your Name]

## Test Environment
- OS: $(uname -s)
- Python: $(python3 --version)
- uv: $(uv --version 2>/dev/null || echo "Not used")

## Installation Test: uv
- Status: [PASS/FAIL]
- Time: [X minutes]
- Output:
```
[Paste test output]
```

## Issues Found
- [None / List any issues]

## Verdict
- [x] ✅ PASS - Ready for production
- [ ] ⚠️  PASS WITH NOTES
- [ ] ❌ FAIL

## Notes
[Any observations]
EOF

# Edit the file with actual results
vim FRESH_INSTALL_TEST_RESULTS.md
```

---

## Part 5: Report Back (5 minutes)

If tests pass:

```bash
# Copy results back to original repo (optional)
cp FRESH_INSTALL_TEST_RESULTS.md /Volumes/WS4TB/newragcity/UltraRAG-main/servers/rot_reasoning/

# Update IMPLEMENTATION_STATUS.md
cd /Volumes/WS4TB/newragcity/UltraRAG-main/servers/rot_reasoning

# Add to IMPLEMENTATION_STATUS.md:
# ## Fresh Install Validation
# - Date: [date]
# - Status: ✅ PASS
# - Method: uv
# - Time: [X] minutes
# - All tests passed on fresh clone
```

If tests fail:

1. Document all errors in FRESH_INSTALL_TEST_RESULTS.md
2. Fix issues in original repo
3. Commit fixes
4. Re-test

---

## Quick Command Summary

**Complete workflow in one go:**

```bash
# 1. Commit to GitHub
cd /Volumes/WS4TB/newragcity/UltraRAG-main/servers/rot_reasoning
./commit_to_github.sh

# 2. Fresh clone
mkdir -p ~/fresh_install_test && cd ~/fresh_install_test
git clone https://github.com/YOUR_USERNAME/UltraRAG.git fresh-test
cd fresh-test/servers/rot_reasoning

# 3. Test
uv sync
uv run python src/rot_reasoning.py --test

# 4. If tests pass - celebrate! 🎉
echo "✅ Fresh install validation PASSED!"

# 5. Cleanup (optional)
cd ~
rm -rf fresh_install_test/
```

---

## Expected Timeline

| Step | Time | Status |
|------|------|--------|
| Run commit script | 5 min | ⏳ |
| Push to GitHub | 2 min | ⏳ |
| Fresh clone | 3 min | ⏳ |
| uv sync (dependencies) | 10-20 min | ⏳ |
| Run tests | 2 min | ⏳ |
| Document results | 5 min | ⏳ |
| **Total** | **30-40 min** | ⏳ |

---

## Troubleshooting

### Issue: commit_to_github.sh fails

```bash
# Run steps manually
cd /Volumes/WS4TB/newragcity/UltraRAG-main
git add servers/rot_reasoning/
git commit -m "Add RoT v0.2.0"
git push origin main
```

### Issue: Fresh clone fails

```bash
# Check GitHub URL
git remote -v

# Try with https instead of ssh (or vice versa)
git clone https://github.com/YOUR_USERNAME/UltraRAG.git
```

### Issue: Tests fail in fresh clone

```bash
# Check if files are missing
ls -la src/
# Should have 8 .py files

# Check Python version
python3 --version
# Should be 3.11 or 3.12

# Try venv instead of uv
./setup_venv.sh
source venv/bin/activate
python src/rot_reasoning.py --test
```

---

## Success Indicators

You'll know it worked when:

1. ✅ GitHub shows your commit
2. ✅ Fresh clone has all files
3. ✅ Tests output: "Core tests passed! ✅"
4. ✅ No import errors
5. ✅ "Using local UltraRAG: True"

---

## What to Do After Success

1. ✅ **Update documentation** with actual test results
2. ✅ **Create GitHub release** (if not done by script)
3. ✅ **Clean up test directory** (optional)
4. ✅ **Proceed to model setup** (See MODEL_SETUP.md)
5. ✅ **Mark project as production ready**

---

## Ready to Execute?

**Pre-flight checklist:**
- [ ] All changes in `/Volumes/WS4TB/newragcity/UltraRAG-main/servers/rot_reasoning/`
- [ ] Tests pass locally: `python src/rot_reasoning.py --test`
- [ ] No uncommitted changes you want to keep
- [ ] GitHub credentials ready
- [ ] Internet connection stable
- [ ] 1 hour available for testing

**If all checked: Execute Part 1!**

```bash
cd /Volumes/WS4TB/newragcity/UltraRAG-main/servers/rot_reasoning
./commit_to_github.sh
```

---

**Last Updated**: January 24, 2026
**Status**: Ready to Execute
