#!/usr/bin/env python3
"""
Tafsir Roman Urdu (TRU) - Batch Transliteration Engine
Powered by Google Gemini API.
Translates authentic Urdu Tafsir Ibn Kathir into standardized Roman Urdu (Latin script)
strictly following TRU Style Guide.
"""

import os
import sys
import json
import re
import time
import random
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional

import requests
from dotenv import load_dotenv

# Ensure standard UTF-8 stream output in Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# Load environment variables
load_dotenv()

raw_keys = os.getenv("GEMINI_API_KEYS", "") or os.getenv("GEMINI_API_KEY", "")
API_KEYS = [k.strip() for k in raw_keys.split(",") if k.strip()]
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
FALLBACK_MODELS = ["gemini-3-flash-preview", "gemini-3.5-flash", "gemini-3.5-flash-lite"]
_current_key_idx = 0

SYSTEM_PROMPT = """You are an expert Islamic Computational Linguist for the Tafsir-Roman-Urdu (TRU) project.
Your task is to transliterate authentic Urdu Tafsir Ibn Kathir commentary into standardized, highly readable Roman Urdu (Latin script).

INVIOLABLE RULES:
1. ZERO HALLUCINATION / ZERO OMISSION:
   - Perform an exact, faithful transliteration of every single sentence and concept in the Urdu source.
   - NEVER summarize, abridge, paraphrase, or omit any commentary, citation, or hadith chain.
2. VOWELS & STANDARD SPELLING:
   - Urdu standard forms: 'hai', 'hain', 'nahin', 'yeh', 'woh', 'ke', 'kyunke', 'lekin', 'aur', 'mein', 'par', 'se', 'ko', 'ka', 'ki', 'karein', 'kaha', 'farmaya', 'tarah', 'baat', 'log', 'roz'.
   - Noon Ghunna: soft 'n' (e.g., 'hain', 'nahin', 'karein', 'jahan', 'dilon').
3. SACRED HONORIFICS (Standardize reverently):
   - ﷺ / صلی اللہ علیہ وسلم -> (ﷺ / Sallallahu Alaihi Wasallam)
   - رضی اللہ عنہ / ؓ -> (Razi Allahu Anhu / R.A)
   - رضی اللہ عنہا -> (Razi Allahu Anha / R.A)
   - رضی اللہ عنہم -> (Razi Allahu Anhum / R.A)
   - علیہ السلام / ؑ -> (Alaihis Salam / A.S)
   - علیہم السلام -> (Alaihimas Salam / A.S)
   - رحمہ اللہ / ؒ -> (Rahimahullah / R.H)
   - رحمہم اللہ -> (Rahimahumullah / R.H)
   - اللہ تعالیٰ -> Allah Ta'ala
4. COMPOUND WORDS & IZAFAT:
   - Use hyphenated '-e-' for Izafat-e-Kasra: Amr-e-Ilahi, Ahl-e-Kitab, Rahmat-e-Khuda, Roz-e-Qayamat.
   - Use hyphenated '-o-' for Izafat-e-Waw: Lail-o-Nahar, Subh-o-Sham.
   - Islamic terms: Kitabullah, Bani Israel, Insha'Allah, Masha'Allah, SubhanAllah, Alhamdulillah.
5. EMBEDDED ARABIC CITATIONS:
   - Transliterate Arabic Hadith and Quranic text citations accurately into classical Roman Arabic.
   - Preserve references e.g. (16:98), (Sahih Bukhari), (Surah Al-Baqarah: 255).
6. FORMAT:
   - Output ONLY the transliterated Roman Urdu text.
   - Do NOT wrap in markdown backticks (```).
   - Do NOT include conversational prefixes like "Here is the transliteration:".
"""


def chunk_text(text: str, max_chars: int = 1400) -> List[str]:
    """Splits long Urdu text along sentence boundaries (Khatma/Arabic periods/newlines) to prevent token exhaustion."""
    if len(text) <= max_chars:
        return [text]

    # Split on Urdu Khatma (۔), question marks (؟), exclamations (!), newlines
    sentences = re.split(r'([۔؟!\n]+)', text)
    chunks = []
    curr = ""
    for i in range(0, len(sentences), 2):
        s = sentences[i]
        sep = sentences[i + 1] if i + 1 < len(sentences) else ""
        piece = s + sep
        if len(curr) + len(piece) > max_chars and curr:
            chunks.append(curr.strip())
            curr = piece
        else:
            curr += piece

    if curr.strip():
        chunks.append(curr.strip())

    return chunks if chunks else [text]


