import pandas as pd
import streamlit as st
from pathlib import Path


PASTA_PROJETO = Path(__file__).parent
ARQUIVO_NBR = PASTA_PROJETO / "AREAS REVIT NBR 12721 R15.xlsx"
ARQUIVO_UNIDADES = PASTA_PROJETO / "UNIDADES VICENZO.xlsx"
ARQUIVO_VAGAS = PASTA_PROJETO / "VAGAS VICENZO R15 2026-04-26.xlsx"

ORDEM_NIVEIS = [
    "PAVIMENTO SUBSOLO",
    "PAVIMENTO TÉRREO",
    "PAVIMENTO 01",
    "PAVIMENTO 02",
    "PAVIMENTO 03",
    "PAVIMENTO 04",
    "PAVIMENTO 05",
    "PAVIMENTO 06",
    "PAVIMENTO 07",
    "PAVIMENTO 08",
    "PAVIMENTO 09",
    "PAVIMENTO 10",
    "PAVIMENTO 11",
    "COBERTURA",
]

ORDEM_PAVIMENTOS_TIPO = [
    "PAVIMENTO 01",
    "PAVIMENTO 02",
    "PAVIMENTO 03",
    "PAVIMENTO 04",
    "PAVIMENTO 05",
    "PAVIMENTO 06",
    "PAVIMENTO 07",
    "PAVIMENTO 08",
    "PAVIMENTO 09",
    "PAVIMENTO 10",
    "PAVIMENTO 11",
]


def _extrair_torre(valor):
    if pd.isna(valor):
        return "Área Comum"
    valor = str(valor).strip()
    if valor.endswith(" A"):
        return "Norte"
    elif valor.endswith(" B"):
        return "Sul"
    return "Área Comum"


# --- Dados NBR 12721 (áreas do Revit) ---

@st.cache_data
def carregar_dados() -> pd.DataFrame:
    df = pd.read_excel(ARQUIVO_NBR, sheet_name="Areas", header=0)

    df = df.rename(columns={
        "Nível": "Nivel",
        "Área": "Area",
        "NBR 12721 - UNIDADE AUTONOMA": "Unidade_Autonoma",
        "NBR 12721 - GRUPO": "Grupo",
        "NBR 12721 - USO": "Uso",
        "NBR 12721 - ACABAMENTO": "Acabamento",
    })

    df = df.drop(columns=["ID", "Grupo"])
    df["Torre"] = df["Unidade_Autonoma"].apply(_extrair_torre)
    df["Nivel"] = pd.Categorical(df["Nivel"], categories=ORDEM_NIVEIS, ordered=True)

    return df


def filtrar_dados(df: pd.DataFrame, niveis, torres, usos, acabamentos) -> pd.DataFrame:
    mask = pd.Series(True, index=df.index)

    if niveis:
        mask &= df["Nivel"].isin(niveis)
    if torres:
        mask &= df["Torre"].isin(torres)
    if usos:
        mask &= df["Uso"].isin(usos)
    if acabamentos:
        mask &= df["Acabamento"].isin(acabamentos)

    return df[mask]


# --- Dados de Preços e Unidades ---

@st.cache_data
def carregar_dados_precos() -> pd.DataFrame:
    df_unidades = pd.read_excel(ARQUIVO_UNIDADES, sheet_name="UNIDADES", header=0)
    df_precos_raw = pd.read_excel(ARQUIVO_UNIDADES, sheet_name="TABELA PRECOS", header=0)

    # Selecionar colunas relevantes de UNIDADES
    cols_unidades = [
        "UNIDADE", "PAVIMENTO", "TORRE", "COLUNA",
        "SUITES", "QUARTOS", "SUITES+QUARTOS",
        "POSICAO NASCENTE/POENTE", "POSICAO NORTE/SUL", "POSICAO INTERNO/EXTERNO",
        "AREA PADRAO", "AREA TECNICA", "AREA TERRACO", "AREA CALCULO DE PRECO",
        "TIPOLOGIA",
    ]
    df_unidades = df_unidades[cols_unidades]
    df_unidades = df_unidades.dropna(subset=["UNIDADE"])

    # Selecionar colunas de TABELA PRECOS por posição (encoding dos nomes é instável)
    # [0]=UNIDADE, [5]=REFERÊNCIA, [6]=FRACAO VGV, [7]=PREÇO,
    # [8]=SINAL, [9]=MENSAIS, [10]=SEMESTRAIS, [11]=CHAVES
    df_precos = df_precos_raw.iloc[:, [0, 5, 6, 7, 8, 9, 10, 11]].copy()
    df_precos.columns = [
        "UNIDADE", "REFERENCIA", "FRACAO_VGV", "PRECO",
        "SINAL_10", "MENSAIS_52X", "SEMESTRAIS_7X", "CHAVES_45",
    ]

    # Merge
    df = df_unidades.merge(df_precos, on="UNIDADE", how="left")

    # Mapear torre A/B para Norte/Sul
    df["Torre_Nome"] = df["TORRE"].map({"A": "Norte", "B": "Sul"})

    # Calcular preço/m²
    df["PRECO_M2"] = df["PRECO"] / df["AREA CALCULO DE PRECO"]

    # Ordenar pavimento
    df["PAVIMENTO"] = pd.Categorical(
        df["PAVIMENTO"], categories=ORDEM_PAVIMENTOS_TIPO, ordered=True
    )

    return df


def filtrar_precos(df, pavimentos=None, torres=None, tipologias=None,
                   quartos=None, posicao_sol=None, posicao_face=None, posicao_acesso=None):
    mask = pd.Series(True, index=df.index)

    if pavimentos:
        mask &= df["PAVIMENTO"].isin(pavimentos)
    if torres:
        mask &= df["Torre_Nome"].isin(torres)
    if tipologias:
        mask &= df["TIPOLOGIA"].isin(tipologias)
    if quartos:
        mask &= df["SUITES+QUARTOS"].isin(quartos)
    if posicao_sol:
        mask &= df["POSICAO NASCENTE/POENTE"].isin(posicao_sol)
    if posicao_face:
        mask &= df["POSICAO NORTE/SUL"].isin(posicao_face)
    if posicao_acesso:
        mask &= df["POSICAO INTERNO/EXTERNO"].isin(posicao_acesso)

    return df[mask]


# --- Dados de Vagas ---

@st.cache_data
def carregar_vagas() -> pd.DataFrame:
    df = pd.read_excel(ARQUIVO_VAGAS, sheet_name="VAGAS", header=0)

    # Classificar tipo de vaga
    def tipo_vaga(row):
        if row.get("SOLTA TOTAL", 0) == 1:
            return "Solta Total"
        elif row.get("SOLTA PARCIAL", 0) == 1:
            return "Solta Parcial"
        elif row.get("PRESA", 0) == 1:
            return "Presa"
        return "Indefinida"

    df["Tipo_Vaga"] = df.apply(tipo_vaga, axis=1)

    return df


def vagas_por_unidade(df_vagas: pd.DataFrame) -> pd.DataFrame:
    """Retorna DataFrame com contagem de vagas por unidade e tipos."""
    if df_vagas.empty:
        return pd.DataFrame()

    resumo = df_vagas.groupby("UNIDADE").agg(
        Total_Vagas=("VAGA", "count"),
        Soltas_Total=("SOLTA TOTAL", "sum"),
        Soltas_Parcial=("SOLTA PARCIAL", "sum"),
        Presas=("PRESA", "sum"),
    ).reset_index()

    return resumo
