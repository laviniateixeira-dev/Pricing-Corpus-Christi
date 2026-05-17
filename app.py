import streamlit as st
import pandas as pd
import numpy as np
import requests
import io
import base64
import json
import os
from datetime import datetime
import plotly.express as px

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
# CONFIGURAÇÕES DO FERIADO E LINKS
# ==========================================
feriado_atual = "corpus_2026"

# DATAS ÂNCORA PARA A ABA DE RESULTADOS
data_ancora_ida   = "2026-06-03" 
data_ancora_volta = "2026-06-07" 

# ==========================================
# 🚨 LINKS PARA O REPOSITÓRIO: Pricing-Feriados
# ==========================================
GITHUB_RAW_GERAL = f"https://raw.githubusercontent.com/laviniateixeira-dev/Pricing-Feriados/main/data/resultados_geral_{feriado_atual}.csv?v=5"
GITHUB_RAW_DIA   = f"https://raw.githubusercontent.com/laviniateixeira-dev/Pricing-Feriados/main/data/resultados_dia_{feriado_atual}.csv?v=5"
GITHUB_RAW_ROTA  = f"https://raw.githubusercontent.com/laviniateixeira-dev/Pricing-Feriados/main/data/resultados_rota_antecedencia_{feriado_atual}.csv?v=5"
GITHUB_RAW_CURVA = f"https://raw.githubusercontent.com/laviniateixeira-dev/Pricing-Feriados/main/data/curva_{feriado_atual}.csv?v=5"
GITHUB_RAW_ALT   = f"https://raw.githubusercontent.com/laviniateixeira-dev/Pricing-Feriados/main/data/alteracoes_{feriado_atual}.csv?v=5"

st.set_page_config(
    page_title="Pricing · Corpus Christi",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS PREMIUM VIBRANTE: ADAPTATIVO (LIGHT/DARK) + BUSER PINK ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,300&display=swap');

:root {
  --buser-pink: #FF3377;
  --buser-pink-transp: rgba(255, 51, 119, 0.15);
}

html, body, [class*="css"], [data-testid="stMetricLabel"] p { font-family: 'DM Sans', sans-serif !important; }
h1, h2, h3, .pg-title, .section-title { font-family: 'DM Serif Display', serif !important; color: var(--text-color) !important; }

.pg-header { display: flex; align-items: flex-end; justify-content: space-between; padding-bottom: 1rem; margin-bottom: 1.5rem; border-bottom: 2px solid var(--buser-pink-transp); }
.pg-eyebrow { font-size: .75rem; font-weight: 800; letter-spacing: 1.5px; text-transform: uppercase; color: var(--buser-pink); margin-bottom: 4px; }
.pg-title { font-size: 2.5rem; font-weight: 400; line-height: 1.1; display: flex; align-items: center; }

.live-dot { height: 12px; width: 12px; background-color: var(--buser-pink); border-radius: 50%; display: inline-block; margin-right: 15px; box-shadow: 0 0 0 0 rgba(255, 51, 119, 0.7); animation: pulse-pink 2s infinite; }
@keyframes pulse-pink { 0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(255, 51, 119, 0.7); } 70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(255, 51, 119, 0); } 100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(255, 51, 119, 0); } }

.section-label { font-size: .75rem; font-weight: 800; letter-spacing: 1.2px; text-transform: uppercase; color: var(--buser-pink) !important; margin-bottom: 8px; margin-top: 2rem; }
.section-title { font-size: 1.5rem; font-weight: 400; margin-bottom: 5px; }

[data-testid="metric-container"] { background-color: var(--secondary-background-color); border: 1px solid rgba(150, 150, 150, 0.15); border-top: 4px solid var(--buser-pink) !important; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); transition: all 0.3s ease-in-out; }
[data-testid="metric-container"]:hover { transform: translateY(-5px); background-color: var(--buser-pink-transp); box-shadow: 0 10px 15px -3px rgba(255, 51, 119, 0.2); }
[data-testid="metric-container"] label p { color: var(--buser-pink) !important; font-weight: 700 !important; font-size: 0.9rem !important; text-transform: uppercase; letter-spacing: 0.5px; }

