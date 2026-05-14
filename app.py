import streamlit as st
import pandas as pd
import numpy as np
import requests
import io
import base64
import json
import plotly.express as px
from datetime import datetime

# ==========================================
# INICIALIZAÇÃO DE SESSÃO GERAL (HISTÓRICO)
# ==========================================
if 'history_df' not in st.session_state:
    st.session_state['history_df'] = pd.DataFrame()

# ==========================================
# CONFIGURAÇÕES DO FERIADO
# ==========================================
feriado_atual = "corpus_2026"
ref_1         = "pascoa_2026"
ref_2         = "consciencia_2025" 
ref_3         = "corpus_2025"

# DATAS ÂNCORA PARA A ABA DE RESULTADOS (Edite com as datas reais de Corpus Christi do seu banco)
data_ancora_ida   = "2026-06-03" 
data_ancora_volta = "2026-06-07" 

# OS SEUS LINKS DO GITHUB
GITHUB_RAW_CURVA = f"https://raw.githubusercontent.com/laviniateixeira-dev/Pricing-Feriados/main/data/curva_{feriado_atual}.csv"
GITHUB_RAW_GERAL = f"https://raw.githubusercontent.com/laviniateixeira-dev/Pricing-Feriados/main/data/resultados_geral_{feriado_atual}.csv"
GITHUB_RAW_DIA   = f"https://raw.githubusercontent.com/laviniateixeira-dev/Pricing-Feriados/main/data/resultados_dia_{feriado_atual}.csv"
GITHUB_RAW_ROTA  = f"https://raw.githubusercontent.com/laviniateixeira-dev/Pricing-Feriados/main/data/resultados_rota_antecedencia_{feriado_atual}.csv"
# ==========================================

st.set_page_config(
    page_title="Pricing · Corpus Christi",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- PALETA: PRETO/GRAFITE NEUTRO PURO & ROSA ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,300&display=swap');

:root {
  --bg-page:   #0D0D0D; 
  --bg-card:   #171717; 
  --ink:       #FFFFFF; 
  --ink-muted: #999999; 
  --buser:     #FF66A3; 
  --buser-lt:  #FFB3D1; 
  --bdr:       #2A2A2A; 
  --ink-dark:  #000000; 
}

*,*::before,*::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
section[data-testid="stMain"] > div {
  background-color: var(--bg-page) !important;
  color: var(--ink) !important;
  font-family: 'DM Sans', sans-serif !important;
}

[data-testid="stWidgetLabel"] p {
  color: var(--ink) !important;
  font-size: .88rem !important;
  font-weight: 500 !important;
  margin-bottom: 6px !important;
}

[data-testid="stSidebar"] {
  background-color: var(--bg-card) !important;
  border-right: 1px solid var(--bdr) !important;
}
[data-testid="stSidebar"] * {
  color: var(--ink) !important;
}

.block-container { padding: 3rem 4rem !important; max-width: 100% !important; }

::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--bdr); border-radius: 4px; }

/* Inputs Padrão */
[data-testid="stTextInput"] input {
  background-color: var(--bg-page) !important;
  border: 1px solid var(--bdr) !important;
  border-radius: 6px !important;
  color: #FFFFFF !important; 
  font-size: .9rem !important;
  padding: 10px 12px !important;
}
[data-testid="stTextInput"] input:focus {
  border-color: var(--buser) !important; 
  box-shadow: 0 0 0 1px var(--buser) !important;
}

/* Base do Multiselect */
[data-testid="stMultiSelect"] [data-baseweb="select"] > div {
  background-color: var(--bg-page) !important;
  border: 1px solid var(--bdr) !important;
  border-radius: 6px !important;
  min-height: 38px !important;
  color: #FFFFFF !important;
}
[data-testid="stMultiSelect"] [data-baseweb="select"] > div:focus-within {
  border-color: var(--buser) !important;
}

/* Efeito nas Tags dos Filtros (Multiselect Aba 1) */
[data-baseweb="tag"] {
  background-color: #26111A !important; 
  border: 1px solid #401B2B !important;
  border-radius: 4px !important;
}
[data-baseweb="tag"] span:first-child { color: var(--buser) !important; font-size: .75rem !important; }

/* Transformando os Selectboxes (Aba 2 e 3) para ficarem com efeito Rosinha igual as Tags */
[data-testid="stSelectbox"] [data-baseweb="select"] > div {
  background-color: #26111A !important; 
  border: 1px solid #401B2B !important;
  border-radius: 4px !important;
  min-height: 38px !important;
}
[data-testid="stSelectbox"] [data-baseweb="select"] > div * {
  color: var(--buser) !important;
}
[data-testid="stSelectbox"] [data-baseweb="select"] > div:focus-within,
[data-testid="stSelectbox"] [data-baseweb="select"] > div:hover {
  border-color: var(--buser) !important;
}

/* Menus suspensos (Dropdowns abertos) */
[data-baseweb="popover"] [data-baseweb="menu"] {
  background-color: var(--bg-card) !important;
  border: 1px solid var(--bdr) !important;
  border-radius: 6px !important;
}
[data-baseweb="option"] { background-color: var(--bg-card) !important; font-size: .85rem !important; color: var(--ink) !important; padding: 10px 12px !important; }
[data-baseweb="option"]:hover, [aria-selected="true"][data-baseweb="option"] { background-color: #27272A !important; }

/* Botões */
[data-testid="stButton"] > button {
  background-color: var(--bg-card) !important;
  border: 1px solid var(--bdr) !important;
  color: var(--ink) !important;
  font-size: .85rem !important;
  font-weight: 500 !important;
  border-radius: 6px !important;
  padding: 6px 16px !important;
  transition: all .2s ease-in-out !important;
}
[data-testid="stButton"] > button:hover {
  border-color: var(--buser) !important;
  color: var(--buser) !important;
}
[data-testid="stButton"] > button[kind="primary"] {
  background-color: var(--buser) !important;
  color: var(--ink-dark) !important;
  border-color: var(--buser) !important;
  font-weight: 600 !important;
}
[data-testid="stButton"] > button[kind="primary"]:hover {
  opacity: 0.85;
}

/* Checkbox */
[data-testid="stCheckbox"] label { color: var(--ink-muted) !important; }

/* Abas */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
  background: transparent !important;
  border-bottom: 2px solid var(--bdr) !important;
  gap: 20px !important;
  padding-bottom: 5px !important;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
  background: transparent !important;
  color: var(--ink-muted) !important;
  font-size: 1rem !important;
  font-weight: 500 !important;
  border: none !important;
  border-bottom: 3px solid transparent !important;
  padding: 10px 5px !important;
  margin-bottom: -7px !important;
}
[data-testid="stTabs"] [data-baseweb="tab"]:hover { color: var(--ink) !important; }
[data-testid="stTabs"] [aria-selected="true"][data-baseweb="tab"] {
  color: var(--buser) !important; 
  border-bottom-color: var(--buser) !important;
}
[data-testid="stTabs"] [data-baseweb="tab-highlight"],
[data-testid="stTabs"] [data-baseweb="tab-border"] { display: none !important; }

/* Tipografia e Headers (Espaçamento reduzido) */
.pg-header {
  display: flex; align-items: flex-end; justify-content: space-between;
  padding-bottom: 1rem; margin-bottom: 1rem; border-bottom: 1px solid var(--bdr);
}
.pg-eyebrow { font-size: .75rem; font-weight: 600; letter-spacing: 1.5px; text-transform: uppercase; color: var(--buser); margin-bottom: 8px; }
.pg-title { font-family: 'DM Serif Display', serif; font-size: 2.5rem; font-weight: 400; color: var(--ink) !important; line-height: 1.1; }
.live-dot {
  width: 8px; height: 8px; border-radius: 50%; background-color: var(--buser); display: inline-block; animation: pulse 3s infinite; margin-right: 6px;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.4} }

