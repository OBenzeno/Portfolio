CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #0f1117; }
[data-testid="stMainBlockContainer"] { padding-top: 3.5rem !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #161b27;
    border-right: 1px solid #1e2535;
}

/* ── Expanders (filtros suspensos) ── */
[data-testid="stSidebar"] details {
    background: #1a2235;
    border: 1px solid #2a3550 !important;
    border-radius: 10px !important;
    margin-bottom: 8px;
}
[data-testid="stSidebar"] details summary {
    color: #94a3b8;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    padding: 9px 14px;
    display: flex;
    align-items: center;
    gap: 8px;
}
[data-testid="stSidebar"] details summary:hover { color: #e2e8f0; }
[data-testid="stSidebar"] details[open] summary {
    color: #4f8ef7;
    border-bottom: 1px solid #2a3550;
}

/* ── Nav radio como botões verticais ── */
[data-testid="stSidebar"] [role="radiogroup"] {
    gap: 4px !important;
    display: flex;
    flex-direction: column;
}
[data-testid="stSidebar"] [role="radiogroup"] label[data-baseweb="radio"] {
    background: #1a2235 !important;
    border: 1px solid #2a3550 !important;
    border-radius: 9px !important;
    padding: 9px 14px !important;
    cursor: pointer;
    width: 100%;
    display: flex !important;
    align-items: center;
    transition: all 0.15s ease;
    color: #cbd5e1 !important;
    font-size: 13px !important;
    font-weight: 500 !important;
}
[data-testid="stSidebar"] [role="radiogroup"] label[data-baseweb="radio"] > div:last-child,
[data-testid="stSidebar"] [role="radiogroup"] label[data-baseweb="radio"] > div:last-child * {
    color: inherit !important;
}
[data-testid="stSidebar"] [role="radiogroup"] label[data-baseweb="radio"]:hover {
    background: #1e2a40 !important;
    border-color: #4f8ef7 !important;
    color: #f1f5f9 !important;
}
[data-testid="stSidebar"] [role="radiogroup"] label[data-baseweb="radio"]:active {
    transform: scale(0.97) !important;
    background: #172333 !important;
    border-color: #4f8ef7 !important;
    box-shadow: 0 0 8px rgba(79,142,247,0.2) !important;
    transition: transform 0.08s ease, background 0.08s ease !important;
}
[data-testid="stSidebar"] [role="radiogroup"] label[data-baseweb="radio"]:has(input:checked) {
    background: linear-gradient(135deg,#1e3a5f,#172641) !important;
    border-color: #4f8ef7 !important;
    color: #60a5fa !important;
    font-weight: 600 !important;
    box-shadow: 0 0 10px rgba(79,142,247,0.12) !important;
}
[data-testid="stSidebar"] [role="radiogroup"] label[data-baseweb="radio"]:has(input:checked) > div:last-child,
[data-testid="stSidebar"] [role="radiogroup"] label[data-baseweb="radio"]:has(input:checked) > div:last-child * {
    color: #60a5fa !important;
}
/* oculta o círculo mas mantém o input funcional */
[data-testid="stSidebar"] [role="radiogroup"] label[data-baseweb="radio"] > div:first-child {
    display: none !important;
}
[data-testid="stSidebar"] [role="radiogroup"] label[data-baseweb="radio"] input {
    position: absolute;
    opacity: 0;
    width: 0;
    height: 0;
}
/* ── Nav SVG icons ── */
[data-testid="stSidebar"] [role="radiogroup"] label[data-baseweb="radio"]::before {
    content: '';
    display: inline-block;
    width: 17px;
    height: 17px;
    margin-right: 10px;
    background-size: contain;
    background-repeat: no-repeat;
    background-position: center;
    flex-shrink: 0;
}
[data-testid="stSidebar"] [role="radiogroup"] label[data-baseweb="radio"]:nth-child(1)::before {
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%2300d4a0' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z'/%3E%3Cpolyline points='9 22 9 12 15 12 15 22'/%3E%3C/svg%3E");
}
[data-testid="stSidebar"] [role="radiogroup"] label[data-baseweb="radio"]:nth-child(2)::before {
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%234f8ef7' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect x='2' y='13' width='4' height='8' rx='1'/%3E%3Crect x='9' y='8' width='4' height='13' rx='1'/%3E%3Crect x='16' y='3' width='4' height='18' rx='1'/%3E%3C/svg%3E");
}
[data-testid="stSidebar"] [role="radiogroup"] label[data-baseweb="radio"]:nth-child(3)::before {
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23a855f7' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='12' cy='12' r='10'/%3E%3Cline x1='2' y1='12' x2='22' y2='12'/%3E%3Cpath d='M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z'/%3E%3C/svg%3E");
}

/* ── KPI Cards (compactos) ── */
.kpi-card {
    background: linear-gradient(135deg, #1a2235 0%, #1e2a40 100%);
    border: 1px solid #2a3550;
    border-radius: 14px;
    padding: 14px 14px 12px;
    text-align: left;
    box-shadow: 0 4px 20px rgba(0,0,0,0.25);
    position: relative;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: flex-start;
    min-height: 90px;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    border-radius: 14px 14px 0 0;
}
.kpi-card.green::before  { background: linear-gradient(90deg,#00d4a0,#00a878); }
.kpi-card.blue::before   { background: linear-gradient(90deg,#4f8ef7,#2563eb); }
.kpi-card.purple::before { background: linear-gradient(90deg,#a855f7,#7c3aed); }
.kpi-card.orange::before { background: linear-gradient(90deg,#fb923c,#ea580c); }
.kpi-card.red::before    { background: linear-gradient(90deg,#f43f5e,#be123c); }

.kpi-icon  { font-size: 22px; position: absolute; top: 10px; right: 10px; }
.kpi-text  { display: flex; flex-direction: column; }
.kpi-label { font-size: 9px; font-weight: 600; letter-spacing: 1px;
             text-transform: uppercase; color: #94a3b8; margin-bottom: 4px; }
.kpi-value { font-size: 22px; font-weight: 700; color: #f1f5f9;
             line-height: 1.1; margin-bottom: 3px; }
.kpi-delta { font-size: 13px; font-weight: 500; color: #00d4a0; }

/* ── Header ── */
.dashboard-header {
    background: linear-gradient(135deg,#1a2235 0%,#0f1724 100%);
    border: 1px solid #2a3550;
    border-radius: 18px;
    padding: 20px 28px;
    margin-bottom: 18px;
    display: flex;
    align-items: center;
    gap: 14px;
}
p.header-title { font-size: 28px !important; font-weight: 700 !important; color: #f1f5f9 !important; margin: 0 !important; line-height: 1.1 !important; text-transform: uppercase !important; letter-spacing: 1.5px !important; }
p.header-sub   { font-size: 13px !important; color: #94a3b8 !important; margin: 4px 0 0 0 !important; }

/* ── Section title ── */
.section-title {
    font-size: 13px; font-weight: 600; color: #94a3b8;
    text-transform: uppercase; letter-spacing: 1px;
    margin: 4px 0; padding-left: 2px;
}
.continent-label {
    font-size: 11px; font-weight: 600; letter-spacing: 0.8px;
    text-transform: uppercase; color: #94a3b8; margin-bottom: 4px;
}
/* ── Pills de continente ── */
[data-testid="stPills"] button {
    background: #1a2235 !important;
    border: 1px solid #2a3550 !important;
    color: #cbd5e1 !important;
    font-size: 12px !important;
}
[data-testid="stPills"] button:hover {
    border-color: #4f8ef7 !important;
    color: #f1f5f9 !important;
}
[data-testid="stPills"] button[aria-pressed="true"] {
    background: #1e3a5f !important;
    border-color: #4f8ef7 !important;
    color: #60a5fa !important;
}
hr { border-color: #1e2535; }

.period-label {
    font-size: 10px !important; font-weight: 600 !important;
    color: #94a3b8 !important; text-transform: uppercase !important;
    letter-spacing: 0.8px !important; margin: 0 0 4px 0 !important;
}
/* ── Period radio como pills em grid ── */
[data-testid="stSidebar"] details [role="radiogroup"] {
    display: grid !important;
    grid-template-columns: 1fr 1fr 1fr !important;
    gap: 4px !important;
    padding: 2px 0 4px !important;
}
[data-testid="stSidebar"] details [role="radiogroup"] label[data-baseweb="radio"] {
    background: #1a2235 !important;
    border: 1px solid #2a3550 !important;
    border-radius: 8px !important;
    padding: 6px 4px !important;
    justify-content: center !important;
    font-size: 12px !important;
    color: #cbd5e1 !important;
    font-weight: 500 !important;
    width: 100% !important;
    min-width: 0 !important;
    box-shadow: none !important;
}
[data-testid="stSidebar"] details [role="radiogroup"] label[data-baseweb="radio"]:has(input:checked) {
    background: #1e3a5f !important;
    border-color: #4f8ef7 !important;
    color: #60a5fa !important;
    font-weight: 600 !important;
}
[data-testid="stSidebar"] details [role="radiogroup"] label[data-baseweb="radio"] > div:first-child {
    display: none !important;
}
[data-testid="stSidebar"] details [role="radiogroup"] label[data-baseweb="radio"]::before {
    display: none !important;
}
/* "Personalizado" ocupa colunas 2-3 (5º item) */
[data-testid="stSidebar"] details [role="radiogroup"] label[data-baseweb="radio"]:nth-child(5) {
    grid-column: 2 / 4 !important;
}


/* ── Fade-in na troca de página ── */
@keyframes pageFadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}
section[data-testid="stMainBlockContainer"] > div:first-child {
    animation: pageFadeIn 0.35s ease forwards;
}
</style>
"""
