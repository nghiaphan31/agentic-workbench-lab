# Honor Rules Enforcement Plan

**Document ID:** HONOR-RULES-ENFORCEMENT-PLAN  
**Version:** 1.0  
**Created:** 2026-04-26  
**Status:** ACTIVE  
**Classification:** Internal — Workbench Governance  
**Author:** Code Agent  

---

## 1. Overview

This document provides concrete enforcement mechanisms for 6 rules currently classified as "HONOR" (agent self-compliance only) or "WARNED" (detection without blocking). Each rule is analyzed with:

1. **Current Gap** — Why the rule remains honor-only
2. **Proposed Mechanism** — How to make it enforceable
3. **Implementation Steps** — Concrete code/hook changes required
4. **Trigger Point** — When enforcement executes
5. **Difficulty** — Estimated implementation complexity

---

## 2. Rule-by-Rule Enforcement Plans

---

### Rule 2.1: FOR-1(1) — Self-Declaring Completion

**Original Rule:** Agent must not self-declare GREEN without Arbiter confirmation

| Field | Value |
|-------|-------|
| **Current Status** | WARNED |
| **Current Mechanism** | `check_forbidden_self_declaration()` at Session Start |
| **Gap Severity** | HIGH |

#### 2.1.1 Current Gap

The `check_forbidden_self_declaration()` function only scans `handoff-state.md` for completion markers and warns if found while state is not GREEN/MERGED/INIT. This is a heuristic check that:
- Cannot distinguish between "claiming completion" vs "reporting Arbiter-confirmed GREEN"
- Does not verify state transitions came from `test_orchestrator.py`
- Relies on pattern matching in text files rather than state machine validation

#### 2.1.2 Proposed Mechanism

**Cryptographic State Transition Attribution (CSTA)**

1. `test_orchestrator.py` signs state transitions with a workspace private key
2. `state.json` stores transition signatures in `transition_signatures[]`
3. Pre-commit hook validates signature chain before allowing merge to `develop`
4. `check_feature_green_from_arbiter()` verifies signature authorship

**Key Properties:**
- Only `test_orchestrator.py` holds the signing key
- State transitions are attributed and non-repudiable
- Agent cannot forge Arbiter confirmation

#### 2.1.3 Implementation Steps

1. **Key Management (Day 1)**
   ```
   .workbench/keys/
   ├── arbiter_private.pem  (0600, git-ignored)
   └── arbiter_public.pem   (0644, in repo)
   ```
   Generate Ed25519 key pair. Private key stays in `.workbench/keys/`.

2. **Signed State Transitions (Day 1)**
   Modify `test_orchestrator.py`:
   ```python
   # After each Phase 2 pass, sign the state transition
   def sign_state_transition(feature_id: str, old_state: str, new_state: str) -> str:
       """Sign a state transition with arbiter private key."""
       import json
       import ed25519
       from datetime import datetime, timezone
      
       payload = json.dumps({
           "feature_id": feature_id,
           "old_state": old_state,
           "new_state": new_state,
           "timestamp": datetime.now(timezone.utc).isoformat()
       }, sort_keys=True)
      
       with open(".workbench/keys/arbiter_private.pem", "rb") as f:
           private_key = ed25519.SigningKey(f.read())
       signature = private_key.sign(payload.encode())
      
       return signature.hex()
   ```

3. **State JSON Schema Update (Day 1)**
   Add to `state.json`:
   ```json
   {
     "transition_signatures": [
       {
         "feature_id": "REQ-042",
         "old_state": "RED",
         "new_state": "GREEN",
         "signature": "abc123...",
         "timestamp": "2026-04-26T07:00:00Z"
       }
     ]
   }
   ```

