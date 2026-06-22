import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data_loader import carregar_dados, filtrar_dados


st.set_page_config(
    page_title="Vicenzo — Dashboard de Áreas",
    page_icon="🏢",
    layout="wide",
)

CORES_USO = {
    "PRIVATIVA PRINCIPAL": "#2563EB",
    "PRIVATIVA ACESSORIA": "#7C3AED",
    "COMUM": "#059669",
}

CORES_TORRE = {
    "Norte": "#2563EB",
    "Sul": "#DC2626",
    "Área Comum": "#6B7280",
}


# --- Carregar dados ---
df_completo = carregar_dados()


# --- Sidebar: Filtros ---
st.sidebar.title("Filtros")

niveis_disponiveis = sorted(df_completo["Nivel"].dropna().unique())
niveis_selecionados = st.sidebar.multiselect(
    "Pavimento",
    options=niveis_disponiveis,
    default=[],
    placeholder="Todos os pavimentos",
)

torres_disponiveis = sorted(df_completo["Torre"].dropna().unique())
torres_selecionadas = st.sidebar.multiselect(
    "Torre",
    options=torres_disponiveis,
    default=[],
    placeholder="Todas as torres",
)

usos_disponiveis = sorted(df_completo["Uso"].dropna().unique())
usos_selecionados = st.sidebar.multiselect(
    "Tipo de Uso (NBR 12721)",
    options=usos_disponiveis,
    default=[],
    placeholder="Todos os tipos",
)

acabamentos_disponiveis = sorted(df_completo["Acabamento"].dropna().unique())
acabamentos_selecionados = st.sidebar.multiselect(
    "Acabamento",
    options=acabamentos_disponiveis,
    default=[],
    placeholder="Todos os acabamentos",
)

df = filtrar_dados(
    df_completo,
    niveis_selecionados,
    torres_selecionadas,
    usos_selecionados,
    acabamentos_selecionados,
)

st.sidebar.markdown("---")
st.sidebar.caption(f"**{len(df)}** ambientes filtrados de **{len(df_completo)}** total")


# --- Título ---
st.title("🏢 Vicenzo — Dashboard de Áreas")

pagina = st.tabs([
    "📊 Visão Geral",
    "🏗️ Por Pavimento",
    "🏠 Por Unidade",
    "⚖️ Comparativo Torres",
])


# =====================================================
# PÁGINA 1 — Visão Geral
# =====================================================
with pagina[0]:

    area_total = df["Area"].sum()
    area_privativa = df.loc[df["Uso"] == "PRIVATIVA PRINCIPAL", "Area"].sum()
    area_comum = df.loc[df["Uso"] == "COMUM", "Area"].sum()
    area_acessoria = df.loc[df["Uso"] == "PRIVATIVA ACESSORIA", "Area"].sum()
    qtd_unidades = df.loc[df["Uso"] == "PRIVATIVA PRINCIPAL", "Unidade_Autonoma"].nunique()

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Área Total", f"{area_total:,.2f} m²")
    col2.metric("Privativa Principal", f"{area_privativa:,.2f} m²")
    col3.metric("Área Comum", f"{area_comum:,.2f} m²")
    col4.metric("Privativa Acessória", f"{area_acessoria:,.2f} m²")
    col5.metric("Unidades Autônomas", qtd_unidades)

    st.markdown("---")

    col_grafico1, col_grafico2 = st.columns(2)

    with col_grafico1:
        st.subheader("Distribuição por Tipo de Uso")
        df_uso = df.groupby("Uso", observed=True)["Area"].sum().reset_index()
        df_uso.columns = ["Uso", "Área (m²)"]

        fig_uso = px.pie(
            df_uso,
            values="Área (m²)",
            names="Uso",
            hole=0.45,
            color="Uso",
            color_discrete_map=CORES_USO,
        )
        fig_uso.update_traces(textinfo="percent+value", texttemplate="%{percent:.1%}<br>%{value:,.1f} m²")
        fig_uso.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=400)
        st.plotly_chart(fig_uso, use_container_width=True)

    with col_grafico2:
        st.subheader("Área por Tipo de Acabamento")
        df_acab = df.groupby("Acabamento", observed=True)["Area"].sum().reset_index()
        df_acab.columns = ["Acabamento", "Área (m²)"]
        df_acab = df_acab.sort_values("Área (m²)", ascending=True)

        fig_acab = px.bar(
            df_acab,
            x="Área (m²)",
            y="Acabamento",
            orientation="h",
            color_discrete_sequence=["#2563EB"],
            text="Área (m²)",
        )
        fig_acab.update_traces(texttemplate="%{text:,.1f} m²", textposition="outside")
        fig_acab.update_layout(
            margin=dict(t=20, b=20, l=20, r=20),
            height=400,
            xaxis_title="Área (m²)",
            yaxis_title="",
        )
        st.plotly_chart(fig_acab, use_container_width=True)

    st.subheader("Quadro de Áreas NBR 12721")
    tabela_quadro = pd.pivot_table(
        df,
        values="Area",
        index="Acabamento",
        columns="Uso",
        aggfunc="sum",
        fill_value=0,
        margins=True,
        margins_name="TOTAL",
        observed=True,
    )
    tabela_quadro = tabela_quadro.round(2)
    st.dataframe(
        tabela_quadro.style.format("{:,.2f}"),
        use_container_width=True,
    )


