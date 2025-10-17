# 📘 Dataset: Official State Gazette (BOE) Provisions – Structured Text 2024

This repository contains the process and structured data from the **Boletín Oficial del Estado (BOE)** of Spain, obtained through its **public open data API**.  
The goal is to build an **annual corpus in JSONL format** with textual information and metadata for each provision published during 2024, **ready for AI, NLP, or text mining analysis**.

The dataset has been generated transparently and documented using the `boe_sumario_text_json.py` script, which downloads BOE summaries, extracts the full text of each provision, and organizes it into a clean, unified, and reusable format.

---

## 🧭 Overview

- **Original source:** [Agencia Estatal Boletín Oficial del Estado](https://www.boe.es)
- **Covered period:** Full year **2024**
- **Output format:** JSON Lines (`.jsonl` or `.jsonl.gz`)
- **Granularity:** 1 record per published provision or announcement  
- **Estimated volume:** ~70,000–80,000 annual provisions  
- **Language:** Spanish  
- **License:** Based on public BOE data, reusable under AEBOE conditions (Resolution of June 27, 2024), and distributed under CC BY 4.0.

The resulting corpus allows the study of **linguistic, thematic, and temporal patterns** of the BOE and supports the development of **legal classification, semantic analysis, or regulatory trend detection models**.

---

## 📘 Dataset documentation

Full dataset structure documentation — including detailed structure, collection process, transformations, thematic classification, and maintenance policy — is available in the **official datasheet**:

👉 [View full datasheet (data/datasheet_boe_2024.md)](data/datasheet_boe_2024.md)

This document follows the *Datasheets for Datasets* format (Gebru et al., 2021) and describes all variables, design decisions, and ethical or legal considerations associated with the dataset.

---

## ⚙️ Retrieval and transformation process

The main script `boe_sumario_text_json.py` implements the complete workflow for downloading, parsing, and transforming data from the Official Spanish Government Gazette (BOE) using the official Open Data API.

1. **Data Retrieval:**  
   Data is obtained directly from the BOE Open Data API:
   (`/datosabiertos/api/boe/sumario/{YYYYMMDD}`)  
   For each date within the range (e.g., 2024/01/01 → 2024/12/31), the script requests the daily BOE summary, which returns a hierarchical XML/JSON structure with the following nodes:
   - `<sumario>` → Root node containing the full daily summary  
   - `<metadatos>` → Metadata about the publication (type of issue, publication date)  
   - `<diario>` → Daily issue node  
   - `<seccion>` → Section (I. General Provisions, II. Authorities and Personnel, III. Other Provisions, IV. Announcements, etc.)  
   - `<departamento>` → Ministry, public institution, or issuing authority  
   - `<epigrafe>` → Optional thematic grouping (sections 1, 2A, 2B, 3, 5)  
   - `<item>` → Individual document (law, resolution, order, decree, or notice)  

   Each `<item>` includes its identifier (BOE-A-XXXX-YYYY), title, and canonical URLs for XML, HTML, and PDF versions.  
   (Reference: [BOE API documentation, 2024](https://www.boe.es/datosabiertos/documentos/APIsumarioBOE.pdf))

2. **Text Retrieval:**  
   After metadata extraction, the script obtains the complete text body of each document.  
   - Primary source: official XML (`xml.php?id=...`)  
   - Fallback: HTML version (`txt.php?id=...`) when XML lacks `<texto>` content  
   Full content is preserved (signatures, appendices, editorial notes).  
   Optionally, text can be truncated (e.g., 25,000 characters) for lightweight exploration or efficiency.

3. **Normalization and light cleaning:**  
   Once extraction is complete, normalization and enrichment steps enhance data quality:
   - *Unicode normalization (NFKC)* for consistent encoding  
   - *Whitespace cleanup* (removes redundant spaces and breaks)  
   - *Deduplication* of repeated entries  
   - *Temporal derivation* (`month`, `quarter` fields)  
   - *Heuristic classification* (e.g., Health, Education, Economy, Justice) based on title keywords  

4. **Serialization and Output:**  
   All records are serialized into JSON Lines (`.jsonl`), one per document.  
   Optionally compressed with gzip (`.jsonl.gz`) for efficiency.

---

## 📄 Data structure

| Field | Description | Example |
|--------|--------------|---------|
| `identificador` | Official provision code | `"BOE-A-2024-1234"` |
| `fecha` | Publication date | `"2024-01-08"` |
| `diario_numero` | Daily issue number | `"7"` |
| `seccion_codigo` | Section code | `"2A"` |
| `seccion_nombre` | Section name | `"II. Authorities and Personnel - A. Appointments"` |
| `departamento_nombre` | Ministry or institution | `"MINISTRY OF FINANCE AND PUBLIC FUNCTION"` |
| `epigrafe_nombre` | Subcategory | `"Appointments"` |
| `titulo` | Full title | `"Resolution of December 21, 2023, of the University of Murcia..."` |
| `tematica` | Thematic classification | `"Education/University"` |
| `texto_limpio` | Full text extracted from XML/HTML | `"Pursuant to Article 15 of the Statute... Murcia, January 1, 2024..."` |
| `mes` | Month of publication (`YYYY-MM`) | `"2024-01"` |
| `trimestre` | Quarter (`Q1–Q4`) | `"Q1"` |

---

## 🧰 Requirements

```bash
python >= 3.9
pip install -r requirements.txt
```

---

## 🚀 Execution

### Example 1: Download base only (no text)

```bash
python boe_sumario_text_json.py --year 2024 --out-base data/base_2024.jsonl --gzip
```

### Example 2: Download including text

```bash
python boe_sumario_text_json.py --year 2024 --out-base data/base_2024_text.jsonl --inline-text --truncate-text 25000 --gzip
```

---

## 🔍 Example JSON record

```json
{
  "identificador": "BOE-A-2024-11842",
  "fecha": "2024-01-08",
  "diario_numero": "7",
  "seccion_codigo": "2A",
  "seccion_nombre": "II. Authorities and Personnel - A. Appointments",
  "departamento_nombre": "UNIVERSITIES",
  "epigrafe_nombre": "Appointments",
  "titulo": "Resolution of December 21, 2023, of the University of Murcia...",
  "tematica": "Education/University",
  "texto_limpio": "Pursuant to the provisions... Murcia, January 1, 2024. — The Rector, José Luján Alcaraz.",
  "mes": "2024-01",
  "trimestre": "Q1"
}
```

---

## 🧠 Analytical applications

- **Legal topic classification** (supervised learning or embeddings)  
- **Automatic summarization** or **entity extraction** (legal NLP)  
- **Legislative trend analysis** by ministry or quarter  
- **Thematic frequency** and **legal language** studies  

---

## ⚖️ License and attribution

Licensed under Creative Commons Attribution 4.0 International (**CC BY 4.0**).
You are free to use, modify, and redistribute the code provided in this repository, provided that appropriate credit is given and all applicable laws are respected.

Data reference (external resource):
This repository references or interacts with data derived from the Boletín Oficial del Estado (BOE), obtained via its public Open Data API.
These data are governed by the “[Condiciones de reutilización](https://www.boe.es/informacion/aviso_legal/index.php#reutilizacion)” established in the Resolución de la Agencia Estatal Boletín Oficial del Estado de 27 de junio de 2024 (Aviso Legal del BOE).

“Based on data from the Agencia Estatal Boletín Oficial del Estado (AEBOE).
This dataset is not official and does not replace the authentic electronic edition of the BOE.”

The BOE materials are reused under their own open data terms (non exclusive, free reuse with mandatory source attribution and without implying official status).
Those terms apply only to the BOE data, not to the code or documentation in this repository.