4. **Verification Function (Day 2)**
   Add to `arbiter_check.py`:
   ```python
   def check_feature_green_from_arbiter(feature_id: str, expected_state: str) -> tuple[bool, str]:
       """
       Verify feature reached expected_state via Arbiter (test_orchestrator) signature.
       Returns (is_valid, reason).
       """
       state = load_state_json()
       sigs = state.get("transition_signatures", [])
       feature_sigs = [s for s in sigs if s["feature_id"] == feature_id]
      
       if not feature_sigs:
           return False, f"No signature found for {feature_id}"
      
       latest = max(feature_sigs, key=lambda s: s["timestamp"])
       if latest["new_state"] != expected_state:
           return False, f"Latest state for {feature_id} is {latest['new_state']}, not {expected_state}"
      
       # Verify signature
       with open(".workbench/keys/arbiter_public.pem", "rb") as f:
           public_key = ed25519.VerifyingKey(f.read())
       try:
           payload = json.dumps({
               "feature_id": latest["feature_id"],
               "old_state": latest["old_state"],
               "new_state": latest["new_state"],
               "timestamp": latest["timestamp"]
           }, sort_keys=True)
           public_key.verify(latest["signature"].encode(), payload.encode())
           return True, f"Valid Arbiter signature for {feature_id} → {expected_state}"
       except Exception as e:
           return False, f"Signature verification failed: {e}"
   ```

5. **Pre-Merge Hook Validation (Day 2)**
   Modify `pre-push` hook to verify feature branch merges include valid signature.

6. **Startup Protocol Update (Day 3)**
   Update `check-session` to call `check_feature_green_from_arbiter()` for active feature.

#### 2.1.4 Trigger Point

- **Pre-Merge (Feature → develop):** Primary enforcement when feature branch is merged
- **Session Start:** Optional verification of active feature state attribution
- **On-Demand:** Human can invoke via `workbench-cli.py verify-green REQ-NNN`

#### 2.1.5 Difficulty

| Aspect | Difficulty | Notes |
|--------|------------|-------|
| Key generation | LOW | Single `openssl ecparam` command |
| Signing logic | MEDIUM | Requires ed25519 library integration |
| State schema change | LOW | Additive JSON field |
| Verification function | MEDIUM | Requires signature validation |
| Pre-merge hook | MEDIUM | New validation section |
| **Overall** | **MEDIUM** | 6–8 hours estimated |

---

### Rule 2.2: FOR-1(4) — Skipping Phase 2 Regression

**Original Rule:** Cannot force agent to run full test suite

| Field | Value |
|-------|-------|
| **Current Status** | ENFORCED (via test_orchestrator.py) |
| **Current Mechanism** | `test_orchestrator.py` enforces two-phase loop internally |
| **Gap Severity** | MEDIUM |

#### 2.2.1 Current Gap

`test_orchestrator.py` internally enforces Phase 1 → Phase 2, but:
- Agent can bypass by never running `test_orchestrator.py`
- Agent could claim "Phase 2 passed" without evidence
- No proof of `--full-suite` flag usage stored
- `regression_state` in `state.json` can be set by agent directly

The rule assumes the agent will invoke the test orchestrator. If the agent never calls it, Phase 2 is effectively skipped.

#### 2.2.2 Proposed Mechanism

**Test Execution Evidence Seal (TEES)**

1. `test_orchestrator.py` writes a signed evidence token to `.workbench/test_evidence/` after each Phase 2 run
2. Token includes: commit hash, timestamp, test counts, pass/fail results
3. Post-commit hook verifies Phase 2 evidence exists for staged changes
4. Evidence tokens are immutable (append-only directory)

#### 2.2.3 Implementation Steps

1. **Evidence Directory Structure (Day 1)**
   ```
   .workbench/test_evidence/
   ├── manifest.jsonl  (append-only log)
   └── seals/
       └── {commit_hash}.seal  (individual evidence files)
   ```

2. **Evidence Seal Structure (Day 1)**
   ```json
   {
     "commit_hash": "abc123def456",
     "phase": "phase2",
     "timestamp": "2026-04-26T07:00:00Z",
     "tests_run": 247,
     "tests_passed": 247,
     "tests_failed": 0,
     "duration_seconds": 423,
     "signature": "abc123..."
   }
   ```

