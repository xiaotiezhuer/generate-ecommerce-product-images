# Specifications Image Implementation Plan

> Superseded by `2026-06-07-required-specifications-input.md`. The current workflow requires specification input in the initial request and a complete seven-image delivery.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a seventh specifications image to the default ecommerce set, with strict user-supplied data rules and a validated waiting-for-input fallback.

**Architecture:** Extend the existing manifest scaffold with one `specifications` asset per requested ratio and an explicit CLI flag for the one permitted incomplete state. Keep validation centralized in `validate_delivery.py`, where only a specification asset carrying the exact waiting metadata may omit its image; all other assets retain the current strict completion rules. Update the Skill instructions and prompt references so ImageGen creates the selected classic parameter-table layout without estimating facts.

**Tech Stack:** Python 3 standard library, `unittest`, Markdown Skill instructions, YAML UI metadata, Codex Skill validator.

---

## File Map

- `scripts/create_delivery.py`: define the seventh asset, CLI waiting flag, schema v2 manifest metadata.
- `scripts/validate_delivery.py`: recognize strict `awaiting-user-input` specification assets and report conditional completion.
- `tests/test_delivery_scripts.py`: executable contract for seven-image scaffolds and both validation success modes.
- `SKILL.md`: default seven-image workflow, one-time parameter question, factual constraints, and conditional delivery.
- `references/image-set-prompts.md`: dedicated ImageGen prompt for the classic specifications layout.
- `references/quality-checklist.md`: exact parameter, number, unit, annotation-line, and disclaimer checks.
- `references/product-fidelity.md`: classify uploaded specification/reference sheets separately from product identity images.
- `references/research-workflow.md`: update the visual brief from six to seven image responsibilities.
- `agents/openai.yaml`: advertise seven generated image categories.
- `README.md`: document the seventh image, parameter input, CLI flag, and output tree.
- `/Users/mac/.codex/skills/generate-ecommerce-product-images/`: receive a mechanical copy of the verified repository Skill files.

### Task 1: Define Seven-Asset Scaffold Behavior

**Files:**
- Modify: `tests/test_delivery_scripts.py`
- Modify: `scripts/create_delivery.py`

- [ ] **Step 1: Write failing scaffold tests**

Update the test helper so it can request the conditional state:

```python
def create_delivery(root, *ratios, specifications_awaiting_input=False):
    args = [root, "--product-name", "测试产品"]
    for ratio in ratios:
        args.extend(["--ratio", ratio])
    if specifications_awaiting_input:
        args.append("--specifications-awaiting-input")
    return run_script(CREATE_SCRIPT, *args)
```

Change the standard scaffold assertions to require:

```python
self.assertEqual(manifest["schema_version"], 2)
self.assertEqual(len(manifest["assets"]), 7)
self.assertEqual(
    manifest["assets"][-1]["filename"],
    "07-specifications-square.png",
)
self.assertEqual(manifest["assets"][-1]["type"], "specifications")
```

Change the extra-ratio expectation from 12 to 14 assets and add:

```python
self.assertIn("07-specifications-square.png", filenames)
self.assertIn("07-specifications-3x4.png", filenames)
```

Add:

```python
def test_marks_specifications_as_awaiting_user_input(self):
    with tempfile.TemporaryDirectory() as tmp:
        output = Path(tmp) / "delivery"

        result = create_delivery(
            output,
            specifications_awaiting_input=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        manifest = json.loads(
            (output / "manifest.json").read_text(encoding="utf-8")
        )
        specifications = manifest["assets"][-1]
        self.assertEqual(specifications["type"], "specifications")
        self.assertEqual(specifications["status"], "pending")
        self.assertEqual(
            specifications["availability"],
            "awaiting-user-input",
        )
        self.assertIn("等待用户提供规格参数", specifications["notes"])
```

- [ ] **Step 2: Run scaffold tests and verify RED**

Run:

```bash
python3 -m unittest \
  tests.test_delivery_scripts.CreateDeliveryTests -v
```

Expected: failures showing six assets, schema version 1, and an unrecognized `--specifications-awaiting-input` argument.

- [ ] **Step 3: Implement the seventh asset and CLI flag**

Extend `STANDARD_ASSETS`:

```python
STANDARD_ASSETS = [
    ("01-main", "main"),
    ("02-atmosphere", "atmosphere"),
    ("03-detail", "detail"),
    ("04-meaning-copy", "meaning-copy"),
    ("05-usage", "usage"),
    ("06-selling-points", "selling-points"),
    ("07-specifications", "specifications"),
]
```

