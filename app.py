import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURAÇÃO DE CAMINHO ---
try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    BASE_DIR = os.getcwd()
DB_FILE = os.path.join(BASE_DIR, "database_arte_criativa.csv")

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Arte Criativa - Gestão", layout="wide", page_icon="🎨")

# --- ESTILIZAÇÃO PERSONALIZADA ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetricValue"] { color: #00ffcc !important; font-size: 32px !important; font-weight: bold; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; background-color: #00ffcc; color: black; font-weight: bold; border: none; }
    h1, h2, h3 { color: #00ffcc !important; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÃO PARA CARREGAR DADOS ---
def carregar_dados():
    if os.path.exists(DB_FILE):
        data = pd.read_csv(DB_FILE)
        data['Data'] = pd.to_datetime(data['Data']).dt.date
        return data
    return pd.DataFrame(columns=["Data", "Descrição", "Tipo", "Valor", "Status"])

df = carregar_dados()

# --- BARRA LATERAL ---
with st.sidebar:
    # AJUSTE PARA A SUA LOGO (Nome exato conforme a sua pasta)
    caminho_logo = os.path.join(BASE_DIR, "logo.jpg") 
    
    if os.path.exists(caminho_logo):
        st.image(caminho_logo, use_container_width=True)
    else:
        st.title("🎨 Arte Criativa")
    
    st.divider()
    
    with st.form("novo_lancamento"):
        st.subheader("📝 Novo Registro")
        f_data = st.date_input("Data", datetime.now())
        f_desc = st.text_input("Descrição")
        f_tipo = st.selectbox("Tipo", ["Entrada", "Saída"])
        f_val = st.number_input("Valor", min_value=0.0, format="%.2f")
        f_stat = st.selectbox("Status", ["Pago", "Pendente"])
        
        if st.form_submit_button("SALVAR REGISTRO"):
            if f_desc:
                nova_linha = pd.DataFrame([[f_data, f_desc, f_tipo, f_val, f_stat]], 
                                          columns=["Data", "Descrição", "Tipo", "Valor", "Status"])
                df = pd.concat([df, nova_linha], ignore_index=True)
                df.to_csv(DB_FILE, index=False)
                st.success("✅ Salvo!")
                st.rerun()

# --- ÁREA PRINCIPAL ---
st.header("📊 Painel de Controle - Arte Criativa")

# Filtros de Fechamento
meses = {1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho", 
         7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"}

col_m1, col_m2 = st.columns(2)
mes_sel = col_m1.selectbox("Mês de Referência", options=list(meses.keys()), format_func=lambda x: meses[x], index=datetime.now().month-1)
ano_sel = col_m2.selectbox("Ano", [2025, 2026, 2027], index=1)

# Lógica de resumo do mês
df_temp = df.copy()
df_temp['Data'] = pd.to_datetime(df_temp['Data'])
df_filtrado = df_temp[(df_temp['Data'].dt.month == mes_sel) & (df_temp['Data'].dt.year == ano_sel)]

receitas = df_filtrado[df_filtrado['Tipo'] == 'Entrada']['Valor'].sum()
despesas = df_filtrado[df_filtrado['Tipo'] == 'Saída']['Valor'].sum()
saldo = receitas - despesas

# Cards de Indicadores
c1, c2, c3 = st.columns(3)
c1.metric("Receitas (Mês)", f"R$ {receitas:,.2f}")
c2.metric("Despesas (Mês)", f"R$ {despesas:,.2f}")
c3.metric("Saldo Mensal", f"R$ {saldo:,.2f}")

st.divider()

# Tabela de Edição
st.subheader("📋 Histórico e Edição")
df_editado = st.data_editor(
    df.sort_index(ascending=False),
    use_container_width=True,
    num_rows="dynamic",
    column_config={
        "Tipo": st.column_config.SelectboxColumn(options=["Entrada", "Saída"]),
        "Status": st.column_config.SelectboxColumn(options=["Pago", "Pendente"]),
        "Valor": st.column_config.NumberColumn(format="R$ %.2f")
    }
)

if st.button("💾 SALVAR ALTERAÇÕES DA TABELA"):
    df_editado.to_csv(DB_FILE, index=False)
    st.success("✅ Alterações guardadas!")
    st.rerun()
                                          