3. **Modify test_orchestrator.py (Day 1)**
   After Phase 2 completes successfully:
   ```python
   def write_phase2_seal(commit_hash: str, test_results: dict):
       """Write signed evidence seal for Phase 2 completion."""
       import hashlib
      
       seal = {
           "commit_hash": commit_hash,
           "phase": "phase2",
           "timestamp": datetime.now(timezone.utc).isoformat(),
           "tests_run": test_results["run"],
           "tests_passed": test_results["passed"],
           "tests_failed": test_results["failed"],
           "duration_seconds": test_results["duration"]
       }
      
       # Create deterministic payload for signing
       payload = json.dumps(seal, sort_keys=True)
       seal["payload_hash"] = hashlib.sha256(payload.encode()).hexdigest()
       seal["signature"] = sign_payload(payload)  # Same CSTA signing as Rule 2.1
      
       # Write to immutable seal file
       seal_path = f".workbench/test_evidence/seals/{commit_hash}.seal"
       with open(seal_path, "w") as f:
           json.dump(seal, f, indent=2)
      
       # Append to manifest
       with open(".workbench/test_evidence/manifest.jsonl", "a") as f:
           f.write(json.dumps(seal) + "\n")
   ```

4. **Post-Commit Hook Validation (Day 2)**
   Modify `.workbench/hooks/post-commit`:
   ```python
   def check_phase2_evidence():
       """Verify Phase 2 evidence exists for the committed state."""
       import subprocess
      
       # Get current commit hash
       commit = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
       seal_path = f".workbench/test_evidence/seals/{commit}.seal"
      
       if not os.path.exists(seal_path):
           # Check manifest instead
           with open(".workbench/test_evidence/manifest.jsonl") as f:
               seals = [json.loads(line) for line in f]
           if not any(s["commit_hash"] == commit for s in seals):
               print("WARNING: No Phase 2 evidence for current commit")
               print("Run: workbench-cli.py run-tests --full-suite")
               return False
       return True
   ```

5. **Pre-Push Hook Enhancement (Day 2)**
   Block push if Phase 2 evidence missing for HEAD commit.

#### 2.2.4 Trigger Point

- **Post-Commit:** Verify evidence exists for committed state
- **Pre-Push:** Block if evidence missing for commits being pushed
- **On-Demand:** `workbench-cli.py verify-phase2 REQ-NNN`

#### 2.2.5 Difficulty

| Aspect | Difficulty | Notes |
|--------|------------|-------|
| Evidence directory | LOW | Simple file structure |
| Seal writing | LOW | JSON + signing |
| Post-commit check | MEDIUM | Git hook modification |
| Pre-push validation | MEDIUM | New section in pre-push |
| **Overall** | **MEDIUM** | 4–6 hours estimated |

---

### Rule 2.3: FOR-1(6) — Direct Cold Zone Access

**Original Rule:** Agent must not directly read `archive-cold/`

| Field | Value |
|-------|-------|
| **Current Status** | WARNED |
| **Current Mechanism** | `check_cold_zone_access()` scans git log for direct edits |
| **Gap Severity** | MEDIUM |

#### 2.3.1 Current Gap

`check_cold_zone_access()` is post-hoc detection:
- Only detects edits after they are committed
- Cannot prevent a determined agent from reading files directly
- Agent can still access `archive-cold/` via file system reads
- MEM-1 relies on `archive-query` MCP tool, but nothing blocks direct filesystem access

#### 2.3.2 Proposed Mechanism

**Filesystem Permission Lockdown (FPL)**

Apply Unix file permissions to make `archive-cold/` directly inaccessible:

```bash
chmod 000 memory-bank/archive-cold/
chmod 000 memory-bank/archive-cold/*
```

Combined with git note: the directory is owned by the archive-query MCP server exclusively.

**Additional Layer:** Git hook to detect and reject any commits modifying `archive-cold/`.

#### 2.3.3 Implementation Steps

