import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Arte Criativa - Gestão", layout="wide")

url = "https://docs.google.com/spreadsheets/d/13Qqqr2IgjZKsUzGSEBcZl3OWWeXc4NIW0QoWw2X4ktE/edit?usp=sharing"

conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(spreadsheet=url, usecols=[0, 1, 2, 3, 4])

# Removemos qualquer espaço extra e garantimos a limpeza
df['Tipo'] = df['Tipo'].astype(str).str.strip()
df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce').fillna(0)

st.markdown("<h1 style='color: #00ffcc;'>📊 Painel de Controle</h1>", unsafe_allow_html=True)

# Lógica de cálculo forçada (aceita Saída ou Saida)
receitas = df[df['Tipo'].str.contains('Entrada', case=False, na=False)]['Valor'].sum()
despesas = df[df['Tipo'].str.contains('Saíd|Said', case=False, na=False)]['Valor'].sum()

c1, c2, c3 = st.columns(3)
c1.metric("Receitas", f"R$ {receitas:,.2f}")
c2.metric("Despesas", f"R$ {despesas:,.2f}")
c3.metric("Saldo", f"R$ {receitas-despesas:,.2f}")

st.dataframe(df, use_container_width=True)
