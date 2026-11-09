#!/usr/bin/env python3
"""
Tafsir Roman Urdu (TRU) - CLI Reader
Read any Surah or Ayah commentary directly in your terminal.
Usage:
  python scripts/reader.py 1 1       # Read Surah 1 Ayah 1
  python scripts/reader.py 18        # Read Surah 18 (All Ayahs)
"""

import sys
import json
import argparse
from pathlib import Path

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

def main():
    parser = argparse.ArgumentParser(description="Read Tafsir Ibn Kathir in Roman Urdu directly in your terminal.")
    parser.add_argument("surah", type=int, help="Surah number (1..114)")
    parser.add_argument("ayah", type=int, nargs="?", default=None, help="Optional Ayah number")
    args = parser.parse_args()

    ru_path = Path(f"data/roman_urdu/{args.surah}.json")
    if not ru_path.exists():
        print(f"Error: Surah {args.surah} not found at {ru_path}.")
        return

    with open(ru_path, "r", encoding="utf-8") as f:
        items = json.load(f)

    if args.ayah is not None:
        matched = [x for x in items if x.get("ayah") == args.ayah]
        if not matched:
            print(f"Error: Ayah {args.ayah} not found in Surah {args.surah}.")
            return
        items_to_show = matched
    else:
        items_to_show = items

    print("=" * 70)
    print(f"  📖 Tafsir Ibn Kathir — Roman Urdu | Surah {args.surah}")
    print("=" * 70)

    for item in items_to_show:
        ayah_num = item.get("ayah")
        text = item.get("text", "").strip()
        print(f"\n[Ayah {ayah_num}]")
        print("-" * 40)
        print(text if text else "(Commentary grouped with adjacent Ayahs)")
        print()

if __name__ == "__main__":
    main()