1. **Permission Lockdown (Day 1)**
   Create `.workbench/scripts/cold_zone_lockdown.py`:
   ```python
   #!/usr/bin/env python3
   """Lock down Cold Zone to prevent direct access."""
   import os
   import stat
   
   def lockdown_cold_zone():
       cold_path = "memory-bank/archive-cold/"
       for root, dirs, files in os.walk(cold_path):
           # Lock the directory itself
           os.chmod(root, stat.S_IRUSR | stat.S_IXUSR)  # 0500
           for d in dirs:
               path = os.path.join(root, d)
               os.chmod(path, stat.S_IRUSR | stat.S_IXUSR)
           for f in files:
               path = os.path.join(root, f)
               os.chmod(path, stat.S_IRUSR)  # 0400
       
       print(f"Cold Zone locked: {cold_path}")
   
   if __name__ == "__main__":
       lockdown_cold_zone()
   ```

2. **Install Lockdown in Startup (Day 1)**
   Add to `arbiter_check.py check-session`:
   ```python
   def ensure_cold_zone_lockdown():
       """Ensure Cold Zone permissions prevent direct access."""
       import os
       cold_path = "memory-bank/archive-cold/"
       st = os.stat(cold_path)
       mode = st.st_mode & 0o777
       if mode & (stat.S_IWGRP | stat.S_IWOTH):
           lockdown_cold_zone()
           return False, "Cold Zone permissions fixed"
       return True, "Cold Zone locked"
   ```

3. **Pre-Commit Hook Enhancement (Day 2)**
   Add to `pre-commit`:
   ```python
   def check_cold_zone_not_staged():
       """Block commit if archive-cold/ files are staged."""
       import subprocess
       staged = subprocess.check_output(["git", "diff", "--cached", "--name-only"]).decode()
       cold_files = [f for f in staged.split() if f.startswith("memory-bank/archive-cold/")]
       if cold_files:
           print("ERROR: Cannot commit files in archive-cold/")
           print("Cold Zone access must go through archive-query MCP")
           return False
       return True
   ```

4. **Startup Verification (Day 1)**
   Add `ensure_cold_zone_lockdown()` to `check-session` CRITICAL checks.

#### 2.3.4 Trigger Point

- **Session Start:** Verify Cold Zone is locked
- **Pre-Commit:** Block any staged changes to `archive-cold/`
- **On-Demand:** `workbench-cli.py lockdown-cold-zone`

#### 2.3.5 Difficulty

| Aspect | Difficulty | Notes |
|--------|------------|-------|
| Permission lockdown | LOW | Simple chmod |
| Startup verification | LOW | Add to check-session |
| Pre-commit block | LOW | Filter staged files |
| **Overall** | **LOW** | 2–3 hours estimated |

---

### Rule 2.4: FOR-1(7) — Live API Imports from Non-MERGED Features

**Original Rule:** Agent must not import live APIs from non-MERGED features

| Field | Value |
|-------|-------|
| **Current Status** | WARNED |
| **Current Mechanism** | `check_live_imports_from_non_merged()` provides WARNING only |
| **Gap Severity** | HIGH |

#### 2.5.1 Current Gap

`check_live_imports_from_non_merged()` uses regex/grep-based scanning:
- Cannot perform true AST analysis
- Misses dynamic imports, `__import__()`, `importlib`
- Does not understand alias chains
- Only warns, does not block

#### 2.5.2 Proposed Mechanism

**Language-Specific AST Analysis at Commit Time (LAACT)**

Perform real AST parsing on staged source files:
- Python: Use `ast` module to parse and extract imports
- JavaScript/TypeScript: Use TypeScript Compiler API or SWC
- Block commit if imports reference non-MERGED feature modules

#### 2.5.3 Implementation Steps

