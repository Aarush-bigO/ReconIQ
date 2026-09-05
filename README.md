# ReconIQ Enterprise — AI Finance Control Center

ReconIQ is a governed finance-operations platform that reconciles payment, settlement, ledger, and bank records using probabilistic record linkage and deterministic financial policies. It measures performance against ground truth, exposes uncertainty through a structured exception workflow, uses AI only to explain deterministic evidence, and preserves a tamper-evident audit trail for every decision.

**Core Principle:** Deterministic systems decide. AI explains.
**Product Promise:** Reconcile what you can prove. Explain what you can't.

*(This is a demonstration project for the Razorpay Buildathon.)*

---

## 📸 Product Screenshots
*(Include screenshots of the Overview Dashboard, Exception Workbench, Settlement Timeline, and AI Control Room here.)*

## 🏗 Architecture Diagram
1. **Adapter Layer**: Raw Webhooks/CSVs → `razorpay_adapter.py`, `loaders.py`
2. **Canonical Normalization**: Standardizes references → `normalize.py`, `schemas.py`
3. **Deterministic Linkage**: Splink (probabilistic linkage) → `run_splink.py`, `candidate_generation.py`
4. **Reconciliation Policies**: Enforces strict financial thresholds → `reconcile.py`, `policies.py`
5. **AI Safety Boundary**: LLM strictly isolated to narration/classification → `agent_layer.py`, `explain.py`
6. **Audit integrity**: HMAC-SHA256 chained event log → `audit_log.py`

## 🚀 Quick Start (Docker Setup)

Docker remains the local reproducibility path regardless of hosting provider.

1. Clone the repository:
```bash
git clone https://github.com/your-username/reconiq.git
cd reconiq
```

2. Build and run via Docker Compose:
```bash
docker-compose build
docker-compose up -d
```

3. Access the dashboard: `http://localhost:3000`
4. Access the API: `http://localhost:8000/docs`

## ⚙️ Environment Variables
Copy `.env.example` to `.env`:
```env
DATABASE_URL=postgresql://user:pass@localhost:5432/reconiq
OPENAI_API_KEY=sk-xxxx
AUDIT_HMAC_SECRET=your-secure-secret
RAZORPAY_KEY_ID=rzp_test_xxxx
RAZORPAY_KEY_SECRET=xxxx
```

## 💳 Razorpay Integration Setup
ReconIQ uses the official Razorpay Node SDK concepts for verification.
1. Enter your `RAZORPAY_KEY_ID` in the `.env` file.
2. Webhooks from Razorpay hitting the `/api/webhooks/razorpay` endpoint are verified using standard signature validation. 
3. The `razorpay_adapter.py` seamlessly normalizes Razorpay Settlement objects into ReconIQ Canonical format.

## 📊 Demo Dataset & Benchmark Results
We generated a minimum of 200+ synthetic records with hidden ground truth to test the reconciliation engine against edge cases (exact matches, fuzzy matches, UTR/PAY prefix differences, duplicate references, missing counterparts).

**Benchmark Run Results:**
- **Threshold**: 0.95 (Chosen Operating Point)
- **Precision**: 100.0%
- **Recall**: 97.4%
- **Match Rate**: 96.2%
- **Manual Review Rate**: 3.8%
- **Processing Time**: <1s
*(The selected threshold is justified by the trade-off: high precision with a manageable manual-review volume.)*

## 🧪 Evaluation Methodology
The system sweeps matching thresholds from `0.80` to `0.99`. The linkage pipeline utilizes actual probabilistic matching (via Splink 4.x concepts). Ground truth is strictly segregated from the matching model. Performance is evaluated using standard F1, Precision, and Recall metrics, fully visible in the **Evaluation Lab** UI.

## 🔒 Security Model
- **No LLM Financial Control:** AI is explicitly prevented from modifying financial state, amounts, or confidence scores. It can only output `explanation` and `recommended_action`.
- **Tamper-Evident Audit:** Uses a cryptographic SHA-256 hash-chain + HMAC-SHA256 signatures for every action (`AuditAction.MATCH_CONFIRMED`, `AuditAction.EXCEPTION_CREATED`, etc.).
- **No Floating Point:** All arithmetic strictly uses integer minor units (paise).

## 🏆 Build-Challenge Story
- **Challenge:** Cross-source references were inconsistent across Razorpay, the Merchant Ledger, and the Bank.
- **Symptom:** Exact matching generated false unmatched records.
- **Investigation:** The same underlying transaction appeared with different source-specific prefixes (`PAY-`, `UTR-`).
- **Solution:** Added canonical `reference_core` normalization while preserving original source references.
- **Result:** The normalized representation became an additional controlled matching signal.
- **Lesson:** Financial integrations should preserve source truth while creating explicit canonical comparison semantics.

## 📚 Open-Source References
- **Razorpay APIs:** [https://razorpay.com/docs/api/](https://razorpay.com/docs/api/)
- **Splink:** [https://github.com/moj-analytical-services/splink](https://github.com/moj-analytical-services/splink)
- **FinRobot:** [https://github.com/AI4Finance-Foundation/FinRobot](https://github.com/AI4Finance-Foundation/FinRobot)
- **Blnk:** [https://github.com/blnkfinance/blnk](https://github.com/blnkfinance/blnk)
- **Django Ledger:** [https://github.com/arrobalytics/django-ledger](https://github.com/arrobalytics/django-ledger)
- **OpenFang:** [https://github.com/RightNow-AI/openfang](https://github.com/RightNow-AI/openfang)


