import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="RGM Analytics", layout="wide")

# Cargar datos una sola vez y guardarlos en cache.
# Sin esto, los CSV se releerian en cada clic del usuario.
@st.cache_data
def cargar_datos():
    return {
        'elasticidad': pd.read_csv("data/elasticity_by_commodity.csv"),
        'clv': pd.read_csv("data/clv_por_hogar.csv"),
        'baseline': pd.read_csv("data/baseline_por_categoria.csv"),
        'perfiles': pd.read_csv("data/segmentacion_promocional.csv"),
        'eficiencia': pd.read_csv("data/eficiencia_por_segmento.csv"),
    }

d = cargar_datos()

# Menu lateral
st.sidebar.title("RGM Analytics")
pagina = st.sidebar.radio(
    "Navegacion",
    ["Resumen", "Pricing", "Clientes", "Perfiles", "Consulta"]
)
# ─────────────────────────────────────────────
# PAGINA 1: RESUMEN
# ─────────────────────────────────────────────
if pagina == "Resumen":
    st.title("Revenue Growth Management")
    st.caption("Analisis comercial sobre 2.500 hogares y 2,6M de transacciones")

    el = d['elasticidad']
    clv = d['clv']

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Valor de cartera", f"{clv['clv_12m'].sum()/1e6:.2f} M€")
    col2.metric("Volumen incremental", "32,8%")
    col3.metric("Categorias analizadas", f"{len(el)}")
    col4.metric("Categorias sensibles al precio", f"{(el['efecto_rebaja_pct'] > 10).sum()}")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Conclusiones principales")
        st.write("""
        - Dos de cada tres unidades vendidas en promocion se habrian vendido igualmente
        - El 20% de hogares concentra el 54% del valor total de la cartera
        - Solo 36 de 211 categorias responden con claridad a la rebaja de precio
        - El descuento generalizado transfiere margen al segmento menos eficiente
        """)

    with col2:
        st.subheader("Eficiencia por perfil de cliente")
        ef = d['eficiencia'].copy()
        fig = px.bar(
            ef.sort_values('eficiencia'),
            x='eficiencia', y='segmento',
            orientation='h',
            color='eficiencia',
            color_continuous_scale=['#C44536', '#F0E68C', '#2E8B57'],
            labels={'eficiencia': 'Valor aportado / descuento consumido',
                    'segmento': ''}
        )
        fig.add_vline(x=1, line_dash="dash", line_color="black")
        fig.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────