[data-testid="stSelectbox"] [data-baseweb="select"] > div { background-color: transparent !important; border: 1px solid var(--buser-pink) !important; border-radius: 8px !important; min-height: 45px !important; }
[data-testid="stSelectbox"] [data-baseweb="select"] span, [data-testid="stSelectbox"] [data-baseweb="select"] div { color: var(--buser-pink) !important; font-weight: 600 !important; }
[data-baseweb="popover"] [data-baseweb="menu"] { border: 1px solid var(--buser-pink) !important; }
[data-baseweb="option"] { color: var(--buser-pink) !important; font-weight: 500 !important; }
[data-baseweb="option"]:hover, [aria-selected="true"][data-baseweb="option"] { background-color: var(--buser-pink-transp) !important; }

[data-testid="stSidebar"] [data-testid="stButton"] button { border-color: var(--buser-pink) !important; color: var(--buser-pink) !important; font-weight: 600 !important; border-radius: 8px !important; }
[data-testid="stSidebar"] [data-testid="stButton"] button:hover { background-color: var(--buser-pink) !important; color: white !important; }

[data-testid="stDataTable"] { border: 1px solid rgba(150, 150, 150, 0.2) !important; border-radius: 10px !important; }
[data-testid="stTabs"] [data-baseweb="tab"] { font-family: 'DM Sans', sans-serif !important; padding-top: 10px; padding-bottom: 10px; }
[data-testid="stTabs"] [aria-selected="true"][data-baseweb="tab"] { color: var(--buser-pink) !important; border-bottom-color: var(--buser-pink) !important; font-weight: 700 !important; }
.warn-banner { background-color: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); border-left: 4px solid #F59E0B; border-radius: 8px; padding: 12px 18px; margin-bottom: 1rem; font-size: .9rem; color: #F59E0B; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ── LOAD ──────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=60)
def load_data(url: str) -> pd.DataFrame:
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        df = pd.read_csv(io.StringIO(r.text))
        # TRITURADOR DE FORMATAÇÃO: Força todas as colunas para minúsculo logo de cara
        df.columns = [str(c).lower().strip() for c in df.columns]
        return df
    except Exception:
        return pd.DataFrame()

def prep_editor(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty: return df
    df = df.copy()
    
    if "data" in df.columns and "data_atual" not in df.columns:
        df = df.rename(columns={"data": "data_atual"})
    
    for c in df.columns:
        if any(keyword in c for keyword in ["lf", "ratio", "tkm", "price", "mult", "preco"]):
            df[c] = pd.to_numeric(df[c].astype(str).str.replace("null", ""), errors="coerce")
        elif any(keyword in c for keyword in ["buscas", "pax", "capacidade", "vagas", "antecedencia"]):
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)
            
    if "data_atual" in df.columns: df["data_atual"] = pd.to_datetime(df["data_atual"], errors="coerce")
    return df

