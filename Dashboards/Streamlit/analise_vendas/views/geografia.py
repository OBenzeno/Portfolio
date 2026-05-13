import streamlit as st
import pandas as pd
import plotly.express as px

from utils import BG, GRID, FONT, COLORS, theme, fmt_brl, kpi_card, make_svg_icon


def render(df_base: pd.DataFrame, receita_total: float):
    # ── KPI row geográfico ────────────────────────────────────────────────────
    continents_all = sorted([c for c in df_base["Continente"].dropna().unique() if c != "nan"])
    num_paises = df_base["País"].nunique()
    top_pais   = df_base.groupby("País")["Receita"].sum().idxmax()
    top_cont   = df_base.groupby("Continente")["Receita"].sum().idxmax()

    c1, c2, c3, c4, c5 = st.columns(5)
    kpi_card(c1, "green",  make_svg_icon("#00d4a0", '<line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>'),
             "Receita Total",  fmt_brl(receita_total), "Global")
    kpi_card(c2, "blue",   make_svg_icon("#4f8ef7",  '<circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>'),
             "Países Ativos", str(num_paises),         "Com vendas registradas")
    kpi_card(c3, "purple", make_svg_icon("#a855f7",  '<path d="M3 12a9 9 0 1 0 18 0 9 9 0 0 0-18 0"/><path d="M3.6 9h16.8M3.6 15h16.8"/><path d="M12 3a9 9 0 0 0-4.5 7.5h9A9 9 0 0 0 12 3z"/><path d="M12 21a9 9 0 0 0 4.5-7.5h-9A9 9 0 0 0 12 21z"/>'),
             "Continentes",   str(len(continents_all)), "Regiões presentes")
    kpi_card(c4, "orange", make_svg_icon("#fb923c",  '<circle cx="12" cy="8" r="6"/><path d="M15.477 12.89L17 22l-5-3-5 3 1.523-9.11"/>'),
             "Top País",      top_pais,               "Maior receita")
    kpi_card(c5, "red",    make_svg_icon("#f43f5e",  '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>'),
             "Top Continente", top_cont,              "Maior receita")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Filtro de continentes ─────────────────────────────────────────────────
    sel_cont = st.pills(
        "Continentes",
        options=continents_all,
        default=continents_all,
        selection_mode="multi",
        label_visibility="collapsed",
    )

    df_geo = df_base[df_base["Continente"].isin(sel_cont)].copy() if sel_cont else df_base.copy()

    if df_geo.empty:
        st.warning("Selecione ao menos um continente.")
        st.stop()

    # ── Mapa + Tabela ─────────────────────────────────────────────────────────
    col_map, col_tbl = st.columns([2.5, 1.5])

    with col_map:
        map_data = (
            df_geo.dropna(subset=["ISO"])
            .groupby(["País", "ISO"])
            .agg(Receita=("Receita", "sum"), Lucro=("Lucro", "sum"), Qtd=("Qtd. Vendida", "sum"))
            .reset_index()
        )
        map_data["Receita_fmt"] = map_data["Receita"].apply(fmt_brl)
        map_data["Margem"]      = (map_data["Lucro"] / map_data["Receita"] * 100).round(1)

        fig = px.choropleth(
            map_data, locations="ISO", color="Receita",
            hover_name="País",
            hover_data={"ISO": False, "Receita_fmt": True, "Margem": True, "Qtd": True},
            color_continuous_scale=["#064e3b", "#047857", "#10b981", "#00d4a0", "#6ee7b7"],
            labels={"Receita_fmt": "Receita", "Margem": "Margem (%)", "Qtd": "Unidades"},
        )
        fig.update_traces(marker_line_color="#0f1117", marker_line_width=0.5)
        fig.update_layout(
            paper_bgcolor=BG, plot_bgcolor=BG,
            geo=dict(
                bgcolor=BG, showframe=False,
                showcoastlines=True, coastlinecolor="#2a3550",
                showland=True, landcolor="#1a2235",
                showocean=True, oceancolor="#0f1117",
                showlakes=False,
                showcountries=True, countrycolor="#2a3550",
                projection_type="natural earth",
            ),
            coloraxis_colorbar=dict(
                title=dict(text="Receita", font=dict(color=FONT, size=11)),
                tickfont=dict(color=FONT, size=10),
                bgcolor=BG, bordercolor=GRID,
            ),
            margin=dict(l=0, r=0, t=36, b=0),
            height=420,
            title=dict(text="Receita por País", font=dict(size=13, color="#e2e8f0"), x=0.01),
            font_color=FONT,
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_tbl:
        top_c = (
            df_geo.groupby("País")
            .agg(Receita=("Receita", "sum"), Lucro=("Lucro", "sum"), Qtd=("Qtd. Vendida", "sum"))
            .sort_values("Receita", ascending=False).head(15).reset_index()
        )
        top_c["Margem"] = (top_c["Lucro"] / top_c["Receita"] * 100).round(1)
        max_receita = top_c["Receita"].max()
        max_lucro   = top_c["Lucro"].max()
        max_qtd     = top_c["Qtd"].max()
        st.dataframe(
            top_c[["País", "Receita", "Lucro", "Margem", "Qtd"]],
            use_container_width=True,
            hide_index=True,
            height=423,
            column_config={
                "País":    st.column_config.TextColumn("País"),
                "Receita": st.column_config.ProgressColumn("Receita",      format="R$ %.0f", min_value=0, max_value=max_receita),
                "Lucro":   st.column_config.ProgressColumn("Lucro",        format="R$ %.0f", min_value=0, max_value=max_lucro),
                "Margem":  st.column_config.ProgressColumn("Margem %",     format="%.1f%%",  min_value=0, max_value=100),
                "Qtd":     st.column_config.ProgressColumn("Qtd. Vendida", format="%d",      min_value=0, max_value=max_qtd),
            },
        )

    # ── Barras por Continente ─────────────────────────────────────────────────
    by_cont = (
        df_geo.groupby("Continente")["Receita"]
        .sum().sort_values(ascending=True).reset_index()
    )
    fig = px.bar(by_cont, x="Receita", y="Continente", orientation="h",
                 color="Continente", color_discrete_sequence=COLORS)
    fig.update_traces(hovertemplate="<b>%{y}</b><br>R$ %{x:,.0f}<extra></extra>")
    theme(fig, "Receita por Continente", height=280)
    fig.update_layout(
        showlegend=False, yaxis_title="",
        xaxis=dict(tickformat=",.0f", tickprefix="R$ "),
    )
    st.plotly_chart(fig, use_container_width=True)
