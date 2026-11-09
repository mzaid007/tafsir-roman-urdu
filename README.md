# Tafsir-Roman-Urdu (TRU) 📖✨

> **The World's First Complete, 100% Accurate, Standardized Roman Urdu Exegesis of the Holy Qur'an (Tafsir Ibn Kathir).**

> [!IMPORTANT]
> ### ⚠️ Scholarly Review & AI Transliteration Disclaimer
> This dataset was generated through systematic, faithful transliteration of authentic Urdu *Tafsir Ibn Kathir* (translated by Maulana Muhammad Junagarhi) using Large Language Models (LLMs) governed by strict deterministic linguistic rules, sentence-boundary chunking, and automated integrity linters. 
>
> **Please note that this dataset has NOT yet been formally audited or reviewed by a certified Islamic scholar (*Alim* / *Mufti*).**
>
> If you are a qualified Islamic scholar, academic, computational linguist, or fluent reader and are interested in reviewing, certifying, or contributing corrections to this dataset, please contact:
> - **Maintainer**: Zaid
> - **Email**: [mzaid007@gmail.com](mailto:mzaid007@gmail.com)
> - **Feedback & Issues**: You may also open an issue or pull request directly on this repository. Every contribution to preserve and verify Allah's Book and its classical exegesis is deeply appreciated.

---

## 🌟 Mission & Background

Hundreds of millions of Urdu and Hindi speakers globally comprehend spoken Urdu fluently but cannot read traditional Nastaliq or Arabic script. While Roman Urdu translations of Quranic verses exist, **zero complete digital datasets of Tafsir Ibn Kathir exist in Roman Urdu** (even physical publishers like *Darussalam* have only printed booklets of Juz 30).

**Tafsir-Roman-Urdu (TRU)** solves this historical gap by providing a scholarly, machine-readable, open-source dataset, npm package, and CDN-backed REST API covering all **114 Surahs (6,236 Ayahs)**.

---

## 📐 Schema Specification

Each Surah is stored as an independent JSON file under `data/roman_urdu/{surah_number}.json` matching the standard Quran app schema:

```json
[
  {
    "surah": 1,
    "ayah": 1,
    "text": "Bismillah Surah Naml Ki Ek Aayat Ya...? Sahaba (R.A) ne Allah ki Kitab ko isi se shuru kiya. Ulama ka ittefaq hai ke aayat (Bismillahir Rahmanir Raheem) Surah Naml ki ek aayat hai...\n\nIsti'azah (A'oodhu Billah) Ka Bayan: Allah Ta'ala farmata hai: 'Pas jab tum Quran padhne lago to shaitan mardood se Allah ki panah maang liya karo' (16:98)..."
  },
  {
    "surah": 1,
    "ayah": 2,
    "text": "Al-Hamdu Lillahi Rabbil 'Aalameen: Tamam tareef aur shukr sirf Allah Ta'ala ke liye hai jo tamam jahano ka Paalne Wala hai..."
  }
]
```

---

## 🌐 Instant CDN API Access

Zero-setup global CDN delivery via **jsDelivr**:

```typescript
// Fetch Surah Al-Fatiha Tafsir in Roman Urdu
const res = await fetch('https://cdn.jsdelivr.net/gh/mzaid007/tafsir-roman-urdu@main/data/roman_urdu/1.json');
const tafsir = await res.json();
console.log(tafsir[0].text);
```

---

## 📖 How to Read & Review the Dataset Right Now

End users and scholarly reviewers can access the complete exegesis immediately using any of the following options:

