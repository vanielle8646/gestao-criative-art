import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Configuração da Página
st.set_page_config(page_title="Arte Criativa - Gestão", layout="wide")

# --- CONEXÃO COM GOOGLE SHEETS ---
# Usando o link que você forneceu
url = "https://docs.google.com/spreadsheets/d/13Qqqr2IgjZKsUzGSEBcZl3OWWeXc4NIW0QoWw2X4ktE/edit?usp=sharing"

conn = st.connection("gsheets", type=GSheetsConnection)

# Ler dados da planilha
df = conn.read(spreadsheet=url)

# Título Principal
st.markdown("<h1 style='color: #00ffcc;'>📊 Painel de Controle - Arte Criativa</h1>", unsafe_allow_html=True)

# --- FORMULÁRIO DE ENTRADA (Lado Esquerdo) ---
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
        # Criar nova linha
        nova_linha = pd.DataFrame([{
            "Data": data.strftime("%Y-%m-%d"),
            "Descrição": descricao,
            "Valor": valor,
            "Tipo": tipo,
            "Status": status
        }])
        
        # Combinar com dados existentes
        df_atualizado = pd.concat([df, nova_linha], ignore_index=True)
        
        # Salvar de volta na planilha do Google
        conn.update(spreadsheet=url, data=df_atualizado)
        st.success("Informação salva e sincronizada!")
        st.rerun()

# --- RESUMO FINANCEIRO (Cálculos automáticos) ---
if not df.empty:
    receitas = df[df['Tipo'] == 'Entrada']['Valor'].sum()
    despesas = df[df['Tipo'] == 'Saída']['Valor'].sum()
    saldo = receitas - despesas

    col1, col2, col3 = st.columns(3)
    col1.metric("Receitas (Mês)", f"R$ {receitas:,.2f}")
    col2.metric("Despesas (Mês)", f"R$ {despesas:,.2f}")
    col3.metric("Saldo Mensal", f"R$ {saldo:,.2f}")

# --- HISTÓRICO (Visualização no Celular e PC) ---
st.markdown("---")
st.subheader("📋 Histórico e Edição")
st.dataframe(df, use_container_width=True)
