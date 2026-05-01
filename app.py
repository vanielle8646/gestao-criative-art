import streamlit as st
import pandas as pd
import os

# 1. Configuração de Layout
st.set_page_config(page_title="Gestão Criative ART", layout="wide")

# CSS "ULTRA" - Força as cores por cima do tema escuro do Streamlit
st.markdown("""
<style>
    /* Forçar Título a ficar BRANCO */
    h1, .main-title { 
        color: #ffffff !important; 
        font-weight: bold !important; 
        opacity: 1 !important;
    }

    /* Sidebar e Botões */
    [data-testid="stSidebar"] { background-color: #1e293b !important; }
    [data-testid="stSidebar"] button { 
        background-color: #334155 !important; 
        color: white !important; 
    }

    /* Cards Estilizados */
    .card { padding: 20px; border-radius: 12px; color: white !important; display: flex; justify-content: space-between; align-items: center; min-height: 110px; margin-bottom: 10px; }
    .bg-receita { background-color: #22c55e !important; }
    .bg-despesa { background-color: #3b82f6 !important; }
    .bg-pendente { background-color: #ff0000 !important; border: 2px solid white !important; } /* VERMELHO TOTAL */
    .bg-saldo { background-color: #10b981 !important; }

    .val { font-size: 26px; font-weight: bold; color: white !important; }
    span { color: white !important; }
</style>
""", unsafe_allow_html=True)

# 2. Dados
DB_FILE = "dados_arte_criativa_v3.csv"
if os.path.exists(DB_FILE):
    df = pd.read_csv(DB_FILE)
else:
    df = pd.DataFrame(columns=['Data', 'Descrição', 'Tipo', 'Valor', 'Status'])

# 3. Sidebar (Menu Completo)
with st.sidebar:
    if os.path.exists("logo.jpg"):
        st.image("logo.jpg", use_container_width=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.button("🏠 Painel", use_container_width=True)
    st.button("💰 Fluxo de Caixa", use_container_width=True)
    st.button("📅 Fechamento", use_container_width=True)
    st.button("📥 Entradas", use_container_width=True)
    st.button("📤 Saídas", use_container_width=True)

# 4. Cabeçalho
st.markdown('<h1 class="main-title">📊 Dashboard Financeiro</h1>', unsafe_allow_html=True)

if st.button("🔄 Atualizar Página"):
    st.rerun()

# 5. Cálculos
receitas = df[(df['Tipo'] == 'Entrada') & (df['Status'] == 'Pago')]['Valor'].sum()
despesas = df[(df['Tipo'] == 'Saída') & (df['Status'] == 'Pago')]['Valor'].sum()
pendentes = df[df['Status'] == 'Pendente']['Valor'].sum()
saldo = receitas - despesas

# 6. Layout de Cards
col_esq, col_dir = st.columns(2)

with col_esq:
    st.markdown(f'<div class="card bg-receita"><div><span>Receitas do Mês</span><br><span class="val">R$ {receitas:,.2f}</span></div><span>💵</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="card bg-pendente"><div><span>Pendentes</span><br><span class="val">R$ {pendentes:,.2f}</span></div><span>⏳</span></div>', unsafe_allow_html=True)

with col_dir:
    # Botão Novo Lançamento Acima de Despesas
    with st.popover("➕ Novo Lançamento", use_container_width=True):
        with st.form("form_novo"):
            f_data = st.date_input("Data")
            f_desc = st.text_input("Descrição")
            f_val = st.number_input("Valor", min_value=0.0)
            f_tipo = st.selectbox("Tipo", ["Entrada", "Saída"])
            f_stat = st.selectbox("Status", ["Pago", "Pendente"])
            if st.form_submit_button("Salvar"):
                nova = pd.DataFrame([[f_data, f_desc, f_tipo, f_val, f_stat]], columns=df.columns)
                df = pd.concat([df, nova], ignore_index=True)
                df.to_csv(DB_FILE, index=False)
                st.rerun()

    st.markdown(f'<div class="card bg-despesa"><div><span>Despesas Pagas</span><br><span class="val">R$ {despesas:,.2f}</span></div><span>💳</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="card bg-saldo"><div><span>Saldo do Mês</span><br><span class="val">R$ {saldo:,.2f}</span></div><span>📉</span></div>', unsafe_allow_html=True)

st.divider()

# 7. Tabela
st.subheader("🕒 Transações")
df_edit = st.data_editor(df.sort_index(ascending=False), use_container_width=True)

if st.button("💾 Salvar Alterações"):
    df_edit.to_csv(DB_FILE, index=False)
    st.success("Salvo!")
    st.rerun()