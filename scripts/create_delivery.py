#!/usr/bin/env python3
"""Create a non-destructive ecommerce image delivery scaffold."""

import argparse
import json
import sys
from pathlib import Path


STANDARD_ASSETS = [
    ("01-main", "main"),
    ("02-atmosphere", "atmosphere"),
    ("03-detail", "detail"),
    ("04-meaning-copy", "meaning-copy"),
    ("05-usage", "usage"),
    ("06-selling-points", "selling-points"),
    ("07-specifications", "specifications"),
]

RATIOS = {
    "square": [1, 1],
    "3x4": [3, 4],
    "4x5": [4, 5],
    "16x9": [16, 9],
}

REPORT_TEMPLATES = {
    "research.md": "# Market Research\n\n",
    "visual-brief.md": "# Visual Brief\n\n",
    "prompts.md": "# Final Image Prompts\n\n",
    "quality-report.md": "# Quality Report\n\n",
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Create a standard ecommerce product-image delivery directory."
    )
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--product-name", required=True)
    parser.add_argument(
        "--ratio",
        action="append",
        choices=RATIOS,
        help="Requested aspect ratio. Repeat for multiple ratios; defaults to square.",
    )
    parser.add_argument(
        "--specifications-awaiting-input",
        action="store_true",
        help=(
            "Mark specification images as waiting for user-supplied parameters "
            "instead of requiring generated files."
        ),
    )
    return parser.parse_args()


def unique_ratios(raw_ratios):
    ratios = raw_ratios or ["square"]
    return list(dict.fromkeys(ratios))


def build_manifest(product_name, ratios, specifications_awaiting_input=False):
    requested_ratios = [
        {"name": name, "width": RATIOS[name][0], "height": RATIOS[name][1]}
        for name in ratios
    ]
    assets = []
    for ratio in ratios:
        ratio_width, ratio_height = RATIOS[ratio]
        for asset_id, asset_type in STANDARD_ASSETS:
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

    return {
        "schema_version": 2,
        "product_name": product_name,
        "requested_ratios": requested_ratios,
        "assets": assets,
    }


def create_delivery(
    output_dir,
    product_name,
    ratios,
    specifications_awaiting_input=False,
):
    if output_dir.exists() and any(output_dir.iterdir()):
        raise ValueError(f"Refusing to overwrite non-empty directory: {output_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = build_manifest(
        product_name,
        ratios,
        specifications_awaiting_input=specifications_awaiting_input,
    )

    for filename, content in REPORT_TEMPLATES.items():
        (output_dir / filename).write_text(content, encoding="utf-8")

    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


def main():
    args = parse_args()
    ratios = unique_ratios(args.ratio)
    try:
        manifest = create_delivery(
            args.output_dir,
            args.product_name,
            ratios,
            specifications_awaiting_input=args.specifications_awaiting_input,
        )
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Created delivery: {args.output_dir.resolve()}")
    print("Expected images:")
    for asset in manifest["assets"]:
        print(f"- {asset['filename']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
