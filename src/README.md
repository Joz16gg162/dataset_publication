# BOE 2024 — Entrega 4 (Final)

Este repositorio integra las fases del proyecto de *Knowledge Discovery* aplicadas al **BOE 2024**, con el objetivo de contrastar una hipótesis de estacionalidad (efecto agosto) y presentar resultados de forma clara, crítica y reproducible.

## Dataset (Entrega 1)
El dataset original fue publicado en **Hugging Face** para garantizar trazabilidad y reutilización. En este repositorio se incluye además el dataset derivado agregado semanalmente, usado en Entrega 3 y 4:

- `data/dataset_boe_temporal_sin_sentimiento_por_semana_con_topico.csv`

> Enlace (rellenar) al dataset en Hugging Face:
```text
https://huggingface.co/datasets/<TU_USUARIO>/<TU_DATASET_BOE_2024>
```

## Hipótesis e indicadores (Entrega 2)
La hipótesis central:
**H1:** en agosto baja el volumen semanal del BOE respecto al patrón anual y cambia la distribución temática.

Indicadores principales:
- Volumen: `publicaciones_semana` (agregado por semana).
- Temas: columnas `topico_*` (conteos y proporciones semanales).
- Drift: KL semanal vs anual y Jensen–Shannon (t vs t−1).
- Modelos: comparación Holt–Winters vs SARIMAX (train/test temporal).

## Análisis temporal/temático (Entrega 3)
Resultados clave:
- Media anual ≈ 531 vs media agosto ≈ 381.
- Holt–Winters RMSE ≈ 97.73.
- SARIMAX(1,0,2) con exógenas (`is_august`, `holiday_count`) RMSE ≈ 46.58; `is_august` negativo y significativo.
- χ² agosto vs resto: p ≈ 1.34e−21 (cambio temático robusto).
- Drift temático fuerte alrededor de finales de agosto/inicios de septiembre (KL/JS).

## Entrega 4: informe final y resultados
- Informe: `report/report.md`
- Figuras definitivas: `results/*.png`

## Estructura
```text
entrega4/
├── report/
│   └── report.md
├── results/
│   └── *.png
├── data/
│   └── dataset_boe_temporal_sin_sentimiento_por_semana_con_topico.csv
└── notebooks/
    └── *.ipynb
```

## Reproducibilidad: pasos
### 1) Crear entorno e instalar dependencias
Python 3.10+ recomendado.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install numpy pandas matplotlib scikit-learn scipy statsmodels
```

### 2) Datos
Coloca el CSV semanal en `data/` (ya incluido en este pack). Si necesitas regenerarlo, ejecuta los notebooks de Entrega 1–2.

### 3) Ejecutar notebooks (orden recomendado)
1. Entrega 1 (recolección/publicación).  
2. Entrega 2 (limpieza e indicadores).  
3. Entrega 3 (análisis temporal y temático v2).  
4. Entrega 4 (consolidación y presentación).

### 4) Resultados
Las figuras se generan en `results/` y se utilizan en la presentación oral.

## Presentación oral (10 minutos)
Contenido mínimo:
1. Contexto y dataset.  
2. Hipótesis y motivación.  
3. Indicadores calculados.  
4. Técnicas aplicadas y resultados clave.  
5. Conclusiones y limitaciones.

Sugerencia: priorizar 4–6 figuras (serie semanal con agosto sombreado, comparación mensual, forecast SARIMAX, χ² y tópicos con mayores residuos, KL/JS de drift).
