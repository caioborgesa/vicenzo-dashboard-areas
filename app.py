import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data_loader import (
    carregar_dados, filtrar_dados,
    carregar_dados_precos, filtrar_precos,
    carregar_vagas, vagas_por_unidade,
)


st.set_page_config(
    page_title="Vicenzo — Dashboard",
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

CORES_TIPOLOGIA = {
    "GRANDE": "#2563EB",
    "MEDIO": "#7C3AED",
    "PEQUENO": "#059669",
    "TERRAÇO": "#D97706",
}


def formatar_brl(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# --- Carregar dados ---
df_completo = carregar_dados()
df_precos_completo = carregar_dados_precos()
df_vagas = carregar_vagas()
df_vagas_resumo = vagas_por_unidade(df_vagas)


# --- Sidebar: Filtros ---
st.sidebar.title("Filtros")

st.sidebar.subheader("Áreas NBR 12721")

niveis_disponiveis = sorted(df_completo["Nivel"].dropna().unique())
niveis_selecionados = st.sidebar.multiselect(
    "Pavimento (NBR)",
    options=niveis_disponiveis,
    default=[],
    placeholder="Todos os pavimentos",
)

torres_disponiveis = sorted(df_completo["Torre"].dropna().unique())
torres_selecionadas = st.sidebar.multiselect(
    "Torre (NBR)",
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
st.sidebar.subheader("Preços e Unidades")

pav_preco_disp = sorted(df_precos_completo["PAVIMENTO"].dropna().unique())
pav_preco_sel = st.sidebar.multiselect(
    "Pavimento",
    options=pav_preco_disp,
    default=[],
    placeholder="Todos os pavimentos",
    key="pav_preco",
)

torres_preco_disp = sorted(df_precos_completo["Torre_Nome"].dropna().unique())
torres_preco_sel = st.sidebar.multiselect(
    "Torre",
    options=torres_preco_disp,
    default=[],
    placeholder="Todas as torres",
    key="torre_preco",
)

tipologias_disp = sorted(df_precos_completo["TIPOLOGIA"].dropna().unique())
tipologias_sel = st.sidebar.multiselect(
    "Tipologia",
    options=tipologias_disp,
    default=[],
    placeholder="Todas as tipologias",
)

quartos_disp = sorted(df_precos_completo["SUITES+QUARTOS"].dropna().unique())
quartos_sel = st.sidebar.multiselect(
    "Suítes + Quartos",
    options=[int(q) for q in quartos_disp],
    default=[],
    placeholder="Todos",
    key="quartos",
)

posicao_sol_disp = sorted(df_precos_completo["POSICAO NASCENTE/POENTE"].dropna().unique())
posicao_sol_sel = st.sidebar.multiselect(
    "Nascente / Poente",
    options=posicao_sol_disp,
    default=[],
    placeholder="Todas",
    key="posicao_sol",
)

posicao_face_disp = sorted(df_precos_completo["POSICAO NORTE/SUL"].dropna().unique())
posicao_face_sel = st.sidebar.multiselect(
    "Norte / Sul",
    options=posicao_face_disp,
    default=[],
    placeholder="Todas",
    key="posicao_face",
)

posicao_acesso_disp = sorted(df_precos_completo["POSICAO INTERNO/EXTERNO"].dropna().unique())
posicao_acesso_sel = st.sidebar.multiselect(
    "Interno / Externo",
    options=posicao_acesso_disp,
    default=[],
    placeholder="Todas",
    key="posicao_acesso",
)

df_preco = filtrar_precos(
    df_precos_completo,
    pavimentos=pav_preco_sel,
    torres=torres_preco_sel,
    tipologias=tipologias_sel,
    quartos=[float(q) for q in quartos_sel] if quartos_sel else None,
    posicao_sol=posicao_sol_sel if posicao_sol_sel else None,
    posicao_face=posicao_face_sel if posicao_face_sel else None,
    posicao_acesso=posicao_acesso_sel if posicao_acesso_sel else None,
)

st.sidebar.markdown("---")
st.sidebar.caption(
    f"**{len(df)}** ambientes (NBR) · **{len(df_preco)}** unidades (Preços)"
)


# --- Título ---
st.title("🏢 Vicenzo — Dashboard do Empreendimento")

pagina = st.tabs([
    "📊 Visão Geral",
    "🏗️ Por Pavimento",
    "🏠 Por Unidade (NBR)",
    "⚖️ Comparativo Torres",
    "💰 Visão Geral Preços",
    "🏷️ Tabela de Preços",
    "🔍 Ficha da Unidade",
])


# =====================================================
# PÁGINA 1 — Visão Geral (NBR)
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
# PÁGINA 3 — Análise por Unidade Autônoma (NBR)
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


# =====================================================
# PÁGINA 5 — Visão Geral Preços
# =====================================================
with pagina[4]:

    if df_preco.empty:
        st.warning("Nenhuma unidade encontrada com os filtros atuais.")
    else:
        vgv_total = df_preco["PRECO"].sum()
        preco_medio = df_preco["PRECO"].mean()
        preco_m2_medio = df_preco["PRECO_M2"].mean()
        preco_min = df_preco["PRECO"].min()
        preco_max = df_preco["PRECO"].max()

        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("VGV Total", formatar_brl(vgv_total))
        col2.metric("Preço Médio", formatar_brl(preco_medio))
        col3.metric("Preço/m² Médio", formatar_brl(preco_m2_medio))
        col4.metric("Menor Preço", formatar_brl(preco_min))
        col5.metric("Maior Preço", formatar_brl(preco_max))

        st.markdown("---")

        col_g1, col_g2 = st.columns(2)

        with col_g1:
            st.subheader("VGV por Torre")
            df_vgv_torre = df_preco.groupby("Torre_Nome")["PRECO"].sum().reset_index()
            df_vgv_torre.columns = ["Torre", "VGV (R$)"]

            fig_vgv = px.pie(
                df_vgv_torre,
                values="VGV (R$)",
                names="Torre",
                hole=0.45,
                color="Torre",
                color_discrete_map=CORES_TORRE,
            )
            fig_vgv.update_traces(
                textinfo="percent+value",
                texttemplate="%{percent:.1%}<br>R$ %{value:,.0f}",
            )
            fig_vgv.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=400)
            st.plotly_chart(fig_vgv, use_container_width=True)

        with col_g2:
            st.subheader("Preço Médio por Tipologia")
            df_tip = df_preco.groupby("TIPOLOGIA")["PRECO"].mean().reset_index()
            df_tip.columns = ["Tipologia", "Preço Médio (R$)"]
            df_tip = df_tip.sort_values("Preço Médio (R$)", ascending=True)

            fig_tip = px.bar(
                df_tip,
                x="Preço Médio (R$)",
                y="Tipologia",
                orientation="h",
                color="Tipologia",
                color_discrete_map=CORES_TIPOLOGIA,
                text="Preço Médio (R$)",
            )
            fig_tip.update_traces(texttemplate="R$ %{text:,.0f}", textposition="outside")
            fig_tip.update_layout(
                margin=dict(t=20, b=20, l=20, r=20),
                height=400,
                xaxis_title="",
                yaxis_title="",
                showlegend=False,
            )
            st.plotly_chart(fig_tip, use_container_width=True)

        st.markdown("---")

        st.subheader("Preço/m² Médio por Pavimento")
        df_pav_preco = df_preco.groupby("PAVIMENTO", observed=True)["PRECO_M2"].mean().reset_index()
        df_pav_preco.columns = ["Pavimento", "Preço/m² (R$)"]

        fig_pav_m2 = px.bar(
            df_pav_preco,
            x="Pavimento",
            y="Preço/m² (R$)",
            color_discrete_sequence=["#2563EB"],
            text="Preço/m² (R$)",
        )
        fig_pav_m2.update_traces(texttemplate="R$ %{text:,.0f}", textposition="outside")
        fig_pav_m2.update_layout(
            margin=dict(t=20, b=40),
            height=450,
            xaxis_title="",
            yaxis_title="Preço/m² (R$)",
            xaxis_tickangle=-45,
        )
        st.plotly_chart(fig_pav_m2, use_container_width=True)

        st.markdown("---")

        st.subheader("Resumo: Preço por Torre × Tipologia")
        tabela_resumo = pd.pivot_table(
            df_preco,
            values=["PRECO", "PRECO_M2"],
            index="TIPOLOGIA",
            columns="Torre_Nome",
            aggfunc="mean",
            observed=True,
        ).round(2)

        tabela_resumo.columns = [
            f"{col[0].replace('PRECO', 'Preço Médio').replace('PRECO_M2', 'Preço/m²')} — {col[1]}"
            for col in tabela_resumo.columns
        ]

        fmt = {c: "R$ {:,.2f}" for c in tabela_resumo.columns}
        st.dataframe(
            tabela_resumo.style.format(fmt),
            use_container_width=True,
        )


# =====================================================
# PÁGINA 6 — Tabela de Preços Completa
# =====================================================
with pagina[5]:

    st.subheader("Tabela de Preços — Todas as Unidades")

    if df_preco.empty:
        st.warning("Nenhuma unidade encontrada com os filtros atuais.")
    else:
        # Juntar vagas
        df_tabela = df_preco.merge(
            df_vagas_resumo[["UNIDADE", "Total_Vagas"]],
            on="UNIDADE",
            how="left",
        )
        df_tabela["Total_Vagas"] = df_tabela["Total_Vagas"].fillna(0).astype(int)

        df_exibir = df_tabela[[
            "UNIDADE", "Torre_Nome", "PAVIMENTO", "TIPOLOGIA",
            "SUITES+QUARTOS", "POSICAO NASCENTE/POENTE", "POSICAO NORTE/SUL",
            "POSICAO INTERNO/EXTERNO",
            "AREA PADRAO", "AREA TERRACO", "AREA CALCULO DE PRECO",
            "Total_Vagas", "PRECO", "PRECO_M2",
            "SINAL_10", "MENSAIS_52X", "SEMESTRAIS_7X", "CHAVES_45",
        ]].copy()

        df_exibir.columns = [
            "Unidade", "Torre", "Pavimento", "Tipologia",
            "Quartos", "Nasc./Poente", "Norte/Sul",
            "Int./Ext.",
            "Área Padrão", "Área Terraço", "Área Cálculo",
            "Vagas", "Preço", "Preço/m²",
            "Sinal (10%)", "Mensais 52x (25%)", "Semestrais 7x (20%)", "Chaves (45%)",
        ]

        df_exibir = df_exibir.sort_values(["Torre", "Pavimento", "Unidade"]).reset_index(drop=True)

        st.caption(f"**{len(df_exibir)}** unidades · VGV filtrado: **{formatar_brl(df_exibir['Preço'].sum())}**")

        fmt_tabela = {
            "Área Padrão": "{:,.2f}",
            "Área Terraço": "{:,.2f}",
            "Área Cálculo": "{:,.2f}",
            "Preço": "R$ {:,.2f}",
            "Preço/m²": "R$ {:,.2f}",
            "Sinal (10%)": "R$ {:,.2f}",
            "Mensais 52x (25%)": "R$ {:,.2f}",
            "Semestrais 7x (20%)": "R$ {:,.2f}",
            "Chaves (45%)": "R$ {:,.2f}",
            "Quartos": "{:.0f}",
        }

        st.dataframe(
            df_exibir.style.format(fmt_tabela),
            use_container_width=True,
            height=600,
        )

        csv = df_exibir.to_csv(index=False, sep=";", decimal=",")
        st.download_button(
            label="Baixar CSV",
            data=csv,
            file_name="tabela_precos_vicenzo.csv",
            mime="text/csv",
        )


# =====================================================
# PÁGINA 7 — Ficha da Unidade
# =====================================================
with pagina[6]:

    unidades_ficha = sorted(df_precos_completo["UNIDADE"].unique())

    if not unidades_ficha:
        st.warning("Nenhuma unidade disponível.")
    else:
        unidade_ficha = st.selectbox(
            "Selecione a unidade:",
            options=unidades_ficha,
            key="ficha_unidade",
        )

        row = df_precos_completo[df_precos_completo["UNIDADE"] == unidade_ficha].iloc[0]

        # --- Cabeçalho ---
        st.subheader(f"Unidade {unidade_ficha} — Torre {row['Torre_Nome']}")

        # --- Info geral ---
        col_a, col_b, col_c, col_d = st.columns(4)
        col_a.metric("Pavimento", row["PAVIMENTO"])
        col_b.metric("Tipologia", row.get("TIPOLOGIA", "—"))
        col_c.metric("Suítes + Quartos", f"{int(row['SUITES+QUARTOS'])}")
        col_d.metric("Coluna", row.get("COLUNA", "—"))

        col_e, col_f, col_g = st.columns(3)
        posicao_sol = row.get("POSICAO NASCENTE/POENTE", "—")
        posicao_face = row.get("POSICAO NORTE/SUL", "—")
        posicao_acesso = row.get("POSICAO INTERNO/EXTERNO", "—")
        col_e.metric("Nascente/Poente", posicao_sol if pd.notna(posicao_sol) else "—")
        col_f.metric("Norte/Sul", posicao_face if pd.notna(posicao_face) else "—")
        col_g.metric("Interno/Externo", posicao_acesso if pd.notna(posicao_acesso) else "—")

        st.markdown("---")

        # --- Preço e Áreas ---
        st.subheader("Preço e Áreas")

        col1, col2, col3 = st.columns(3)
        col1.metric("Preço", formatar_brl(row["PRECO"]))
        col2.metric("Preço/m²", formatar_brl(row["PRECO_M2"]))
        col3.metric("Referência", f"{row['REFERENCIA']:.2f}")

        col4, col5, col6, col7 = st.columns(4)
        col4.metric("Área Padrão", f"{row['AREA PADRAO']:,.2f} m²")
        col5.metric("Área Técnica", f"{row['AREA TECNICA']:,.2f} m²")
        col6.metric("Área Terraço", f"{row['AREA TERRACO']:,.2f} m²")
        col7.metric("Área Cálculo de Preço", f"{row['AREA CALCULO DE PRECO']:,.2f} m²")

        st.markdown("---")

        # --- Vagas ---
        st.subheader("Vagas de Garagem")
        vagas_unidade = df_vagas[df_vagas["UNIDADE"] == unidade_ficha]

        if vagas_unidade.empty:
            st.info("Nenhuma vaga vinculada a esta unidade.")
        else:
            st.caption(f"**{len(vagas_unidade)}** vaga(s)")
            df_vagas_exibir = vagas_unidade[["VAGA", "PAVIMENTO", "Tipo_Vaga"]].copy()
            df_vagas_exibir.columns = ["Vaga", "Pavimento", "Tipo"]
            st.dataframe(df_vagas_exibir, use_container_width=True, hide_index=True)

        st.markdown("---")

        # --- Plano de Pagamento ---
        st.subheader("Plano de Pagamento")

        col_p1, col_p2, col_p3, col_p4 = st.columns(4)
        col_p1.metric("Sinal (10%)", formatar_brl(row["SINAL_10"]))
        col_p2.metric("Mensais 52x (25%)", formatar_brl(row["MENSAIS_52X"]))
        col_p3.metric("Semestrais 7x (20%)", formatar_brl(row["SEMESTRAIS_7X"]))
        col_p4.metric("Chaves (45%)", formatar_brl(row["CHAVES_45"]))

        st.markdown("---")

        # --- Gráficos lado a lado ---
        col_graf1, col_graf2 = st.columns(2)

        with col_graf1:
            st.subheader("Composição de Áreas")
            areas_comp = pd.DataFrame({
                "Tipo": ["Padrão", "Técnica", "Terraço"],
                "Área (m²)": [row["AREA PADRAO"], row["AREA TECNICA"], row["AREA TERRACO"]],
            })
            areas_comp = areas_comp[areas_comp["Área (m²)"] > 0]

            fig_areas = px.bar(
                areas_comp,
                x="Área (m²)",
                y="Tipo",
                orientation="h",
                color_discrete_sequence=["#2563EB"],
                text="Área (m²)",
            )
            fig_areas.update_traces(texttemplate="%{text:,.2f} m²", textposition="outside")
            fig_areas.update_layout(
                margin=dict(t=20, b=20, l=20, r=20),
                height=300,
                xaxis_title="",
                yaxis_title="",
            )
            st.plotly_chart(fig_areas, use_container_width=True)

        with col_graf2:
            st.subheader("Comparação com Médias")
            preco_medio_pav = df_precos_completo[
                df_precos_completo["PAVIMENTO"] == row["PAVIMENTO"]
            ]["PRECO_M2"].mean()
            preco_medio_torre = df_precos_completo[
                df_precos_completo["Torre_Nome"] == row["Torre_Nome"]
            ]["PRECO_M2"].mean()

            comparacao = pd.DataFrame({
                "Referência": ["Esta Unidade", f"Média {row['PAVIMENTO']}", f"Média Torre {row['Torre_Nome']}"],
                "Preço/m² (R$)": [row["PRECO_M2"], preco_medio_pav, preco_medio_torre],
            })

            fig_comp = px.bar(
                comparacao,
                x="Referência",
                y="Preço/m² (R$)",
                color="Referência",
                color_discrete_sequence=["#059669", "#6B7280", "#6B7280"],
                text="Preço/m² (R$)",
            )
            fig_comp.update_traces(texttemplate="R$ %{text:,.0f}", textposition="outside")
            fig_comp.update_layout(
                margin=dict(t=20, b=20, l=20, r=20),
                height=300,
                xaxis_title="",
                yaxis_title="",
                showlegend=False,
            )
            st.plotly_chart(fig_comp, use_container_width=True)
