#!/usr/bin/env python3

import os
import re
import time
import argparse
import logging
import datetime as dt
from typing import List, Dict, Optional, Iterable, Union

import requests
import pandas as pd
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import unicodedata
import json
import gzip
from io import TextIOWrapper

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

BOE_BASE = "https://www.boe.es"
SUMARIO_ENDPOINT = BOE_BASE + "/datosabiertos/api/boe/sumario/{fecha}"

HEADERS_XML = {
    "Accept": "application/xml",
    "User-Agent": "Proyecto-BOE-JSON/2.0 (+tu_repositorio)"
}

THEME_KEYWORDS = {
    "Sanidad": ["covid", "coronavirus", "sars-cov-2", "salud", "sanidad", "mascarilla", "vacuna", "vacunación"],
    "Economía/Empresa": ["impuesto", "tribut", "iva", "irpf", "subvención", "ayuda", "financiación", "ico", "contratación"],
    "Trabajo/Laboral": ["erte", "desempleo", "prestación", "laboral", "trabajo", "seguridad social", "convenio", "empleo"],
    "Educación/Universidad": ["educación", "universidad", "escolar", "alumno", "docente", "beca"],
    "Tráfico/Movilidad/Carreteras": ["tráfico", "dgt", "carretera", "autovía", "autopista", "peaje", "movilidad", "transporte", "vehículo"],
    "Vivienda/Urbanismo": ["vivienda", "alquiler", "hipoteca", "urbanismo", "rehabilitación", "arrendamiento"],
    "Energía/Medio ambiente": ["energía", "eléctrica", "renovable", "clima", "emisiones", "ambiental", "residuos"],
    "Justicia/Procedimientos": ["procedimiento", "plazo", "judicial", "tribunal", "juzgado", "sanción"],
}

def ensure_dir(path: str):
    if path and not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

def _open_text_writer(path: str, gzip_enabled: bool) -> Union[TextIOWrapper, 'TextIOWrapper']:
    if gzip_enabled:
        return TextIOWrapper(gzip.open(path, mode="wb"), encoding="utf-8", newline="\n")
    return open(path, "w", encoding="utf-8", newline="\n")

def write_jsonl(records: Iterable[Dict], out_path: str, gzip_enabled: bool = False):
    ensure_dir(os.path.dirname(out_path) or ".")
    with _open_text_writer(out_path, gzip_enabled) as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

def df_to_jsonl(df: pd.DataFrame, out_path: str, gzip_enabled: bool = False):
    records = json.loads(df.to_json(orient="records", force_ascii=False))
    write_jsonl(records, out_path, gzip_enabled=gzip_enabled)

def clean_final_text(text: str) -> str:
    if not text:
        return ""
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def classify_theme(text: str) -> str:
    t = (text or "").lower()
    for theme, kws in THEME_KEYWORDS.items():
        for kw in kws:
            if kw in t:
                return theme
    return "Otras"

def iterate_days(year: int):
    d = dt.date(year, 1, 1)
    end = dt.date(year, 12, 31)
    while d <= end:
        yield d
        d += dt.timedelta(days=1)

def robust_get(url: str, headers: dict, max_tries: int = 3, timeout: int = 30, backoff: float = 1.6) -> Optional[requests.Response]:
    last_err = None
    for i in range(max_tries):
        try:
            r = requests.get(url, headers=headers, timeout=timeout)
            if r.status_code == 200 and r.content:
                return r
            elif r.status_code in (400,404):
                logging.warning(f"HTTP {r.status_code} {url}")
                return None
            else:
                logging.warning(f"HTTP {r.status_code} {url}")
        except Exception as e:
            last_err = e
            logging.warning(f"{type(e).__name__}: {e} ({url})")
        time.sleep(backoff**(i+1))
    if last_err:
        logging.error(f"Fallo GET {url}: {last_err}")
    return None

def parse_sumario_xml(xml_text: str) -> List[Dict]:
    out: List[Dict] = []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return out

    data = root.find(".//data")
    if data is None:
        return out
    sumario = data.find(".//sumario")
    if sumario is None:
        return out

    for diario in sumario.findall(".//diario"):
        diario_numero = diario.get("numero", "")
        for seccion in diario.findall("./seccion"):
            seccion_codigo = seccion.get("codigo", "")
            seccion_nombre = seccion.get("nombre", "")
            for dept in seccion.findall("./departamento"):
                dept_cod = dept.get("codigo", "")
                dept_nom = dept.get("nombre", "")
                for epi in dept.findall("./epigrafe"):
                    epigrafe_nombre = epi.get("nombre", "")
                    for item in epi.findall("./item"):
                        out.append(_item_to_row(item, diario_numero, seccion_codigo, seccion_nombre,
                                                dept_cod, dept_nom, epigrafe_nombre))
                for item in dept.findall("./item"):
                    out.append(_item_to_row(item, diario_numero, seccion_codigo, seccion_nombre,
                                            dept_cod, dept_nom, ""))
    return out

