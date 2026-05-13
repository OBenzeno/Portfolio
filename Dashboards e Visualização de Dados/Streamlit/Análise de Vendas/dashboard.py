import streamlit as st
from pathlib import Path

from styles import CSS
from data import load_data, get_all_months
from utils import fmt_brl
from sidebar import render_sidebar
from views import visao_geral, performance, geografia

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard de Vendas",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(CSS, unsafe_allow_html=True)

# ── Dados ─────────────────────────────────────────────────────────────────────
CSV_PATH = str(Path(__file__).parent / "vendas.csv")
try:
    df_raw = load_data(CSV_PATH)
except Exception as e:
    st.error(f"Erro ao carregar o arquivo: {e}")
    st.stop()

all_months = get_all_months(df_raw)

# ── Sidebar ───────────────────────────────────────────────────────────────────
filters    = render_sidebar(df_raw, all_months)
page       = filters["page"]
sd_month   = filters["sd_month"]
ed_month   = filters["ed_month"]
sel_cats   = filters["sel_cats"]
sel_brands = filters["sel_brands"]
cats       = filters["cats"]
brands     = filters["brands"]

# ── Header dinâmico ───────────────────────────────────────────────────────────
_h = 'fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
PAGE_INFO = {
    "Visão Geral": (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" {_h} stroke="#00d4a0"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>',
        "Visão Geral", "KPIs · Evolução Temporal · Categorias · Marcas · Produtos",
    ),
    "Performance": (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" {_h} stroke="#4f8ef7"><rect x="2" y="13" width="4" height="8" rx="1"/><rect x="9" y="8" width="4" height="13" rx="1"/><rect x="16" y="3" width="4" height="18" rx="1"/></svg>',
        "Performance", "Margens · Receita vs Custo · Treemap por Categoria",
    ),
    "Geografia": (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" {_h} stroke="#a855f7"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>',
        "Geografia", "Mapa Mundial · Países · Continentes",
    ),
}
ico, titulo, subtitulo = PAGE_INFO[page]
st.markdown(f"""
<div class="dashboard-header">
    {ico}
    <div>
        <p class="header-title">{titulo}</p>
        <p class="header-sub">{subtitulo}</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Filtro base ───────────────────────────────────────────────────────────────
df_base = df_raw[
    (df_raw["Mês"] >= sd_month) &
    (df_raw["Mês"] <= ed_month) &
    (df_raw["Categoria"].isin(sel_cats  if sel_cats  else cats)) &
    (df_raw["Marca"].isin(sel_brands if sel_brands else brands))
].copy()

if df_base.empty:
    st.warning("Nenhum dado para os filtros selecionados.")
    st.stop()

receita_total = df_base["Receita"].sum()
lucro_total   = df_base["Lucro"].sum()
margem_media  = (lucro_total / receita_total * 100) if receita_total > 0 else 0
qtd_total     = df_base["Qtd. Vendida"].sum()
num_clientes  = df_base["Nome Cliente"].nunique()

# ── Roteamento ────────────────────────────────────────────────────────────────
if page == "Visão Geral":
    visao_geral.render(df_base, receita_total, qtd_total, lucro_total, margem_media, num_clientes)
elif page == "Performance":
    performance.render(df_base, receita_total, lucro_total, margem_media, qtd_total)
elif page == "Geografia":
    geografia.render(df_base, receita_total)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align:center;font-size:13px;color:#94a3b8;padding:6px 0'>
    Dashboard de Vendas · Jun/2017 – Ago/2019 · Streamlit + Plotly
</div>
""", unsafe_allow_html=True)