Add the parser flag:

```python
parser.add_argument(
    "--specifications-awaiting-input",
    action="store_true",
    help=(
        "Mark specification images as waiting for user-supplied "
        "parameters instead of requiring generated files."
    ),
)
```

Change the manifest builder signature to:

```python
def build_manifest(product_name, ratios, specifications_awaiting_input=False):
```

For each asset, create the normal record and conditionally extend only specification records:

```python
asset = {
    "id": asset_id,
    "type": asset_type,
    "ratio": ratio,
    "ratio_width": ratio_width,
    "ratio_height": ratio_height,
    "filename": f"{asset_id}-{ratio}.png",
    "status": "pending",
    "fidelity": "A",
    "notes": [],
}
if asset_type == "specifications" and specifications_awaiting_input:
    asset["availability"] = "awaiting-user-input"
    asset["notes"].append("等待用户提供规格参数")
assets.append(asset)
```

Return `"schema_version": 2`, thread the boolean through `create_delivery`, and pass `args.specifications_awaiting_input` from `main`.

- [ ] **Step 4: Run scaffold tests and verify GREEN**

Run:

```bash
python3 -m unittest \
  tests.test_delivery_scripts.CreateDeliveryTests -v
```

Expected: all scaffold tests pass.

- [ ] **Step 5: Commit scaffold changes**

```bash
git add scripts/create_delivery.py tests/test_delivery_scripts.py
git commit -m "feat: add specifications image scaffold"
```

### Task 2: Validate Complete and Waiting Deliveries

**Files:**
- Modify: `tests/test_delivery_scripts.py`
- Modify: `scripts/validate_delivery.py`

- [ ] **Step 1: Write failing validation tests**

Update existing complete-delivery expectations from 6 to 7 images and from 12 to 14 images.

Add a helper that completes all non-waiting assets:

```python
def complete_available_assets(root, dimensions_by_ratio=None):
    dimensions_by_ratio = dimensions_by_ratio or {"square": (120, 120)}
    manifest_path = root / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    for report in REPORTS:
        (root / report).write_text("# 已完成\n\n有效内容。\n", encoding="utf-8")

    for asset in manifest["assets"]:
        if asset.get("availability") == "awaiting-user-input":
            continue
        write_png(
            root / asset["filename"],
            *dimensions_by_ratio[asset["ratio"]],
        )
        asset["status"] = "complete"
        asset["fidelity"] = "A"

    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest
```

Add:

```python
def test_accepts_specifications_waiting_for_user_input(self):
    with tempfile.TemporaryDirectory() as tmp:
        output = Path(tmp) / "delivery"
        created = create_delivery(
            output,
            specifications_awaiting_input=True,
        )
        self.assertEqual(created.returncode, 0, created.stderr)
        complete_available_assets(output)

        result = run_script(VALIDATE_SCRIPT, output)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("6 completed image", result.stdout.lower())
        self.assertIn("1 awaiting", result.stdout.lower())
```

Add strict failure tests:

```python
def test_rejects_plain_pending_specifications(self):
    with tempfile.TemporaryDirectory() as tmp:
        output = Path(tmp) / "delivery"
        self.assertEqual(create_delivery(output).returncode, 0)
        complete_available_assets(output)

        result = run_script(VALIDATE_SCRIPT, output)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("incomplete asset status", result.stdout.lower())

def test_rejects_waiting_specifications_without_required_note(self):
    with tempfile.TemporaryDirectory() as tmp:
        output = Path(tmp) / "delivery"
        self.assertEqual(
            create_delivery(
                output,
                specifications_awaiting_input=True,
            ).returncode,
            0,
        )
        manifest = complete_available_assets(output)
        manifest["assets"][-1]["notes"] = []
        (output / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        result = run_script(VALIDATE_SCRIPT, output)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invalid awaiting metadata", result.stdout.lower())

def test_rejects_image_for_waiting_specifications(self):
    with tempfile.TemporaryDirectory() as tmp:
        output = Path(tmp) / "delivery"
        self.assertEqual(
            create_delivery(
                output,
                specifications_awaiting_input=True,
            ).returncode,
            0,
        )
        manifest = complete_available_assets(output)
        specifications = manifest["assets"][-1]
        write_png(output / specifications["filename"], 120, 120)

        result = run_script(VALIDATE_SCRIPT, output)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unexpected image", result.stdout.lower())
```

