import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils import BG, GRID, FONT, COLORS, theme, fmt_brl, _wrap, _mute, kpi_card, make_svg_icon


def render(
    df_base: pd.DataFrame,
    receita_total: float,
    lucro_total: float,
    margem_media: float,
    qtd_total: float,
):
    # ── KPI row ──────────────────────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    kpi_card(c1, "green",  make_svg_icon("#00d4a0", '<line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>'),
             "Receita Total",    fmt_brl(receita_total),                              "Todas as vendas")
    kpi_card(c2, "purple", make_svg_icon("#a855f7",  '<polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/>'),
             "Lucro Bruto",      fmt_brl(lucro_total),                               "Receita – Custo")
    kpi_card(c3, "orange", make_svg_icon("#fb923c",  '<line x1="19" y1="5" x2="5" y2="19"/><circle cx="6.5" cy="6.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/>'),
             "Margem Bruta",     f"{margem_media:.1f}%",                             "Média ponderada")
    kpi_card(c4, "blue",   make_svg_icon("#4f8ef7",  '<path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/>'),
             "Unidades Vendidas", f"{int(qtd_total):,}".replace(",", "."),           "Qtd. total")
    kpi_card(c5, "red",    make_svg_icon("#f43f5e",  '<rect x="1" y="4" width="22" height="16" rx="2" ry="2"/><line x1="1" y1="10" x2="23" y2="10"/>'),
             "Custo Total",      fmt_brl(receita_total - lucro_total),               "Custo acumulado")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Margem por Categoria + Receita vs Custo vs Lucro por Marca ───────────
    col_m1, col_m2 = st.columns(2)

    with col_m1:
        margin_cat = (
            df_base.groupby("Categoria")
            .apply(lambda x: (x["Lucro"].sum() / x["Receita"].sum() * 100) if x["Receita"].sum() > 0 else 0)
            .reset_index(name="Margem %")
            .sort_values("Margem %", ascending=True).tail(12)
        )
        fig = px.bar(margin_cat, x="Margem %", y="Categoria", orientation="h",
                     color="Margem %", color_continuous_scale=["#064e3b", "#00d4a0"],
                     text="Margem %")
        fig.update_traces(
            texttemplate="%{text:.1f}%", textposition="outside",
            hovertemplate="<b>%{y}</b><br>Margem: %{x:.1f}%<extra></extra>",
        )
        fig.update_layout(coloraxis_showscale=False)
        theme(fig, "Margem de Lucro por Categoria (%)", height=360)
        fig.update_layout(xaxis=dict(ticksuffix="%", range=[10, margin_cat["Margem %"].max() * 1.12]))
        st.plotly_chart(fig, use_container_width=True)

    with col_m2:
        bp = (
            df_base.groupby("Marca")
            .agg(Receita=("Receita", "sum"), Custo=("Custo Total", "sum"), Lucro=("Lucro", "sum"))
            .reset_index().sort_values("Receita", ascending=False)
        )
        bp["Marca_label"] = bp["Marca"].apply(_wrap)
        fig = go.Figure()
        for name, color in [("Receita", "#2563eb"), ("Lucro", "#00b389"), ("Custo", "#f43f5e")]:
            fig.add_trace(go.Bar(
                name=name, x=bp["Marca_label"], y=bp[name], marker_color=color,
                customdata=bp["Marca"],
                hovertemplate=f"<b>%{{customdata}}</b><br>{name}: R$ %{{y:,.0f}}<extra></extra>",
            ))
        theme(fig, "Receita vs Custo vs Lucro por Marca", height=360)
        fig.update_layout(
            barmode="group",
            legend=dict(orientation="h", y=1.08, x=0.01),
            yaxis=dict(tickformat=",.0f", tickprefix="R$ "),
            xaxis=dict(tickangle=0, automargin=True, range=[-0.52, len(bp) - 0.48]),
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── Treemap ───────────────────────────────────────────────────────────────
    tree_df = df_base.groupby(["Categoria", "Marca"])["Receita"].sum().reset_index()
    _tm_palette = [_mute(c) for c in [
        "#00d4a0", "#4f8ef7", "#a855f7", "#fb923c", "#f43f5e",
        "#eab308", "#10b981", "#3b82f6", "#9333ea", "#ec4899",
        "#0891b2", "#7c3aed", "#dc2626", "#d97706", "#059669",
        "#2563eb", "#be185d", "#b45309", "#0f766e", "#6d28d9",
    ]]
    cats_sorted = sorted(tree_df["Categoria"].unique())
    _color_map  = {cat: _tm_palette[i % len(_tm_palette)] for i, cat in enumerate(cats_sorted)}
    fig = px.treemap(
        tree_df, path=["Categoria", "Marca"], values="Receita",
        color="Categoria", color_discrete_map=_color_map,
    )
    fig.update_traces(
        hovertemplate="<b>%{label}</b><br>R$ %{value:,.0f}<extra></extra>",
        textfont=dict(color="white", size=12),
        marker=dict(line=dict(color="#0f1117", width=2)),
    )
    theme(fig, "Receita por Categoria e Marca (Treemap)", height=300)
    fig.update_layout(margin=dict(l=0, r=0, t=36, b=0))
    st.plotly_chart(fig, use_container_width=True)
