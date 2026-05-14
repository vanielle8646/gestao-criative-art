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
    df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
    df['Valor'] = df['Valor'].apply(limpar_valor)
    df['Tipo'] = df['Tipo'].astype(str).str.strip()
    df['Mes'] = df['Data'].dt.month
    df['Ano'] = df['Data'].dt.year

st.markdown("<h1 style='color: #00ffcc;'>📊 Painel de Controle - Arte Criativa</h1>", unsafe_allow_html=True)

# --- FILTROS ---
meses_nome = {1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho", 
              7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"}

st.subheader("🔍 Selecione o Período")
col_mes, col_ano = st.columns(2)
with col_mes:
    mes_selecionado = st.selectbox("Mês", options=list(meses_nome.keys()), format_func=lambda x: meses_nome[x], index=datetime.now().month - 1)
with col_ano:
    anos_disponiveis = sorted(df['Ano'].dropna().unique().astype(int).tolist())
    if not anos_disponiveis: anos_disponiveis = [datetime.now().year]
    ano_selecionado = st.selectbox("Ano", options=anos_disponiveis, index=len(anos_disponiveis)-1)

df_filtrado = df[(df['Mes'] == mes_selecionado) & (df['Ano'] == ano_selecionado)]

# --- FECHAMENTO DO MÊS SELECIONADO ---
st.markdown(f"### 📅 Fechamento de {meses_nome[mes_selecionado]} / {ano_selecionado}")
if not df_filtrado.empty:
    receitas = df_filtrado[df_filtrado['Tipo'].str.contains('Entrada', case=False, na=False)]['Valor'].sum()
    despesas = df_filtrado[df_filtrado['Tipo'].str.contains('Saíd|Said', case=False, na=False)]['Valor'].sum()
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Entradas", f"R$ {receitas:,.2f}")
    c2.metric("Total Saídas", f"R$ {despesas:,.2f}")
    c3.metric("Saldo Mensal", f"R$ {receitas-despesas:,.2f}", delta=float(receitas-despesas))
else:
    st.info("Sem dados para este mês.")

st.divider()

# --- NOVO: TABELA DE FECHAMENTO ANUAL ---
with st.expander("📈 Ver Fechamento de Todos os Meses"):
    st.write(f"Resumo de {ano_selecionado}")
    resumo_anual = []
    for m in range(1, 13):
        temp_df = df[(df['Mes'] == m) & (df['Ano'] == ano_selecionado)]
        ent = temp_df[temp_df['Tipo'].str.contains('Entrada', case=False, na=False)]['Valor'].sum()
        sai = temp_df[temp_df['Tipo'].str.contains('Saíd|Said', case=False, na=False)]['Valor'].sum()
        resumo_anual.append({"Mês": meses_nome[m], "Entradas": ent, "Saídas": sai, "Saldo": ent - sai})
    
    df_resumo = pd.DataFrame(resumo_anual)
    st.table(df_resumo.style.format({"Entradas": "R$ {:.2f}", "Saídas": "R$ {:.2f}", "Saldo": "R$ {:.2f}"}))

st.divider()

# --- FORMULÁRIO ---
st.subheader("➕ Novo Lançamento")
with st.form("add", clear_on_submit=True):
    c1, c2 = st.columns(2)
    with c1:
        d = st.date_input("Data", datetime.now())
        desc = st.text_input("Descrição")
    with c2:
        v = st.number_input("Valor", min_value=0.0, format="%.2f")
        t = st.selectbox("Tipo", ["Entrada", "Saída"])
    if st.form_submit_button("Salvar"):
        nova = pd.DataFrame([{"Data": d.strftime("%Y/%m/%d"), "Descrição": desc, "Tipo": t, "Valor": v, "Status": "Pago"}])
        conn.update(spreadsheet=url, data=pd.concat([df.drop(columns=['Mes', 'Ano']), nova], ignore_index=True))
        st.rerun()

st.subheader("📝 Registros do Mês")
st.dataframe(df_filtrado.drop(columns=['Mes', 'Ano']), use_container_width=True)
