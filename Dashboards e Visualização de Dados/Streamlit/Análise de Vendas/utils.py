import streamlit as st
import plotly.graph_objects as go

BG     = "#1a2235"
GRID   = "#2a3550"
FONT   = "#cbd5e1"
COLORS = ["#4f8ef7","#00d4a0","#a855f7","#fb923c","#f43f5e",
          "#facc15","#34d399","#60a5fa","#c084fc","#f472b6"]

_SVG_ATTRS = 'stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'


def make_svg_icon(color: str, path: str, size: int = 28) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="none" stroke="{color}" {_SVG_ATTRS}>{path}</svg>'
    )


def theme(fig, title: str = "", height: int = 320):
    fig.update_layout(
        plot_bgcolor=BG, paper_bgcolor=BG, font_color=FONT,
        title=dict(text=title, font=dict(size=13, color="#e2e8f0"), x=0.01),
        margin=dict(l=12, r=12, t=38, b=12),
        height=height,
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor=GRID, font=dict(color=FONT)),
        colorway=COLORS,
    )
    fig.update_xaxes(gridcolor=GRID, linecolor=GRID, tickfont=dict(color="#94a3b8"), title_text="")
    fig.update_yaxes(gridcolor=GRID, linecolor=GRID, tickfont=dict(color="#94a3b8"), title_text="")
    return fig


def fmt_brl(val: float) -> str:
    if val >= 1_000_000:
        return f"R$ {val/1_000_000:.1f}M"
    if val >= 1_000:
        return f"R$ {val/1_000:.1f}K"
    return f"R$ {val:,.0f}"


def _wrap(text: str, width: int = 10) -> str:
    words, lines, cur = text.split(), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > width:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        lines.append(cur)
    return "<br>".join(lines)


def _mute(c: str, f: float = 0.88) -> str:
    r, g, b = int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16)
    return (
        f"#{int(r*f+0x1a*(1-f)):02x}"
        f"{int(g*f+0x22*(1-f)):02x}"
        f"{int(b*f+0x35*(1-f)):02x}"
    )


def kpi_card(col, color: str, icon: str, label: str, value: str, sub: str):
    with col:
        st.markdown(f"""
        <div class="kpi-card {color}">
            <span class="kpi-icon">{icon}</span>
            <div class="kpi-text">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{value}</div>
                <div class="kpi-delta">{sub}</div>
            </div>
        </div>""", unsafe_allow_html=True)