1. **Python AST Analyzer (Day 1)**
   Add to `arbiter_check.py`:
   ```python
   import ast
   import os
   import subprocess
   
   def extract_python_imports(filepath: str) -> set[str]:
       """Extract all imported module names from a Python file using AST."""
       imports = set()
       try:
           with open(filepath) as f:
               tree = ast.parse(f.read(), filename=filepath)
           for node in ast.walk(tree):
               if isinstance(node, ast.Import):
                   for alias in node.names:
                       imports.add(alias.name.split('.')[0])
               elif isinstance(node, ast.ImportFrom):
                   if node.module:
                       imports.add(node.module.split('.')[0])
       except Exception as e:
           print(f"Warning: Could not parse {filepath}: {e}")
       return imports
   
   def check_no_live_imports(staged_files: list[str]) -> tuple[bool, list[str]]:
       """
       Check staged files for imports from non-MERGED features.
       Returns (is_safe, violations).
       """
       state = load_state_json()
       merged_features = {
           fid for fid, info in state["feature_registry"].items()
           if info.get("state") == "MERGED"
       }
       
       violations = []
       for filepath in staged_files:
           if filepath.endswith(".py"):
               file_imports = extract_python_imports(filepath)
               # Map imports to features (simplified - would need feature map)
               for imp in file_imports:
                   if imp.startswith("features/"):
                       feature_id = extract_feature_id(imp)
                       if feature_id and feature_id not in merged_features:
                           violations.append(f"{filepath}: imports {feature_id} (not MERGED)")
       
       return len(violations) == 0, violations
   ```

2. **Feature ID Extraction (Day 1)**
   Add helper to map import paths to feature IDs:
   ```python
   def extract_feature_id(import_path: str) -> str | None:
       """Extract REQ-NNN from import path like 'features.REQ-042.module'."""
       import re
       match = re.search(r'REQ-\d+', import_path)
       return match.group(0) if match else None
   ```

3. **Pre-Commit Hook Integration (Day 2)**
   Modify `.workbench/hooks/pre-commit`:
   ```python
   def check_import_gate():
       """Block commit if source files import from non-MERGED features."""
       import subprocess
       
       # Get staged source files
       staged_py = subprocess.check_output(
           ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"]
       ).decode().strip().split('\n')
       staged_py = [f for f in staged_py if f.endswith('.py') and f.startswith('src/')]
       
       if not staged_py:
           return True  # No source files staged
       
       is_safe, violations = check_no_live_imports(staged_py)
       if not is_safe:
           print("ERROR: Import gate violation")
           for v in violations:
               print(f"  {v}")
           print("\nCannot import from features with state != MERGED")
           return False
       return True
   ```

4. **JavaScript/TypeScript Support (Day 3)**
   Create separate analyzer using SWC or esbuild AST:
   ```python
   def extract_js_imports(filepath: str) -> set[str]:
       """Extract imports from JS/TS using esprima or SWC."""
       # Placeholder - requires npm dependency or subprocess call
       import subprocess
       result = subprocess.run(
           ["npx", "swc", "--filename", filepath, "-o", "/dev/null"],
           capture_output=True
       )
       # Parse AST output...
   ```

#### 2.5.4 Trigger Point

- **Pre-Commit:** Primary enforcement on source file commits
- **Session Start:** Optional scan of `src/` for regression

#### 2.5.5 Difficulty

| Aspect | Difficulty | Notes |
|--------|------------|-------|
| Python AST analysis | LOW | Built-in ast module |
| Import-to-feature mapping | MEDIUM | Requires feature path convention |
| Pre-commit integration | LOW | Add to pre-commit hook |
| JS/TS support | HIGH | Requires SWC/esbuild/npm |
| **Overall** | **MEDIUM-HIGH** | 8–12 hours estimated (Python only) |

---

### Rule 2.5: TRC-2 / FOR-1(7) — Duplicate Live Imports Rule

**Note:** TRC-2 and FOR-1(7) are effectively the same rule (no live imports from non-MERGED features). They are listed separately in `.clinerules` but should be unified into a single enforcement mechanism.

**Unified Mechanism:** LAACT (Language-specific AST Analysis at Commit Time) from Rule 2.4 above.

#### 2.5.1 Implementation Synergy

Rather than implementing separate mechanisms:
1. Implement LAACT once (Rule 2.4)
2. Apply to both TRC-2 and FOR-1(7) enforcement points
3. Single `check_import_gate()` function satisfies both rules

#### 2.5.2 Enforcement Points

| Rule | Current | Proposed |
|------|---------|----------|
| TRC-2 | On-Demand (WARNED) | Pre-Commit (BLOCKING) |
| FOR-1(7) | On-Demand (WARNED) | Pre-Commit (BLOCKING) |

---

### Rule 2.6: PVT-2 — Only Architect Initiates Stage 1 Pivot

