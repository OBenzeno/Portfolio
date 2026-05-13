import pandas as pd
import streamlit as st

PAIS_ISO = {
    "Alemanha":"DEU","Argentina":"ARG","Austrália":"AUS","Áustria":"AUT",
    "Bélgica":"BEL","Brasil":"BRA","Canadá":"CAN","Chile":"CHL","China":"CHN",
    "Colômbia":"COL","Coreia do Sul":"KOR","Dinamarca":"DNK","Egito":"EGY",
    "Emirados Árabes":"ARE","Espanha":"ESP","Estados Unidos":"USA",
    "Filipinas":"PHL","Finlândia":"FIN","França":"FRA","Grécia":"GRC",
    "Holanda":"NLD","Hong Kong":"HKG","Hungria":"HUN","Índia":"IND",
    "Indonésia":"IDN","Irlanda":"IRL","Israel":"ISR","Itália":"ITA",
    "Japão":"JPN","Malásia":"MYS","México":"MEX","Noruega":"NOR",
    "Nova Zelândia":"NZL","Peru":"PER","Polônia":"POL","Portugal":"PRT",
    "Reino Unido":"GBR","República Checa":"CZE","Rússia":"RUS",
    "Singapura":"SGP","Suécia":"SWE","Suíça":"CHE","Taiwan":"TWN",
    "Tailândia":"THA","Turquia":"TUR","Venezuela":"VEN","África do Sul":"ZAF",
    "Marrocos":"MAR","Uruguai":"URY","Arábia Saudita":"SAU","Irã":"IRN",
    "Romênia":"ROU","Bulgária":"BGR","Croácia":"HRV","Eslováquia":"SVK",
    "Ucrânia":"UKR","Cazaquistão":"KAZ","Bolívia":"BOL","Equador":"ECU",
    "Costa Rica":"CRI","Guatemala":"GTM","Panamá":"PAN","Cuba":"CUB",
    "Vietnã":"VNM","Bangladesh":"BGD","Paquistão":"PAK","Nigéria":"NGA",
    "Angola":"AGO","Kênia":"KEN","Tanzânia":"TZA","Gana":"GHA",
    "Tunísia":"TUN","Argélia":"DZA","Líbia":"LBY","Etiópia":"ETH",
    "Moçambique":"MOZ","Zâmbia":"ZMB","Jordânia":"JOR","Kuwait":"KWT",
    "Qatar":"QAT","Líbano":"LBN","República Dominicana":"DOM",
}

_PAIS_CONTINENTE = {
    "Austrália": "Oceania",
    "Nova Zelândia": "Oceania",
}


@st.cache_data(show_spinner="Carregando dados...")
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="utf-8-sig")
    df = df.drop(columns=[c for c in df.columns if "Unnamed" in str(c)], errors="ignore")
    for col in ["Marca", "Categoria", "Localidade", "Produto"]:
        df[col] = df[col].astype(str).str.strip()
    df["Data da Venda"] = pd.to_datetime(df["Data da Venda"], errors="coerce")
    df = df.dropna(subset=["Data da Venda"])
    df["Receita"]     = df["PrecoUnitario"] * df["Qtd. Vendida"]
    df["Custo Total"] = df["Custo Unitário"] * df["Qtd. Vendida"]
    df["Lucro"]       = df["Receita"] - df["Custo Total"]
    split = df["Localidade"].str.split(" - ", n=1, expand=True)
    df["País"]       = split[0].str.strip()
    df["Continente"] = split[1].str.strip() if 1 in split.columns else "Desconhecido"
    mask = df["Continente"] == df["País"]
    df.loc[mask, "Continente"] = df.loc[mask, "País"].map(_PAIS_CONTINENTE).fillna("Desconhecido")
    df["ISO"] = df["País"].map(PAIS_ISO)
    df["Ano"] = df["Data da Venda"].dt.year
    df["Mês"] = df["Data da Venda"].dt.to_period("M").astype(str)
    return df


def get_all_months(df: pd.DataFrame) -> list:
    return sorted(df["Mês"].unique())
