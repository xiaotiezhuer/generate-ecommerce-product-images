import json
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
CREATE_SCRIPT = SKILL_DIR / "scripts" / "create_delivery.py"
VALIDATE_SCRIPT = SKILL_DIR / "scripts" / "validate_delivery.py"
REPORTS = ("research.md", "visual-brief.md", "prompts.md", "quality-report.md")


def png_chunk(chunk_type, data):
    payload = chunk_type + data
    return (
        struct.pack(">I", len(data))
        + payload
        + struct.pack(">I", zlib.crc32(payload) & 0xFFFFFFFF)
    )


def write_png(path, width, height):
    signature = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    row = b"\xff\xff\xff" * width
    raw = b"".join(b"\x00" + row for _ in range(height))
    path.write_bytes(
        signature
        + png_chunk(b"IHDR", ihdr)
        + png_chunk(b"IDAT", zlib.compress(raw))
        + png_chunk(b"IEND", b"")
    )


def run_script(script, *args):
    return subprocess.run(
        [sys.executable, str(script), *map(str, args)],
        text=True,
        capture_output=True,
        check=False,
    )


def create_delivery(root, *ratios):
    args = [root, "--product-name", "测试产品"]
    for ratio in ratios:
        args.extend(["--ratio", ratio])
    return run_script(CREATE_SCRIPT, *args)


def complete_delivery(root, dimensions_by_ratio=None, skip_types=()):
    dimensions_by_ratio = dimensions_by_ratio or {"square": (120, 120)}
    manifest_path = root / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    for report in REPORTS:
        (root / report).write_text("# 已完成\n\n有效内容。\n", encoding="utf-8")

    for asset in manifest["assets"]:
        if asset["type"] in skip_types:
            continue
        dimensions = dimensions_by_ratio[asset["ratio"]]
        write_png(root / asset["filename"], *dimensions)
        asset["status"] = "complete"
        asset["fidelity"] = "A"

    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


class CreateDeliveryTests(unittest.TestCase):
    def test_creates_standard_tree_and_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "delivery"

            result = create_delivery(output)

            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["schema_version"], 2)
            self.assertEqual(manifest["product_name"], "测试产品")
            self.assertEqual([item["name"] for item in manifest["requested_ratios"]], ["square"])
            self.assertEqual(len(manifest["assets"]), 7)
            self.assertEqual(manifest["assets"][0]["filename"], "01-main-square.png")
            self.assertEqual(
                manifest["assets"][-1]["filename"],
                "07-specifications-square.png",
            )
            self.assertEqual(manifest["assets"][-1]["type"], "specifications")
            self.assertTrue(all(asset["status"] == "pending" for asset in manifest["assets"]))
            self.assertTrue(all(asset["fidelity"] == "A" for asset in manifest["assets"]))
            for report in REPORTS:
                self.assertTrue((output / report).is_file())

    def test_refuses_to_overwrite_existing_delivery(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "delivery"
            first = create_delivery(output)
            self.assertEqual(first.returncode, 0, first.stderr)

            second = create_delivery(output)

            self.assertNotEqual(second.returncode, 0)
            self.assertIn("refus", (second.stdout + second.stderr).lower())

    def test_accepts_requested_extra_ratios(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "delivery"

            result = create_delivery(output, "square", "3x4")

            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(
                [item["name"] for item in manifest["requested_ratios"]],
                ["square", "3x4"],
            )
            self.assertEqual(len(manifest["assets"]), 14)
            filenames = {asset["filename"] for asset in manifest["assets"]}
            self.assertIn("01-main-square.png", filenames)
            self.assertIn("01-main-3x4.png", filenames)
            self.assertIn("07-specifications-square.png", filenames)
            self.assertIn("07-specifications-3x4.png", filenames)

    def test_rejects_removed_specifications_awaiting_input_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "delivery"

            result = run_script(
                CREATE_SCRIPT,
                output,
                "--product-name",
                "测试产品",
                "--specifications-awaiting-input",
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("unrecognized arguments", result.stderr.lower())


class ValidateDeliveryTests(unittest.TestCase):
    def test_accepts_complete_square_delivery(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "delivery"
            created = create_delivery(output)
            self.assertEqual(created.returncode, 0, created.stderr)
            complete_delivery(output)

            result = run_script(VALIDATE_SCRIPT, output)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("7 image", result.stdout.lower())

    def test_reports_missing_image(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "delivery"
            self.assertEqual(create_delivery(output).returncode, 0)
            manifest = complete_delivery(output)
            missing = output / manifest["assets"][0]["filename"]
            missing.unlink()

            result = run_script(VALIDATE_SCRIPT, output)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("missing image", result.stdout.lower())

    def test_reports_non_square_default_image(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "delivery"
            self.assertEqual(create_delivery(output).returncode, 0)
            manifest = complete_delivery(output)
            wrong = output / manifest["assets"][0]["filename"]
            write_png(wrong, 120, 100)

            result = run_script(VALIDATE_SCRIPT, output)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("aspect ratio", result.stdout.lower())

    def test_reports_missing_reports(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "delivery"
            self.assertEqual(create_delivery(output).returncode, 0)
            complete_delivery(output)
            (output / "research.md").unlink()

            result = run_script(VALIDATE_SCRIPT, output)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("missing report", result.stdout.lower())

    def test_accepts_declared_extra_ratio(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "delivery"
            created = create_delivery(output, "square", "3x4")
            self.assertEqual(created.returncode, 0, created.stderr)
            complete_delivery(
                output,
                dimensions_by_ratio={"square": (120, 120), "3x4": (90, 120)},
            )

            result = run_script(VALIDATE_SCRIPT, output)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("14 image", result.stdout.lower())

    def test_rejects_plain_pending_specifications(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "delivery"
            self.assertEqual(create_delivery(output).returncode, 0)
            complete_delivery(output, skip_types={"specifications"})

            result = run_script(VALIDATE_SCRIPT, output)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("incomplete asset status", result.stdout.lower())

    def test_rejects_legacy_awaiting_specifications_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "delivery"
            self.assertEqual(create_delivery(output).returncode, 0)
            manifest = complete_delivery(output, skip_types={"specifications"})
            specifications = manifest["assets"][-1]
            specifications["availability"] = "awaiting-user-input"
            specifications["notes"] = ["等待用户提供规格参数"]
            (output / "manifest.json").write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            result = run_script(VALIDATE_SCRIPT, output)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("incomplete asset status", result.stdout.lower())


if __name__ == "__main__":
    unittest.main()
