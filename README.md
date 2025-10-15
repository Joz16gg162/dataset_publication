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
- **Volumen estimado:** ~15.000–20.000 disposiciones anuales  
- **Idioma:** Español  
- **Licencia:** Basado en datos públicos del BOE, reutilizables bajo las condiciones de la AEBOE (Resolución de 27 de junio de 2024) y distribuidos bajo licencia CC BY 4.0.

El corpus resultante permite estudiar **patrones lingüísticos, temáticos y temporales** del BOE, así como desarrollar modelos de **clasificación jurídica, análisis semántico o detección de tendencias normativas**.

---

## ⚙️ Proceso de obtención y transformación

El script `boe_sumario_text_json.py` realiza las siguientes etapas:

1. **Descarga diaria del sumario del BOE** (`/datosabiertos/api/boe/sumario/{YYYYMMDD}`)  
   Se obtiene el listado estructurado de disposiciones y anuncios de cada fecha.

2. **Extracción de metadatos:**  
   Se registran campos como sección, departamento, epígrafe, título e identificador oficial (`BOE-A-XXXX-YYYY`).

3. **Obtención del texto principal:**  
   - Fuente principal: XML oficial (`xml.php?id=...`)  
   - Fallback: versión HTML (`txt.php?id=...`) cuando el XML no incluye cuerpo textual.  
   - Se conserva el texto íntegro, **incluyendo firmas y notas editoriales.**

4. **Normalización y limpieza ligera:**  
   - Normalización Unicode (NFKC)  
   - Eliminación de duplicados, espacios y saltos múltiples  
   - Conversión de fechas y derivación de `mes` y `trimestre`

5. **Clasificación temática automática (MVP):**  
   Basada en palabras clave del título (Sanidad, Educación, Economía, etc.).

6. **Serialización final en formato JSONL**, una línea por disposición, lista para carga directa en Python, R o SQL.

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

> ⚠️ Los campos de URLs (`url_html`, `url_xml`, `url_pdf`) se eliminan del dataset final para reducir tamaño, aunque se conservan durante el proceso de extracción.

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