def call_gemini(urdu_chunk: str, model: str = DEFAULT_MODEL, max_retries: int = 2) -> str:
    """Calls Gemini API with multi-key rotation, automatic exponential backoff, fast model fallbacks, and outer recovery rounds."""
    global _current_key_idx
    if not API_KEYS:
        raise ValueError("No Gemini API key configured. Please set GEMINI_API_KEY in .env.")

    models_to_try = [model] + [m for m in FALLBACK_MODELS if m != model]

    for pool_round in range(6):
        if pool_round > 0:
            wait_time = 15.0 * pool_round
            print(f"\nAll models/keys temporarily busy. Waiting {wait_time:.0f}s before pool retry (attempt {pool_round + 1}/6)...")
            time.sleep(wait_time)

        for current_model in models_to_try:
            # Try across available API keys
            for key_attempt in range(len(API_KEYS)):
                current_key = API_KEYS[_current_key_idx]
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{current_model}:generateContent?key={current_key}"
                payload = {
                    "contents": [
                        {
                            "parts": [
                                {
                                    "text": f"{SYSTEM_PROMPT}\n\nUrdu Source Text to Transliterate:\n{urdu_chunk}"
                                }
                            ]
                        }
                    ],
                    "generationConfig": {
                        "temperature": 0.1,
                        "topP": 0.95,
                        "maxOutputTokens": 8192
                    }
                }

                for attempt in range(max_retries):
                    try:
                        resp = requests.post(url, json=payload, timeout=45)
                        if resp.status_code == 200:
                            data = resp.json()
                            candidates = data.get("candidates", [])
                            if candidates and "content" in candidates[0]:
                                parts = candidates[0]["content"].get("parts", [])
                                if parts:
                                    res_text = parts[0].get("text", "").strip()
                                    if res_text.startswith("```"):
                                        res_text = re.sub(r"^```[a-zA-Z]*\n?", "", res_text)
                                        res_text = re.sub(r"\n?```$", "", res_text).strip()
                                    finish_reason = candidates[0].get("finishReason", "")
                                    if finish_reason == "MAX_TOKENS" or (len(urdu_chunk) > 150 and len(res_text) < 0.65 * len(urdu_chunk)):
                                        print(f"Warning: Incomplete output detected ({finish_reason=}, ratio={len(res_text)/len(urdu_chunk):.2f}). Retrying...")
                                        continue
                                    return res_text
                        elif resp.status_code in (429, 503):
                            # Rotate key if multi-key available
                            if len(API_KEYS) > 1:
                                _current_key_idx = (_current_key_idx + 1) % len(API_KEYS)
                                print(f"[{current_model}] Status {resp.status_code}. Rotated to key #{_current_key_idx + 1}...")
                            else:
                                sleep_time = 2.0 * (attempt + 1)
                                print(f"[{current_model}] Status {resp.status_code}. Backing off {sleep_time}s...")
                                time.sleep(sleep_time)
                            break  # Try next key or model
                        else:
                            print(f"[{current_model}] Error HTTP {resp.status_code}: {resp.text[:100]}")
                            break  # Try next model
                    except requests.exceptions.RequestException as e:
                        sleep_time = 2.0
                        print(f"Network issue on {current_model}: {e}. Trying next model...")
                        time.sleep(sleep_time)
                        break

    raise RuntimeError(f"All models failed to transliterate chunk of length {len(urdu_chunk)}")


