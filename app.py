import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Arte Criativa - Gestão", layout="wide")

# Link da sua planilha
url = "https://docs.google.com/spreadsheets/d/13Qqqr2IgjZKsUzGSEBcZl3OWWeXc4NIW0QoWw2X4ktE/edit?usp=sharing"

# Conectar e ler
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(spreadsheet=url)

# Limpeza dos dados: Remove R$ e converte para número
if not df.empty:
    df['Valor'] = df['Valor'].astype(str).str.replace('R$', '', regex=False).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
    df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce').fillna(0)

st.markdown("<h1 style='color: #00ffcc;'>📊 Painel de Controle - Arte Criativa</h1>", unsafe_allow_html=True)

# Formulário de Cadastro
with st.sidebar:
    st.header("Novo Registro")
    with st.form("add_registro", clear_on_submit=True):
        data = st.date_input("Data")
        descricao = st.text_input("Descrição")
        valor = st.number_input("Valor", min_value=0.0, format="%.2f")
        tipo = st.selectbox("Tipo", ["Entrada", "Saída"])
        status = st.selectbox("Status", ["Pago", "Pendente"])
        botao_salvar = st.form_submit_button("Salvar no Sistema")

    if botao_salvar:
        nova_linha = pd.DataFrame([{"Data": data.strftime("%Y-%m-%d"), "Descrição": descricao, "Valor": valor, "Tipo": tipo, "Status": status}])
        df_atualizado = pd.concat([df, nova_linha], ignore_index=True)
        conn.update(spreadsheet=url, data=df_atualizado)
        st.success("Sincronizado!")
        st.rerun()

# Exibição dos Totais
if not df.empty:
    receitas = df[df['Tipo'] == 'Entrada']['Valor'].sum()
    despesas = df[df['Tipo'] == 'Saída']['Valor'].sum()
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Receitas", f"R$ {receitas:,.2f}")
    c2.metric("Despesas", f"R$ {despesas:,.2f}")
    c3.metric("Saldo", f"R$ {receitas-despesas:,.2f}")

st.dataframe(df, use_container_width=True)
