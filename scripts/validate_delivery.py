#!/usr/bin/env python3
"""Validate ecommerce image delivery files against manifest.json."""

import argparse
import json
import struct
import sys
from pathlib import Path


REPORTS = ("research.md", "visual-brief.md", "prompts.md", "quality-report.md")
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
JPEG_SOF_MARKERS = {
    0xC0,
    0xC1,
    0xC2,
    0xC3,
    0xC5,
    0xC6,
    0xC7,
    0xC9,
    0xCA,
    0xCB,
    0xCD,
    0xCE,
    0xCF,
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Validate an ecommerce product-image delivery directory."
    )
    parser.add_argument("delivery_dir", type=Path)
    return parser.parse_args()


def png_dimensions(data):
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("invalid PNG header")
    return struct.unpack(">II", data[16:24])


def jpeg_dimensions(data):
    if len(data) < 4 or data[:2] != b"\xff\xd8":
        raise ValueError("invalid JPEG header")

    offset = 2
    while offset + 4 <= len(data):
        if data[offset] != 0xFF:
            offset += 1
            continue
        while offset < len(data) and data[offset] == 0xFF:
            offset += 1
        if offset >= len(data):
            break

        marker = data[offset]
        offset += 1
        if marker in (0xD8, 0xD9):
            continue
        if offset + 2 > len(data):
            break

        segment_length = struct.unpack(">H", data[offset : offset + 2])[0]
        if segment_length < 2 or offset + segment_length > len(data):
            break
        if marker in JPEG_SOF_MARKERS:
            if segment_length < 7:
                break
            height, width = struct.unpack(">HH", data[offset + 3 : offset + 7])
            return width, height
        offset += segment_length

    raise ValueError("JPEG dimensions not found")


def webp_dimensions(data):
    if len(data) < 30 or data[:4] != b"RIFF" or data[8:12] != b"WEBP":
        raise ValueError("invalid WebP header")

    chunk_type = data[12:16]
    payload = data[20:]
    if chunk_type == b"VP8X":
        width = 1 + int.from_bytes(payload[4:7], "little")
        height = 1 + int.from_bytes(payload[7:10], "little")
        return width, height
    if chunk_type == b"VP8 ":
        frame = payload.find(b"\x9d\x01\x2a")
        if frame == -1 or frame + 7 > len(payload):
            raise ValueError("VP8 frame header not found")
        width = int.from_bytes(payload[frame + 3 : frame + 5], "little") & 0x3FFF
        height = int.from_bytes(payload[frame + 5 : frame + 7], "little") & 0x3FFF
        return width, height
    if chunk_type == b"VP8L":
        if len(payload) < 5 or payload[0] != 0x2F:
            raise ValueError("invalid VP8L header")
        bits = int.from_bytes(payload[1:5], "little")
        width = (bits & 0x3FFF) + 1
        height = ((bits >> 14) & 0x3FFF) + 1
        return width, height
    raise ValueError(f"unsupported WebP chunk {chunk_type!r}")


def image_dimensions(path):
    data = path.read_bytes()
    suffix = path.suffix.lower()
    if suffix == ".png":
        return png_dimensions(data)
    if suffix in {".jpg", ".jpeg"}:
        return jpeg_dimensions(data)
    if suffix == ".webp":
        return webp_dimensions(data)
    raise ValueError(f"unsupported image extension: {suffix}")


def load_manifest(delivery_dir, errors):
    manifest_path = delivery_dir / "manifest.json"
    if not manifest_path.is_file():
        errors.append("Missing manifest: manifest.json")
        return None
    try:
        return json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        errors.append(f"Invalid manifest.json: {exc}")
        return None


def validate_reports(delivery_dir, errors):
    for filename in REPORTS:
        path = delivery_dir / filename
        if not path.is_file():
            errors.append(f"Missing report: {filename}")
            continue
        try:
            if not path.read_text(encoding="utf-8").strip():
                errors.append(f"Empty report: {filename}")
        except (OSError, UnicodeDecodeError) as exc:
            errors.append(f"Unreadable report {filename}: {exc}")


def validate_asset(delivery_dir, asset, errors):
    filename = asset.get("filename")
    if not filename:
        errors.append("Asset missing filename")
        return

    image_path = delivery_dir / filename
    if image_path.suffix.lower() not in ALLOWED_EXTENSIONS:
        errors.append(f"Unsupported image format: {filename}")
        return
    if not image_path.is_file():
        errors.append(f"Missing image: {filename}")
        return

    if asset.get("status") != "complete":
        errors.append(f"Incomplete asset status: {filename}")
    if asset.get("fidelity") not in {"A", "B"}:
        errors.append(f"Invalid fidelity level: {filename}")

    try:
        width, height = image_dimensions(image_path)
    except (OSError, ValueError, struct.error) as exc:
        errors.append(f"Unreadable image {filename}: {exc}")
        return

    ratio_width = asset.get("ratio_width")
    ratio_height = asset.get("ratio_height")
    if not isinstance(ratio_width, (int, float)) or not isinstance(
        ratio_height, (int, float)
    ):
        errors.append(f"Missing ratio metadata: {filename}")
        return
    if width <= 0 or height <= 0 or ratio_width <= 0 or ratio_height <= 0:
        errors.append(f"Invalid dimensions or ratio metadata: {filename}")
        return

    actual_ratio = width / height
    expected_ratio = ratio_width / ratio_height
    relative_error = abs(actual_ratio - expected_ratio) / expected_ratio
    if relative_error > 0.01:
        errors.append(
            f"Aspect ratio mismatch: {filename} is {width}x{height}, "
            f"expected {ratio_width}:{ratio_height}"
        )


def validate_delivery(delivery_dir):
    errors = []
    if not delivery_dir.is_dir():
        return [f"Delivery directory not found: {delivery_dir}"], 0

    manifest = load_manifest(delivery_dir, errors)
    validate_reports(delivery_dir, errors)
    if manifest is None:
        return errors, 0

    assets = manifest.get("assets")
    if not isinstance(assets, list) or not assets:
        errors.append("Manifest assets must be a non-empty list")
        return errors, 0

    for asset in assets:
        if not isinstance(asset, dict):
            errors.append("Manifest asset must be an object")
            continue
        validate_asset(delivery_dir, asset, errors)
    return errors, len(assets)


def main():
    args = parse_args()
    errors, asset_count = validate_delivery(args.delivery_dir)
    if errors:
        print(f"Validation failed with {len(errors)} error(s):")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Validation passed: {asset_count} image(s) and {len(REPORTS)} report(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