def _get_text(node, path):
    el = node.find(path)
    return (el.text or "").strip() if el is not None and el.text else ""

def _get_attr(node, path, attr):
    el = node.find(path)
    return el.get(attr, "") if el is not None else ""

def _item_to_row(item, diario_num, sec_cod, sec_nom, dep_cod, dep_nom, epi_nom):
    return {
        "fecha": None,
        "diario_numero": diario_num,
        "seccion_codigo": sec_cod,
        "seccion_nombre": sec_nom,
        "departamento_codigo": dep_cod,
        "departamento_nombre": dep_nom,
        "epigrafe_nombre": epi_nom,
        "identificador": _get_text(item, "./identificador"),
        "titulo": _get_text(item, "./titulo"),
        "url_html": _get_text(item, "./url_html"),
        "url_xml": _get_text(item, "./url_xml"),
        "url_pdf": _get_text(item, "./url_pdf"),
        "szBytes": _get_attr(item, "./url_pdf", "szBytes"),
        "szKBytes": _get_attr(item, "./url_pdf", "szKBytes"),
        "pagina_inicial": _get_attr(item, "./url_pdf", "pagina_inicial"),
        "pagina_final": _get_attr(item, "./url_pdf", "pagina_final"),
    }

def extract_plain_from_xml(xml_bytes_or_str) -> str:
    soup = BeautifulSoup(xml_bytes_or_str, "lxml-xml")
    root = (soup.find("disposicion") or soup.find("documento") or soup)

    parts = []
    textos = root.find_all("texto")
    for t in textos:
        txt = t.get_text(" ", strip=True)
        if txt:
            parts.append(txt)

    for node in root.find_all(["articulo","capitulo","titulo","seccion","apartado","epigrafe","parrafo"]):
        head = node.get("titulo") or node.get("nombre")
        if head:
            parts.append(head.strip())
        for p in node.find_all(["p","li"]):
            txt = p.get_text(" ", strip=True)
            if len(txt) >= 1:
                parts.append(txt)

    if not parts:
        for p in root.find_all(["p","li"]):
            txt = p.get_text(" ", strip=True)
            if len(txt) >= 1:
                parts.append(txt)

    plain = "\n".join([x for x in parts if x and x.strip()])
    return clean_final_text(plain)

def extract_plain_from_html(html_bytes_or_str, known_title=None) -> str:
    soup = BeautifulSoup(html_bytes_or_str, "lxml")
    for sel in ["nav","header","footer",".pie",".breadcrumbs","#barra_cabecera","#barra_portada",".enlaces",".reproductor"]:
        for el in soup.select(sel):
            el.decompose()

    h1 = soup.find("h1")
    if h1 and known_title:
        h1_text = " ".join(h1.get_text(" ", strip=True).split())
        if h1_text.lower() == known_title.strip().lower():
            h1.decompose()

    main = soup.select_one("#text, .texto, #contenido, article, .contenido") or soup.body or soup
    parts = []
    for tag in main.find_all(["p","li","blockquote","h4","h5","h6"]):
        txt = " ".join(tag.get_text(" ", strip=True).split())
        if txt:
            parts.append(txt)

    plain = "\n".join(parts)
    return clean_final_text(plain)

def attach_inline_text(df_base: pd.DataFrame,
                       sleep: float = 0.2,
                       max_texts: Optional[int] = None,
                       truncate_text: Optional[int] = None) -> pd.DataFrame:
    df = df_base.copy()
    if "texto_limpio" not in df.columns:
        df["texto_limpio"] = ""

    processed = 0
    start = time.time()

    for idx, row in df.iterrows():
        if max_texts and processed >= max_texts:
            break

        boe_id = row.get("identificador", "")
        url_xml = row.get("url_xml", "")
        url_html = row.get("url_html", "")
        titulo = row.get("titulo", "")

        logging.info(f"[{processed+1}/{len(df)}] Procesando {boe_id or '(sin id)'}...")

        body_plain = ""
        source = "N/A"

        if url_xml and url_xml.startswith(("http://","https://")):
            rx = robust_get(url_xml, headers=HEADERS_XML)
            if rx:
                try:
                    body_plain = extract_plain_from_xml(rx.content)
                    source = "XML"
                except Exception as e:
                    logging.warning(f"Parse XML error {type(e).__name__}: {e} ({url_xml})")

        if not body_plain and url_html and url_html.startswith(("http://","https://")):
            rh = robust_get(url_html, headers={"User-Agent": HEADERS_XML["User-Agent"]})
            if rh:
                try:
                    body_plain = extract_plain_from_html(rh.content, known_title=titulo)
                    source = "HTML"
                except Exception as e:
                    logging.warning(f"Parse HTML error {type(e).__name__}: {e} ({url_html})")

        if not body_plain:
            logging.warning(f"⚠️ Texto vacío: {boe_id or url_html or url_xml}")
            time.sleep(sleep)
            continue

        if truncate_text and len(body_plain) > truncate_text:
            body_plain = body_plain[:truncate_text].rstrip() + "…"

        df.at[idx, "texto_limpio"] = body_plain
        processed += 1

        elapsed = (time.time() - start) / 60
        speed = processed / elapsed if elapsed > 0 else 0
        logging.info(f"✔️ {boe_id} ({source}) → {len(body_plain):,} caracteres | {speed:.1f} docs/min")

        time.sleep(sleep)

    return df

