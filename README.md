# 📘 Dataset: Disposiciones del Boletín Oficial del Estado (BOE) – Texto estructurado 2024

Este repositorio contiene el proceso y los datos estructurados del **Boletín Oficial del Estado (BOE)** de España, obtenidos mediante su **API pública de datos abiertos**.  
El objetivo es construir un **corpus anual en formato JSONL** con información textual y metadatos de cada disposición publicada durante el año 2024, **listo para análisis con IA, PLN o minería de texto**.

El dataset ha sido generado de manera transparente y documentada, utilizando el script `boe_sumario_text_json.py`, que descarga los sumarios del BOE, extrae el texto completo de cada disposición y lo organiza en un formato limpio, unificado y reutilizable.

---

## 🧭 Descripción general

- **Fuente original:** [Agencia Estatal Boletín Oficial del Estado](https://www.boe.es)
- **Periodo cubierto:** Año **2024** completo  
- **Formato de salida:** JSON Lines (`.jsonl` o `.jsonl.gz`)  
- **Granularidad:** 1 registro por disposición o anuncio publicado  
- **Volumen estimado:** ~70.000–80.000 disposiciones anuales  
- **Idioma:** Español  
- **Licencia:** Basado en datos públicos del BOE, reutilizables bajo las condiciones de la AEBOE (Resolución de 27 de junio de 2024) y distribuidos bajo licencia CC BY 4.0.

El corpus resultante permite estudiar **patrones lingüísticos, temáticos y temporales** del BOE, así como desarrollar modelos de **clasificación jurídica, análisis semántico o detección de tendencias normativas**.

---

---

## 📘 Documentación del dataset

La documentación completa de la estructura del conjunto de datos —incluyendo su estructura detallada, proceso de recolección, transformaciones, clasificación temática y política de mantenimiento— se encuentra en el **datasheet oficial**:

👉 [Ver datasheet completo (data/datasheet_boe_2024.md)](data/datasheet_boe_2024.md)

Este documento sigue el formato propuesto por *Datasheets for Datasets* (Gebru et al., 2021) y describe todas las variables, decisiones de diseño y consideraciones éticas o legales asociadas al dataset.

---

## ⚙️ Proceso de obtención y transformación

The main script `boe_sumario_text_json.py` implements the complete workflow for downloading, parsing, and transforming data from the Official Spanish Government Gazette (BOE), using the official BOE Open Data API.

1. **Data Retrieval:**
   Data is obtained directly from the BOE Open Data API:
   (`/datosabiertos/api/boe/sumario/{YYYYMMDD}`)  
   For each date in the range (e.g., 2024/01/01 → 2024/12/31), the script requests       the daily BOE summary, which returns a hierarchical XML/JSON structure with the       following nodes
   - `<sumario>` → Root node containing the full daily summary 
   - `<metadatos>` → Metadata about the publication (type of issue, publication date)
   - `<diario>` → Individual BOE issue of that day  
   - `<seccion>` → Section (e.g., I. General Provisions, II. Authorities and Personnel, III. Other Provisions, IV. Announcements, etc.)  
   - `<departamento>` → Ministry, public institution, or issuing authority  
   - `<epigrafe>` → Thematic or legal subcategory within each section
   - `<item>` → Specific document, such as a law, resolution, order, decree, or public notice

   (Reference: [BOE API documentation, 2024](https://www.boe.es/datosabiertos/documentos/APIsumarioBOE.pdf)).

2. **Metadata Extraction:**  
   For each item, the script captures structured fields such as section, department, epigraph, title, official identifier (BOE-A-XXXX-YYYY), publication date and reference URLs (url_xml, url_html).

3. **Text Retrieval:**  
   After metadata extraction, the script attempts to obtain the complete textual body of each BOE document.
   - Primary source: official XML (`xml.php?id=...`), which usually contains the full legal text in structured form.
   - Fallback: HTML version (`txt.php?id=...`), sed when the XML lacks a <texto>          section or omits the full content.
   Full content is preserved (signatures, apprendices, editorial notes).
   Optionally, text can be truncated (e.g., to 25,000 characters) for lightweight        exploration or storage efficiency 

4. **Normalización y limpieza ligera:**  
   Once text extraction is completed, a series of normalization and enrichment steps     are applied to enhance data quality and analytical usability:
     - *Unicode normalization (NFKC)*: standardizes characters and encodings for                consistent text representation.
     - *Whitespace cleanup*: collapses multiple spaces, newlines, and redundant line breaks.
     - *Deduplication*: removes duplicate entries caused by repeated API retrievals or          content overlaps.
   
      - *Temporal derivation*: parses the publication date and automatically derives both  month (*mes*) and quarter (*trimestre*) fields for time-based analysis.
      - *Coarse thematic classification (tematic)*: assigns a preliminary semantic label       based on keyword detection in the title (e.g., Sanidad, Educación, Economía,          Justicia, etc.), enabling quick exploratory categorization without external             models.
   These transformations ensure a standardized, machine-readable, and analysis-ready dataset while preserving all essential legal and contextual information

5. **Serialization and Output:**  
   After processing, all records are serialized into JSON Lines (JSONL) format, where each line corresponds to one BOE disposition or document.
   This format facilitates efficient streaming, line-by-line parsing, and direct loading in Python, R, SQL, or big data frameworks.
   Optionally, output files can be compressed using gzip (.jsonl.gz) for storage efficiency.

---

## 📄 Estructura de los datos

Cada registro del dataset contiene los siguientes campos:

| Campo | Descripción | Ejemplo |
|--------|--------------|---------|
| `identificador` | Código oficial de la disposición | `"BOE-A-2024-1234"` |
| `fecha` | Fecha de publicación | `"2024-01-08"` |
| `diario_numero` | Número de diario dentro del año | `"7"` |
| `seccion_codigo` | Código interno de la sección | `"2A"` |
| `seccion_nombre` | Nombre de la sección oficial | `"II. Autoridades y personal. - A. Nombramientos, situaciones e incidencias"` |
| `departamento_nombre` | Ministerio u organismo responsable | `"MINISTERIO DE HACIENDA Y FUNCIÓN PÚBLICA"` |
| `epigrafe_nombre` | Subcategoría o epígrafe temático | `"Nombramientos"` |
| `titulo` | Título completo de la disposición | `"Resolución de 21 de diciembre de 2023, de la Universidad de Murcia, por la que se nombra Catedráticos..."` |
| `tematica` | Clasificación temática por palabras clave | `"Educación/Universidad"` |
| `texto_limpio` | Texto completo de la disposición (extraído del XML/HTML) | `"En virtud de lo establecido en el artículo 15 del Estatuto... Murcia, 1 de enero de 2024..."` |
| `mes` | Mes de publicación (`YYYY-MM`) | `"2024-01"` |
| `trimestre` | Trimestre natural (`Q1–Q4`) | `"Q1"` |

> Existen campos de URLs (`url_html`, `url_xml`, `url_pdf`), estos se eliminan del dataset final para reducir tamaño, aunque se conservan durante el proceso de extracción.

---

## 🧰 Requisitos

```bash
python >= 3.9
Para reproducir el proceso de extracción o generar nuevamente el dataset, instala las dependencias indicadas en el archivo `requirements.txt`:

```bash
pip install -r requirements.txt

```

---

## 🚀 Ejecución

### Ejemplo 1: Descargar solo la base (sin texto)

```bash
python boe_sumario_text_json.py --year 2024 --out-base data/base_2024.jsonl --gzip
```

### Ejemplo 2: Descargar también el texto desde el XML

```bash
python boe_sumario_text_json.py --year 2024 --out-base data/base_2024_text.jsonl --inline-text --truncate-text 25000 --gzip
```

### Parámetros principales

| Parámetro | Descripción |
|------------|-------------|
| `--year` | Año a procesar (requerido) |
| `--out-base` | Ruta de salida del JSONL |
| `--inline-text` | Descarga y agrega `texto_limpio` |
| `--truncate-text` | Recorta el texto a N caracteres |
| `--gzip` | Guarda comprimido (`.jsonl.gz`) |
| `--max-texts` | Límite opcional de textos (debug) |
| `--sleep-day` | Pausa entre días (default: 0.10 s) |
| `--sleep-text` | Pausa entre descargas (default: 0.20 s) |

---

## 🔍 Ejemplo de registro JSON

```json
{
  "identificador": "BOE-A-2024-11842",
  "fecha": "2024-01-08",
  "diario_numero": "7",
  "seccion_codigo": "2A",
  "seccion_nombre": "II. Autoridades y personal. - A. Nombramientos, situaciones e incidencias",
  "departamento_nombre": "UNIVERSIDADES",
  "epigrafe_nombre": "Nombramientos",
  "titulo": "Resolución de 21 de diciembre de 2023, de la Universidad de Murcia...",
  "tematica": "Educación/Universidad",
  "texto_limpio": "En virtud de lo establecido... Murcia, 1 de enero de 2024. — El Rector, José Luján Alcaraz.",
  "mes": "2024-01",
  "trimestre": "Q1"
}
```

---

## 📊 Cómo cargar el dataset

```python
import pandas as pd

# JSONL normal
df = pd.read_json("data/base_2024_text.jsonl", lines=True)

# JSONL comprimido
df = pd.read_json("data/base_2024_text.jsonl.gz", lines=True, compression="gzip")

print(df.head())
```

---

## 🧠 Posibles usos analíticos

- Clasificación de **temas normativos** (aprendizaje supervisado o embeddings)  
- **Resumen automático** o extracción de entidades (NLP jurídico)  
- Análisis de **tendencias legislativas** por ministerio o trimestre  
- Estudio de **frecuencia temática** y **lenguaje jurídico**

---

## 📈 Indicadores de ejecución

Durante la descarga y el procesamiento, el script muestra logs como:

```
[412/15840] Procesando BOE-A-2024-11842...
✔️ BOE-A-2024-11842 (XML) → 14,236 caracteres | 8.3 docs/min
```

Esto permite monitorear:
- Progreso total  
- Fuente del texto (XML/HTML)  
- Longitud del texto  
- Velocidad de procesamiento

---

## 🧾 Limitaciones

- No todos los documentos del BOE contienen texto accesible vía XML.  
- La estructura interna varía según tipo (A, B, C...).  
- La clasificación temática es **heurística** (basada en palabras clave del título).  
- Se conserva el texto íntegro, por lo que incluye **firmas, anexos y notas editoriales.**

---

## 🧩 Créditos y atribución

- **Datos originales:** Agencia Estatal Boletín Oficial del Estado (AEBOE)  
- **Licencia de uso:** según condiciones de reutilización del BOE  
- **Autor del script y dataset:** [Tu nombre o equipo]  
- **Versión:** 1.0 (Octubre 2025)

---

## ⚖️ Licencia y reutilización

Este dataset deriva de información pública del **Boletín Oficial del Estado (BOE)**, obtenida mediante su [API de datos abiertos](https://www.boe.es/datosabiertos/), conforme a la **Resolución de la Agencia Estatal BOE de 27 de junio de 2024**, sobre condiciones de reutilización.

> **Basado en datos de la [Agencia Estatal Boletín Oficial del Estado](https://www.boe.es)**.  
> Este dataset no tiene carácter oficial ni sustituye a la edición electrónica auténtica del BOE.

La reutilización de este dataset se permite bajo una licencia **CC BY 4.0** (atribución requerida), siempre que se cite la fuente y se respete la normativa aplicable.