.section-label { font-size: .7rem; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; color: var(--ink-muted); margin-bottom: 10px; margin-top: 2rem; }
.section-title { font-family: 'DM Serif Display', serif; font-size: 1.4rem; font-weight: 400; color: var(--ink) !important; margin-bottom: 5px; }

/* Banners (Cores frias e limpas) */
.acion-banner {
  display: flex; align-items: center; background-color: #052616; border: 1px solid #064024;
  border-left: 4px solid #10B981; border-radius: 6px; padding: 14px 20px; margin: 1.5rem 0 1rem;
}
.acion-txt { font-size: .9rem; color: #10B981 !important; font-weight: 500; }

.warn-banner {
  background-color: #2E1A05; border: 1px solid #4D2B08; border-left: 4px solid #F59E0B;
  border-radius: 6px; padding: 12px 18px; margin-bottom: 1rem;
  font-size: .85rem; color: #FCD34D; font-weight: 400;
}

/* Dataframe Nativo do Streamlit */
[data-testid="stDataTable"] {
  border: 1px solid var(--bdr) !important;
  border-radius: 8px !important;
  overflow: hidden !important;
}

.footer { display: flex; justify-content: space-between; align-items: center; padding-top: 1.5rem; margin-top: 2rem; border-top: 1px solid var(--bdr); }
.ftxt { font-size: .75rem; color: var(--ink-muted); }
</style>
""", unsafe_allow_html=True)

# ── LOAD & PREP ───────────────────────────────────────────────────────────────
@st.cache_data(ttl=60)
def load_data(url: str) -> pd.DataFrame:
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        df = pd.read_csv(io.StringIO(r.text))
        df.columns = df.columns.str.strip()
        return df
    except Exception:
        return pd.DataFrame()

def prep_editor(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty: return df
    df = df.copy()
    
    float_cols = ["occ_atual", "load_factor_atual", f"lf_{ref_1}", f"lf_{ref_3}", f"ratio_lf_{ref_1}", f"ratio_lf_{ref_3}",
                  f"tkm_{ref_1}", f"tkm_{ref_3}", "tkm_atual", "preco_cenario_atual", "preco_atual_bucket", "max_split",
                  "mult_atual_aplicado", "price_cc", "mult_flutuacao", "preco_flutuacao", "preco_maximo_feriado", f"buscas_{ref_1}", f"buscas_{ref_3}", "buscas_atual"]
    for c in float_cols:
        if c in df.columns: df[c] = pd.to_numeric(df[c].replace("null", None), errors="coerce")
            
    int_cols = ["pax", "capacidade_atual", "vagas_restantes", "antecedencia", f"grupos_{ref_1}", f"grupos_{ref_3}", "grupos_atual"]
    for c in int_cols:
        if c in df.columns: df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)
            
    if "data" in df.columns: df["data"] = pd.to_datetime(df["data"], errors="coerce")
    return df

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="section-label" style="margin-top:0;">Controle de Dados</div>', unsafe_allow_html=True)
    url_editor = st.text_input("URL dos dados (Curva):", value=GITHUB_RAW_CURVA)

    if st.button("Atualizar Cache", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    df_editor_raw = prep_editor(load_data(url_editor))
    df_geral_raw  = load_data(GITHUB_RAW_GERAL)
    df_dia_raw    = load_data(GITHUB_RAW_DIA)
    df_rota_raw   = load_data(GITHUB_RAW_ROTA)

# ── ABAS DA PÁGINA ────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["Resultados", "Acompanhamento por Antecedência", "Editor de Preços", "Histórico de Alterações"])

# ── FUNÇÃO 1: EDITOR DE PREÇOS ────────────────────────────────────────────────
def render_editor(df_raw: pd.DataFrame, tab_key: str, titulo: str):
    agora_t = datetime.now().strftime("%d/%m/%Y %H:%M")

    st.markdown(f"""
    <div class="pg-header">
      <div>
        <div class="pg-eyebrow">Ações de Pricing</div>
        <div class="pg-title">{titulo}</div>
      </div>
      <div><span class="live-dot"></span><span style="color:var(--ink-muted); font-size:0.8rem;">Atualizado via Databricks às {agora_t}</span></div>
    </div>
    """, unsafe_allow_html=True)

    if df_raw.empty:
        st.info("Nenhum dado encontrado para o editor. Verifique o arquivo no GitHub.")
        return

    def calc_row_id(row):
        d_str = pd.to_datetime(row["data"]).strftime("%Y-%m-%d") if pd.notna(row["data"]) else ""
        return f"{d_str}|{row.get('turno','')}|{row.get('sentido','')}|{row.get('tipo_assento','')}"

    if "row_id" not in df_raw.columns:
        df_raw["row_id"] = df_raw.apply(calc_row_id, axis=1)

    dict_key = f"{tab_key}_edits_dict"
    if dict_key not in st.session_state: st.session_state[dict_key] = {}
    key_enviadas = f"{tab_key}_linhas_enviadas"
    if key_enviadas not in st.session_state: st.session_state[key_enviadas] = set()
    key_version = f"{tab_key}_editor_version"
    if key_version not in st.session_state: st.session_state[key_version] = 0

    st.markdown('<div class="section-label" style="margin-top: 0.5rem;">Filtros de Busca</div>', unsafe_allow_html=True)
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        datas_c = sorted(df_raw["data"].dt.date.dropna().unique())
        datas_c_sel = st.multiselect("Data da Viagem:", options=datas_c, default=datas_c, format_func=lambda d: d.strftime("%d/%m"), key=f"{tab_key}_datas")
    with col_f2:
        turnos_c = sorted(df_raw["turno"].dropna().unique())
        turnos_sel = st.multiselect("Turno:", options=turnos_c, default=turnos_c, key=f"{tab_key}_turnos")
    with col_f3:
        # ATUALIZADO AQUI
        rota_c = st.text_input("Buscar Sentido:", placeholder="Ex: BHZ-RIO", key=f"{tab_key}_rota")

    df_cv = df_raw.copy()
    if datas_c_sel: df_cv = df_cv[df_cv["data"].dt.date.isin(datas_c_sel)]
    if turnos_sel:  df_cv = df_cv[df_cv["turno"].isin(turnos_sel)]
    if rota_c:      df_cv = df_cv[df_cv["sentido"].str.upper().str.contains(rota_c.upper(), na=False)]

    mask_enviadas = df_cv["row_id"].isin(st.session_state[key_enviadas])
    n_ocultas = int(mask_enviadas.sum())
    df_cv_editor = df_cv[~mask_enviadas].reset_index(drop=True)

    if n_ocultas > 0:
        col_oc1, col_oc2 = st.columns([5, 1])
        with col_oc1:
            st.markdown(f'<div class="warn-banner">Atenção: {n_ocultas} linhas que você já enviou estão ocultas.</div>', unsafe_allow_html=True)
        with col_oc2:
            if st.button("Mostrar Todas", key=f"{tab_key}_mostrar"):
                st.session_state[key_enviadas] = set()
                st.rerun()

    cols_editor = ["row_id", "data", "antecedencia", "rota_principal", "sentido", "tipo_assento", "turno", f"buscas_{ref_1}", "buscas_atual", f"grupos_{ref_1}", "grupos_atual", "pax", "capacidade_atual", "vagas_restantes", f"lf_{ref_1}", "load_factor_atual", f"ratio_lf_{ref_1}", f"tkm_{ref_1}", "tkm_atual", "price_cc", "mult_atual_aplicado", "mult_flutuacao", "preco_flutuacao", "preco_cenario_atual", "preco_atual_bucket", "max_split", "preco_maximo_feriado"]
    cols_presentes = [c for c in cols_editor if c in df_cv_editor.columns]
    df_editor = df_cv_editor[cols_presentes].copy()

    df_editor["data_fmt"] = pd.to_datetime(df_editor["data"]).dt.strftime("%d/%m/%Y")
    
    if f"ratio_lf_{ref_1}" in df_editor.columns: df_editor["ratio_r1_fmt"] = df_editor[f"ratio_lf_{ref_1}"].astype(float).round(3).astype(str) + "x"
    if f"lf_{ref_1}" in df_editor.columns: df_editor["lf_r1_fmt"] = (df_editor[f"lf_{ref_1}"] * 100).astype(float).round(1).astype(str) + "%"
    if "load_factor_atual" in df_editor.columns: df_editor["lf_a_fmt"] = (df_editor["load_factor_atual"] * 100).astype(float).round(1).astype(str) + "%"

    df_editor["incluir"] = df_editor["row_id"].map(lambda x: st.session_state[dict_key].get(x, {}).get("incluir", True))
    df_editor["Preco novo"] = df_editor["row_id"].map(lambda x: st.session_state[dict_key].get(x, {}).get("Preco novo", None))

    show_cols = [
        "incluir", "data_fmt", "antecedencia", "rota_principal", "sentido", 
        "tipo_assento", "turno", f"buscas_{ref_1}", "buscas_atual", 
        "pax", "capacidade_atual", "vagas_restantes", "lf_r1_fmt", "lf_a_fmt", 
        "ratio_r1_fmt", f"tkm_{ref_1}", "tkm_atual", "price_cc", "mult_atual_aplicado", 
        "preco_cenario_atual", "mult_flutuacao", "preco_flutuacao", "preco_maximo_feriado", "Preco novo"
    ]
    show_cols = [c for c in show_cols if c in df_editor.columns or c in ["incluir", "Preco novo"]]
    df_show = df_editor[show_cols].copy()

    col_config = {
        "incluir": st.column_config.CheckboxColumn("Incluir", default=True),
        "data_fmt": st.column_config.TextColumn("Data", disabled=True),
        "antecedencia": st.column_config.NumberColumn("Antec.", disabled=True),
        "rota_principal": st.column_config.TextColumn("Rota", disabled=True),
        "sentido": st.column_config.TextColumn("Sentido", disabled=True),
        "tipo_assento": st.column_config.TextColumn("Assento", disabled=True),
        "turno": st.column_config.TextColumn("Turno", disabled=True),
        f"buscas_{ref_1}": st.column_config.NumberColumn("Buscas Ref", disabled=True),
        "buscas_atual": st.column_config.NumberColumn("Buscas Atual", disabled=True),
        "pax": st.column_config.NumberColumn("PAX", disabled=True),
        "capacidade_atual": st.column_config.NumberColumn("Capacidade", disabled=True),
        "vagas_restantes": st.column_config.NumberColumn("↑ Vagas", disabled=True),
        "lf_r1_fmt": st.column_config.TextColumn("LF Referência", disabled=True),
        "lf_a_fmt": st.column_config.TextColumn("LF Atual", disabled=True),
        "ratio_r1_fmt": st.column_config.TextColumn("Ratio LF", disabled=True),
        f"tkm_{ref_1}": st.column_config.NumberColumn("TKM Ref", disabled=True, format="R$ %.0f"),
        "tkm_atual": st.column_config.NumberColumn("TKM Atual", disabled=True, format="R$ %.0f"),
        "price_cc": st.column_config.NumberColumn("Price CC", disabled=True, format="R$ %.0f"),
        "mult_atual_aplicado": st.column_config.NumberColumn("Mult Final", disabled=True, format="%.3fx"),
        "preco_cenario_atual": st.column_config.NumberColumn("Preço Cenario", disabled=True, format="R$ %.2f"),
        "mult_flutuacao": st.column_config.NumberColumn("Mult Flutuação", disabled=True, format="%.2fx"),
        "preco_flutuacao": st.column_config.NumberColumn("Preço Flutuação", disabled=True, format="R$ %.2f"),
        "preco_maximo_feriado": st.column_config.NumberColumn("Teto Flutuação", disabled=True, format="R$ %.2f"),
        "Preco novo": st.column_config.NumberColumn("Preço Novo", min_value=0.0, format="R$ %.2f"),
    }

    st.markdown('<div class="section-label">Planilha de Edição</div>', unsafe_allow_html=True)
    edited = st.data_editor(
        df_show, use_container_width=True, hide_index=True, column_config=col_config,
        num_rows="fixed", key=f"{tab_key}_editor_{st.session_state[key_version]}"
    )

    for idx, row in edited.iterrows():
        r_id = df_editor.loc[idx, "row_id"]
        preco, inc = row["Preco novo"], row["incluir"]
        if pd.notna(preco):
            st.session_state[dict_key][r_id] = {"Preco novo": preco, "incluir": inc}
        else:import streamlit as st
import pandas as pd
import numpy as np
import requests
import io
import base64
import json
import plotly.express as px
from datetime import datetime

# ==========================================
# INICIALIZAÇÃO DE SESSÃO GERAL (HISTÓRICO)
# ==========================================
if 'history_df' not in st.session_state:
    st.session_state['history_df'] = pd.DataFrame()

# ==========================================
# CONFIGURAÇÕES DO FERIADO
# ==========================================
feriado_atual = "corpus_2026"
ref_1         = "pascoa_2026"
ref_2         = "consciencia_2025" 
ref_3         = "corpus_2025"

# DATAS ÂNCORA PARA A ABA DE RESULTADOS (Edite com as datas reais de Corpus Christi do seu banco)
data_ancora_ida   = "2026-06-03" 
data_ancora_volta = "2026-06-07" 

# OS SEUS LINKS DO GITHUB
GITHUB_RAW_CURVA = f"https://raw.githubusercontent.com/laviniateixeira-dev/Pricing-Corpus-Christi/main/data/curva_{feriado_atual}.csv"
GITHUB_RAW_GERAL = f"https://raw.githubusercontent.com/laviniateixeira-dev/Pricing-Corpus-Christi/main/data/resultados_geral_{feriado_atual}.csv"
GITHUB_RAW_DIA   = f"https://raw.githubusercontent.com/laviniateixeira-dev/Pricing-Corpus-Christi/main/data/resultados_dia_{feriado_atual}.csv"
GITHUB_RAW_ROTA  = f"https://raw.githubusercontent.com/laviniateixeira-dev/Pricing-Corpus-Christi/main/data/resultados_rota_antecedencia_{feriado_atual}.csv"
# ==========================================

st.set_page_config(
    page_title="Pricing · Corpus Christi",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- PALETA: PRETO/GRAFITE NEUTRO PURO & ROSA ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,300&display=swap');

:root {
  --bg-page:   #0D0D0D; 
  --bg-card:   #171717; 
  --ink:       #FFFFFF; 
  --ink-muted: #999999; 
  --buser:     #FF66A3; 
  --buser-lt:  #FFB3D1; 
  --bdr:       #2A2A2A; 
  --ink-dark:  #000000; 
}

*,*::before,*::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
section[data-testid="stMain"] > div {
  background-color: var(--bg-page) !important;
  color: var(--ink) !important;
  font-family: 'DM Sans', sans-serif !important;
}

[data-testid="stWidgetLabel"] p {
  color: var(--ink) !important;
  font-size: .88rem !important;
  font-weight: 500 !important;
  margin-bottom: 6px !important;
}

[data-testid="stSidebar"] {
  background-color: var(--bg-card) !important;
  border-right: 1px solid var(--bdr) !important;
}
[data-testid="stSidebar"] * {
  color: var(--ink) !important;
}

.block-container { padding: 3rem 4rem !important; max-width: 100% !important; }

::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--bdr); border-radius: 4px; }

/* Inputs Padrão */
[data-testid="stTextInput"] input {
  background-color: var(--bg-page) !important;
  border: 1px solid var(--bdr) !important;
  border-radius: 6px !important;
  color: #FFFFFF !important; 
  font-size: .9rem !important;
  padding: 10px 12px !important;
}
[data-testid="stTextInput"] input:focus {
  border-color: var(--buser) !important; 
  box-shadow: 0 0 0 1px var(--buser) !important;
}

/* Base do Multiselect */
[data-testid="stMultiSelect"] [data-baseweb="select"] > div {
  background-color: var(--bg-page) !important;
  border: 1px solid var(--bdr) !important;
  border-radius: 6px !important;
  min-height: 38px !important;
  color: #FFFFFF !important;
}
[data-testid="stMultiSelect"] [data-baseweb="select"] > div:focus-within {
  border-color: var(--buser) !important;
}

/* Efeito nas Tags dos Filtros (Multiselect Aba 1) */
[data-baseweb="tag"] {
  background-color: #26111A !important; 
  border: 1px solid #401B2B !important;
  border-radius: 4px !important;
}
[data-baseweb="tag"] span:first-child { color: var(--buser) !important; font-size: .75rem !important; }

/* Transformando os Selectboxes (Aba 2 e 3) para ficarem com efeito Rosinha igual as Tags */
[data-testid="stSelectbox"] [data-baseweb="select"] > div {
  background-color: #26111A !important; 
  border: 1px solid #401B2B !important;
  border-radius: 4px !important;
  min-height: 38px !important;
}
[data-testid="stSelectbox"] [data-baseweb="select"] > div * {
  color: var(--buser) !important;
}
[data-testid="stSelectbox"] [data-baseweb="select"] > div:focus-within,
[data-testid="stSelectbox"] [data-baseweb="select"] > div:hover {
  border-color: var(--buser) !important;
}

/* Menus suspensos (Dropdowns abertos) */
[data-baseweb="popover"] [data-baseweb="menu"] {
  background-color: var(--bg-card) !important;
  border: 1px solid var(--bdr) !important;
  border-radius: 6px !important;
}
[data-baseweb="option"] { background-color: var(--bg-card) !important; font-size: .85rem !important; color: var(--ink) !important; padding: 10px 12px !important; }
[data-baseweb="option"]:hover, [aria-selected="true"][data-baseweb="option"] { background-color: #27272A !important; }

/* Botões */
[data-testid="stButton"] > button {
  background-color: var(--bg-card) !important;
  border: 1px solid var(--bdr) !important;
  color: var(--ink) !important;
  font-size: .85rem !important;
  font-weight: 500 !important;
  border-radius: 6px !important;
  padding: 6px 16px !important;
  transition: all .2s ease-in-out !important;
}
[data-testid="stButton"] > button:hover {
  border-color: var(--buser) !important;
  color: var(--buser) !important;
}
[data-testid="stButton"] > button[kind="primary"] {
  background-color: var(--buser) !important;
  color: var(--ink-dark) !important;
  border-color: var(--buser) !important;
  font-weight: 600 !important;
}
[data-testid="stButton"] > button[kind="primary"]:hover {
  opacity: 0.85;
}

/* Checkbox */
[data-testid="stCheckbox"] label { color: var(--ink-muted) !important; }

/* Abas */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
  background: transparent !important;
  border-bottom: 2px solid var(--bdr) !important;
  gap: 20px !important;
  padding-bottom: 5px !important;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
  background: transparent !important;
  color: var(--ink-muted) !important;
  font-size: 1rem !important;
  font-weight: 500 !important;
  border: none !important;
  border-bottom: 3px solid transparent !important;
  padding: 10px 5px !important;
  margin-bottom: -7px !important;
}
[data-testid="stTabs"] [data-baseweb="tab"]:hover { color: var(--ink) !important; }
[data-testid="stTabs"] [aria-selected="true"][data-baseweb="tab"] {
  color: var(--buser) !important; 
  border-bottom-color: var(--buser) !important;
}
[data-testid="stTabs"] [data-baseweb="tab-highlight"],
[data-testid="stTabs"] [data-baseweb="tab-border"] { display: none !important; }

/* Tipografia e Headers (Espaçamento reduzido) */
.pg-header {
  display: flex; align-items: flex-end; justify-content: space-between;
  padding-bottom: 1rem; margin-bottom: 1rem; border-bottom: 1px solid var(--bdr);
}
.pg-eyebrow { font-size: .75rem; font-weight: 600; letter-spacing: 1.5px; text-transform: uppercase; color: var(--buser); margin-bottom: 8px; }
.pg-title { font-family: 'DM Serif Display', serif; font-size: 2.5rem; font-weight: 400; color: var(--ink) !important; line-height: 1.1; }
.live-dot {
  width: 8px; height: 8px; border-radius: 50%; background-color: var(--buser); display: inline-block; animation: pulse 3s infinite; margin-right: 6px;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.4} }

.section-label { font-size: .7rem; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; color: var(--ink-muted); margin-bottom: 10px; margin-top: 2rem; }
.section-title { font-family: 'DM Serif Display', serif; font-size: 1.4rem; font-weight: 400; color: var(--ink) !important; margin-bottom: 5px; }

/* Banners (Cores frias e limpas) */
.acion-banner {
  display: flex; align-items: center; background-color: #052616; border: 1px solid #064024;
  border-left: 4px solid #10B981; border-radius: 6px; padding: 14px 20px; margin: 1.5rem 0 1rem;
}
.acion-txt { font-size: .9rem; color: #10B981 !important; font-weight: 500; }

.warn-banner {
  background-color: #2E1A05; border: 1px solid #4D2B08; border-left: 4px solid #F59E0B;
  border-radius: 6px; padding: 12px 18px; margin-bottom: 1rem;
  font-size: .85rem; color: #FCD34D; font-weight: 400;
}

/* Dataframe Nativo do Streamlit */
[data-testid="stDataTable"] {
  border: 1px solid var(--bdr) !important;
  border-radius: 8px !important;
  overflow: hidden !important;
}

.footer { display: flex; justify-content: space-between; align-items: center; padding-top: 1.5rem; margin-top: 2rem; border-top: 1px solid var(--bdr); }
.ftxt { font-size: .75rem; color: var(--ink-muted); }
</style>
""", unsafe_allow_html=True)