- [ ] **Step 2: Run validation tests and verify RED**

Run:

```bash
python3 -m unittest \
  tests.test_delivery_scripts.ValidateDeliveryTests -v
```

Expected: waiting-delivery tests fail because the validator still requires every image and only reports the old image count.

- [ ] **Step 3: Implement strict waiting metadata validation**

Add:

```python
AWAITING_SPECIFICATIONS_NOTE = "等待用户提供规格参数"
```

Add:

```python
def is_awaiting_specifications(asset):
    notes = asset.get("notes")
    return (
        asset.get("type") == "specifications"
        and asset.get("status") == "pending"
        and asset.get("availability") == "awaiting-user-input"
        and isinstance(notes, list)
        and AWAITING_SPECIFICATIONS_NOTE in notes
    )
```

At the top of `validate_asset`, after resolving the filename and path:

```python
if asset.get("availability") == "awaiting-user-input":
    if not is_awaiting_specifications(asset):
        errors.append(f"Invalid awaiting metadata: {filename}")
        return "invalid"
    if image_path.exists():
        errors.append(f"Unexpected image for awaiting asset: {filename}")
        return "invalid"
    return "awaiting"
```

Return `"complete"` after a normal asset passes all checks and `"invalid"` on all error exits. In `validate_delivery`, count the returned states:

```python
completed_count = 0
awaiting_count = 0
for asset in assets:
    ...
    state = validate_asset(delivery_dir, asset, errors)
    if state == "complete":
        completed_count += 1
    elif state == "awaiting":
        awaiting_count += 1
return errors, len(assets), completed_count, awaiting_count
```

Update `main`:

```python
errors, asset_count, completed_count, awaiting_count = validate_delivery(
    args.delivery_dir
)
...
if awaiting_count:
    print(
        "Validation passed: "
        f"{completed_count} completed image(s), "
        f"{awaiting_count} awaiting user input, "
        f"and {len(REPORTS)} report(s)."
    )
else:
    print(
        f"Validation passed: {asset_count} image(s) "
        f"and {len(REPORTS)} report(s)."
    )
```

- [ ] **Step 4: Run all tests and verify GREEN**

Run:

```bash
python3 -m unittest discover -s tests -v
```

Expected: all tests pass, including seven-image, extra-ratio, strict waiting, missing-image, report, and aspect-ratio cases.

- [ ] **Step 5: Commit validator changes**

```bash
git add scripts/validate_delivery.py tests/test_delivery_scripts.py
git commit -m "feat: validate conditional specifications delivery"
```

### Task 3: Teach the Skill the Specifications Workflow

**Files:**
- Modify: `SKILL.md`
- Modify: `references/image-set-prompts.md`
- Modify: `references/quality-checklist.md`
- Modify: `references/product-fidelity.md`
- Modify: `references/research-workflow.md`
- Modify: `agents/openai.yaml`
- Modify: `README.md`

- [ ] **Step 1: Write a documentation contract check**

Run this before editing:

```bash
rg -n \
  '07-specifications|specification-reference|awaiting-user-input|规格尺寸图|七类' \
  SKILL.md references agents/openai.yaml README.md
```

Expected: no complete cross-file coverage; the seventh image workflow is absent.

- [ ] **Step 2: Update `SKILL.md`**

Make these exact behavioral changes:

- Description includes `specification sheets` and `dimension graphics`.
- Overview says seven default `1:1` images.
- Deliverables include `07-specifications-square.png`.
- Input roles include `specification-reference`.
- Before normal autonomous execution, ask once when no dimension field was supplied:

```text
请提供规格尺寸，例如：
品牌：归银堂
材质：足银999
容量：80毫升
口径：约6厘米
高度：约4厘米
底径：约3厘米
工艺：一张打
```

- Require at least one user-confirmed dimension field to generate image 07.
- Forbid estimating dimensions or factual specifications from photos.
- If the user does not answer, run `create_delivery.py` with `--specifications-awaiting-input`, generate the first six images, and document image 07 as waiting.
- If parameters are supplied, generate image 07 through one dedicated ImageGen call and validate every character, number, unit, annotation line, and disclaimer.

- [ ] **Step 3: Add the exact ImageGen prompt**

Rename the prompt guide heading to seven image types and add:

