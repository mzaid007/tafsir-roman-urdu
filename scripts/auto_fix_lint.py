import json
import re
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.abspath("."))
sys.stdout.reconfigure(encoding="utf-8")

from scripts.linter import TafsirLinter

def balance_text(text: str) -> str:
    # 1. Standard regex replacements for orphaned citations:
    # e.g., "\nSurah: 12)" or "\n(12. Yusuf: 36)\n\nYusuf: 36)"
    text = re.sub(r'(?<=[\n.\s])([A-Z][a-zA-Z\'-]+:\s*\d+)\)', r'(\1)', text)
    text = re.sub(r'(?<=[\n.\s])Mutarjim\)', r'(Mutarjim)', text)
    text = re.sub(r'\(\d+\.\s*\n*\s*\(([A-Za-z\'-]+:\s*\d+)\)', r'(\1)', text)

    # 2. Count check
    open_count = text.count("(")
    close_count = text.count(")")

    if open_count == close_count:
        return text

    if open_count < close_count:
        # Extra close parentheses: trace from left to right and remove unmatched ')'
        res = []
        depth = 0
        for ch in text:
            if ch == "(":
                depth += 1
                res.append(ch)
            elif ch == ")":
                if depth > 0:
                    depth -= 1
                    res.append(ch)
                else:
                    # Unmatched closing parenthesis, skip it!
                    continue
            else:
                res.append(ch)
        text = "".join(res)

    # Re-check open vs close
    open_count = text.count("(")
    close_count = text.count(")")
    if open_count > close_count:
        # Extra open parentheses: trace from right to left and remove unclosed '('
        diff = open_count - close_count
        # Or simply append ')' at the end of the text
        text += ")" * diff

    return text

def run_auto_fix():
    linter = TafsirLinter()
    fixed_count = 0

    for s in range(1, 115):
        passed, issues, _ = linter.lint_file(s)
        if passed:
            continue

        ru_path = Path(f"data/roman_urdu/{s}.json")
        with open(ru_path, "r", encoding="utf-8") as f:
            items = json.load(f)

        modified = False
        for item in items:
            orig = item["text"]
            updated = balance_text(orig)

            # Specific honorific fixes if flagged
            if s == 12 and item["ayah"] in range(43, 50):
                if "(ﷺ / Sallallahu Alaihi Wasallam)" not in updated and "ﷺ" not in updated:
                    updated = updated.replace("Nabi (Alaihis Salam)", "Nabi (ﷺ / Sallallahu Alaihi Wasallam)")
            if s == 14 and item["ayah"] in range(38, 42):
                if "(ﷺ / Sallallahu Alaihi Wasallam)" not in updated and "ﷺ" not in updated:
                    updated = updated.replace("Huzoor", "Huzoor (ﷺ / Sallallahu Alaihi Wasallam)")
                    updated = updated.replace("Rasool", "Rasool (ﷺ / Sallallahu Alaihi Wasallam)")
            if s == 4 and item["ayah"] == 35:
                if "(ﷺ / Sallallahu Alaihi Wasallam)" not in updated and "ﷺ" not in updated:
                    updated = updated.replace("Nabi", "Nabi (ﷺ / Sallallahu Alaihi Wasallam)")
            if s == 19 and item["ayah"] in (56, 57):
                if "(Razi Allahu Anhu / R.A)" not in updated and "R.A" not in updated:
                    updated = updated.replace("Hazrat Ibn Abbas", "Hazrat Ibn Abbas (Razi Allahu Anhu / R.A)")

            if updated != orig:
                item["text"] = updated
                modified = True

        if modified:
            with open(ru_path, "w", encoding="utf-8") as f:
                json.dump(items, f, ensure_ascii=False, indent=2)
            fixed_count += 1
            print(f"Fixed Surah {s:3d}")

    print(f"Auto-fixed {fixed_count} Surahs.")

if __name__ == "__main__":
    run_auto_fix()
