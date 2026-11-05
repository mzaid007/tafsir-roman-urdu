#!/usr/bin/env python3
"""
Tafsir Roman Urdu (TRU) - Quality Control & Integrity Linter
Validates structure, honorifics preservation, character length ratios, and schema conformity.
"""

import os
import sys
import json
import re
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Any

# Ensure standard UTF-8 stream output in Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


class TafsirLinter:
    def __init__(self, data_ur_dir: str = "data/ur", data_ru_dir: str = "data/roman_urdu"):
        self.data_ur_dir = Path(data_ur_dir)
        self.data_ru_dir = Path(data_ru_dir)

    def lint_file(self, surah: int) -> Tuple[bool, List[str], Dict[str, Any]]:
        """Lints a single surah Roman Urdu file against its Urdu source counterpart."""
        issues = []
        metrics = {
            "surah": surah,
            "ur_ayahs": 0,
            "ru_ayahs": 0,
            "ur_char_count": 0,
            "ru_char_count": 0,
            "ratio": 0.0,
            "honorifics_preserved": True
        }

        ur_file = self.data_ur_dir / f"{surah}.json"
        ru_file = self.data_ru_dir / f"{surah}.json"

        if not ur_file.exists():
            issues.append(f"Source file missing: {ur_file}")
            return False, issues, metrics

        if not ru_file.exists():
            issues.append(f"Target transliterated file missing: {ru_file}")
            return False, issues, metrics

        # Parse JSON
        try:
            with open(ur_file, "r", encoding="utf-8") as f:
                ur_data = json.load(f)
        except Exception as e:
            issues.append(f"Failed to parse source JSON {ur_file}: {e}")
            return False, issues, metrics

        try:
            with open(ru_file, "r", encoding="utf-8") as f:
                ru_data = json.load(f)
        except Exception as e:
            issues.append(f"Failed to parse target JSON {ru_file}: {e}")
            return False, issues, metrics

        metrics["ur_ayahs"] = len(ur_data)
        metrics["ru_ayahs"] = len(ru_data)

        # 1. Ayah Count Verification
        if len(ur_data) != len(ru_data):
            issues.append(f"Ayah count mismatch: UR={len(ur_data)}, RU={len(ru_data)}")

        # Map by ayah number
        ur_map = {item.get("ayah"): item for item in ur_data}
        ru_map = {item.get("ayah"): item for item in ru_data}

        # 2. Sequential & Schema Invariants
        for idx, item in enumerate(ru_data, start=1):
            if "surah" not in item or "ayah" not in item or "text" not in item:
                issues.append(f"Item at index {idx} violates schema (missing surah, ayah, or text)")
            if item.get("surah") != surah:
                issues.append(f"Surah ID mismatch at index {idx}: expected {surah}, found {item.get('surah')}")

        total_ur_chars = sum(len(x.get("text", "")) for x in ur_data)
        total_ru_chars = sum(len(x.get("text", "")) for x in ru_data)
        metrics["ur_char_count"] = total_ur_chars
        metrics["ru_char_count"] = total_ru_chars

        if total_ur_chars > 0:
            ratio = total_ru_chars / total_ur_chars
            metrics["ratio"] = round(ratio, 3)
            # Acceptable expansion ratio for Urdu Nastaliq -> Latin Roman Urdu is 0.7x to 2.2x
            if ratio < 0.65:
                issues.append(f"Warning: Low text expansion ratio ({ratio:.2f}x). Possible truncation or summarization.")
            elif ratio > 2.5:
                issues.append(f"Warning: Excessive text expansion ratio ({ratio:.2f}x). Possible hallucination or repetition.")

        # 3. Ayah-by-Ayah Checks
        for ayah_num, ur_entry in ur_map.items():
            if ayah_num not in ru_map:
                issues.append(f"Ayah {ayah_num} missing in Roman Urdu output")
                continue

            ru_entry = ru_map[ayah_num]
            ur_text = ur_entry.get("text", "")
            ru_text = ru_entry.get("text", "")

            if not ru_text.strip() and ur_text.strip():
                issues.append(f"Ayah {ayah_num} has empty text in Roman Urdu output")

            # Check Prophet honorifics preservation
            has_prophet_ur = bool(re.search(r"ﷺ|صلی اللہ علیہ وسلم", ur_text))
            has_prophet_ru = bool(re.search(r"ﷺ|Sallallahu\s+Alaihi\s+Wasallam|SAW|PBUH", ru_text, re.IGNORECASE))
            if has_prophet_ur and not has_prophet_ru:
                issues.append(f"Ayah {ayah_num}: Prophet honorific present in Urdu but missing in Roman Urdu")
                metrics["honorifics_preserved"] = False

            # Check Sahaba honorifics preservation
            has_sahaba_ur = bool(re.search(r"رضی اللہ عنہ|رضی اللہ عنہا|رضی اللہ عنہم|ؓ", ur_text))
            has_sahaba_ru = bool(re.search(r"Razi\s+Allahu|R\.A\b|RA\b", ru_text, re.IGNORECASE))
            if has_sahaba_ur and not has_sahaba_ru:
                issues.append(f"Ayah {ayah_num}: Sahaba honorific present in Urdu but missing in Roman Urdu")
                metrics["honorifics_preserved"] = False

            # Check for unbalanced parentheses
            if ru_text.count("(") != ru_text.count(")"):
                issues.append(f"Ayah {ayah_num}: Unbalanced parentheses in Roman Urdu text")

        passed = len(issues) == 0
        return passed, issues, metrics