def transliterate_surah(surah: int, data_ur_dir: str = "data/ur", data_ru_dir: str = "data/roman_urdu", overwrite: bool = False, model: str = DEFAULT_MODEL) -> bool:
    """Processes all ayahs of a surah with chunk-level checkpointing, saving to data/roman_urdu/{surah}.json."""
    ur_path = Path(data_ur_dir) / f"{surah}.json"
    ru_path = Path(data_ru_dir) / f"{surah}.json"
    checkpoint_dir = Path("data/.checkpoints")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_path = checkpoint_dir / f"{surah}_checkpoint.json"

    if not ur_path.exists():
        print(f"❌ Error: Source file not found: {ur_path}")
        return False

    if ru_path.exists() and not overwrite:
        print(f"⏩ Surah {surah} already exists at {ru_path}. Skipping (use --overwrite to re-run).")
        return True

    print(f"\n=======================================================")
    print(f"  Transliterating Surah {surah} with model: {model}")
    print(f"=======================================================")

    with open(ur_path, "r", encoding="utf-8") as f:
        ur_ayahs = json.load(f)

    # Load persistent chunk checkpoints if available
    checkpoints: Dict[str, str] = {}
    if checkpoint_path.exists() and not overwrite:
        try:
            with open(checkpoint_path, "r", encoding="utf-8") as f:
                checkpoints = json.load(f)
            print(f"Loaded {len(checkpoints)} cached parts from checkpoint.")
        except Exception:
            checkpoints = {}

    def save_checkpoint():
        try:
            with open(checkpoint_path, "w", encoding="utf-8") as f:
                json.dump(checkpoints, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save checkpoint: {e}")

    # Cache translations for duplicate text bodies (e.g. grouped ayahs)
    text_cache: Dict[str, str] = {}
    ru_ayahs = []

    total_ayahs = len(ur_ayahs)
    for idx, ayah_item in enumerate(ur_ayahs, start=1):
        ayah_num = ayah_item.get("ayah")
        ur_text = ayah_item.get("text", "")

        print(f"Ayah {ayah_num}/{total_ayahs} ({len(ur_text)} chars)...", end=" ", flush=True)

        if not ur_text.strip():
            ru_ayahs.append({
                "surah": surah,
                "ayah": ayah_num,
                "text": ""
            })
            print("Empty.")
            continue

        if ur_text in text_cache:
            ru_text = text_cache[ur_text]
            print("(cached)")
        else:
            chunks = chunk_text(ur_text, max_chars=2500)
            ru_chunks = []
            for c_idx, chunk in enumerate(chunks, start=1):
                chunk_key = f"{ayah_num}_{c_idx}"
                if len(chunks) > 1:
                    print(f"[part {c_idx}/{len(chunks)}]", end=" ", flush=True)

                if chunk_key in checkpoints:
                    translated_part = checkpoints[chunk_key]
                    print("(ckpt)", end=" ", flush=True)
                else:
                    translated_part = call_gemini(chunk, model=model)
                    checkpoints[chunk_key] = translated_part
                    save_checkpoint()
                    # Polite interval between API calls
                    time.sleep(0.5)

                ru_chunks.append(translated_part)

            ru_text = "\n\n".join(ru_chunks)
            text_cache[ur_text] = ru_text
            print(f"Done ({len(ru_text)} chars).")

        ru_ayahs.append({
            "surah": surah,
            "ayah": ayah_num,
            "text": ru_text
        })

    # Sort sequentially by numerical ayah
    ru_ayahs.sort(key=lambda x: int(x.get("ayah", 0)))

    # Save to destination atomically
    ru_path.parent.mkdir(parents=True, exist_ok=True)
    with open(ru_path, "w", encoding="utf-8") as f:
        json.dump(ru_ayahs, f, ensure_ascii=False, indent=2)

    print(f" Saved Surah {surah} to {ru_path}")

    # Clean up checkpoint after successful full save
    if checkpoint_path.exists():
        try:
            checkpoint_path.unlink()
        except Exception:
            pass

    # Immediately run linter verification
    try:
        from linter import TafsirLinter
        linter = TafsirLinter(data_ur_dir=data_ur_dir, data_ru_dir=data_ru_dir)
        passed, issues, metrics = linter.lint_file(surah)
        if passed:
            print(f" Linter passed for Surah {surah} (Ratio: {metrics['ratio']:.2f}x)")
        else:
            print(f"⚠️  Linter found {len(issues)} issue(s) in Surah {surah}:")
            for is_msg in issues[:5]:
                print(f"   - {is_msg}")
    except Exception as e:
        print(f"Notice: Linter run skipped: {e}")

    return True


def main():
    parser = argparse.ArgumentParser(description="Transliterate Tafsir Ibn Kathir into Roman Urdu using Gemini.")
    parser.add_argument("--surah", type=int, help="Single Surah number (1..114)")
    parser.add_argument("--surahs", type=int, nargs="+", help="List of Surah numbers, e.g. 1 112 113 114")
    parser.add_argument("--range", type=int, nargs=2, metavar=("START", "END"), help="Range of Surahs, e.g. 78 114")
    parser.add_argument("--all", action="store_true", help="Process all 114 Surahs")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Gemini model name (default: {DEFAULT_MODEL})")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite already generated files")
    parser.add_argument("--ur-dir", default="data/ur", help="Urdu source directory")
    parser.add_argument("--ru-dir", default="data/roman_urdu", help="Roman Urdu target directory")

    args = parser.parse_args()

    targets = []
    if args.surah:
        targets = [args.surah]
    elif args.surahs:
        targets = args.surahs
    elif args.range:
        targets = list(range(args.range[0], args.range[1] + 1))
    elif args.all:
        targets = list(range(1, 115))
    else:
        print("Please specify --surah, --surahs, --range, or --all.")
        return

    print(f"Starting transliteration pipeline for {len(targets)} Surah(s)...")
    for s in targets:
        transliterate_surah(
            surah=s,
            data_ur_dir=args.ur_dir,
            data_ru_dir=args.ru_dir,
            overwrite=args.overwrite,
            model=args.model
        )


if __name__ == "__main__":
    main()
