# Required Specifications Input Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Require specification data in the initial Skill request and restore strict complete-seven-image delivery.

**Architecture:** Remove the conditional waiting flag and metadata from the scaffold and validator. Keep the seventh asset and schema v2, while making every manifest asset follow the same strict completion path.

**Tech Stack:** Python 3 standard library, `unittest`, Markdown Skill instructions, YAML metadata.

---

### Task 1: Remove Conditional Waiting Behavior

**Files:**
- Modify: `tests/test_delivery_scripts.py`
- Modify: `scripts/create_delivery.py`
- Modify: `scripts/validate_delivery.py`

- [ ] Add tests that reject the removed CLI flag and reject legacy waiting metadata.
- [ ] Run the focused tests and confirm both fail against the old behavior.
- [ ] Remove the flag, conditional manifest fields, waiting validator branch, and conditional success output.
- [ ] Run all tests and confirm strict seven-image behavior.
- [ ] Commit the script and test changes.

### Task 2: Update Skill Instructions

**Files:**
- Modify: `SKILL.md`
- Modify: `README.md`
- Modify: `references/quality-checklist.md`

- [ ] Remove one-time questioning and partial-delivery instructions.
- [ ] State that callers provide dimensions in the initial request.
- [ ] State that all seven images are required for successful validation.
- [ ] Confirm no runtime documentation contains waiting-state language.
- [ ] Commit documentation changes.

### Task 3: Install and Publish

- [ ] Run the full test suite and official Skill validator.
- [ ] Sync runtime files to `/Users/mac/.codex/skills/generate-ecommerce-product-images/`.
- [ ] Confirm Codex `skills/list` loads the Skill with no errors.
- [ ] Merge to `main`, push GitHub, and confirm local and remote SHAs match.
