import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils import BG, GRID, FONT, COLORS, theme, fmt_brl, _wrap, kpi_card, make_svg_icon


def render(
    df_base: pd.DataFrame,
    receita_total: float,
    qtd_total: float,
    lucro_total: float,
    margem_media: float,
    num_clientes: int,
):
    # ── KPI row ──────────────────────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    kpi_card(c1, "green",  make_svg_icon("#00d4a0", '<line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>'),
             "Receita Total",    fmt_brl(receita_total),                        "Todas as vendas")
    kpi_card(c2, "blue",   make_svg_icon("#4f8ef7",  '<path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/>'),
             "Unidades Vendidas", f"{int(qtd_total):,}".replace(",", "."),      "Qtd. total")
    kpi_card(c3, "purple", make_svg_icon("#a855f7",  '<polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/>'),
             "Lucro Bruto",      fmt_brl(lucro_total),                          "Receita – Custo")
    kpi_card(c4, "orange", make_svg_icon("#fb923c",  '<line x1="19" y1="5" x2="5" y2="19"/><circle cx="6.5" cy="6.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/>'),
             "Margem Bruta",     f"{margem_media:.1f}%",                        "Média ponderada")
    kpi_card(c5, "red",    make_svg_icon("#f43f5e",  '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>'),
             "Clientes Únicos",  f"{num_clientes:,}".replace(",", "."),         "Compradores distintos")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Série temporal + Top Categorias ──────────────────────────────────────
    col_l, col_r = st.columns([3, 2])

    with col_l:
        monthly = (
            df_base.groupby("Mês")
            .agg(Receita=("Receita", "sum"), Lucro=("Lucro", "sum"))
            .reset_index().sort_values("Mês")
        )
        monthly["Data"] = pd.to_datetime(monthly["Mês"] + "-01")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=monthly["Data"], y=monthly["Receita"], name="Receita",
            mode="lines+markers", line=dict(color="#4f8ef7", width=2.5),
            marker=dict(size=5), fill="tozeroy", fillcolor="rgba(79,142,247,0.08)",
        ))
        fig.add_trace(go.Scatter(
            x=monthly["Data"], y=monthly["Lucro"], name="Lucro",
            mode="lines+markers", line=dict(color="#00d4a0", width=2.5),
            marker=dict(size=5), fill="tozeroy", fillcolor="rgba(0,212,160,0.08)",
        ))
        theme(fig, "Receita e Lucro ao Longo do Tempo")
        fig.update_layout(
            xaxis=dict(
                tickformatstops=[
                    dict(dtickrange=[None, "M1"],  value="%b/%y"),
                    dict(dtickrange=["M1", "M12"], value="%b/%y"),
                    dict(dtickrange=["M12", None], value="%Y"),
                ],
                tickangle=0, automargin=True,
            ),
            yaxis=dict(tickformat=",.0f", tickprefix="R$ "),
            legend=dict(orientation="h", y=1.08, x=0.01),
            hovermode="x unified",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        by_cat = (
            df_base.groupby("Categoria")["Receita"]
            .sum().sort_values(ascending=True).tail(10).reset_index()
        )
        by_cat["_txt"] = by_cat["Receita"].apply(fmt_brl)
        fig = px.bar(by_cat, x="Receita", y="Categoria", orientation="h",
                     color="Receita", color_continuous_scale=["#1e3a5f", "#60a5fa"],
                     text="_txt")
        fig.update_traces(
            hovertemplate="<b>%{y}</b><br>R$ %{x:,.0f}<extra></extra>",
            textposition="outside",
            textfont=dict(color="#cbd5e1", size=13),
            cliponaxis=False,
        )
        fig.update_layout(coloraxis_showscale=False)
        _xtvals = list(range(0, 25_000_001, 5_000_000))
        _xttxt  = ["R$ 0"] + [f"R$ {v // 1_000_000}M" for v in _xtvals[1:]]
        theme(fig, "Top 10 Categorias por Receita")
        fig.update_layout(
            xaxis=dict(tickvals=_xtvals, ticktext=_xttxt, range=[0, 25_000_000], showgrid=True),
            yaxis=dict(range=[-0.52, len(by_cat) - 0.48], showgrid=False),
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── Donut Marca + Top Produtos ────────────────────────────────────────────
    col_a, col_b = st.columns([1.5, 2.5])

    with col_a:
        by_brand = (
            df_base.groupby("Marca")["Receita"]
            .sum().sort_values(ascending=False).reset_index()
        )
        clrs = ["#4f8ef7", "#00d4a0", "#a855f7", "#fb923c", "#f43f5e",
                "#facc15", "#34d399", "#60a5fa"]
        fig = go.Figure(go.Pie(
            labels=by_brand["Marca"], values=by_brand["Receita"], hole=0.55,
            marker=dict(colors=clrs[:len(by_brand)], line=dict(color="#0f1117", width=2)),
            textinfo="label+percent",
            textposition="outside",
            textfont=dict(color="#cbd5e1", size=13),
            hovertemplate="<b>%{label}</b><br>R$ %{value:,.0f}<br>%{percent}<extra></extra>",
            domain=dict(x=[0.08, 0.92], y=[0.08, 0.92]),
        ))
        theme(fig, "Receita por Marca", height=380)
        fig.update_layout(
            showlegend=False,
            annotations=[dict(
                text=f"<b>{fmt_brl(receita_total)}</b>",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=26, color="#f1f5f9"),
            )],
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        top_prod = (
            df_base.groupby("Produto")["Receita"]
            .sum().sort_values(ascending=False).head(10).reset_index()
        )
        top_prod["label"] = top_prod["Produto"].apply(_wrap)
        top_prod["_txt"] = top_prod["Receita"].apply(fmt_brl)
        fig = px.bar(top_prod, x="label", y="Receita", text="_txt")
        fig.update_traces(
            marker_color="#a855f7",
            hovertemplate="<b>%{customdata[0]}</b><br>R$ %{y:,.0f}<extra></extra>",
            customdata=top_prod[["Produto"]].values,
            textposition="outside",
            textfont=dict(color="#cbd5e1", size=14),
            cliponaxis=False,
        )
        _y_max  = top_prod["Receita"].max() * 1.25
        _ystep  = 10_000_000 if _y_max > 30_000_000 else 5_000_000
        _ytvals = list(range(0, int(_y_max) + _ystep, _ystep))
        _yttxt  = ["R$ 0"] + [f"R$ {v // 1_000_000}M" for v in _ytvals[1:]]
        theme(fig, "Top 10 Produtos por Receita", height=380)
        fig.update_layout(
            xaxis=dict(tickangle=0, automargin=True, range=[-0.52, len(top_prod) - 0.48]),
            yaxis=dict(tickvals=_ytvals, ticktext=_yttxt, range=[0, _y_max]),
        )
        st.plotly_chart(fig, use_container_width=True)
