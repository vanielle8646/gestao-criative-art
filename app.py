import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Arte Criativa - Gestão", layout="wide")

url = "https://docs.google.com/spreadsheets/d/13Qqqr2IgjZKsUzGSEBcZl3OWWeXc4NIW0QoWw2X4ktE/edit?usp=sharing"

conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(spreadsheet=url)

st.markdown("<h1 style='color: #00ffcc;'>📊 Painel de Controle - Arte Criativa</h1>", unsafe_allow_html=True)

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

if not df.empty:
    receitas = df[df['Tipo'] == 'Entrada']['Valor'].sum()
    despesas = df[df['Tipo'] == 'Saída']['Valor'].sum()
    st.columns(3)[0].metric("Receitas", f"R$ {receitas:,.2f}")
    st.columns(3)[1].metric("Despesas", f"R$ {despesas:,.2f}")
    st.columns(3)[2].metric("Saldo", f"R$ {receitas-despesas:,.2f}")

st.dataframe(df, use_container_width=True)