# PAGINA 2: PRICING
# ─────────────────────────────────────────────
elif pagina == "Pricing":
    st.title("Sensibilidad al precio por categoria")

    el = d['elasticidad'].copy()
    baseline = d['baseline'].copy()

    tab1, tab2 = st.tabs(["Simulador", "Ranking de categorias"])

    with tab1:
        st.caption("Estima el impacto de un cambio de precio usando el efecto "
                   "de rebaja medido en cada categoria")

        col1, col2 = st.columns([1, 2])

        with col1:
            cats = sorted(el[el['n_total'] >= 1000]['COMMODITY_DESC'].unique())
            cat = st.selectbox("Categoria", cats,
                               index=cats.index('SOFT DRINKS') if 'SOFT DRINKS' in cats else 0)

            cambio = st.slider("Cambio de precio (%)", -20, 20, 0, step=1)
            margen_sim = st.slider("Margen bruto (%)", 15, 45, 25, key="margen_pricing") / 100

        fila = el[el['COMMODITY_DESC'] == cat].iloc[0]

        efecto_por_punto = fila['efecto_rebaja_pct'] / 10
        cambio_volumen_pct = -cambio * efecto_por_punto

        base = baseline[baseline['COMMODITY_DESC'] == cat]
        if len(base) > 0:
            unidades_base = base['unidades_reales'].iloc[0]
        else:
            unidades_base = fila['n_total']

        precio_base = 3.0
        bl = baseline[baseline['COMMODITY_DESC'] == cat]
        if len(bl) > 0 and 'precio_paid' in bl.columns:
            precio_base = bl['precio_paid'].iloc[0]

        ingresos_act = unidades_base * precio_base
        margen_act = ingresos_act * margen_sim

        precio_new = precio_base * (1 + cambio / 100)
        unidades_new = unidades_base * (1 + cambio_volumen_pct / 100)
        ingresos_new = unidades_new * precio_new
        margen_new = ingresos_new * margen_sim

        with col2:
            st.subheader(f"{cat}")

            c1, c2, c3 = st.columns(3)
            c1.metric("Precio", f"{precio_new:.2f} €", delta=f"{cambio:+.0f}%")
            c2.metric("Volumen", f"{unidades_new:,.0f} ud", delta=f"{cambio_volumen_pct:+.1f}%")
            c3.metric("Margen", f"{margen_new:,.0f} €", delta=f"{margen_new - margen_act:+,.0f} €")

            if cambio != 0:
                if margen_new > margen_act:
                    st.success(f"El cambio mejora el margen en {margen_new - margen_act:,.0f} €")
                else:
                    st.error(f"El cambio reduce el margen en {abs(margen_new - margen_act):,.0f} €")

        st.divider()

        rango = list(range(-20, 21, 1))
        curva = []
        for ch in rango:
            cv = -ch * efecto_por_punto
            u = unidades_base * (1 + cv / 100)
            p = precio_base * (1 + ch / 100)
            curva.append({'cambio_precio': ch, 'margen': u * p * margen_sim})

        curva = pd.DataFrame(curva)
        optimo = curva.loc[curva['margen'].idxmax(), 'cambio_precio']

        fig = px.line(curva, x='cambio_precio', y='margen',
                      labels={'cambio_precio': 'Cambio de precio (%)',
                              'margen': 'Margen estimado (€)'})
        fig.add_vline(x=cambio, line_dash="dash", line_color="#4A7C9E")
        fig.add_vline(x=optimo, line_dash="dot", line_color="#2E8B57")
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

        st.caption(f"Linea azul: escenario seleccionado. "
                   f"Linea verde: punto de margen maximo ({optimo:+.0f}%). "
                   f"Sensibilidad medida: una rebaja del 10% mueve el volumen "
                   f"un {fila['efecto_rebaja_pct']:+.1f}%.")

        st.warning("Modelo simplificado: asume respuesta lineal y no considera "
                   "canibalizacion entre categorias ni reaccion de la competencia.")

    with tab2:
        n = st.slider("Categorias a mostrar", 5, 30, 15)

        c1, c2 = st.columns(2)

        with c1:
            st.subheader("Mas sensibles a la rebaja")
            top = el.nlargest(n, 'efecto_rebaja_pct')
            fig = px.bar(top.sort_values('efecto_rebaja_pct'),
                         x='efecto_rebaja_pct', y='COMMODITY_DESC',
                         orientation='h', color_discrete_sequence=['#2E8B57'],
                         labels={'efecto_rebaja_pct': '% incremento de volumen',
                                 'COMMODITY_DESC': ''})
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            st.subheader("Menos sensibles")
            bottom = el.nsmallest(n, 'efecto_rebaja_pct')
            fig = px.bar(bottom.sort_values('efecto_rebaja_pct', ascending=False),
                         x='efecto_rebaja_pct', y='COMMODITY_DESC',
                         orientation='h', color_discrete_sequence=['#C44536'],
                         labels={'efecto_rebaja_pct': '% incremento de volumen',
                                 'COMMODITY_DESC': ''})
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)

        st.dataframe(el[['COMMODITY_DESC', 'normal', 'rebajado',
                         'efecto_rebaja_pct', 'n_total']].round(2),
                     use_container_width=True)

# ─────────────────────────────────────────────
# PAGINA 3: CLIENTES
# ─────────────────────────────────────────────
elif pagina == "Clientes":
    st.title("Segmentacion de hogares por valor")

    clv = d['clv']

    col1, col2, col3 = st.columns(3)
    col1.metric("Hogares", f"{len(clv):,}")
    col2.metric("CLV medio", f"{clv['clv_12m'].mean():,.0f} €")
    col3.metric("Valor total", f"{clv['clv_12m'].sum()/1e6:.2f} M€")

    seg = clv.groupby('segmento').agg(
        hogares=('clv_12m', 'count'),
        clv_total=('clv_12m', 'sum')
    ).reset_index().sort_values('clv_total', ascending=False)

    fig = px.bar(seg, x='segmento', y='clv_total',
                 labels={'clv_total': 'Valor total (€)', 'segmento': ''},
                 color_discrete_sequence=['#4A7C9E'])
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(seg, use_container_width=True)

# ─────────────────────────────────────────────
# PAGINA 4: PERFILES
# ─────────────────────────────────────────────
elif pagina == "Perfiles":
    st.title("Perfiles de respuesta promocional")
    st.caption("Como se comporta cada hogar frente a las promociones (K-Means)")

    ef = d['eficiencia'].copy()

    st.subheader("Valor aportado frente a descuento consumido")
    st.dataframe(ef, use_container_width=True)

    fig = px.scatter(ef, x='pct_descuento', y='pct_valor',
                     size='n_hogares', text='segmento',
                     labels={'pct_descuento': '% del descuento consumido',
                             'pct_valor': '% del valor aportado'})
    fig.add_shape(type="line", x0=0, y0=0, x1=30, y1=30,
                  line=dict(dash="dash", color="gray"))
    fig.update_traces(textposition='top center')
    fig.update_layout(height=450)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Por encima de la diagonal: el perfil aporta mas valor del descuento que consume. "
               "Por debajo: consume mas descuento del valor que aporta.")
