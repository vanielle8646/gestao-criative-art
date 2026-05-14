import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

st.set_page_config(page_title="Arte Criativa - Gestão", layout="wide")

# Link da planilha
url = "https://docs.google.com/spreadsheets/d/13Qqqr2IgjZKsUzGSEBcZl3OWWeXc4NIW0QoWw2X4ktE/edit?usp=sharing"

conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(spreadsheet=url)

# Função para limpar os valores
def limpar_valor(val):
    if pd.isna(val): return 0.0
    val_str = str(val).replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
    try: return float(val_str)
    except: return 0.0

if not df.empty:
    df['Valor'] = df['Valor'].apply(limpar_valor)
    df['Tipo'] = df['Tipo'].astype(str).str.strip()

st.markdown("<h1 style='color: #00ffcc;'>📊 Painel de Controle - Arte Criativa</h1>", unsafe_allow_html=True)

# Exibição dos Totais (Métricas)
if not df.empty:
    receitas = df[df['Tipo'].str.contains('Entrada', case=False, na=False)]['Valor'].sum()
    despesas = df[df['Tipo'].str.contains('Saíd|Said', case=False, na=False)]['Valor'].sum()
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Receitas", f"R$ {receitas:,.2f}")
    c2.metric("Despesas", f"R$ {despesas:,.2f}")
    c3.metric("Saldo", f"R$ {receitas-despesas:,.2f}")

st.divider()

# FORMULÁRIO DE CADASTRO (Agora direto na tela!)
st.subheader("➕ Cadastrar Novo Registro")
with st.form("novo_registro", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        data_input = st.date_input("Data", datetime.now())
        desc_input = st.text_input("Descrição (Ex: Xerox, Impressão)")
    with col2:
        valor_input = st.number_input("Valor", min_value=0.0, format="%.2f")
        tipo_input = st.selectbox("Tipo", ["Entrada", "Saída"])
    
    status_input = st.selectbox("Status", ["Pago", "Pendente"])
    botao = st.form_submit_button("Salvar no Sistema")

if botao:
    nova_linha = pd.DataFrame([{
        "Data": data_input.strftime("%Y/%m/%d"),
        "Descrição": desc_input,
        "Tipo": tipo_input,
        "Valor": valor_input,
        "Status": status_input
    }])
    df_final = pd.concat([df, nova_linha], ignore_index=True)
    conn.update(spreadsheet=url, data=df_final)
    st.success("Dados salvos com sucesso!")
    st.rerun()

st.divider()
st.subheader("📝 Histórico de Lançamentos")
st.dataframe(df, use_container_width=True)
