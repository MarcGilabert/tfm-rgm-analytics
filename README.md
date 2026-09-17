# Promotional Analytics \& Revenue Growth Management

Sistema de analítica comercial sobre datos reales de distribución alimentaria: sensibilidad al precio, valor de cliente y medición de la incrementalidad promocional.

Trabajo Fin de Máster — Máster en Big Data, Data Science \& Business Analytics.

## El problema

Cuando un producto está en promoción, sus ventas suben casi siempre. Pero eso no demuestra que la promoción funcione: parte de ese volumen se habría vendido igual sin descuento. Este proyecto responde a tres preguntas de negocio:

* **¿Qué categorías aguantan una subida de precio sin perder volumen?**
* **¿Qué hogares concentran el valor de la cartera de clientes?**
* **¿Qué porcentaje de las ventas promocionadas es realmente atribuible a la promoción?**

Un cuarto bloque identifica perfiles de comportamiento promocional que matizan las conclusiones anteriores.

## Hallazgos principales

|Bloque|Hallazgo|
|-|-|
|**Sensibilidad al precio**|De 211 categorías analizadas, solo 36 muestran una respuesta clara a la rebaja de precio — concentradas en productos no perecederos y almacenables.|
|**Valor de cliente**|El 20% de los hogares concentra el 53,9% del valor total de la cartera (4,05 M$ a 12 meses).|
|**Baseline e incrementalidad**|El 27.6% del volumen vendido en promoción es incremental. Dos de cada tres unidades se habrían vendido igual sin descuento.|
|**Segmentación promocional**|El perfil "Cazador de ofertas" consume el 23% del presupuesto promocional pero solo aporta el 14,5% del valor — el descuento generalizado es regresivo.|

## Dataset

[Dunnhumby — The Complete Journey](https://data.mendeley.com/datasets/7myy93ym6k/1) (Mendeley Data, licencia CC BY 4.0). Historial de compra de 2.500 hogares durante 711 días en una cadena de distribución alimentaria.

## Estructura del repositorio

```
tfm-app/
├── app.py                          # Aplicación Streamlit
├── Dockerfile
├── requirements.txt
├── data/                           # Resultados procesados (CSV)
└── notebooks/
    ├── 00\\\_EDA.ipynb
    ├── 01\\\_Feature\\\_Engineering.ipynb
    ├── 02\\\_Price\\\_Elasticity.ipynb
    ├── 03\\\_CLV.ipynb
    ├── 04\\\_Baseline.ipynb
    └── 05\\\_Segmentacion\\\_Promocional.ipynb
```

## Metodología y técnicas

|Bloque|Técnica|
|-|-|
|Sensibilidad al precio|Comparación de grupos de precio (rebajado / normal / encarecido)|
|Valor de cliente|BG/NBD + Gamma-Gamma (`lifetimes`)|
|Baseline e incrementalidad|XGBoost, con comparación frente a Regresión Lineal, Árbol de Decisión, Random Forest, Extra Trees y Gradient Boosting|
|Segmentación promocional|K-Means|

## Aplicación desplegada

La aplicación está containerizada con Docker y desplegada en Google Cloud Run:

[**https://tfm-rgm-app-3606564883.europe-west1.run.app**](https://tfm-rgm-app-3606564883.europe-west1.run.app)

Arquitectura de despliegue: imagen Docker → Google Artifact Registry → Google Cloud Run.

## Ejecutar la aplicación en local

**Opción 1 — Con Python:**

```bash
git clone https://github.com/MarcGilabert/tfm-rgm-analytics.git
cd tfm-rgm-analytics
pip install -r requirements.txt
streamlit run app.py
```

**Opción 2 — Con Docker:**

```bash
git clone https://github.com/MarcGilabert/tfm-rgm-analytics.git
cd tfm-rgm-analytics
docker build -t tfm-rgm-app .
docker run -p 8501:8501 tfm-rgm-app
```

## Limitaciones

El conjunto de datos no incluye coste de producto, lo que impide calcular el retorno económico de las promociones en términos de margen. El canje de cupón no responde a una asignación aleatoria, lo que impide estimar con garantías el efecto causal de las campañas a nivel de hogar sin un diseño experimental — línea de trabajo futuro detallada en la memoria.

## Autor

Marc Gilabert — Máster en Big Data, Data Science \& Business Analytics, 2025-2026