# =====================================================
# PÁGINA 2 — Análise por Pavimento
# =====================================================
with pagina[1]:

    st.subheader("Área por Pavimento — Segmentado por Tipo de Uso")
    df_pav_uso = (
        df.groupby(["Nivel", "Uso"], observed=True)["Area"]
        .sum()
        .reset_index()
    )
    df_pav_uso.columns = ["Pavimento", "Uso", "Área (m²)"]

    fig_pav_uso = px.bar(
        df_pav_uso,
        x="Pavimento",
        y="Área (m²)",
        color="Uso",
        color_discrete_map=CORES_USO,
        barmode="stack",
        text="Área (m²)",
    )
    fig_pav_uso.update_traces(texttemplate="%{text:,.0f}", textposition="inside")
    fig_pav_uso.update_layout(
        margin=dict(t=20, b=20),
        height=500,
        xaxis_title="",
        yaxis_title="Área (m²)",
        xaxis_tickangle=-45,
    )
    st.plotly_chart(fig_pav_uso, use_container_width=True)

    st.markdown("---")

    st.subheader("Área por Pavimento — Segmentado por Acabamento")
    df_pav_acab = (
        df.groupby(["Nivel", "Acabamento"], observed=True)["Area"]
        .sum()
        .reset_index()
    )
    df_pav_acab.columns = ["Pavimento", "Acabamento", "Área (m²)"]

    fig_pav_acab = px.bar(
        df_pav_acab,
        x="Pavimento",
        y="Área (m²)",
        color="Acabamento",
        barmode="stack",
        text="Área (m²)",
    )
    fig_pav_acab.update_traces(texttemplate="%{text:,.0f}", textposition="inside")
    fig_pav_acab.update_layout(
        margin=dict(t=20, b=20),
        height=500,
        xaxis_title="",
        yaxis_title="Área (m²)",
        xaxis_tickangle=-45,
    )
    st.plotly_chart(fig_pav_acab, use_container_width=True)

    st.markdown("---")

    st.subheader("Detalhamento por Pavimento")
    pav_detalhe = st.selectbox(
        "Selecione o pavimento:",
        options=sorted(df["Nivel"].dropna().unique()),
        key="pav_detalhe",
    )
    df_detalhe = df[df["Nivel"] == pav_detalhe][["Nome", "Area", "Uso", "Acabamento", "Unidade_Autonoma", "Torre"]]
    df_detalhe = df_detalhe.sort_values("Area", ascending=False).reset_index(drop=True)
    df_detalhe.columns = ["Nome", "Área (m²)", "Uso", "Acabamento", "Unidade Autônoma", "Torre"]

    st.caption(f"**{len(df_detalhe)}** ambientes — Área total: **{df_detalhe['Área (m²)'].sum():,.2f} m²**")
    st.dataframe(
        df_detalhe.style.format({"Área (m²)": "{:,.2f}"}),
        use_container_width=True,
        height=400,
    )


# =====================================================
# PÁGINA 3 — Análise por Unidade Autônoma
# =====================================================
with pagina[2]:

    unidades = sorted(df.loc[df["Unidade_Autonoma"].notna(), "Unidade_Autonoma"].unique())

    if not unidades:
        st.warning("Nenhuma unidade autônoma encontrada com os filtros atuais.")
    else:
        unidade_sel = st.selectbox(
            "Selecione a unidade autônoma:",
            options=unidades,
            key="unidade_sel",
        )

        df_unidade = df[df["Unidade_Autonoma"] == unidade_sel]
        torre_unidade = df_unidade["Torre"].iloc[0] if len(df_unidade) > 0 else "—"

        area_priv = df_unidade.loc[df_unidade["Uso"] == "PRIVATIVA PRINCIPAL", "Area"].sum()
        area_aces = df_unidade.loc[df_unidade["Uso"] == "PRIVATIVA ACESSORIA", "Area"].sum()
        area_total_un = df_unidade["Area"].sum()

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Torre", torre_unidade)
        col2.metric("Área Privativa", f"{area_priv:,.2f} m²")
        col3.metric("Área Acessória", f"{area_aces:,.2f} m²")
        col4.metric("Área Total", f"{area_total_un:,.2f} m²")

        st.markdown("---")

        col_tab, col_graf = st.columns([3, 2])

        with col_tab:
            st.subheader("Ambientes da Unidade")
            df_amb = df_unidade[["Nome", "Area", "Nivel", "Uso", "Acabamento"]].copy()
            df_amb = df_amb.sort_values("Area", ascending=False).reset_index(drop=True)
            df_amb.columns = ["Nome", "Área (m²)", "Pavimento", "Uso", "Acabamento"]
            st.dataframe(
                df_amb.style.format({"Área (m²)": "{:,.2f}"}),
                use_container_width=True,
                height=400,
            )

        with col_graf:
            st.subheader("Composição por Acabamento")
            df_comp = df_unidade.groupby("Acabamento", observed=True)["Area"].sum().reset_index()
            df_comp.columns = ["Acabamento", "Área (m²)"]
            df_comp = df_comp.sort_values("Área (m²)", ascending=True)

            fig_comp = px.bar(
                df_comp,
                x="Área (m²)",
                y="Acabamento",
                orientation="h",
                color_discrete_sequence=["#7C3AED"],
                text="Área (m²)",
            )
            fig_comp.update_traces(texttemplate="%{text:,.2f} m²", textposition="outside")
            fig_comp.update_layout(
                margin=dict(t=20, b=20, l=20, r=20),
                height=400,
                xaxis_title="Área (m²)",
                yaxis_title="",
            )
            st.plotly_chart(fig_comp, use_container_width=True)


