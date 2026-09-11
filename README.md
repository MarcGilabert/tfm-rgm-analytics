# Promotional Analytics & Revenue Growth Management

Sistema de analítica comercial sobre datos reales de distribución alimentaria: sensibilidad al precio, valor de cliente y medición de la incrementalidad promocional.

Trabajo Fin de Máster — Máster en Big Data, Data Science & Business Analytics.

## El problema

Cuando un producto está en promoción, sus ventas suben casi siempre. Pero eso no demuestra que la promoción funcione: parte de ese volumen se habría vendido igual sin descuento. Este proyecto responde a tres preguntas de negocio:

- **¿Qué categorías aguantan una subida de precio sin perder volumen?**
- **¿Qué hogares concentran el valor de la cartera de clientes?**
- **¿Qué porcentaje de las ventas promocionadas es realmente atribuible a la promoción?**

Un cuarto bloque identifica perfiles de comportamiento promocional que matizan las conclusiones anteriores.

## Hallazgos principales

| Bloque | Hallazgo |
|---|---|
| **Sensibilidad al precio** | De 211 categorías analizadas, solo 36 muestran una respuesta clara a la rebaja de precio — concentradas en productos no perecederos y almacenables. |
| **Valor de cliente** | El 20% de los hogares concentra el 53,9% del valor total de la cartera (4,05 M$ a 12 meses). |
| **Baseline e incrementalidad** | El 32,8% del volumen vendido en promoción es incremental. Dos de cada tres unidades se habrían vendido igual sin descuento. |
| **Segmentación promocional** | El perfil "Cazador de ofertas" consume el 23% del presupuesto promocional pero solo aporta el 14,5% del valor — el descuento generalizado es regresivo. |

## Dataset

[Dunnhumby — The Complete Journey](https://data.mendeley.com/datasets/7myy93ym6k/1) (Mendeley Data, licencia CC BY 4.0). Historial de compra de 2.500 hogares durante 711 días en una cadena de distribución alimentaria.

## Estructura del repositorio

```
tfm-app/
├── app.py                          # Aplicación Streamlit
├── requirements.txt
├── data/                           # Resultados procesados (CSV)
└── notebooks/
    ├── 00_EDA.ipynb
    ├── 01_Feature_Engineering.ipynb
    ├── 02_Price_Elasticity.ipynb
    ├── 03_CLV.ipynb
    ├── 04_Baseline.ipynb
    └── 05_Segmentacion_Promocional.ipynb
```

## Metodología y técnicas

| Bloque | Técnica |
|---|---|
| Sensibilidad al precio | Comparación de grupos de precio (rebajado / normal / encarecido) |
| Valor de cliente | BG/NBD + Gamma-Gamma (`lifetimes`) |
| Baseline e incrementalidad | XGBoost, con comparación frente a Regresión Lineal, Árbol de Decisión, Random Forest, Extra Trees y Gradient Boosting |
| Segmentación promocional | K-Means |

## Ejecutar la aplicación en local

```bash
git clone https://github.com/MarcGilabert/tfm-rgm-analytics.git
cd tfm-rgm-analytics
pip install -r requirements.txt
streamlit run app.py
```

## Limitaciones

El conjunto de datos no incluye coste de producto, lo que impide calcular el retorno económico de las promociones en términos de margen. El canje de cupón no responde a una asignación aleatoria, lo que impide estimar con garantías el efecto causal de las campañas a nivel de hogar sin un diseño experimental — línea de trabajo futuro detallada en la memoria.

## Autor

Marc Gilabert — Máster en Big Data, Data Science & Business Analytics, 2025-2026
