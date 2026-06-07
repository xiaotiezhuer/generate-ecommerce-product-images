---
name: generate-ecommerce-product-images
description: Use when a user provides one or more product photos and wants ecommerce product images, marketplace listing visuals, lifestyle shots, detail shots, Chinese meaning-copy posters, selling-point graphics, specification sheets, dimension graphics, competitor-style research, or an automated product-photo set.
---

# Generate Ecommerce Product Images

## Overview

Turn one or more photos of the same real product into a researched, product-faithful ecommerce image set. Default to seven `1:1` images and complete the workflow automatically unless the product identity is genuinely ambiguous or specification data requires one user confirmation.

**REQUIRED SUB-SKILL:** Use `imagegen` for every generated or edited raster image. Use the built-in `image_gen` path by default and follow its save-path, reference-image, inspection, and iteration rules.

## Default Deliverables

Generate these seven square images unless the user requests a different set:

1. `01-main-square.png` — white or restrained clean-background main image.
2. `02-atmosphere-square.png` — premium category-appropriate atmosphere image.
3. `03-detail-square.png` — material or craftsmanship macro detail.
4. `04-meaning-copy-square.png` — Chinese meaning-copy poster.
5. `05-usage-square.png` — realistic use and scale scene.
6. `06-selling-points-square.png` — no more than three evidence-backed selling points.
7. `07-specifications-square.png` — user-confirmed parameters and dimension annotations.

Only add `3:4`, `4:5`, `16:9`, or other ratios when explicitly requested. Generate each extra ratio as a separately composed image; do not substitute a damaging mechanical crop.

## Question Policy

Proceed without asking when optional brand, audience, price, material, or copy information is missing. Infer a conservative visual direction and avoid unsupported factual claims.

Specifications are the one conditional exception. If the user has not supplied at least one confirmed dimension field, ask once:

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

Accept flexible `字段：内容` lines. Common dimension fields include length, width, height, diameter, opening diameter, base diameter, and thickness. Do not estimate any value from the photos. If the user does not provide the data after this one question, continue with the first six images and mark image 07 as awaiting user input.

Stop and ask only when:

- Inputs are too unclear to identify essential product structure.
- Images likely show different SKUs, colorways, or models that would be unsafe to merge.
- Reference images contradict each other on a key functional feature.
- Supplied dimensions or specification fields conflict with each other.
- The user requests a factual claim that lacks necessary evidence.

## Resource Loading

Read resources only when entering the relevant phase:

- Before classifying inputs or generating anything, read `references/product-fidelity.md`.
- Before market research, read `references/research-workflow.md`.
- Before composing prompts, read `references/image-set-prompts.md`.
- Before accepting, retrying, or delivering an image, read `references/quality-checklist.md`.

## Workflow

### 1. Inspect and Classify Inputs

Treat attached images as visible inputs. For local filesystem images not yet visible in the conversation, inspect them with `view_image` before using built-in ImageGen.

Label every image as one of:

- `main-identity`
- `alternate-angle`
- `detail-reference`
- `packaging-reference`
- `accessory-reference`
- `usage-reference`
- `specification-reference`

Identify likely mixed SKUs before proceeding.

### 2. Build the Product Fingerprint

Follow `references/product-fidelity.md`. Record:

- Silhouette and proportions.
- Component count, location, shape, connection, and orientation.
- Openings, handles, spouts, buttons, interfaces, lids, or other functional features.
- Color, material, reflections, texture, logos, inscriptions, and distinctive natural marks.
- Packaging and real accessories as separate entities.
- User-confirmed specification fields, dimensions, units, qualifiers, and source.
- Any uncertainty.

Keep original product photos as the identity truth throughout the task. Never use a structurally failed generated image as an identity reference.

### 3. Research Current Market Visuals

When internet access is available, perform current research; do not rely only on memory. Follow `references/research-workflow.md`.

Research multiple merchants, brands, or recent content examples. Record dates, links, evidence classes, repeated visual patterns, and limitations in `research.md`.