```text
## 07 规格尺寸图

销售任务：准确呈现用户确认的商品规格和尺寸关系。

数据规则：
- 至少有一项用户确认的尺寸字段才生成。
- 所有字段、数值、单位和“约”字逐字照录。
- 不从照片估算或补全任何规格。

Use case: product-mockup
Asset type: ecommerce specifications and dimensions graphic, 1:1 square
Primary request: create a classic Chinese ecommerce specification sheet
Layout:
- top: clean two-column or adaptive parameter table
- center: complete exact product with generous white space
- around product: thin dimension lines connected to the correct structures
- bottom: exact measurement disclaimer
Text (verbatim):
- Parameters: <逐项列出用户确认的字段和值>
- Dimensions: <逐项列出尺寸字段和值>
- Disclaimer: "尺寸为手工测量，存在合理误差，请以实物为准"
Fidelity: A
Constraints: preserve the exact product; render every character, number,
decimal point, unit and qualifier exactly once; connect each dimension line
to the correct product edge or feature
Avoid: estimated values, rewritten units, added parameters, repeated or
missing fields, incorrect dimension targets, decorative clutter, watermark
```

- [ ] **Step 4: Update references, metadata, and README**

Add specification checks to `quality-checklist.md`, the `specification-reference` role to `product-fidelity.md`, and change the visual brief responsibility from six to seven images in `research-workflow.md`.

Set:

```yaml
short_description: "从产品原始照片自动调研市场风格并生成七类电商商品图片"
```

Update README capability counts, table row 07, output tree, parameter example, missing-parameter behavior, and CLI example:

```bash
python3 scripts/create_delivery.py \
  ./output/product-ecommerce-images \
  --product-name "产品名称" \
  --specifications-awaiting-input
```

- [ ] **Step 5: Verify documentation coverage**

Run:

```bash
rg -n \
  '07-specifications|specification-reference|awaiting-user-input|规格尺寸图|七类' \
  SKILL.md references agents/openai.yaml README.md
```

Expected: matches in every relevant file, with no remaining statement that the default set contains only six images.

Run:

```bash
rg -n '默认.{0,10}6|默认只生成 6|六类电商图片|六张图的销售任务' \
  SKILL.md references agents/openai.yaml README.md
```

Expected: no matches.

- [ ] **Step 6: Commit Skill documentation**

```bash
git add SKILL.md references agents/openai.yaml README.md
git commit -m "feat: add specifications image workflow"
```

### Task 4: Verify, Install, and Publish

**Files:**
- Verify: all repository files
- Update mechanically: `/Users/mac/.codex/skills/generate-ecommerce-product-images/`

- [ ] **Step 1: Run the full test suite**

```bash
python3 -m unittest discover -s tests -v
```

Expected: all tests pass.

- [ ] **Step 2: Run the official Skill validator**

```bash
PYTHONPATH=/tmp/codex-skill-validator-deps \
python3 \
  /Users/mac/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  .
```

If `/tmp/codex-skill-validator-deps` is absent, install PyYAML only into that temporary directory:

```bash
python3 -m pip install --quiet \
  --target /tmp/codex-skill-validator-deps PyYAML
```

Expected: `Skill is valid!`

- [ ] **Step 3: Check repository cleanliness and diffs**

```bash
git diff --check
git status --short
git log --oneline -4
```

Expected: no uncommitted implementation changes and three focused feature commits after the design commit.

- [ ] **Step 4: Sync the verified Skill into Codex**

Copy only runtime Skill files, excluding repository-only `.git`, `.gitignore`, `docs`, and `README.md`:

```bash
rsync -a --delete \
  --exclude '.DS_Store' \
  SKILL.md agents references scripts tests \
  /Users/mac/.codex/skills/generate-ecommerce-product-images/
```

- [ ] **Step 5: Verify Codex reloads the installed Skill**

Call Codex app-server `skills/list` with:

```json
{
  "cwds": ["/Users/mac/Desktop/电商/铜器"],
  "forceReload": true
}
```

Expected installed entry:

```json
{
  "name": "generate-ecommerce-product-images",
  "enabled": true,
  "interface": {
    "displayName": "Generate Ecommerce Product Images",
    "shortDescription": "从产品原始照片自动调研市场风格并生成七类电商商品图片"
  }
}
```

Expected errors: `[]`.

- [ ] **Step 6: Push commits to GitHub**

```bash
git push origin main
git rev-parse HEAD
git ls-remote origin refs/heads/main
```

Expected: local HEAD and remote `main` SHA match.