**Original Rule:** Only Architect Agent may initiate pivot during Stage 1

| Field | Value |
|-------|-------|
| **Current Status** | WARNED |
| **Current Mechanism** | `check_pivot_mode()` with email heuristic detection |
| **Gap Severity** | HIGH |

#### 2.6.1 Current Gap

`check_pivot_mode()` uses git author email heuristics:
- Email pattern matching is brittle and spoofable
- Cannot truly verify agent identity
- Agent mode is not cryptographically bound to commits
- Heuristic can be bypassed by modifying git config

#### 2.6.2 Proposed Mechanism

**Cryptographic Mode Signing (CMS)**

1. Each mode (Architect, Developer, Test Engineer, etc.) has a mode-specific private key
2. Mode keys are stored in `.workbench/keys/modes/`
3. Commits include mode assertion via git notes or signed commit trailer
4. Pivot branch creation blocked without valid Architect signature

#### 2.6.3 Implementation Steps

1. **Mode Key Structure (Day 1)**
   ```
   .workbench/keys/modes/
   ├── architect_private.pem
   ├── architect_public.pem
   ├── developer_private.pem
   ├── developer_public.pem
   ├── test_engineer_private.pem
   ├── test_engineer_public.pem
   └── [other modes...]
   ```

2. **Mode Signing Function (Day 1)**
   Add to `arbiter_check.py`:
   ```python
   def sign_as_mode(mode: str, payload: str) -> str:
       """Sign payload as specific mode using mode's private key."""
       import ed25519
      
       mode_key_path = f".workbench/keys/modes/{mode}_private.pem"
       if not os.path.exists(mode_key_path):
           raise ValueError(f"No key found for mode: {mode}")
      
       with open(mode_key_path, "rb") as f:
           private_key = ed25519.SigningKey(f.read())
      
       signature = private_key.sign(payload.encode())
       return signature.hex()
   
   def verify_mode_signature(mode: str, payload: str, signature: str) -> bool:
       """Verify signature was created by specified mode."""
       import ed25519
      
       mode_pub_path = f".workbench/keys/modes/{mode}_public.pem"
       with open(mode_pub_path, "rb") as f:
           public_key = ed25519.VerifyingKey(f.read())
      
       try:
           public_key.verify(signature.encode(), payload.encode())
           return True
       except:
           return False
   ```

3. **Git Notes for Mode Assertion (Day 2)**
   On every commit, agent adds a signed git note:
   ```bash
   git notes add --force -m "mode-signature: <sig>\nmode: architect\ntimestamp: ..."
   ```

4. **Pivot Branch Detection (Day 2)**
   Add to `pre-commit` hook:
   ```python
   def check_pivot_mode_assertion():
       """Block pivot/* branch creation without valid Architect signature."""
       import subprocess
       
       branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).decode().strip()
       
       if branch.startswith("pivot/"):
           # Check for Architect signature in HEAD commit's notes
           notes = subprocess.check_output(["git", "notes", "show", "HEAD"]).decode()
           
           if "mode: architect" not in notes:
               print("ERROR: Pivot branch created without Architect mode assertion")
               print("Only Architect Agent may initiate pivot")
               return False
           
           # Verify signature
           # Extract and verify...
       
       return True
   ```

5. **Startup Protocol Mode Verification (Day 2)**
   Verify current session's mode identity against git config:
   ```python
   def verify_session_mode_against_gitconfig(expected_mode: str):
       """Verify agent's declared mode matches git author configuration."""
       import subprocess
       
       author = subprocess.check_output(["git", "config", "user.email"]).decode().strip()
       
       # Mode-specific email patterns
       mode_patterns = {
           "architect": r".*architect@.*",
           "developer": r".*developer@.*",
           "test-engineer": r".*test-engineer@.*",
       }
       
       pattern = mode_patterns.get(expected_mode, r".*")
       if not re.match(pattern, author):
           return False, f"Git author email does not match {expected_mode} pattern"
       
       return True, "Mode verified"
   ```