Never translate search prominence or engagement into unsupported sales claims. If research is blocked, continue using conservative category heuristics and explicitly mark `未完成实时市场验证`.

### 4. Create the Visual and Copy Brief

Write `visual-brief.md` with:

- Target audience and price impression.
- Core style, palette, background materials, light, camera, props, and mood.
- A distinct sales task for each of the seven images.
- Global product invariants and avoid list.

Create a 4–8 Chinese-character meaning phrase when appropriate. Limit selling points to three. Use only user-supplied facts, directly visible features, or reliable sources. Do not invent material purity, origin, handmade status, heritage, safety, certification, medical benefit, performance, or sales data.

For image 07, use only user-confirmed specification text. Product photos may identify where a dimension line should point, but cannot establish the numeric value, unit, capacity, weight, material purity, brand, model, or process.

### 5. Create the Delivery Scaffold

Choose the user destination when supplied; otherwise create a descriptive project-local delivery directory. Never overwrite an existing non-empty directory; use a versioned sibling.

Run:

```bash
python3 <skill-dir>/scripts/create_delivery.py \
  <delivery-dir> \
  --product-name "<product name>"
```

Add repeated `--ratio` arguments only for explicitly requested extra ratios.

If the user did not supply a confirmed dimension after the one question, add:

```bash
--specifications-awaiting-input
```

### 6. Compose Prompts and Generate

Read `references/image-set-prompts.md`. Write the final prompt for every requested asset into `prompts.md`.

For each asset:

1. Use one dedicated built-in `image_gen` call.
2. Identify every input image role in the prompt.
3. Repeat the product fingerprint and the most important invariants.
4. Default to Fidelity A.
5. Generate the image, inspect it, and copy the selected final into the delivery directory.
6. Do not let a failed candidate influence later product identity.

Use the original images for identity and the visual brief for styling. Keep props secondary and do not imply that unprovided props are included with the product.

Skip the ImageGen call for image 07 only when its manifest record is marked `availability: "awaiting-user-input"`. Otherwise, image 07 requires at least one confirmed dimension field and one dedicated ImageGen call using the classic specification layout in `references/image-set-prompts.md`.

### 7. Inspect, Retry, and Apply Fallbacks

Read `references/quality-checklist.md`. Check every image immediately for:

- Product identity.
- Exact text.
- Exact specification fields, numbers, units, qualifiers, and dimension targets.
- Ecommerce usability.
- Factual and platform compliance.

Allow at most two targeted retries per image. Change only the failed element and repeat all invariants.

Use Fidelity B only after A-level targeted retries fail and only within `references/product-fidelity.md`. Mark every B result in the manifest and quality report.

For persistent text failure:

1. Shorten and simplify text once.
2. Then generate a no-text base with a safe text area.
3. Record the exact intended copy and failure; never deliver incorrect text as complete.

For image 07, wrong dimensions, units, parameter values, or annotation targets are factual failures, not cosmetic text issues. After two targeted retries, mark the asset `failed`; do not deliver an incorrect specification image or replace it with estimated data.

### 8. Finalize and Validate

Complete:

- `research.md`
- `visual-brief.md`
- `prompts.md`
- `quality-report.md`
- `manifest.json`

For every image, set manifest `status` to `complete` or `failed`, preserve `fidelity` as `A` or `B`, and add concise notes for retries, text fallback, or unresolved issues.

The only permitted final `pending` asset is image 07 with `availability: "awaiting-user-input"` and the note `等待用户提供规格参数`. This state is allowed only after the one specification question went unanswered.

Run:

```bash
python3 <skill-dir>/scripts/validate_delivery.py <delivery-dir>
```

Do not claim full completion unless validation passes. If validation fails because an image could not be made usable, report the exact missing or failed item rather than hiding it.

## Final Response

Report:

- Delivery directory and final image paths.
- Short market-trend summary and research limitation, if any.
- The prompts file path.
- Any Fidelity B images and exact changes.
- Failed or no-text fallback assets.
- Any specification image waiting for user input.
- Validation result.
- Reminder to manually confirm product structure, color, copy, logos, dimensions, units, scale, and all factual claims before listing.
