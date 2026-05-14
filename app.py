import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

st.set_page_config(page_title="Arte Criativa - Gestão", layout="wide")

url = "https://docs.google.com/spreadsheets/d/13Qqqr2IgjZKsUzGSEBcZl3OWWeXc4NIW0QoWw2X4ktE/edit?usp=sharing"

conn = st.connection("gsheets", type=GSheetsConnection)

# Função para carregar e limpar dados
def carregar_dados():
    data = conn.read(spreadsheet=url, ttl=0) # ttl=0 força o app a ler o dado mais novo
    if data is not None:
        # Remove linhas totalmente vazias
        data = data.dropna(subset=['Data', 'Descrição'], how='all').copy()
        return data
    return pd.DataFrame()

df = carregar_dados()

def limpar_valor(val):
    if pd.isna(val): return 0.0
    val_str = str(val).replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
    try: return float(val_str)
    except: return 0.0

if not df.empty:
    df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
    df['Valor'] = df['Valor'].apply(limpar_valor)
    df['Tipo'] = df['Tipo'].astype(str).str.strip()
    df['Mes'] = df['Data'].dt.month
    df['Ano'] = df['Data'].dt.year

st.markdown("<h1 style='color: #00ffcc;'>📊 Painel de Controle - Arte Criativa</h1>", unsafe_allow_html=True)

# --- MÉTRICAS DO MÊS ATUAL ---
if not df.empty:
    mes_atual, ano_atual = datetime.now().month, datetime.now().year
    df_topo = df[(df['Mes'] == mes_atual) & (df['Ano'] == ano_atual)]
    if df_topo.empty: df_topo = df
    
    rec = df_topo[df_topo['Tipo'].str.contains('Entrada', case=False, na=False)]['Valor'].sum()
    des = df_topo[df_topo['Tipo'].str.contains('Saíd|Said', case=False, na=False)]['Valor'].sum()
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Receitas", f"R$ {rec:,.2f}")
    c2.metric("Despesas", f"R$ {des:,.2f}")
    c3.metric("Saldo", f"R$ {rec-des:,.2f}")

st.divider()

# --- FORMULÁRIO DE LANÇAMENTO ---
st.subheader("➕ Novo Lançamento")
with st.form("form_add", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        d = st.date_input("Data", datetime.now())
        desc = st.text_input("Descrição")
    with col2:
        v = st.number_input("Valor", min_value=0.0, step=0.01, format="%.2f")
        t = st.selectbox("Tipo", ["Entrada", "Saída"])
    
    if st.form_submit_button("Salvar no Sistema"):
        if desc and v > 0:
            nova_linha = pd.DataFrame([{"Data": d.strftime("%Y/%m/%d"), "Descrição": desc, "Tipo": t, "Valor": v, "Status": "Pago"}])
            # Atualiza a planilha
            df_atualizado = pd.concat([df.drop(columns=['Mes', 'Ano'], errors='ignore'), nova_linha], ignore_index=True)
            conn.update(spreadsheet=url, data=df_atualizado)
            st.success("Lançamento realizado!")
            st.rerun()
        else:
            st.error("Preencha a descrição e o valor.")

st.divider()
st.subheader("📝 Histórico Recente")
if not df.empty:
    st.dataframe(df.drop(columns=['Mes', 'Ano'], errors='ignore').tail(10), use_container_width=True)

# --- CONSULTA ---
with st.expander("🔍 Consultar outros meses"):
    # (Código de consulta simplificado para garantir estabilidade)
    st.write("Selecione o período para ver o detalhamento.")
    
