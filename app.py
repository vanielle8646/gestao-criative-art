import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

st.set_page_config(page_title="Arte Criativa - Gestão", layout="wide")

# URL da planilha
url = "https://docs.google.com/spreadsheets/d/13Qqqr2IgjZKsUzGSEBcZl3OWWeXc4NIW0QoWw2X4ktE/edit?usp=sharing"

conn = st.connection("gsheets", type=GSheetsConnection)

# Função para ler os dados ignorando lixo
def carregar():
    dados = conn.read(spreadsheet=url, ttl=0)
    if dados is not None:
        return dados.dropna(subset=['Data', 'Descrição'], how='all').copy()
    return pd.DataFrame()

df = carregar()

def limpar_v(val):
    if pd.isna(val): return 0.0
    s = str(val).replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
    try: return float(s)
    except: return 0.0

st.markdown("<h1 style='color: #00ffcc;'>📊 Painel de Controle - Arte Criativa</h1>", unsafe_allow_html=True)

# --- RESUMO DO MÊS ---
if not df.empty:
    df['Data_dt'] = pd.to_datetime(df['Data'], errors='coerce')
    df['V_num'] = df['Valor'].apply(limpar_v)
    
    hoje = datetime.now()
    df_mes = df[(df['Data_dt'].dt.month == hoje.month) & (df['Data_dt'].dt.year == hoje.year)]
    
    if df_mes.empty: df_mes = df # Se o mês tá vazio, mostra o total
    
    ent = df_mes[df_mes['Tipo'].str.contains('Entrada', case=False, na=False)]['V_num'].sum()
    sai = df_mes[df_mes['Tipo'].str.contains('Saíd|Said', case=False, na=False)]['V_num'].sum()
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Receitas", f"R$ {ent:,.2f}")
    c2.metric("Despesas", f"R$ {sai:,.2f}")
    c3.metric("Saldo", f"R$ {ent-sai:,.2f}")

st.divider()

# --- FORMULÁRIO DE LANÇAMENTO ---
st.subheader("➕ Novo Lançamento")
with st.form("meu_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        data_f = st.date_input("Data", datetime.now())
        desc_f = st.text_input("Descrição")
    with col2:
        val_f = st.number_input("Valor", min_value=0.0, format="%.2f")
        tipo_f = st.selectbox("Tipo", ["Entrada", "Saída"])
    
    if st.form_submit_button("Salvar no Sistema"):
        if desc_f and val_f > 0:
            # Prepara a nova linha exatamente com as colunas da planilha
            nova = pd.DataFrame([{
                "Data": data_f.strftime("%Y/%m/%d"),
                "Descrição": desc_f,
                "Tipo": tipo_f,
                "Valor": val_f,
                "Status": "Pago"
            }])
            
            # Pega o que já existe (sem as colunas temporárias de cálculo)
            df_atual = df[['Data', 'Descrição', 'Tipo', 'Valor', 'Status']].copy()
            df_final = pd.concat([df_atual, nova], ignore_index=True)
            
            # TENTA GRAVAR
            try:
                conn.update(spreadsheet=url, data=df_final)
                st.success("Salvo com sucesso! Atualizando...")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao gravar: Verifique se a planilha está como 'Editor' para todos com o link.")
        else:
            st.warning("Preencha a descrição e o valor!")

st.divider()
st.subheader("📝 Histórico")
if not df.empty:
    st.dataframe(df[['Data', 'Descrição', 'Tipo', 'Valor', 'Status']].tail(10), use_container_width=True)
    