6. **Arbiter Enforcement (Day 3)**
   `arbiter_check.py` verifies on check-session:
   - Current branch is `pivot/*` → HEAD commit must have `mode: architect` note
   - Non-Arbiter modes attempting pivot → CRITICAL violation

#### 2.6.4 Trigger Point

- **Pre-Commit:** Block pivot branch creation without Architect signature
- **Session Start:** Verify mode identity against git author
- **Pre-Push:** Final validation before sharing work

#### 2.6.5 Difficulty

| Aspect | Difficulty | Notes |
|--------|------------|-------|
| Key structure | LOW | Multiple PEM files |
| Mode signing | MEDIUM | ed25519 integration |
| Git notes integration | MEDIUM | Git hook modifications |
| Pivot detection | LOW | Branch name pattern |
| Session verification | MEDIUM | Email pattern matching |
| **Overall** | **MEDIUM** | 10–14 hours estimated |

---

## 3. Implementation Priority Matrix

| Rule | Current Status | Proposed Status | Difficulty | Priority |
|------|---------------|-----------------|------------|----------|
| FOR-1(6) Cold Zone | WARNED | ENFORCED | LOW | **P0** — Fastest win |
| FOR-1(4) Phase 2 | ENFORCED* | ENFORCED+ | MEDIUM | **P1** — Evidence seal |
| FOR-1(1) Self-declare | WARNED | ENFORCED | MEDIUM | **P1** — CSTA |
| FOR-1(7)/TRC-2 Live imports | WARNED | ENFORCED | MEDIUM-HIGH | **P2** — LAACT |
| PVT-2 Pivot mode | WARNED | ENFORCED | MEDIUM | **P2** — CMS |

*test_orchestrator.py enforces internally but agent can bypass

---

## 4. Cross-Cutting Concerns

### 4.1 Key Management

All cryptographic mechanisms (CSTA, TEES, CMS) share the key infrastructure:
- `.workbench/keys/` directory
- Git-ignored (never committed)
- Ed25519 key pairs per purpose (Arbiter, test evidence, mode)
- Key rotation procedure TBD

### 4.2 Shared Libraries

Create shared signing/verification module:
```python
# .workbench/scripts/crypto_utils.py
"""Shared cryptographic utilities for enforcement mechanisms."""
```

### 4.3 Test Coverage

Each mechanism requires:
1. Unit tests for signing/verification
2. Integration tests for hook interactions
3. Failure mode tests (missing keys, invalid signatures)

---

## 5. Backward Compatibility

| Mechanism | Breaking Change? | Migration Path |
|-----------|------------------|----------------|
| CSTA (State signatures) | No | Additive JSON field, optional signing |
| TEES (Test evidence) | No | Append-only evidence directory |
| FPL (Permission lockdown) | **Yes** | `archive-query` MCP already enforces; permission lockdown is additional defense |
| LAACT (AST imports) | No | Stricter pre-commit validation |
| CMS (Mode signing) | No | Git notes are advisory; pivot detection still heuristic without notes |

---

## 6. Estimated Effort

| Rule | Days | Hours |
|------|------|-------|
| FOR-1(6) Cold Zone | 2 | 4–6 |
| FOR-1(4) Phase 2 | 3 | 8–12 |
| FOR-1(1) Self-declare | 4 | 12–16 |
| FOR-1(7)/TRC-2 Live imports | 4 | 12–16 |
| PVT-2 Pivot mode | 4 | 14–18 |
| **Total** | **17** | **50–68** |

---

## 7. Verification Checklist

After implementation, verify each rule:

- [ ] **FOR-1(1):** Feature merge blocked without valid Arbiter signature
- [ ] **FOR-1(4):** Phase 2 evidence seal exists for HEAD commit
- [ ] **FOR-1(6):** `ls -la memory-bank/archive-cold/` shows `d---------+`
- [ ] **FOR-1(7)/TRC-2:** Pre-commit blocked for Python file importing non-MERGED feature
- [ ] **PVT-2:** Pivot branch creation blocked without Architect note/signature

---

*Document generated: 2026-04-26*  
*Source: RULES_ENFORCEMENT_MATRIX.md, .clinerules v2.2-root*