def robust_get_sumario_xml(url: str, max_tries: int = 3, timeout: int = 25, backoff: float = 1.6) -> Optional[str]:
    last_err = None
    for i in range(max_tries):
        try:
            r = requests.get(url, headers=HEADERS_XML, timeout=timeout)
            if r.status_code == 200 and r.text.strip():
                return r.text
            elif r.status_code in (400, 404):
                logging.warning(f"HTTP {r.status_code} en {url}")
                return None
            else:
                logging.warning(f"HTTP {r.status_code} en {url}")
        except Exception as e:
            last_err = e
            logging.warning(f"Error {type(e).__name__}: {e}")
        time.sleep(backoff ** (i + 1))
    if last_err:
        logging.error(f"Fallo al obtener {url}: {last_err}")
    return None

def build_base(year: int, sleep_each_day: float = 0.1) -> pd.DataFrame:
    rows: List[Dict] = []
    for d in iterate_days(year):
        fecha_api = d.strftime("%Y%m%d")
        fecha_hum = d.strftime("%Y-%m-%d")
        url = SUMARIO_ENDPOINT.format(fecha=fecha_api)
        logging.info(f"Sumario {fecha_hum}")
        xml_text = robust_get_sumario_xml(url)
        if not xml_text:
            continue
        items = parse_sumario_xml(xml_text)
        for it in items:
            titulo = (it.get("titulo") or "").strip()
            if not titulo:
                continue
            it["fecha"] = fecha_hum
            it["tematica"] = classify_theme(titulo)
            rows.append(it)
        time.sleep(sleep_each_day)

    df = pd.DataFrame(rows)
    if df.empty:
        logging.warning("No se obtuvieron filas del año solicitado.")
        return df

    dt_series = pd.to_datetime(df["fecha"], errors="coerce")
    df["mes"] = dt_series.dt.strftime("%Y-%m")
    qmap = {1:"Q1",2:"Q1",3:"Q1",4:"Q2",5:"Q2",6:"Q2",7:"Q3",8:"Q3",9:"Q3",10:"Q4",11:"Q4",12:"Q4"}
    df["trimestre"] = dt_series.dt.month.map(qmap)
    return df

def main():
    ap = argparse.ArgumentParser(description="BOE sumarios → JSONL. Texto desde XML (fallback HTML). Sin enriquecimiento, sin resumen.")
    ap.add_argument("--year", type=int, required=True, help="Año (ej. 2024)")
    ap.add_argument("--out-base", type=str, default="data/base.jsonl", help="Ruta de salida JSONL")
    ap.add_argument("--inline-text", action="store_true", help="Descargar y añadir 'texto_limpio' a cada registro")
    ap.add_argument("--truncate-text", type=int, default=None, help="Cortar texto_limpio a N caracteres")
    ap.add_argument("--sleep-day", type=float, default=0.10, help="Pausa entre días (s)")
    ap.add_argument("--sleep-text", type=float, default=0.20, help="Pausa entre descargas de XML/HTML (s)")
    ap.add_argument("--max-texts", type=int, default=None, help="Procesar como máximo N textos (debug)")
    ap.add_argument("--gzip", action="store_true", help="Guardar comprimido (.jsonl.gz)")
    args = ap.parse_args()

    ensure_dir(os.path.dirname(args.out_base) or ".")

    df_base = build_base(args.year, sleep_each_day=args.sleep_day)

    if args.inline_text and not df_base.empty:
        df_base = attach_inline_text(
            df_base, sleep=args.sleep_text, max_texts=args.max_texts, truncate_text=args.truncate_text
        )

    cols_keep = [
        "identificador", "fecha", "diario_numero", "seccion_codigo","seccion_nombre",
        "departamento_nombre", "epigrafe_nombre",
        "titulo", "tematica", "texto_limpio", "mes", "trimestre"
    ]
    df_base = df_base[[c for c in cols_keep if c in df_base.columns]]

    out_base_path = args.out_base + (".gz" if args.gzip and not args.out_base.endswith(".gz") else "")
    df_to_jsonl(df_base.fillna(""), out_base_path, gzip_enabled=args.gzip)
    logging.info(f"BASE JSONL guardado en {out_base_path} (filas: {len(df_base)})")

if __name__ == "__main__":
    main()