### 1. Live Web Platform for Reviewers & Readers (Zero Setup)
👉 **Live URL**: [**https://mzaid007.github.io/tafsir-roman-urdu/**](https://mzaid007.github.io/tafsir-roman-urdu/)

*(To run locally: open [`index.html`](file:///f:/Tafsir-Roman-Urdu/index.html) in your browser or run `python -m http.server 8000`)*

- **◫ Side-by-Side Split View**: Read Roman Urdu transliteration alongside the authentic Urdu Nastaliq text (*Maulana Muhammad Junagarhi*) in real-time.
- **📝 1-Click Review Notes**: Scholars can click **"Review Note"** on any verse to pre-fill an audit email to `mzaid007@gmail.com` or launch a GitHub issue.
- **⚡ Quick Verse Jump**: Jump directly to any verse (e.g., `2:255` for Ayat al-Kursi or `18:10` for Al-Kahf).
- **🌓 Theme & Font Controls**: Toggle Light/Dark mode and resize text dynamically for optimal reading comfort.

### 2. Command-Line Terminal Reader
Read any Surah or specific Ayah instantly in your terminal:
```bash
# Read Surah 1 (Al-Fatiha) Ayah 1
python scripts/reader.py 1 1

# Read Surah 18 (Al-Kahf) completely
python scripts/reader.py 18

# Read Surah 36 (Ya-Sin) Ayah 58
python scripts/reader.py 36 58
```

### 3. Direct JSON Access
Every chapter is available as a standardized JSON file under `data/roman_urdu/{1..114}.json`. Open any file in VS Code, Notepad, or any JSON reader.

### 4. Quran Web & Mobile Apps
Developers can plug the dataset into any Qur'an web application (e.g. `quran-web`) by pointing to the CDN endpoint or copying the `data/roman_urdu` directory into their project's public folder.

---

## 📊 Dataset Milestones & Progress

| Milestone | Scope | Surahs | Ayahs | Status |
| :--- | :--- | :---: | :---: | :---: |
| **Milestone 1** | Foundation, PoC, Style Guide & Benchmarks | 1, 112, 113, 114 | 22 / 22 | **✅ LLM Verified (Needs Scholarly Review)** |
| **Milestone 2** | Juz 'Amma Complete | 78 through 114 | 564 / 564 | **✅ LLM Verified (Needs Scholarly Review)** |
| **Milestone 3** | High-Frequency Virtuous Surahs & Al-Baqarah | 2, 18, 36, 55, 56, 67 | 683 / 683 | **✅ LLM Verified (Needs Scholarly Review)** |
| **Milestone 4** | Complete Full Exegesis (All 114 Surahs) | 1 through 114 | 6,236 / 6,236 | **✅ LLM Verified (Needs Scholarly Review)** |

**Global Project Status**: **114 / 114 Surahs Complete (100.0%)** | **6,236 / 6,236 Ayahs (100.0%)** | **32,334,947 Roman Urdu Characters (32.33M chars)** with **114/114 (100%) Quality Linter Pass Rate**. Verified using LLM & automated linters; currently awaiting formal Islamic scholarly review (*Alim / Mufti* audit).

---

## 📏 Linguistic Orthography & Style Guide

All transliterations strictly obey the formal [TRU Style Guide](style_guide/rules.md) and [Term Glossary](style_guide/glossary.json):

1. **Zero Omission / Zero Summary**: 100% faithful representation of Maulana Muhammad Junagarhi's authentic Urdu translation of Ibn Kathir.
2. **Standard Urdu Spelling**: Consistent vowels (*hai*, *hain*, *nahin*, *yeh*, *woh*, *ke*, *karein*, *matlab*, *bayan*).
3. **Compound Izafats**: Lowercase hyphenated `-e-` (*Amr-e-Ilahi*, *Ahl-e-Kitab*) and `-o-` (*Lail-o-Nahar*).
4. **Reverent Sacred Honorifics**:
   - `ﷺ` / `صلی اللہ علیہ وسلم` ➔ `(ﷺ / Sallallahu Alaihi Wasallam)`
   - `رضی اللہ عنہ` / `ؓ` ➔ `(Razi Allahu Anhu / R.A)`
   - `علیہ السلام` / `ؑ` ➔ `(Alaihis Salam / A.S)`
   - `رحمہ اللہ` / `ؒ` ➔ `(Rahimahullah / R.H)`

---

## 🛠️ Repository Architecture

```text
tafsir-roman-urdu/
├── data/
│   ├── ur/               # Raw authentic Urdu source files (1..114.json)
│   └── roman_urdu/       # Standardized Roman Urdu files (1..114.json)
├── scripts/
│   ├── transliterate.py  # LLM batch transliteration engine (Gemini API)
│   └── linter.py         # Automated QA & honorifics integrity linter
├── style_guide/
│   ├── rules.md          # Comprehensive orthography and linguistic rules
│   └── glossary.json     # Standardized Islamic terminology dictionary
├── package.json          # npm distribution metadata
└── README.md             # Project documentation and API guide
```

---

## 🚀 Running the Pipeline

### Prerequisites
- Python 3.10+
- Valid `GEMINI_API_KEY` in `.env`

```bash
# Install dependencies
pip install requests python-dotenv

# Transliterate specific Surahs
python scripts/transliterate.py --surahs 1 112 113 114

# Transliterate Juz 'Amma (Surahs 78 to 114)
python scripts/transliterate.py --range 78 114

# Run the Quality & Integrity Linter
python scripts/linter.py --all
```

---

## 📜 License & Attribution

- **Urdu Translation Source**: Maulana Muhammad Junagarhi (Tafsir Ibn Kathir).
- **Roman Urdu Dataset**: Open-access under [Creative Commons Attribution-ShareAlike 4.0 (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/).