# =====================================================
# PÁGINA 4 — Comparativo entre Torres
# =====================================================
with pagina[3]:

    df_torres = df[df["Torre"].isin(["Norte", "Sul"])]

    if df_torres.empty:
        st.warning("Nenhum dado de torres encontrado com os filtros atuais.")
    else:
        col_n, col_s = st.columns(2)

        df_norte = df_torres[df_torres["Torre"] == "Norte"]
        df_sul = df_torres[df_torres["Torre"] == "Sul"]

        with col_n:
            st.subheader("🔵 Torre Norte")
            st.metric("Área Total", f"{df_norte['Area'].sum():,.2f} m²")
            st.metric("Unidades", df_norte["Unidade_Autonoma"].nunique())
            st.metric("Ambientes", len(df_norte))

        with col_s:
            st.subheader("🔴 Torre Sul")
            st.metric("Área Total", f"{df_sul['Area'].sum():,.2f} m²")
            st.metric("Unidades", df_sul["Unidade_Autonoma"].nunique())
            st.metric("Ambientes", len(df_sul))

        st.markdown("---")

        st.subheader("Área por Tipo de Uso — Norte vs Sul")
        df_torre_uso = (
            df_torres.groupby(["Torre", "Uso"], observed=True)["Area"]
            .sum()
            .reset_index()
        )
        df_torre_uso.columns = ["Torre", "Uso", "Área (m²)"]

        fig_torre_uso = px.bar(
            df_torre_uso,
            x="Uso",
            y="Área (m²)",
            color="Torre",
            color_discrete_map=CORES_TORRE,
            barmode="group",
            text="Área (m²)",
        )
        fig_torre_uso.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
        fig_torre_uso.update_layout(
            margin=dict(t=20, b=20),
            height=450,
            xaxis_title="",
            yaxis_title="Área (m²)",
        )
        st.plotly_chart(fig_torre_uso, use_container_width=True)

        st.markdown("---")

        st.subheader("Área Média por Unidade — Norte vs Sul")
        media_norte = df_norte.groupby("Unidade_Autonoma")["Area"].sum()
        media_sul = df_sul.groupby("Unidade_Autonoma")["Area"].sum()

        df_media = pd.DataFrame({
            "Torre": ["Norte", "Sul"],
            "Área Média (m²)": [media_norte.mean(), media_sul.mean()],
        })

        fig_media = px.bar(
            df_media,
            x="Torre",
            y="Área Média (m²)",
            color="Torre",
            color_discrete_map=CORES_TORRE,
            text="Área Média (m²)",
        )
        fig_media.update_traces(texttemplate="%{text:,.2f} m²", textposition="outside")
        fig_media.update_layout(
            margin=dict(t=20, b=20),
            height=400,
            xaxis_title="",
            showlegend=False,
        )
        st.plotly_chart(fig_media, use_container_width=True)

        st.markdown("---")

        st.subheader("Tabela Comparativa")
        comparativo = []
        for torre_nome, df_t in [("Norte", df_norte), ("Sul", df_sul)]:
            comparativo.append({
                "Torre": torre_nome,
                "Área Total (m²)": df_t["Area"].sum(),
                "Qtd Unidades": df_t["Unidade_Autonoma"].nunique(),
                "Área Priv. Principal (m²)": df_t.loc[df_t["Uso"] == "PRIVATIVA PRINCIPAL", "Area"].sum(),
                "Área Priv. Acessória (m²)": df_t.loc[df_t["Uso"] == "PRIVATIVA ACESSORIA", "Area"].sum(),
                "Qtd Ambientes": len(df_t),
            })

        df_comparativo = pd.DataFrame(comparativo)
        st.dataframe(
            df_comparativo.style.format({
                "Área Total (m²)": "{:,.2f}",
                "Área Priv. Principal (m²)": "{:,.2f}",
                "Área Priv. Acessória (m²)": "{:,.2f}",
            }),
            use_container_width=True,
            hide_index=True,
        )
