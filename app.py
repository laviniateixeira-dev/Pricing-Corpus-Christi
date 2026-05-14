import streamlit as st
import pandas as pd
import numpy as np
import requests
import io
import base64
import json
import os
from datetime import datetime

# ==========================================
# INICIALIZAÇÃO DE SESSÃO GERAL (HISTÓRICO PERMANENTE)
# ==========================================
ARQUIVO_HISTORICO = "historico_pricing.csv"

if 'history_df' not in st.session_state:
    if os.path.exists(ARQUIVO_HISTORICO):
        st.session_state['history_df'] = pd.read_csv(ARQUIVO_HISTORICO)
    else:
        st.session_state['history_df'] = pd.DataFrame()

# ==========================================
# CONFIGURAÇÕES DO FERIADO
# ==========================================
feriado_atual = "corpus_2026"
ref_1         = "pascoa_2026"
ref_2         = "consciencia_2025" 
ref_3         = "corpus_2025"

# OS SEUS LINKS DO GITHUB (Mantido apenas o necessário para o Editor)
GITHUB_RAW_CURVA = f"https://raw.githubusercontent.com/laviniateixeira-dev/Pricing-Corpus-Christi/main/data/curva_{feriado_atual}.csv"
# ==========================================

st.set_page_config(
    page_title="Pricing · Editor",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS PREMIUM VIBRANTE: ADAPTATIVO (LIGHT/DARK) + BUSER PINK ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,300&display=swap');

/* Variáveis da Marca Buser */
:root {
  --buser-pink: #FF3377;
  --buser-pink-light: #FF66A3;
  --buser-pink-transp: rgba(255, 51, 119, 0.15);
  --filter-bg: #1A0B14;
}

/* Tipografia Global */
html, body, [class*="css"], [data-testid="stMetricLabel"] p {
  font-family: 'DM Sans', sans-serif !important;
}
h1, h2, h3, .pg-title, .section-title {
  font-family: 'DM Serif Display', serif !important;
  color: var(--text-color) !important;
}

/* Headers Customizados */
.pg-header {
  display: flex; align-items: flex-end; justify-content: space-between;
  padding-bottom: 1rem; margin-bottom: 1.5rem; 
  border-bottom: 2px solid var(--buser-pink-transp);
}
.pg-eyebrow { 
  font-size: .75rem; font-weight: 800; letter-spacing: 1.5px; 
  text-transform: uppercase; color: var(--buser-pink); margin-bottom: 4px; 
}
.pg-title { 
  font-size: 2.5rem; font-weight: 400; line-height: 1.1; 
  display: flex; align-items: center;
}

/* Ponto Live Pulsante */
.live-dot {
  height: 12px; width: 12px; background-color: var(--buser-pink);
  border-radius: 50%; display: inline-block; margin-right: 15px;
  box-shadow: 0 0 0 0 rgba(255, 51, 119, 0.7);
  animation: pulse-pink 2s infinite;
}

@keyframes pulse-pink {
  0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(255, 51, 119, 0.7); }
  70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(255, 51, 119, 0); }
  100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(255, 51, 119, 0); }
}

/* Labels de Seção */
.section-label { 
  font-size: .75rem; font-weight: 800; letter-spacing: 1.2px; 
  text-transform: uppercase; color: var(--buser-pink) !important;
  margin-bottom: 8px; margin-top: 2rem; 
}

/* ── ESTILIZAÇÃO DOS FILTROS (DARK ROSA) ── */
[data-testid="stMultiSelect"] [data-baseweb="select"] > div,
[data-testid="stSelectbox"] [data-baseweb="select"] > div {
    background-color: var(--filter-bg) !important; 
    border: 1px solid var(--buser-pink) !important; 
    border-radius: 8px !important;
    min-height: 45px !important;
}

[data-testid="stMultiSelect"] [data-baseweb="select"] span, 
[data-testid="stSelectbox"] [data-baseweb="select"] span, 
[data-testid="stMultiSelect"] [data-baseweb="select"] div,
[data-testid="stSelectbox"] [data-baseweb="select"] div {
    color: var(--buser-pink-light) !important;
    font-weight: 600 !important;
}

