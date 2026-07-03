import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch

fig, ax = plt.subplots(figsize=(26, 19))
ax.set_xlim(0, 26)
ax.set_ylim(0, 19)
ax.axis("off")
ax.set_facecolor("#1e1e2e")
fig.patch.set_facecolor("#1e1e2e")

COLOR_FACT = "#4f8ef7"
COLOR_DIM  = "#56c78a"
COLOR_DIM2 = "#e0a84b"
COLOR_TEXT = "#e0e0f0"
COLOR_PK   = "#f7c948"
COLOR_FK   = "#c0c0d0"
COLOR_LINE = "#555577"
COLOR_BG   = "#2a2a3e"

tables = {
    "members": {
        "x": 13.0, "y": 17.5, "type": "dim",
        "cols": [("idmember","PK"), ("firstname",""), ("lastname",""),
                 ("idbranch","FK"), ("status",""), ("birthdate",""),
                 ("registerdate",""), ("idemployeeconsultant","FK"),
                 ("idemployeeinstructor","FK")]
    },
    "dim_partnerships": {
        "x": 20.5, "y": 17.5, "type": "dim2",
        "cols": [("idmember","FK"), ("plataforma","PK"),
                 ("codigo","")]
    },
    "dim_address": {
        "x": 6.5, "y": 17.5, "type": "dim2",
        "cols": [("idaddress","PK"), ("idmember","FK"),
                 ("state",""), ("city",""),
                 ("zipcode",""), ("country","")]
    },
    "sales": {
        "x": 4.5, "y": 11.0, "type": "fact",
        "cols": [("idsale","PK"), ("idsaleitem",""), ("idmember","FK"),
                 ("idbranch","FK"), ("idmembership","FK"),
                 ("idemployeesale","FK"), ("saledate",""),
                 ("salevalue",""), ("itemvalue",""),
                 ("idmembermembership","")]
    },
    "debtors": {
        "x": 20.5, "y": 11.0, "type": "fact",
        "cols": [("receivableid","PK"), ("memberid","FK"),
                 ("branchid","FK"), ("idpaymenttype","FK"),
                 ("memberstatus",""), ("debtamount",""),
                 ("dayslate",""), ("debtstatus",""),
                 ("duedate",""), ("chargeattemptscount","")]
    },
    "dim_branch": {
        "x": 13.0, "y": 5.0, "type": "dim2",
        "cols": [("branchid","PK"), ("branchname","")]
    },
    "dim_planos": {
        "x": 4.0, "y": 3.5, "type": "dim2",
        "cols": [("idmembership","PK"), ("nome_plano","")]
    },
    "dim_employee": {
        "x": 4.0, "y": 1.5, "type": "dim2",
        "cols": [("idemployee","PK"), ("nameemployee","")]
    },
    "dim_payment_type": {
        "x": 19.5, "y": 3.5, "type": "dim2",
        "cols": [("idpaymenttype","PK"), ("paymenttype","")]
    },
}

