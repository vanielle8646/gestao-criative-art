import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Arte Criativa - Gestão", layout="wide")

url = "https://docs.google.com/spreadsheets/d/13Qqqr2IgjZKsUzGSEBcZl3OWWeXc4NIW0QoWw2X4ktE/edit?usp=sharing"

conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(spreadsheet=url)

# Função para limpar o valor de forma segura
def limpar_valor(val):
    if pd.isna(val):
        return 0.0
    val_str = str(val).replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
    try:
        return float(val_str)
    except:
        return 0.0

if not df.empty:
    # Limpa a coluna de valor
    df['Valor'] = df['Valor'].apply(limpar_valor)
    # Limpa a coluna de tipo para evitar erros de acento ou espaços
    df['Tipo'] = df['Tipo'].astype(str).str.strip()

st.markdown("<h1 style='color: #00ffcc;'>📊 Painel de Controle - Arte Criativa</h1>", unsafe_allow_html=True)

if not df.empty:
    # Calcula usando termos flexíveis para evitar erros de digitação
    receitas = df[df['Tipo'].str.contains('Entrada', case=False, na=False)]['Valor'].sum()
    despesas = df[df['Tipo'].str.contains('Saíd|Said', case=False, na=False)]['Valor'].sum()
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Receitas", f"R$ {receitas:,.2f}")
    c2.metric("Despesas", f"R$ {despesas:,.2f}")
    c3.metric("Saldo", f"R$ {receitas-despesas:,.2f}")

st.dataframe(df, use_container_width=True)