/* Dropdown */
[data-baseweb="popover"] [data-baseweb="menu"] {
    background-color: var(--filter-bg) !important;
    border: 1px solid var(--buser-pink) !important;
}
[data-baseweb="option"] {
    color: var(--buser-pink-light) !important;
    font-weight: 500 !important;
}
[data-baseweb="option"]:hover, [aria-selected="true"][data-baseweb="option"] {
    background-color: #2D1422 !important; 
}

/* Tags de Multiselect */
[data-baseweb="tag"] {
  background-color: rgba(255, 51, 119, 0.2) !important; 
  border: 1px solid var(--buser-pink) !important;
  border-radius: 4px !important;
}
[data-baseweb="tag"] span:first-child { color: #FFFFFF !important; font-weight: 700 !important; }

/* Botões */
[data-testid="stButton"] button {
    border-color: var(--buser-pink) !important;
    color: var(--buser-pink) !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
}
[data-testid="stButton"] button:hover {
    background-color: var(--buser-pink) !important;
    color: white !important;
}
[data-testid="stButton"] button[kind="primary"] {
    background-color: var(--buser-pink) !important;
    color: white !important;
}

/* Tabelas e Data Editor */
[data-testid="stDataTable"] {
  border: 1px solid rgba(150, 150, 150, 0.2) !important;
  border-radius: 10px !important;
}

/* Abas */
[data-testid="stTabs"] [data-baseweb="tab"] {
  font-family: 'DM Sans', sans-serif !important;
  padding-top: 10px; padding-bottom: 10px;
}
[data-testid="stTabs"] [aria-selected="true"][data-baseweb="tab"] {
  color: var(--buser-pink) !important; 
  border-bottom-color: var(--buser-pink) !important;
  font-weight: 700 !important;
}

/* Banners (Adaptados para Light/Dark) */
.acion-banner {
  display: flex; align-items: center; background-color: rgba(16, 185, 129, 0.1); 
  border: 1px solid rgba(16, 185, 129, 0.3); border-left: 4px solid #10B981; 
  border-radius: 8px; padding: 14px 20px; margin: 1.5rem 0 1rem;
}
.acion-txt { font-size: .95rem; color: #10B981 !important; font-weight: 700; }

.warn-banner {
  background-color: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); 
  border-left: 4px solid #F59E0B; border-radius: 8px; padding: 12px 18px; margin-bottom: 1rem;
  font-size: .9rem; color: #F59E0B; font-weight: 600;
}

.footer { display: flex; justify-content: space-between; align-items: center; padding-top: 1.5rem; margin-top: 2rem; border-top: 1px solid rgba(150, 150, 150, 0.2); }
.ftxt { font-size: .8rem; font-weight: 500; color: var(--text-color); opacity: 0.6; }
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

# ── ABAS DA PÁGINA ────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["Editor de Preços", "Histórico de Alterações"])

# ── FUNÇÃO 1: EDITOR DE PREÇOS ────────────────────────────────────────────────
def render_editor(df_raw: pd.DataFrame, tab_key: str, titulo: str):
    agora_t = datetime.now().strftime("%d/%m/%Y %H:%M")

    st.markdown(f"""
    <div class="pg-header">
      <div>
        <div class="pg-eyebrow">Ações de Pricing</div>
        <div class="pg-title"><span class="live-dot"></span>{titulo}</div>
      </div>
      <div><span style="color:var(--text-color); opacity: 0.6; font-size:0.85rem; font-weight: 500;">Atualizado via Databricks às {agora_t}</span></div>
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

    cols_editor = ["row_id", "data", "antecedencia", "rota_principal", "sentido", "tipo_assento", "turno", f"buscas_{ref_1}", "buscas_atual", f"grupos_{ref_1}", "grupos_atual", "pax", "capacidade_atual", "vagas_restantes", f"lf_{ref_1}", "load_factor_atual", f"ratio_lf_{ref_1}", f"tkm_{ref_1}", "tkm_atual", "price_cc", "mult_atual_aplicado", "mult_flutuacao", "preco_flutuacao", "preco_cenario_atual", "preco_atual_bucket", "max_split", "preco_maximo_feriado", "data_atualizacao"]
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
        "preco_cenario_atual", "mult_flutuacao", "preco_flutuacao", "preco_maximo_feriado", "Preco novo", "data_atualizacao"
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
        "data_atualizacao": st.column_config.TextColumn("Data Atualização", disabled=True), 
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
                # --- SALVANDO NO ARQUIVO LOCAL PARA FIXAR ---
                st.session_state['history_df'].to_csv(ARQUIVO_HISTORICO, index=False)

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
        st.markdown('<div style="padding:15px 20px; background:var(--secondary-background-color); border:1px dashed var(--buser-pink); border-radius:8px; margin-top:20px; text-align:center; color:var(--text-color); font-weight: 500;">Nenhum preço alterado ainda. Preencha a coluna <b>Preço Novo</b> na tabela acima.</div>', unsafe_allow_html=True)
        if st.button("Limpar Tudo", key=f"t3_reset_empty"):
            st.session_state[key_version] += 1
            st.session_state[key_enviadas] = set()
            st.session_state[dict_key] = {}
            st.rerun()

    st.markdown(f'<div class="footer"><span class="ftxt">{len(df_cv_editor)} linhas exibidas | {n_ocultas} ocultas</span><span class="ftxt">Cálculo: Mult = Preço Novo / COALESCE(Preço Flutuação, Max Split)</span></div>', unsafe_allow_html=True)


# ── FUNÇÃO 2: HISTÓRICO DE ALTERAÇÕES ─────────────────────────────────────────
def render_historico():
    st.markdown("""
    <div class="pg-header">
      <div>
        <div class="pg-eyebrow">Acompanhamento</div>
        <div class="pg-title"><span class="live-dot"></span>Histórico de Alterações</div>
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
                        # --- SALVANDO NO ARQUIVO LOCAL PARA FIXAR ---
                        st.session_state['history_df'].to_csv(ARQUIVO_HISTORICO, index=False)
                        st.success("Tudo certo! Adicionado à tabela.")
                        st.rerun()
                    except Exception as e:
                        st.error("Erro ao ler o arquivo CSV.")
                else:
                    st.warning("Selecione um arquivo primeiro.")
                    
    with col_hist_1:
        st.markdown('<div class="section-label" style="margin-top:0;">Filtros de Pesquisa</div>', unsafe_allow_html=True)
        
        df_hist = st.session_state['history_df'].copy()
        
        if not df_hist.empty:
            col_fh1, col_fh2, col_fh3 = st.columns(3)
            
            with col_fh1:
                if 'rota_principal' in df_hist.columns:
                    rotas_h = ["Todas"] + sorted(df_hist['rota_principal'].dropna().unique().tolist())
                    rota_h_sel = st.selectbox("Rota", rotas_h, key="hist_rota")
                    if rota_h_sel != "Todas":
                        df_hist = df_hist[df_hist['rota_principal'] == rota_h_sel]
                        
            with col_fh2:
                if 'sentido' in df_hist.columns:
                    sentidos_h = ["Todos"] + sorted(df_hist['sentido'].dropna().unique().tolist())
                    sentido_h_sel = st.selectbox("Sentido", sentidos_h, key="hist_sentido")
                    if sentido_h_sel != "Todos":
                        df_hist = df_hist[df_hist['sentido'] == sentido_h_sel]
                        
            with col_fh3:
                busca_livre = st.text_input("Busca Livre", placeholder="Pesquise por qualquer termo...")
                if busca_livre:
                    mask = df_hist.astype(str).apply(lambda x: x.str.contains(busca_livre, case=False, na=False)).any(axis=1)
                    df_hist = df_hist[mask]
            
            st.markdown('<div class="section-label" style="margin-top: 1.5rem;">Tabela de Ações (Permanente)</div>', unsafe_allow_html=True)
            st.dataframe(df_hist, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhuma alteração de preço registrada no histórico ainda. Suas alterações na aba 'Editor de Preços' aparecerão aqui.")

# ── RENDERIZAÇÃO FINAL DAS ABAS ─────────────────────────
with tab1: render_editor(df_editor_raw, tab_key="t3", titulo="Editor de Preços")
with tab2: render_historico()