def draw_table(ax, name, info):
    x, y    = info["x"], info["y"]
    cols    = info["cols"]
    t       = info["type"]
    color   = COLOR_FACT if t == "fact" else (COLOR_DIM if t == "dim" else COLOR_DIM2)
    w       = 4.8
    row_h   = 0.40
    head_h  = 0.55
    total_h = head_h + len(cols) * row_h + 0.12

    ax.add_patch(FancyBboxPatch((x-w/2+0.07, y-total_h-0.07), w, total_h,
                                 linewidth=0, boxstyle="round,pad=0.05",
                                 facecolor="#00000055", zorder=1))
    ax.add_patch(FancyBboxPatch((x-w/2, y-total_h), w, total_h,
                                 linewidth=1.8, boxstyle="round,pad=0.05",
                                 edgecolor=color, facecolor=COLOR_BG, zorder=2))
    ax.add_patch(FancyBboxPatch((x-w/2, y-head_h), w, head_h,
                                 linewidth=0, boxstyle="round,pad=0.02",
                                 facecolor=color, zorder=3))
    ax.text(x, y-head_h/2, name.upper(), ha="center", va="center",
            fontsize=10, fontweight="bold", color="white", zorder=4)

    for i, (col, ctype) in enumerate(cols):
        cy = y - head_h - (i+0.6)*row_h
        if i % 2 == 0:
            ax.add_patch(mpatches.Rectangle((x-w/2+0.02, cy-row_h/2+0.03),
                                             w-0.04, row_h-0.04,
                                             facecolor="#ffffff08", zorder=2))
        col_color = COLOR_PK if ctype=="PK" else (COLOR_FK if ctype=="FK" else COLOR_TEXT)
        prefix    = "PK  " if ctype=="PK" else ("FK  " if ctype=="FK" else "    ")
        ax.text(x-w/2+0.28, cy, f"{prefix}{col}", ha="left", va="center",
                fontsize=7.8, color=col_color, zorder=4, fontfamily="monospace")

    total_h2 = head_h + len(cols)*row_h + 0.12
    return {
        "top":    (x, y),
        "bottom": (x, y-total_h2),
        "left":   (x-w/2, y-total_h2/2),
        "right":  (x+w/2, y-total_h2/2),
        "center": (x, y-total_h2/2),
    }

centers = {}
for name, info in tables.items():
    centers[name] = draw_table(ax, name, info)

def rel(p1, p2, label="", rad=0.05):
    ax.annotate("", xy=p2, xytext=p1,
                arrowprops=dict(arrowstyle="-|>", color=COLOR_LINE,
                                lw=1.5, connectionstyle=f"arc3,rad={rad}"), zorder=0)
    if label:
        mx, my = (p1[0]+p2[0])/2, (p1[1]+p2[1])/2
        ax.text(mx, my+0.18, label, ha="center", va="bottom",
                fontsize=7, color="#9999bb", zorder=5)

# members → fatos
rel(centers["members"]["left"],  centers["sales"]["top"],    "1:N")
rel(centers["members"]["right"], centers["debtors"]["top"],  "1:N")

# members → dim_partnerships / dim_address
rel(centers["members"]["right"], centers["dim_partnerships"]["left"], "1:N")
rel(centers["members"]["left"],  centers["dim_address"]["right"],     "1:N")

# dims → members
rel(centers["dim_branch"]["top"],    centers["members"]["bottom"],  "", rad=0.0)
rel(centers["dim_employee"]["top"],  centers["members"]["bottom"],  "", rad=-0.15)

# dims → sales
rel(centers["dim_planos"]["top"],    centers["sales"]["bottom"],    "")
rel(centers["dim_employee"]["top"],  centers["sales"]["bottom"],    "", rad=0.1)
rel(centers["dim_branch"]["left"],   centers["sales"]["bottom"],    "", rad=0.1)

# dims → debtors
rel(centers["dim_payment_type"]["top"], centers["debtors"]["bottom"], "")
rel(centers["dim_branch"]["right"],     centers["debtors"]["bottom"], "", rad=-0.1)

# ── Legenda ────────────────────────────────────────────────────────────────────
legend_items = [
    mpatches.Patch(facecolor=COLOR_DIM,  label="Dimensao Principal"),
    mpatches.Patch(facecolor=COLOR_FACT, label="Tabela Fato"),
    mpatches.Patch(facecolor=COLOR_DIM2, label="Dimensao Lookup"),
    mpatches.Patch(facecolor=COLOR_PK,   label="Primary Key"),
    mpatches.Patch(facecolor=COLOR_FK,   label="Foreign Key"),
]
ax.legend(handles=legend_items, loc="upper left",
          facecolor=COLOR_BG, edgecolor=COLOR_LINE,
          labelcolor=COLOR_TEXT, fontsize=9.5, framealpha=0.95)

ax.set_title("DER — Tabelas Ativas | Pipeline BI", color=COLOR_TEXT,
             fontsize=15, fontweight="bold", pad=14)

plt.tight_layout()
plt.savefig("C:/Users/wtba2/pipeline/sql/active/der_active.png", dpi=150,
            bbox_inches="tight", facecolor=fig.get_facecolor())
print("Salvo em pipeline/sql/active/der_active.png")