# ── CAÇADORES INTELIGENTES DE COLUNAS ──────────────────────────────────────────
def get_ref_col_name(prefix, ref_name, columns):
    """(Para Aba Resultados) Encontra o nome da coluna."""
    parts = ref_name.lower().replace("á", "a").split(" ")
    kw1 = parts[0]
    kw2 = parts[1][-2:]
    for c in columns:
        if c.startswith(prefix) and kw1 in c and kw2 in c:
            return c
    return f"{prefix}{kw1}_{kw2}_missing"

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="section-label" style="margin-top:0;">Controle de Dados</div>', unsafe_allow_html=True)
    if st.button("Atualizar Cache", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    df_geral_raw  = load_data(GITHUB_RAW_GERAL)
    df_dia_raw    = load_data(GITHUB_RAW_DIA)
    df_rota_raw   = load_data(GITHUB_RAW_ROTA)
    df_alt_raw    = load_data(GITHUB_RAW_ALT)
    df_editor_raw = prep_editor(load_data(GITHUB_RAW_CURVA))

# ── ABAS DA PÁGINA ────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["Resultados", "Evolução da Curva", "Editor de Preços", "Histórico de Alterações"])

# ── FUNÇÃO 1: RESULTADOS ──────────────────────────────────────────────────────
def render_resultados(df_g_raw: pd.DataFrame, df_d_raw: pd.DataFrame):
    
    st.markdown("""
    <div class="pg-header" style="border:none; padding-bottom:0; margin-bottom:1rem;">
      <div>
        <div class="pg-eyebrow">Performance</div>
        <div class="pg-title"><span class="live-dot"></span>Resultados - Corpus Christi</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    
    if df_g_raw.empty or df_d_raw.empty:
        st.info("Nenhum dado encontrado.")
        return

    df_g = df_g_raw.copy()
    df_d = df_d_raw.copy()

    for col_atual in ['corpus_2026', 'corpus2026', 'corpus26']:
        if col_atual in df_g.columns and 'atual' not in df_g.columns: df_g = df_g.rename(columns={col_atual: 'atual'})
        if col_atual in df_d.columns and 'atual' not in df_d.columns: df_d = df_d.rename(columns={col_atual: 'atual'})
        
    if 'data_atual' in df_d.columns and 'data' not in df_d.columns: df_d = df_d.rename(columns={'data_atual': 'data'})

    df_g['metrica'] = df_g['metrica'].str.replace(r' \(Capacidade x Km\)', '', regex=True).str.replace(r' \(Pax x Km\)', '', regex=True)
    df_d['metrica'] = df_d['metrica'].str.replace(r' \(Capacidade x Km\)', '', regex=True).str.replace(r' \(Pax x Km\)', '', regex=True)

    def format_kpi(metrica, valor):
        if pd.isna(valor): return "-"
        if "load factor" in str(metrica).lower(): return f"{valor*100:.1f}%"
        if "rask" in str(metrica).lower() or "yield" in str(metrica).lower(): return f"R$ {valor:.3f}".replace(".", ",")
        if "ticket" in str(metrica).lower() or "gmv" in str(metrica).lower(): return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{int(valor):,}".replace(",", ".")

    def format_delta(atual, passado):
        if pd.isna(atual) or pd.isna(passado) or passado == 0: return "-"
        var = (atual / passado) - 1
        return f"{'+' if var > 0 else ''}{var * 100:.1f}%"

    col_t, col_f1, col_f2 = st.columns([2, 1, 1])
    
    with col_f1:
        opcoes_data = ["Consolidado Feriado", "Ida e Volta Forte", "Dias Fracos"]
        if 'data' in df_d.columns:
            opcoes_data.extend(sorted(df_d['data'].dropna().unique()))
        
        filtro_data = st.selectbox(
            "Filtro de Data:", 
            options=opcoes_data, 
            format_func=lambda x: pd.to_datetime(x).strftime('%d/%m/%Y') if x not in ["Consolidado Feriado", "Ida e Volta Forte", "Dias Fracos"] else x
        )
        
    with col_f2:
        opcoes_ref = {
            "Páscoa 2026": "pascoa_2026", 
            "Corpus 2025": "corpus_2025", 
            "Maio 2026": "maio_2026"
        }
        ref_nome = st.selectbox("Comparar com (Ref):", list(opcoes_ref.keys()), key="res_ref_sel")
        ref_col = opcoes_ref[ref_nome]

    df_g['atual'] = pd.to_numeric(df_g['atual'], errors='coerce')
    df_g[ref_col] = pd.to_numeric(df_g[ref_col], errors='coerce')
    df_d['atual'] = pd.to_numeric(df_d['atual'], errors='coerce')
    df_d[ref_col] = pd.to_numeric(df_d[ref_col], errors='coerce')

    if 'data' in df_d.columns:
        df_d['data_str'] = pd.to_datetime(df_d['data'], errors='coerce').dt.strftime('%Y-%m-%d')

    col_ref_data = f"data_ref_{ref_col}"
    texto_ref = ""

    if filtro_data == "Consolidado Feriado": 
        texto_data = "(02/06 a 08/06)"
        try:
            min_ref = pd.to_datetime(df_d[col_ref_data].dropna()).min().strftime('%d/%m')
            max_ref = pd.to_datetime(df_d[col_ref_data].dropna()).max().strftime('%d/%m')
            texto_ref = f" VS ({min_ref} a {max_ref})"
        except: pass
        
    elif filtro_data == "Ida e Volta Forte": 
        texto_data = "(03/06 e 07/06)"
        try:
            d_ida = pd.to_datetime(df_d[df_d['data_str'] == data_ancora_ida][col_ref_data].iloc[0]).strftime('%d/%m')
            d_volta = pd.to_datetime(df_d[df_d['data_str'] == data_ancora_volta][col_ref_data].iloc[0]).strftime('%d/%m')
            texto_ref = f" VS ({d_ida} e {d_volta})"
        except: pass
        
    elif filtro_data == "Dias Fracos": 
        texto_data = "(02/06, 04/06, 05/06, 06/06 e 08/06)"
        texto_ref = " VS (Dias Relativos Equivalentes)"
        
    else: 
        texto_data = f"({pd.to_datetime(filtro_data).strftime('%d/%m/%Y')})"
        try:
            dia_filtro_str = pd.to_datetime(filtro_data).strftime('%Y-%m-%d')
            d_ref = pd.to_datetime(df_d[df_d['data_str'] == dia_filtro_str][col_ref_data].iloc[0]).strftime('%d/%m/%Y')
            texto_ref = f" VS ({d_ref})"
        except: pass

    with col_t:
        st.write("") 
        st.write("")
        st.markdown(f'''
            <div class="section-title">
                Visão Consolidada 
                <span style="color: var(--buser-pink); font-weight: 600; font-size: 1.1rem; margin-left: 8px;">{texto_data}</span>
                <span style="color: rgba(255, 51, 119, 0.6); font-weight: 500; font-size: 1rem; margin-left: 8px;">{texto_ref}</span>
            </div>
        ''', unsafe_allow_html=True)

    st.markdown('<div class="pg-header" style="padding-top:0; margin-top:0px; margin-bottom: 2rem;"></div>', unsafe_allow_html=True)

    if filtro_data == "Consolidado Feriado":
        df_view = df_g.copy()
        
    elif filtro_data in ["Ida e Volta Forte", "Dias Fracos"]:
        datas_fortes = [data_ancora_ida, data_ancora_volta]
        
        if filtro_data == "Ida e Volta Forte": 
            df_filtrado = df_d[df_d['data_str'].isin(datas_fortes)].copy()
        else: 
            df_filtrado = df_d[~df_d['data_str'].isin(datas_fortes)].copy()

        if not df_filtrado.empty:
            df_filtrado['metrica_limpa'] = df_filtrado['metrica'].apply(lambda x: str(x).split('. ', 1)[-1].strip())
            cols_to_pivot = ['atual']
            if ref_col in df_filtrado.columns: cols_to_pivot.append(ref_col)
                
            df_piv = df_filtrado.pivot_table(index='data_str', columns='metrica_limpa', values=cols_to_pivot, aggfunc='sum')
            somas = df_piv.sum() 
            
            def get_val(cenario, metrica):
                try: return float(somas[(cenario, metrica)])
                except: return 0.0

            rows = []
            for m_orig in df_g['metrica'].unique():
                m_limpa = str(m_orig).split('. ', 1)[-1].strip()
                if m_limpa == "Yield":
                    v_atual = get_val('atual', 'GMV') / get_val('atual', 'RPK') if get_val('atual', 'RPK') else 0
                    v_ref = get_val(ref_col, 'GMV') / get_val(ref_col, 'RPK') if get_val(ref_col, 'RPK') else 0
                elif m_limpa == "Load Factor":
                    v_atual = get_val('atual', 'RPK') / get_val('atual', 'ASK') if get_val('atual', 'ASK') else 0
                    v_ref = get_val(ref_col, 'RPK') / get_val(ref_col, 'ASK') if get_val(ref_col, 'ASK') else 0
                elif m_limpa == "Ticket Médio":
                    v_atual = get_val('atual', 'GMV') / get_val('atual', 'Pax Total') if get_val('atual', 'Pax Total') else 0
                    v_ref = get_val(ref_col, 'GMV') / get_val(ref_col, 'Pax Total') if get_val(ref_col, 'Pax Total') else 0
                elif m_limpa == "RASK":
                    v_atual = get_val('atual', 'GMV') / get_val('atual', 'ASK') if get_val('atual', 'ASK') else 0
                    v_ref = get_val(ref_col, 'GMV') / get_val(ref_col, 'ASK') if get_val(ref_col, 'ASK') else 0
                else:
                    v_atual = get_val('atual', m_limpa)
                    v_ref = get_val(ref_col, m_limpa)
                
                rows.append({'metrica': m_orig, 'atual': v_atual, ref_col: v_ref})
            df_view = pd.DataFrame(rows)
        else:
            df_view = df_g.copy() 
    else: 
        df_view = df_d[df_d['data_str'] == pd.to_datetime(filtro_data).strftime('%Y-%m-%d')].copy()
    
    cols = st.columns(5)
    for i, row in enumerate(df_view.to_dict('records')):
        nome = str(row.get('metrica', '')).split('. ', 1)[-1]
        cols[i % 5].metric(label=nome, value=format_kpi(nome, row.get('atual')), delta=format_delta(row.get('atual'), row.get(ref_col)))

    st.markdown('<div class="section-label">Comparativo Direto (Absolutos)</div>', unsafe_allow_html=True)
    df_tg = df_view.copy()
    df_tg['Métrica'] = df_tg['metrica'].apply(lambda x: str(x).split('. ', 1)[-1])
    df_tg[ref_nome] = df_tg.apply(lambda row: format_kpi(row['Métrica'], row.get(ref_col)), axis=1)
    df_tg['Atual'] = df_tg.apply(lambda row: format_kpi(row['Métrica'], row.get('atual')), axis=1)
    df_tg['Var %'] = df_tg.apply(lambda row: format_delta(row.get('atual'), row.get(ref_col)), axis=1)
    st.dataframe(df_tg[['Métrica', ref_nome, 'Atual', 'Var %']], use_container_width=True, hide_index=True)


# ── FUNÇÃO 2: ACOMPANHAMENTO POR ANTECEDÊNCIA (PLOTLY) ────────────────────────
def render_rota_antecedencia(df_ra_raw: pd.DataFrame):
    
    st.markdown("""
    <div class="pg-header" style="border:none; padding-bottom:0; margin-bottom:0;">
      <div>
        <div class="pg-eyebrow">Acompanhamento</div>
        <div class="pg-title">Evolução da Curva por Antecedência</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    if df_ra_raw.empty:
        st.info("Nenhum dado encontrado.")
        return

    df_ra = df_ra_raw.copy()
    for col_atual in ['data_corpus_2026', 'data_corpus2026']:
        if col_atual in df_ra.columns and 'data' not in df_ra.columns:
            df_ra = df_ra.rename(columns={col_atual: 'data'})
            
    df_ra['data'] = pd.to_datetime(df_ra['data'], errors='coerce')
    
    st.markdown('<div class="section-label" style="margin-top: 10px;">Selecione o Corte</div>', unsafe_allow_html=True)
    
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    with col_f1: 
        rota_sel = st.selectbox("Rota Principal:", options=sorted(df_ra['rota_principal'].dropna().unique()))
    with col_f2:
        df_rota = df_ra[df_ra['rota_principal'] == rota_sel]
        sentido_sel = st.selectbox("Sentido:", options=sorted(df_rota['eixo_sentido'].dropna().unique()))
    with col_f3:
        df_sentido = df_rota[df_rota['eixo_sentido'] == sentido_sel]
        data_sel = st.selectbox("Data da Viagem:", options=sorted(df_sentido['data'].dropna().unique()), format_func=lambda x: pd.to_datetime(x).strftime('%d/%m/%Y'))
    with col_f4:
        opcoes_ref_rota = ["Páscoa 2026", "Corpus 2025", "Maio 2026"]
        ref_nome_rota = st.selectbox("Comparar com (Ref):", opcoes_ref_rota, key="rota_ref_sel")
        ref_col_pax = get_ref_col_name("pax_", ref_nome_rota, df_ra.columns)
        ref_suf = ref_col_pax.replace("pax_", "") 

    st.markdown('<div class="pg-header" style="padding-top:0; margin-top:10px;"></div>', unsafe_allow_html=True)

    df_filt = df_sentido[df_sentido['data'] == data_sel].copy()
    if df_filt.empty: return

    colunas_agg = {
        'pax_atual': 'sum', 
        'lf_atual': 'mean', 
        'yield_atual': 'mean', 
        'ticket_medio_atual': 'mean'
    }
    
    if f'pax_{ref_suf}' in df_filt.columns: colunas_agg[f'pax_{ref_suf}'] = 'sum'
    if f'lf_{ref_suf}' in df_filt.columns: colunas_agg[f'lf_{ref_suf}'] = 'mean'
    if f'yield_{ref_suf}' in df_filt.columns: colunas_agg[f'yield_{ref_suf}'] = 'mean'
    if f'ticket_medio_{ref_suf}' in df_filt.columns: colunas_agg[f'ticket_medio_{ref_suf}'] = 'mean'

    df_plot = df_filt.groupby('antecedencia').agg(colunas_agg).reset_index()

    st.markdown('<div class="section-label" style="margin-top: 1.5rem;">Gráfico de Evolução</div>', unsafe_allow_html=True)
    metrica_grafico = st.radio("Escolha o indicador:", options=["Passageiros (Pax)", "Load Factor", "Yield (R$)", "Ticket Médio (R$)"], horizontal=True, label_visibility="collapsed")

    chart_df = df_plot.copy()
    
    if metrica_grafico == "Passageiros (Pax)": 
        y_cols = ['pax_atual']
        if f'pax_{ref_suf}' in chart_df.columns: y_cols.append(f'pax_{ref_suf}')
    elif metrica_grafico == "Load Factor": 
        y_cols = ['lf_atual']
        if f'lf_{ref_suf}' in chart_df.columns: y_cols.append(f'lf_{ref_suf}')
    elif metrica_grafico == "Yield (R$)": 
        y_cols = ['yield_atual']
        if f'yield_{ref_suf}' in chart_df.columns: y_cols.append(f'yield_{ref_suf}')
    else: 
        y_cols = ['ticket_medio_atual']
        if f'ticket_medio_{ref_suf}' in chart_df.columns: y_cols.append(f'ticket_medio_{ref_suf}')

    renames = {y_cols[0]: "Cenário Atual"}
    if len(y_cols) > 1: renames[y_cols[1]] = ref_nome_rota
        
    chart_df = chart_df[['antecedencia'] + y_cols].rename(columns=renames)
    df_melt = chart_df.melt(id_vars='antecedencia', var_name='Cenário', value_name='Valor')

    fig = px.line(df_melt, x='antecedencia', y='Valor', color='Cenário', color_discrete_map={'Cenário Atual': '#FF3377', ref_nome_rota: '#9CA3AF'}, markers=True)
    
    if metrica_grafico in ["Load Factor", "Yield (R$)"]: fig.update_yaxes(range=[0, 1], title=metrica_grafico)
    else: fig.update_yaxes(rangemode="tozero", title=metrica_grafico)
    
    fig.update_layout(hovermode="x unified", margin=dict(t=20, b=10, l=0, r=0), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title=None))
    fig.update_xaxes(title="Dias de Antecedência", tickformat="d", dtick=2)
    st.plotly_chart(fig, use_container_width=True, theme="streamlit")


# ── FUNÇÃO 3: EDITOR DE PREÇOS (O CAÇADOR DE COLUNAS VIVE AQUI) ────────────────
def render_editor(df_raw: pd.DataFrame, tab_key: str, titulo: str):
    agora_t = datetime.now().strftime("%d/%m/%Y %H:%M")

    col_t1, col_t2 = st.columns([3, 1])
    with col_t1:
        st.markdown(f"""
        <div class="pg-header">
          <div>
            <div class="pg-eyebrow">Ações de Pricing</div>
            <div class="pg-title"><span class="live-dot"></span>{titulo}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_t2:
        opcoes_dropdown = ["Páscoa 2026", "Corpus 2025", "Maio 2026"]
        st.write("") 
        ref_nome = st.selectbox("Comparar com (Ref):", opcoes_dropdown, key=f"{tab_key}_ref_sel")

    st.markdown(f'<div class="header-divider"><span style="color:var(--text-color); opacity: 0.6; font-size:0.85rem; font-weight: 500;">Atualizado via Databricks às {agora_t}</span></div>', unsafe_allow_html=True)

    if df_raw.empty:
        st.info("Nenhum dado encontrado para o editor.")
        return
        
    # --- Caçador Implacável de Colunas ---
    kw1 = ref_nome.split()[0].lower().replace("á", "a")
    kw2 = ref_nome.split()[1][-2:] 

    col_data_ref = next((c for c in df_raw.columns if 'data_ref' in c and kw1 in c), f"data_ref_{kw1}_missing")
    col_buscas_ref = next((c for c in df_raw.columns if 'buscas' in c and kw1 in c), f"buscas_{kw1}_missing")
    col_lf_ref = next((c for c in df_raw.columns if 'lf' in c and kw1 in c and 'ratio' not in c), f"lf_{kw1}_missing")
    col_ratio_ref = next((c for c in df_raw.columns if 'ratio' in c and kw1 in c), f"ratio_lf_{kw1}_missing")
    col_tkm_ref = next((c for c in df_raw.columns if ('tkm' in c or 'ticket_medio' in c) and kw1 in c), f"tkm_{kw1}_missing")

    col_buscas_atual = next((c for c in df_raw.columns if 'buscas' in c and ('atual' in c or '2026' in c or '26' in c)), 'buscas_atual_missing')
    col_pax_atual = next((c for c in df_raw.columns if 'pax' in c and 'atual' in c), 'pax_atual_missing')
    col_lf_atual = next((c for c in df_raw.columns if 'lf' in c and 'atual' in c and 'ratio' not in c), 'lf_atual_missing')

    # Alerta se faltar as colunas base.
    essenciais = [col_data_ref, col_lf_ref, col_tkm_ref]
    faltam = [c for c in essenciais if "missing" in c]
    if faltam:
        st.markdown(f'<div class="warn-banner">⚠️ Atenção: Faltam algumas colunas base para {ref_nome} no CSV ({", ".join([f.replace("_missing", "") for f in faltam])}). Verifique sua tabela no Databricks.</div>', unsafe_allow_html=True)

    def calc_row_id(row):
        data_val = row.get("data_atual")
        d_str = pd.to_datetime(data_val).strftime("%Y-%m-%d") if pd.notna(data_val) else ""
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
        datas_c = sorted(df_raw["data_atual"].dt.date.dropna().unique())
        datas_c_sel = st.multiselect("Data da Viagem:", options=datas_c, default=datas_c, format_func=lambda d: d.strftime("%d/%m"), key=f"{tab_key}_datas")
    with col_f2:
        turnos_c = sorted(df_raw["turno"].dropna().unique())
        turnos_sel = st.multiselect("Turno:", options=turnos_c, default=turnos_c, key=f"{tab_key}_turnos")
    with col_f3:
        rota_c = st.text_input("Buscar Sentido:", placeholder="Ex: BHZ-RIO", key=f"{tab_key}_rota")

    df_cv = df_raw.copy()
    if datas_c_sel: df_cv = df_cv[df_cv["data_atual"].dt.date.isin(datas_c_sel)]
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

    cols_editor = [
        "row_id", col_data_ref, "data_atual", "dia_da_semana", "antecedencia", 
        "rota_principal", "sentido", "tipo_assento", "turno", 
        col_buscas_ref, col_buscas_atual, col_pax_atual, "capacidade_atual", "vagas_restantes", 
        col_lf_ref, col_lf_atual, col_ratio_ref, "price_cc", col_tkm_ref, "tkm_atual", 
        "mult_atual_aplicado", "preco_cenario_atual", "mult_flutuacao", "preco_flutuacao", 
        "preco_maximo_feriado", "data_atualizacao"
    ]
    cols_presentes = [c for c in cols_editor if c in df_cv_editor.columns]
    df_editor = df_cv_editor[cols_presentes].copy()

    # Formatações Visuais das Colunas
    df_editor["data_fmt"] = pd.to_datetime(df_editor["data_atual"]).dt.strftime("%d/%m/%Y")
    
    if col_data_ref in df_editor.columns:
        df_editor["data_ref_fmt"] = pd.to_datetime(df_editor[col_data_ref], errors="coerce").dt.strftime("%d/%m/%Y").fillna("-")

    if col_ratio_ref in df_editor.columns: 
        df_editor["ratio_ref_fmt"] = df_editor[col_ratio_ref].astype(float).round(3).astype(str) + "x"
    
    if col_lf_ref in df_editor.columns: 
        df_editor["lf_ref_fmt"] = (df_editor[col_lf_ref] * 100).astype(float).round(1).astype(str) + "%"
    
    if col_lf_atual in df_editor.columns: 
        df_editor["lf_a_fmt"] = (df_editor[col_lf_atual] * 100).astype(float).round(1).astype(str) + "%"

    df_editor["incluir"] = df_editor["row_id"].map(lambda x: st.session_state[dict_key].get(x, {}).get("incluir", True))
    df_editor["Preco novo"] = df_editor["row_id"].map(lambda x: st.session_state[dict_key].get(x, {}).get("Preco novo", None))

    show_cols = [
        "incluir", "data_ref_fmt", "data_fmt", "dia_da_semana", "antecedencia", "rota_principal", "sentido", "tipo_assento", "turno", 
        col_buscas_ref, col_buscas_atual, col_pax_atual, "capacidade_atual", "vagas_restantes", 
        "lf_ref_fmt", "lf_a_fmt", "ratio_ref_fmt", "price_cc", col_tkm_ref, "tkm_atual", 
        "mult_atual_aplicado", "preco_cenario_atual", "mult_flutuacao", "preco_flutuacao", "preco_maximo_feriado", "data_atualizacao", "Preco novo"
    ]
    
    show_cols_safe = [c for c in show_cols if c in df_editor.columns]
    df_show = df_editor[show_cols_safe].copy()

    col_config = {
        "incluir": st.column_config.CheckboxColumn("Incluir", default=True),
        "data_ref_fmt": st.column_config.TextColumn(f"Data Ref. ({ref_nome})", disabled=True),
        "data_fmt": st.column_config.TextColumn("Data Atual", disabled=True),
        "dia_da_semana": st.column_config.TextColumn("Dia Semana", disabled=True),
        "antecedencia": st.column_config.NumberColumn("Antec.", disabled=True),
        "rota_principal": st.column_config.TextColumn("Rota", disabled=True),
        "sentido": st.column_config.TextColumn("Sentido", disabled=True),
        "tipo_assento": st.column_config.TextColumn("Assento", disabled=True),
        "turno": st.column_config.TextColumn("Turno", disabled=True),
        col_buscas_ref: st.column_config.NumberColumn(f"Buscas ({ref_nome})", disabled=True),
        col_buscas_atual: st.column_config.NumberColumn("Buscas Atual", disabled=True),
        col_pax_atual: st.column_config.NumberColumn("PAX Atual", disabled=True),
        "capacidade_atual": st.column_config.NumberColumn("Capacidade", disabled=True),
        "vagas_restantes": st.column_config.NumberColumn("↑ Vagas", disabled=True),
        "lf_ref_fmt": st.column_config.TextColumn(f"LF ({ref_nome})", disabled=True),
        "lf_a_fmt": st.column_config.TextColumn("LF Atual", disabled=True),
        "ratio_ref_fmt": st.column_config.TextColumn(f"Ratio LF ({ref_nome})", disabled=True),
        "price_cc": st.column_config.NumberColumn("Price CC", disabled=True, format="R$ %.0f"),
        col_tkm_ref: st.column_config.NumberColumn(f"TKM ({ref_nome})", disabled=True, format="R$ %.0f"),
        "tkm_atual": st.column_config.NumberColumn("TKM Atual", disabled=True, format="R$ %.0f"),
        "mult_atual_aplicado": st.column_config.NumberColumn("Mult Final", disabled=True, format="%.3fx"),
        "preco_cenario_atual": st.column_config.NumberColumn("Preço Cenario", disabled=True, format="R$ %.2f"),
        "mult_flutuacao": st.column_config.NumberColumn("Mult Flutuação", disabled=True, format="%.2fx"),
        "preco_flutuacao": st.column_config.NumberColumn("Preço Flutuação", disabled=True, format="R$ %.2f"),
        "preco_maximo_feriado": st.column_config.NumberColumn("Teto Flutuação", disabled=True, format="R$ %.2f"),
        "data_atualizacao": st.column_config.TextColumn("Data Atualização", disabled=True), 
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

            df_editado["data_fmt"] = pd.to_datetime(df_editado["data_atual"]).dt.strftime("%d/%m/%Y")
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
                        repo = "laviniateixeira-dev/Pricing-Feriados"
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

# ── FUNÇÃO 4: HISTÓRICO DE ALTERAÇÕES ─────────────────────────────────────────
def render_historico():
    st.markdown("""
    <div class="pg-header">
      <div>
        <div class="pg-eyebrow">Acompanhamento</div>
        <div class="pg-title"><span class="live-dot"></span>Histórico de Alterações (Envios Próprios)</div>
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
with tab1: render_resultados(df_geral_raw, df_dia_raw)
with tab2: render_rota_antecedencia(df_rota_raw)
with tab3: render_editor(df_editor_raw, tab_key="t3", titulo="Editor de Preços")
with tab4: render_historico()
