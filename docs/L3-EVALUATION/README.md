# KCN L3 Evaluation Package — How to structure the audit

**Current maturity of the product:** L2 (internal evidence).  
**This folder:** the *protocol* for an independent L3 audit. Completing the folder does not grant L3; an unaffiliated evaluator must run it.

## One-sentence rule

L3 = sealed release + independent reproduce + independent falsify + published results — **per claim**.

## Package layout

```text
docs/L3-EVALUATION/
├── README.md                 (this file)
├── RELEASE/
│   ├── VERSION
│   ├── COMMIT_SHA
│   └── ARTIFACT_MANIFEST.md
├── CLAIMS/
│   ├── CLAIM_REGISTER.md
│   ├── NON_UPGRADE_RULE.md
│   └── MATURITY_RULES.md
├── REPRODUCTION/
│   ├── ENVIRONMENT.md
│   ├── BUILD.md
│   └── VERIFY.md
├── FALSIFICATION/
│   ├── F13_acceptance.md
│   ├── F14_watchdog_resume.md
│   └── BOUNDARY_MATRIX.md
└── EVALUATOR/
    ├── PROTOCOL.md
    ├── RESULT_TEMPLATE.md
    └── IMMUTABLE_LOG.md
```

## Process

1. Freeze: tag + commit SHA + this package hash  
2. Hand package to unaffiliated evaluator  
3. They build from pins only  
4. They run honest VERIFY  
5. They run F13/F14 and other falsification cases  
6. They record PASS/PARTIAL/FAIL per claim  
7. Publish report  
8. FAIL → keep v34/artifact; fix in new version

## Non-upgrade

BBS/ZK/ProofVerify PASS ≠ human authority.  
Agent + valid proof → acceptance/resume must still be **403**.