def main():
    parser = argparse.ArgumentParser(description="Lint and validate Tafsir Roman Urdu dataset files.")
    parser.add_argument("--surah", type=int, help="Single Surah number to lint (1..114)")
    parser.add_argument("--surahs", type=int, nargs="+", help="List of Surahs to lint")
    parser.add_argument("--range", type=int, nargs=2, metavar=("START", "END"), help="Range of Surahs, e.g. 78 114")
    parser.add_argument("--all", action="store_true", help="Lint all generated Surah files")
    parser.add_argument("--ur-dir", default="data/ur", help="Directory containing source Urdu files")
    parser.add_argument("--ru-dir", default="data/roman_urdu", help="Directory containing Roman Urdu files")

    args = parser.parse_args()
    linter = TafsirLinter(data_ur_dir=args.ur_dir, data_ru_dir=args.ru_dir)

    surahs_to_lint = []
    if args.surah:
        surahs_to_lint = [args.surah]
    elif args.surahs:
        surahs_to_lint = args.surahs
    elif args.range:
        surahs_to_lint = list(range(args.range[0], args.range[1] + 1))
    elif args.all:
        ru_files = sorted(Path(args.ru_dir).glob("*.json"), key=lambda p: int(p.stem) if p.stem.isdigit() else 999)
        surahs_to_lint = [int(p.stem) for p in ru_files if p.stem.isdigit()]
    else:
        # Default: lint whatever files currently exist in data/roman_urdu
        ru_files = sorted(Path(args.ru_dir).glob("*.json"), key=lambda p: int(p.stem) if p.stem.isdigit() else 999)
        surahs_to_lint = [int(p.stem) for p in ru_files if p.stem.isdigit()]
        if not surahs_to_lint:
            print("No Roman Urdu files found in data/roman_urdu yet.")
            return

    total = len(surahs_to_lint)
    passed_count = 0

    print(f"\n=======================================================")
    print(f"  Tafsir-Roman-Urdu (TRU) Quality Linter")
    print(f"  Validating {total} Surah file(s)...")
    print(f"=======================================================\n")

    for s in surahs_to_lint:
        passed, issues, metrics = linter.lint_file(s)
        status_sym = "✅ PASS" if passed else "❌ FAIL"
        ratio_str = f"{metrics['ratio']:.2f}x" if metrics['ratio'] else "N/A"
        print(f"Surah {s:3d}: {status_sym} | Ayahs: {metrics['ru_ayahs']}/{metrics['ur_ayahs']} | Expansion: {ratio_str}")

        if issues:
            for issue in issues[:10]:
                print(f"   ⚠️  {issue}")
            if len(issues) > 10:
                print(f"   ... and {len(issues) - 10} more issues")
        else:
            passed_count += 1

    print(f"\nSummary: {passed_count}/{total} Surahs passed with 100% integrity.\n")


if __name__ == "__main__":
    main()
