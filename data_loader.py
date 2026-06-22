import pandas as pd
import streamlit as st
from pathlib import Path


ARQUIVO_EXCEL = Path(__file__).parent / "AREAS REVIT NBR 12721 R15.xlsx"

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


@st.cache_data
def carregar_dados() -> pd.DataFrame:
    df = pd.read_excel(ARQUIVO_EXCEL, sheet_name="Areas", header=0)

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


def _extrair_torre(valor):
    if pd.isna(valor):
        return "Área Comum"
    valor = str(valor).strip()
    if valor.endswith(" A"):
        return "Norte"
    elif valor.endswith(" B"):
        return "Sul"
    return "Área Comum"


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