# ── LOAD & PREP ───────────────────────────────────────────────────────────────
@st.cache_data(ttl=60)
def load_data(url: str) -> pd.DataFrame:
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        df = pd.read_csv(io.StringIO(r.text))
        df.columns = df.columns.str.strip()
        return df
    except Exception:
        return pd.DataFrame()

def prep_editor(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty: return df
    df = df.copy()
    
    float_cols = ["occ_atual", "load_factor_atual", f"lf_{ref_1}", f"lf_{ref_3}", f"ratio_lf_{ref_1}", f"ratio_lf_{ref_3}",
                  f"tkm_{ref_1}", f"tkm_{ref_3}", "tkm_atual", "preco_cenario_atual", "preco_atual_bucket", "max_split",
                  "mult_atual_aplicado", "price_cc", "mult_flutuacao", "preco_flutuacao", "preco_maximo_feriado", f"buscas_{ref_1}", f"buscas_{ref_3}", "buscas_atual"]
    for c in float_cols:
        if c in df.columns: df[c] = pd.to_numeric(df[c].replace("null", None), errors="coerce")
            
    int_cols = ["pax", "capacidade_atual", "vagas_restantes", "antecedencia", f"grupos_{ref_1}", f"grupos_{ref_3}", "grupos_atual"]
    for c in int_cols:
        if c in df.columns: df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)
            
    if "data" in df.columns: df["data"] = pd.to_datetime(df["data"], errors="coerce")
    return df

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="section-label" style="margin-top:0;">Controle de Dados</div>', unsafe_allow_html=True)
    url_editor = st.text_input("URL dos dados (Curva):", value=GITHUB_RAW_CURVA)

    if st.button("Atualizar Cache", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    df_editor_raw = prep_editor(load_data(url_editor))
    df_geral_raw  = load_data(GITHUB_RAW_GERAL)
    df_dia_raw    = load_data(GITHUB_RAW_DIA)
    df_rota_raw   = load_data(GITHUB_RAW_ROTA)

# ── ABAS DA PÁGINA ────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["Resultados", "Acompanhamento por Antecedência", "Editor de Preços", "Histórico de Alterações"])

# ── FUNÇÃO 1: EDITOR DE PREÇOS ────────────────────────────────────────────────
def render_editor(df_raw: pd.DataFrame, tab_key: str, titulo: str):
    agora_t = datetime.now().strftime("%d/%m/%Y %H:%M")

    st.markdown(f"""
    <div class="pg-header">
      <div>
        <div class="pg-eyebrow">Ações de Pricing</div>
        <div class="pg-title">{titulo}</div>
      </div>
      <div><span class="live-dot"></span><span style="color:var(--ink-muted); font-size:0.8rem;">Atualizado via Databricks às {agora_t}</span></div>
    </div>
    """, unsafe_allow_html=True)

    if df_raw.empty:
        st.info("Nenhum dado encontrado para o editor. Verifique o arquivo no GitHub.")
        return

    def calc_row_id(row):
        d_str = pd.to_datetime(row["data"]).strftime("%Y-%m-%d") if pd.notna(row["data"]) else ""
        return f"{d_str}|{row.get('turno','')}|{row.get('sentido','')}|{row.get('tipo_assento','')}"

    if "row_id" not in df_raw.columns:
        df_raw["row_id"] = df_raw.apply(calc_row_id, axis=1)

    dict_key = f"{tab_key}_edits_dict"
    if dict_key not in st.session_state: st.session_state[dict_key] = {}
    key_enviadas = f"{tab_key}_linhas_enviadas"
    if key_enviadas not in st.session_state: st.session_state[key_enviadas] = set()
    key_version = f"{tab_key}_editor_version"
    if key_version not in st.session_state: st.session_state[key_version] = 0

    st.markdown('<div class="section-label" style="margin-top: 0.5rem;">Filtros de Busca</div>', unsafe_allow_html=True)
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        datas_c = sorted(df_raw["data"].dt.date.dropna().unique())
        datas_c_sel = st.multiselect("Data da Viagem:", options=datas_c, default=datas_c, format_func=lambda d: d.strftime("%d/%m"), key=f"{tab_key}_datas")
    with col_f2:
        turnos_c = sorted(df_raw["turno"].dropna().unique())
        turnos_sel = st.multiselect("Turno:", options=turnos_c, default=turnos_c, key=f"{tab_key}_turnos")
    with col_f3:
        rota_c = st.text_input("Buscar Sentido:", placeholder="Ex: BHZ-RIO", key=f"{tab_key}_rota")

    df_cv = df_raw.copy()
    if datas_c_sel: df_cv = df_cv[df_cv["data"].dt.date.isin(datas_c_sel)]
    if turnos_sel:  df_cv = df_cv[df_cv["turno"].isin(turnos_sel)]
    if rota_c:      df_cv = df_cv[df_cv["sentido"].str.upper().str.contains(rota_c.upper(), na=False)]

    mask_enviadas = df_cv["row_id"].isin(st.session_state[key_enviadas])
    n_ocultas = int(mask_enviadas.sum())
    df_cv_editor = df_cv[~mask_enviadas].reset_index(drop=True)

    if n_ocultas > 0:
        col_oc1, col_oc2 = st.columns([5, 1])
        with col_oc1:
            st.markdown(f'<div class="warn-banner">Atenção: {n_ocultas} linhas que você já enviou estão ocultas.</div>', unsafe_allow_html=True)
        with col_oc2:
            if st.button("Mostrar Todas", key=f"{tab_key}_mostrar"):
                st.session_state[key_enviadas] = set()
                st.rerun()

    cols_editor = ["row_id", "data", "antecedencia", "rota_principal", "sentido", "tipo_assento", "turno", f"buscas_{ref_1}", "buscas_atual", f"grupos_{ref_1}", "grupos_atual", "pax", "capacidade_atual", "vagas_restantes", f"lf_{ref_1}", "load_factor_atual", f"ratio_lf_{ref_1}", f"tkm_{ref_1}", "tkm_atual", "price_cc", "mult_atual_aplicado", "mult_flutuacao", "preco_flutuacao", "preco_cenario_atual", "preco_atual_bucket", "max_split", "preco_maximo_feriado"]
    cols_presentes = [c for c in cols_editor if c in df_cv_editor.columns]
    df_editor = df_cv_editor[cols_presentes].copy()

    df_editor["data_fmt"] = pd.to_datetime(df_editor["data"]).dt.strftime("%d/%m/%Y")
    
    if f"ratio_lf_{ref_1}" in df_editor.columns: df_editor["ratio_r1_fmt"] = df_editor[f"ratio_lf_{ref_1}"].astype(float).round(3).astype(str) + "x"
    if f"lf_{ref_1}" in df_editor.columns: df_editor["lf_r1_fmt"] = (df_editor[f"lf_{ref_1}"] * 100).astype(float).round(1).astype(str) + "%"
    if "load_factor_atual" in df_editor.columns: df_editor["lf_a_fmt"] = (df_editor["load_factor_atual"] * 100).astype(float).round(1).astype(str) + "%"

    df_editor["incluir"] = df_editor["row_id"].map(lambda x: st.session_state[dict_key].get(x, {}).get("incluir", True))
    df_editor["Preco novo"] = df_editor["row_id"].map(lambda x: st.session_state[dict_key].get(x, {}).get("Preco novo", None))

    show_cols = [
        "incluir", "data_fmt", "antecedencia", "rota_principal", "sentido", 
        "tipo_assento", "turno", f"buscas_{ref_1}", "buscas_atual", 
        "pax", "capacidade_atual", "vagas_restantes", "lf_r1_fmt", "lf_a_fmt", 
        "ratio_r1_fmt", f"tkm_{ref_1}", "tkm_atual", "price_cc", "mult_atual_aplicado", 
        "preco_cenario_atual", "mult_flutuacao", "preco_flutuacao", "preco_maximo_feriado", "Preco novo"
    ]
    show_cols = [c for c in show_cols if c in df_editor.columns or c in ["incluir", "Preco novo"]]
    df_show = df_editor[show_cols].copy()

    col_config = {
        "incluir": st.column_config.CheckboxColumn("Incluir", default=True),
        "data_fmt": st.column_config.TextColumn("Data", disabled=True),
        "antecedencia": st.column_config.NumberColumn("Antec.", disabled=True),
        "rota_principal": st.column_config.TextColumn("Rota", disabled=True),
        "sentido": st.column_config.TextColumn("Sentido", disabled=True),
        "tipo_assento": st.column_config.TextColumn("Assento", disabled=True),
        "turno": st.column_config.TextColumn("Turno", disabled=True),
        f"buscas_{ref_1}": st.column_config.NumberColumn("Buscas Ref", disabled=True),
        "buscas_atual": st.column_config.NumberColumn("Buscas Atual", disabled=True),
        "pax": st.column_config.NumberColumn("PAX", disabled=True),
        "capacidade_atual": st.column_config.NumberColumn("Capacidade", disabled=True),
        "vagas_restantes": st.column_config.NumberColumn("↑ Vagas", disabled=True),
        "lf_r1_fmt": st.column_config.TextColumn("LF Referência", disabled=True),
        "lf_a_fmt": st.column_config.TextColumn("LF Atual", disabled=True),
        "ratio_r1_fmt": st.column_config.TextColumn("Ratio LF", disabled=True),
        f"tkm_{ref_1}": st.column_config.NumberColumn("TKM Ref", disabled=True, format="R$ %.0f"),
        "tkm_atual": st.column_config.NumberColumn("TKM Atual", disabled=True, format="R$ %.0f"),
        "price_cc": st.column_config.NumberColumn("Price CC", disabled=True, format="R$ %.0f"),
        "mult_atual_aplicado": st.column_config.NumberColumn("Mult Final", disabled=True, format="%.3fx"),
        "preco_cenario_atual": st.column_config.NumberColumn("Preço Cenario", disabled=True, format="R$ %.2f"),
        "mult_flutuacao": st.column_config.NumberColumn("Mult Flutuação", disabled=True, format="%.2fx"),
        "preco_flutuacao": st.column_config.NumberColumn("Preço Flutuação", disabled=True, format="R$ %.2f"),
        "preco_maximo_feriado": st.column_config.NumberColumn("Teto Flutuação", disabled=True, format="R$ %.2f"),
        "Preco novo": st.column_config.NumberColumn("Preço Novo", min_value=0.0, format="R$ %.2f"),
    }

    st.markdown('<div class="section-label">Planilha de Edição</div>', unsafe_allow_html=True)
    edited = st.data_editor(
        df_show, use_container_width=True, hide_index=True, column_config=col_config,
        num_rows="fixed", key=f"{tab_key}_editor_{st.session_state[key_version]}"
    )

    for idx, row in edited.iterrows():
        r_id = df_editor.loc[idx, "row_id"]
        preco, inc = row["Preco novo"], row["incluir"]
        if pd.notna(preco):
            st.session_state[dict_key][r_id] = {"Preco novo": preco, "incluir": inc}
        else:
            if r_id in st.session_state[dict_key]: del st.session_state[dict_key][r_id]

    if st.session_state[dict_key]:
        st.markdown('<div class="section-label">Pronto para Enviar (Carrinho)</div>', unsafe_allow_html=True)
        
        edited_ids = list(st.session_state[dict_key].keys())
        df_todas_edicoes = df_raw[df_raw["row_id"].isin(edited_ids)].copy()
        
        df_todas_edicoes["Preco novo"] = df_todas_edicoes["row_id"].map(lambda x: st.session_state[dict_key][x]["Preco novo"])
        df_todas_edicoes["incluir"] = df_todas_edicoes["row_id"].map(lambda x: st.session_state[dict_key][x]["incluir"])
        
        df_editado = df_todas_edicoes[df_todas_edicoes["incluir"] == True].copy()
        n_excluidas = len(df_todas_edicoes) - len(df_editado)

        if not df_editado.empty:
            p_flut = df_editado["preco_flutuacao"].astype(float) if "preco_flutuacao" in df_editado.columns else pd.Series(np.nan, index=df_editado.index)
            m_split = df_editado["max_split"].astype(float) if "max_split" in df_editado.columns else pd.Series(np.nan, index=df_editado.index)
            
            base_vals = p_flut.replace(0.0, np.nan).fillna(m_split)
            
            df_editado["_base_calc"] = base_vals
            df_editado["_mult_novo"] = (df_editado["Preco novo"] / df_editado["_base_calc"]).round(6)

            df_editado["data_fmt"] = pd.to_datetime(df_editado["data"]).dt.strftime("%d/%m/%Y")
            df_acionamento = pd.DataFrame({
                "row_id": df_editado["row_id"].values,
                "data": pd.to_datetime(df_editado["data_fmt"], format="%d/%m/%Y").dt.strftime("%Y-%m-%d"),
                "turno": df_editado["turno"].str.title().values,
                "rota_principal": df_editado["rota_principal"].values,
                "sentido": df_editado["sentido"].str.replace("-", ">").values,
                "mult": df_editado["_mult_novo"].values,
                "max_split_antigo": df_editado["_base_calc"].values,
                "max_split_novo": df_editado["Preco novo"].values
            })

            n_edit = len(df_acionamento)
            excl_str = f" ({n_excluidas} ignoradas no envio)" if n_excluidas > 0 else ""
            st.markdown(f'<div class="acion-banner"><span class="acion-txt"> {n_edit} linha(s) no acionamento{excl_str}</span></div>', unsafe_allow_html=True)
            
            df_export = df_acionamento.drop(columns=["row_id", "max_split_antigo", "max_split_novo"], errors='ignore')
            st.dataframe(df_export, use_container_width=True, hide_index=True)

            col_b1, col_b2, col_b3, _ = st.columns([1.5, 1.5, 1, 3])
            csv_bytes = df_export.to_csv(index=False).encode("utf-8")

            def mark_as_sent():
                df_hist_new = df_export.copy()
                df_hist_new["Data Alteração"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                st.session_state['history_df'] = pd.concat([st.session_state['history_df'], df_hist_new], ignore_index=True)

                for r_id in df_acionamento["row_id"]:
                    st.session_state[key_enviadas].add(r_id)
                    if r_id in st.session_state[dict_key]: del st.session_state[dict_key][r_id]
                st.session_state[key_version] += 1

            with col_b1:
                if st.download_button("Baixar como CSV", data=csv_bytes, file_name=f"pricing_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", mime="text/csv", use_container_width=True):
                    mark_as_sent()
                    st.rerun()

            with col_b2:
                if st.button("Enviar pro GitHub", use_container_width=True, type="primary"):
                    gh_token = st.session_state.get(f"t3_gh_token", "")
                    if not gh_token: 
                        st.warning("Atenção: Cole seu token no campo abaixo primeiro.")
                    else:
                        repo = "laviniateixeira-dev/Pricing-Corpus-Christi"
                        path = f"data/pricing_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
                        r_gh = requests.put(f"https://api.github.com/repos/{repo}/contents/{path}", 
                                            headers={"Authorization": f"token {gh_token}", "Accept": "application/vnd.github.v3+json"},
                                            data=json.dumps({"message": f"pricing: {path}", "content": base64.b64encode(csv_bytes).decode("utf-8"), "branch": "main"}))
                        if r_gh.status_code in (200, 201):
                            mark_as_sent()
                            st.success("Tudo certo! Arquivo enviado com sucesso.")
                            st.rerun()
                        else: st.error(f"Erro ao enviar: {r_gh.status_code}")

            with col_b3:
                if st.button("Limpar Edições", use_container_width=True):
                    st.session_state[key_version] += 1
                    st.session_state[key_enviadas] = set()
                    st.session_state[dict_key] = {}
                    st.rerun()

            st.text_input("Token de Acesso do GitHub (Apenas Sessão):", type="password", key=f"t3_gh_token")
    else:
        st.markdown('<div style="padding:15px 20px; background:var(--bg-card); border:1px dashed var(--bdr); border-radius:6px; margin-top:20px; text-align:center; color:var(--ink-muted);">Nenhum preço alterado ainda. Preencha a coluna <b>Preço Novo</b> na tabela acima.</div>', unsafe_allow_html=True)
        if st.button("Limpar Tudo", key=f"t3_reset_empty"):
            st.session_state[key_version] += 1
            st.session_state[key_enviadas] = set()
            st.session_state[dict_key] = {}
            st.rerun()

    st.markdown(f'<div class="footer"><span class="ftxt">{len(df_cv_editor)} linhas exibidas | {n_ocultas} ocultas</span><span class="ftxt">Cálculo: Mult = Preço Novo / COALESCE(Preço Flutuação, Max Split)</span></div>', unsafe_allow_html=True)


# ── FUNÇÃO 2: ACOMPANHAMENTO POR ANTECEDÊNCIA (PLOTLY) ────────────────────────
def render_rota_antecedencia(df_ra: pd.DataFrame):
    st.markdown("""
    <div class="pg-header">
      <div>
        <div class="pg-eyebrow">Acompanhamento</div>
        <div class="pg-title">Curva por Antecedência</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    if df_ra.empty:
        st.info("Nenhum dado encontrado para acompanhamento de rotas.")
        return

    df_ra['data'] = pd.to_datetime(df_ra['data'], errors='coerce')
    
    st.markdown('<div class="section-label" style="margin-top: 0.5rem;">Selecione o Corte</div>', unsafe_allow_html=True)
    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1: 
        rota_sel = st.selectbox("Rota Principal:", options=sorted(df_ra['rota_principal'].dropna().unique()))
    with col_f2:
        df_rota = df_ra[df_ra['rota_principal'] == rota_sel]
        sentido_sel = st.selectbox("Sentido:", options=sorted(df_rota['eixo_sentido'].dropna().unique()))
    with col_f3:
        df_sentido = df_rota[df_rota['eixo_sentido'] == sentido_sel]
        data_sel = st.selectbox("Data da Viagem:", options=sorted(df_sentido['data'].dropna().unique()), format_func=lambda x: pd.to_datetime(x).strftime('%d/%m/%Y'))

    df_filt = df_sentido[df_sentido['data'] == data_sel].copy()
    if df_filt.empty:
        st.warning("Sem dados para este corte exato.")
        return

    df_plot = df_filt.groupby('antecedencia').agg({
        'pax_atual': 'sum', 'pax_referencia': 'sum', 
        'lf_atual': 'mean', 'lf_referencia': 'mean', 
        'yield_atual': 'mean', 'yield_referencia': 'mean', 
        'ticket_medio_atual': 'mean', 'ticket_medio_referencia': 'mean'
    }).reset_index()

    st.markdown('<div class="section-label">Gráfico de Evolução</div>', unsafe_allow_html=True)
    metrica_grafico = st.radio("Escolha o indicador:", options=["Passageiros (Pax)", "Load Factor", "Yield (R$)", "Ticket Médio (R$)"], horizontal=True)

    chart_df = df_plot.copy()
    
    if metrica_grafico == "Passageiros (Pax)": 
        y_cols = ['pax_atual', 'pax_referencia']
    elif metrica_grafico == "Load Factor": 
        y_cols = ['lf_atual', 'lf_referencia']
    elif metrica_grafico == "Yield (R$)": 
        y_cols = ['yield_atual', 'yield_referencia']
    else: 
        y_cols = ['ticket_medio_atual', 'ticket_medio_referencia']

    chart_df = chart_df[['antecedencia'] + y_cols].rename(columns={y_cols[0]: "Cenário Atual", y_cols[1]: "Referência"})
    df_melt = chart_df.melt(id_vars='antecedencia', var_name='Cenário', value_name='Valor')

    fig = px.line(
        df_melt,
        x='antecedencia',
        y='Valor',
        color='Cenário',
        color_discrete_map={'Cenário Atual': '#FF66A3', 'Referência': '#FFFFFF'},
        markers=True
    )

    if metrica_grafico in ["Load Factor", "Yield (R$)"]:
        fig.update_yaxes(range=[0, 1], title=metrica_grafico, showgrid=True, gridcolor="#2A2A2A")
    else:
        fig.update_yaxes(rangemode="tozero", title=metrica_grafico, showgrid=True, gridcolor="#2A2A2A")

    fig.update_layout(
        hovermode="x unified",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#999999",
        margin=dict(t=10, b=10, l=0, r=0),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            title=None
        )
    )

    fig.update_xaxes(
        title="Dias de Antecedência",
        tickformat="d",
        dtick=2, 
        showgrid=True,
        gridcolor="#2A2A2A"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-label" style="margin-top: 2.5rem;">Tabela de Acompanhamento (Dia a Dia)</div>', unsafe_allow_html=True)
    
    col_config = {
        "antecedencia": st.column_config.NumberColumn("Dias Antec.", format="%d"),
        "pax_atual": st.column_config.NumberColumn("Pax (Atual)"),
        "pax_referencia": st.column_config.NumberColumn("Pax (Ref)"),
        "ticket_medio_atual": st.column_config.NumberColumn("Ticket Médio (Atual)", format="R$ %.2f"),
        "ticket_medio_referencia": st.column_config.NumberColumn("Ticket Médio (Ref)", format="R$ %.2f"),
        "lf_atual": st.column_config.NumberColumn("LF (Atual)", format="%.2f"),
        "lf_referencia": st.column_config.NumberColumn("LF (Ref)", format="%.2f"),
        "yield_atual": st.column_config.NumberColumn("Yield (Atual)", format="R$ %.3f"),
        "yield_referencia": st.column_config.NumberColumn("Yield (Ref)", format="R$ %.3f")
    }
    
    cols_to_show = ["antecedencia", "pax_atual", "pax_referencia", "ticket_medio_atual", "ticket_medio_referencia", "lf_atual", "lf_referencia", "yield_atual", "yield_referencia"]
    
    st.dataframe(
        df_filt.sort_values("antecedencia", ascending=False)[cols_to_show], 
        use_container_width=True, 
        hide_index=True,
        column_config=col_config
    )

# ── FUNÇÃO 3: RESULTADOS ──────────────────────────────────────────────────────
def render_resultados(df_g_raw: pd.DataFrame, df_d_raw: pd.DataFrame):
    st.markdown("""
    <div class="pg-header">
      <div>
        <div class="pg-eyebrow">Performance</div>
        <div class="pg-title">Resultados do Corpus Christi</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    
    if df_g_raw.empty or df_d_raw.empty:
        st.info("Nenhum dado encontrado.")
        return

    # Limpeza dos nomes das métricas
    df_g = df_g_raw.copy()
    df_d = df_d_raw.copy()
    df_g['metrica'] = df_g['metrica'].str.replace(' \(Capacidade x Km\)', '', regex=True).str.replace(' \(Pax x Km\)', '', regex=True)
    df_d['metrica'] = df_d['metrica'].str.replace(' \(Capacidade x Km\)', '', regex=True).str.replace(' \(Pax x Km\)', '', regex=True)

    def format_kpi(metrica, valor):
        if pd.isna(valor): return "-"
        if "Load Factor" in metrica: return f"{valor*100:.1f}%"
        if "RASK" in metrica or "Yield" in metrica: return f"R$ {valor:.3f}".replace(".", ",")
        if "Ticket Médio" in metrica or "GMV" in metrica: return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{int(valor):,}".replace(",", ".")

    def format_delta(atual, passado):
        if pd.isna(atual) or pd.isna(passado) or passado == 0: return "-"
        var = (atual / passado) - 1
        return f"{'+' if var > 0 else ''}{var * 100:.1f}%"

    col_t, col_f = st.columns([3, 1])
    with col_t:
        st.markdown('<div class="section-title">Visão Consolidada</div>', unsafe_allow_html=True)
    with col_f:
        opcoes_data = ["Consolidado Feriado", "Ida e Volta Forte", "Dias Fracos"]
        if 'data' in df_d.columns:
            opcoes_data.extend(sorted(df_d['data'].dropna().unique()))
        
        filtro_data = st.selectbox(
            "Filtro de Data:", 
            options=opcoes_data, 
            format_func=lambda x: pd.to_datetime(x).strftime('%d/%m/%Y') if x not in ["Consolidado Feriado", "Ida e Volta Forte", "Dias Fracos"] else x,
            label_visibility="collapsed"
        )

    st.write("") 
    
    if filtro_data == "Consolidado Feriado":
        df_view = df_g.copy()
        
    elif filtro_data in ["Ida e Volta Forte", "Dias Fracos"]:
        datas_fortes = [data_ancora_ida, data_ancora_volta]
        
        if filtro_data == "Ida e Volta Forte":
            df_filtrado = df_d[df_d['data'].isin(datas_fortes)].copy()
        else: 
            df_filtrado = df_d[~df_d['data'].isin(datas_fortes)].copy()

        if not df_filtrado.empty:
            df_filtrado['metrica_limpa'] = df_filtrado['metrica'].apply(lambda x: str(x).split('. ', 1)[-1].strip())
            df_piv = df_filtrado.pivot_table(index='data', columns='metrica_limpa', values=['atual', 'pascoa_2026'], aggfunc='sum')
            somas = df_piv.sum() 
            
            def get_val(cenario, metrica):
                try: return float(somas[(cenario, metrica)])
                except: return 0.0

            rows = []
            for m_orig in df_g['metrica'].unique():
                m_limpa = str(m_orig).split('. ', 1)[-1].strip()
                
                if m_limpa == "Yield":
                    v_atual = get_val('atual', 'GMV') / get_val('atual', 'RPK') if get_val('atual', 'RPK') else 0
                    v_ref = get_val('pascoa_2026', 'GMV') / get_val('pascoa_2026', 'RPK') if get_val('pascoa_2026', 'RPK') else 0
                elif m_limpa == "Load Factor":
                    v_atual = get_val('atual', 'RPK') / get_val('atual', 'ASK') if get_val('atual', 'ASK') else 0
                    v_ref = get_val('pascoa_2026', 'RPK') / get_val('pascoa_2026', 'ASK') if get_val('pascoa_2026', 'ASK') else 0
                elif m_limpa == "Ticket Médio":
                    v_atual = get_val('atual', 'GMV') / get_val('atual', 'Pax Total') if get_val('atual', 'Pax Total') else 0
                    v_ref = get_val('pascoa_2026', 'GMV') / get_val('pascoa_2026', 'Pax Total') if get_val('pascoa_2026', 'Pax Total') else 0
                elif m_limpa == "RASK":
                    v_atual = get_val('atual', 'GMV') / get_val('atual', 'ASK') if get_val('atual', 'ASK') else 0
                    v_ref = get_val('pascoa_2026', 'GMV') / get_val('pascoa_2026', 'ASK') if get_val('pascoa_2026', 'ASK') else 0
                else:
                    v_atual = get_val('atual', m_limpa)
                    v_ref = get_val('pascoa_2026', m_limpa)
                
                rows.append({'metrica': m_orig, 'atual': v_atual, 'pascoa_2026': v_ref})
            df_view = pd.DataFrame(rows)
        else:
            df_view = df_g.copy() 
            
    else: 
        df_view = df_d[df_d['data'] == filtro_data].copy()
    
    cols = st.columns(5)
    for i, row in enumerate(df_view.to_dict('records')):
        nome = str(row.get('metrica', '')).split('. ', 1)[-1]
        cols[i % 5].metric(label=nome, value=format_kpi(nome, row.get('atual')), delta=format_delta(row.get('atual'), row.get('pascoa_2026')))

    st.markdown('<div class="section-label" style="margin-top: 0.5rem; margin-bottom: 0.5rem;">Comparativo Direto (Absolutos)</div>', unsafe_allow_html=True)
    df_tg = df_view.copy()
    df_tg['Métrica'] = df_tg['metrica'].apply(lambda x: str(x).split('. ', 1)[-1])
    df_tg['Páscoa 2026'] = df_tg.apply(lambda row: format_kpi(row['Métrica'], row['pascoa_2026']), axis=1)
    df_tg['Atual'] = df_tg.apply(lambda row: format_kpi(row['Métrica'], row['atual']), axis=1)
    df_tg['Var %'] = df_tg.apply(lambda row: format_delta(row['atual'], row['pascoa_2026']), axis=1)
    st.dataframe(df_tg[['Métrica', 'Páscoa 2026', 'Atual', 'Var %']], use_container_width=True, hide_index=True)


# ── FUNÇÃO 4: HISTÓRICO DE ALTERAÇÕES ─────────────────────────────────────────
def render_historico():
    st.markdown("""
    <div class="pg-header">
      <div>
        <div class="pg-eyebrow">Acompanhamento</div>
        <div class="pg-title">Histórico de Alterações</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    
    col_hist_1, col_hist_2 = st.columns([3, 1])
    
    with col_hist_2:
        st.markdown('<div class="section-label" style="margin-top:0;">Importar CSV Existente</div>', unsafe_allow_html=True)
        with st.form("upload_form"):
            uploaded_file = st.file_uploader("Selecione um arquivo", type=["csv"], label_visibility="collapsed")
            if st.form_submit_button("Adicionar Arquivo", use_container_width=True):
                if uploaded_file is not None:
                    try:
                        df_up = pd.read_csv(uploaded_file)
                        df_up["Data Alteração"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                        st.session_state['history_df'] = pd.concat([st.session_state['history_df'], df_up], ignore_index=True)
                        st.success("Tudo certo! Adicionado à tabela.")
                        st.rerun()
                    except Exception as e:
                        st.error("Erro ao ler o arquivo CSV.")
                else:
                    st.warning("Selecione um arquivo primeiro.")
                    
    with col_hist_1:
        st.markdown('<div class="section-label" style="margin-top:0;">Tabela de Ações (Sessão Atual)</div>', unsafe_allow_html=True)
        if st.session_state['history_df'].empty:
            st.info("Nenhuma alteração de preço registrada no histórico ainda. Suas alterações na aba 'Editor de Preços' aparecerão aqui.")
        else:
            st.dataframe(st.session_state['history_df'], use_container_width=True, hide_index=True)
            if st.button("Limpar Histórico", use_container_width=False):
                st.session_state['history_df'] = pd.DataFrame()
                st.rerun()

# ── RENDERIZAÇÃO FINAL DAS ABAS ─────────────────────────
with tab1: render_resultados(df_geral_raw, df_dia_raw)
with tab2: render_rota_antecedencia(df_rota_raw)
with tab3: render_editor(df_editor_raw, tab_key="t3", titulo="Corpus Christi")
with tab4: render_historico()
