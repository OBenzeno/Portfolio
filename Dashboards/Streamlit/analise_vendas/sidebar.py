import streamlit as st
import pandas as pd


def render_sidebar(df_raw: pd.DataFrame, all_months: list) -> dict:
    with st.sidebar:
        st.markdown("""
        <div style='text-align:center;padding:12px 0 16px'>
            <svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 24 24" fill="none" stroke="#00d4a0" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
              <rect x="2" y="13" width="4" height="8" rx="1"/>
              <rect x="9" y="8" width="4" height="13" rx="1"/>
              <rect x="16" y="3" width="4" height="18" rx="1"/>
              <polyline points="3,12 10,7 17,2" stroke="#4f8ef7" stroke-width="1.4"/>
            </svg>
            <div style='font-size:24px;font-weight:700;color:#f1f5f9;margin-top:12px;letter-spacing:0.3px'>Vendas Analytics</div>
            <div style='font-size:15px;color:#94a3b8;margin-top:5px'>Dashboard Interativo</div>
        </div>""", unsafe_allow_html=True)

        st.markdown("---")

        if "page" not in st.session_state:
            st.session_state["page"] = "Visão Geral"
        _nav = ["Visão Geral", "Performance", "Geografia"]
        for _p in _nav:
            _type = "primary" if st.session_state["page"] == _p else "secondary"
            if st.button(_p, key=f"nav_{_p}", use_container_width=True, type=_type):
                st.session_state["page"] = _p
                st.rerun()
        page = st.session_state["page"]

        st.markdown("---")

        # ── Filtro de Período ──
        with st.expander("PERÍODO", expanded=True):
            anos_disp = [str(a) for a in sorted(df_raw["Ano"].unique())]
            sel_preset = st.radio(
                "período",
                options=anos_disp + ["Tudo", "Personalizado"],
                index=len(anos_disp),
                label_visibility="collapsed",
            )
            if sel_preset == "Personalizado":
                _min = df_raw["Data da Venda"].min().date()
                _max = df_raw["Data da Venda"].max().date()
                _dr  = st.date_input(
                    "datas", value=(_min, _max),
                    min_value=_min, max_value=_max,
                    label_visibility="collapsed",
                )
                if len(_dr) == 2:
                    sd_month = pd.Timestamp(_dr[0]).strftime("%Y-%m")
                    ed_month = pd.Timestamp(_dr[1]).strftime("%Y-%m")
                else:
                    sd_month, ed_month = all_months[0], all_months[-1]
            elif sel_preset != "Tudo":
                y = int(sel_preset)
                sd_month = max(f"{y}-01", all_months[0])
                ed_month = min(f"{y}-12", all_months[-1])
            else:
                sd_month, ed_month = all_months[0], all_months[-1]

        cats   = sorted([c for c in df_raw["Categoria"].unique() if c != "nan"])
        brands = sorted([b for b in df_raw["Marca"].unique()     if b != "nan"])

        # ── Filtro de Categoria ──
        with st.expander("CATEGORIA", expanded=False):
            sel_all_cats = st.checkbox("Todas", value=True, key="all_cats")
            col1, col2 = st.columns(2)
            sel_cats = []
            for i, cat in enumerate(cats):
                col = col1 if i % 2 == 0 else col2
                if col.checkbox(cat, value=sel_all_cats, key=f"cat_{cat}"):
                    sel_cats.append(cat)

        # ── Filtro de Marca ──
        with st.expander("MARCA", expanded=False):
            sel_all_brands = st.checkbox("Todas", value=True, key="all_brands")
            col1, col2 = st.columns(2)
            sel_brands = []
            for i, brand in enumerate(brands):
                col = col1 if i % 2 == 0 else col2
                if col.checkbox(brand, value=sel_all_brands, key=f"brand_{brand}"):
                    sel_brands.append(brand)

        st.markdown("---")
        st.markdown("""
        <div style='text-align:center;font-size:13px;color:#94a3b8;padding-top:2px'>
            Jun/2017 – Ago/2019 · 203.888 registros
        </div>""", unsafe_allow_html=True)

    return {
        "page":       page,
        "sd_month":   sd_month,
        "ed_month":   ed_month,
        "sel_cats":   sel_cats,
        "sel_brands": sel_brands,
        "cats":       cats,
        "brands":     brands,
    }