# ─────────────────────────────────────────────
# PAGINA 5: CONSULTA POR CATEGORIA
# ─────────────────────────────────────────────
elif pagina == "Consulta":
    st.title("Consulta por categoria")
    st.caption("Cruce de sensibilidad al precio e incrementalidad promocional, "
               "con recomendacion de accion comercial")

    el = d['elasticidad'].copy()
    bl = d['baseline'].copy()

    # Cruzamos las dos tablas por categoria
    cruce = el.merge(bl, on='COMMODITY_DESC', how='inner')

    cats_disponibles = sorted(cruce['COMMODITY_DESC'].unique())
    cat = st.selectbox("Selecciona una categoria", cats_disponibles,
                        index=cats_disponibles.index('SOFT DRINKS') if 'SOFT DRINKS' in cats_disponibles else 0)

    fila = cruce[cruce['COMMODITY_DESC'] == cat].iloc[0]

    efecto_precio = fila['efecto_rebaja_pct']
    incrementalidad = fila['pct_incremental']

    st.subheader(cat)

    c1, c2, c3 = st.columns(3)
    c1.metric("Sensibilidad al precio", f"{efecto_precio:+.1f}%",
              help="Cambio en cantidad por transaccion cuando el producto esta rebajado")
    c2.metric("Incrementalidad (baseline)", f"{incrementalidad:.1f}%",
              help="Porcentaje del volumen en promocion que es realmente nuevo")
    c3.metric("Observaciones", f"{fila['n_observaciones']:,.0f}")

    st.divider()

    # Logica de recomendacion cruzando ambas metricas
    if incrementalidad > 40 and abs(efecto_precio) < 15:
        mecanismo = "penetracion"
        recomendacion = ("Buena candidata para promocion. La alta incrementalidad "
                          "indica que la promocion atrae compradores nuevos, mas que "
                          "hacer que cada comprador se lleve mas unidades. Priorizar "
                          "mecanicas de visibilidad (folleto, display) sobre descuentos "
                          "agresivos de precio.")
        color = "success"
    elif incrementalidad > 40 and efecto_precio >= 15:
        mecanismo = "cantidad por cesta"
        recomendacion = ("Buena candidata para promocion. Tanto la incrementalidad "
                          "como la respuesta al precio son altas: la promocion genera "
                          "volumen nuevo Y hace que cada comprador se lleve mas unidades. "
                          "Las mecanicas de volumen (multipack, 3x2) deberian funcionar bien.")
        color = "success"
    elif incrementalidad <= 20:
        mecanismo = "ninguno claro"
        recomendacion = ("Evitar o reducir la promocion en esta categoria. La mayor "
                          "parte del volumen se venderia igual sin descuento, por lo "
                          "que la inversion promocional regala margen sin generar "
                          "demanda adicional apreciable.")
        color = "error"
    else:
        mecanismo = "moderado"
        recomendacion = ("Categoria de respuesta intermedia. No es prioritaria para "
                          "invertir presupuesto promocional, pero tampoco es candidata "
                          "clara a eliminar la promocion. Revisar caso por caso segun "
                          "el margen disponible.")
        color = "info"

    st.write(f"**Mecanismo de respuesta dominante:** {mecanismo}")

    if color == "success":
        st.success(recomendacion)
    elif color == "error":
        st.error(recomendacion)
    else:
        st.info(recomendacion)

    st.divider()

    st.subheader("Posicion de esta categoria frente al resto")
    fig = px.scatter(cruce, x='efecto_rebaja_pct', y='pct_incremental',
                     hover_name='COMMODITY_DESC',
                     labels={'efecto_rebaja_pct': 'Sensibilidad al precio (%)',
                             'pct_incremental': 'Incrementalidad (%)'},
                     opacity=0.4)

    # Resaltar la categoria seleccionada
    fig.add_scatter(x=[fila['efecto_rebaja_pct']], y=[fila['pct_incremental']],
                     mode='markers', marker=dict(size=16, color='#C44536'),
                     name=cat, showlegend=True)

    fig.add_hline(y=40, line_dash="dash", line_color="gray")
    fig.update_layout(height=450)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("La linea horizontal marca el umbral de incrementalidad alta (40%). "
               "El punto rojo es la categoria seleccionada.")