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
    # Garante que a coluna Data seja lida como data real
    df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
    df['Valor'] = df['Valor'].apply(limpar_valor)
    df['Tipo'] = df['Tipo'].astype(str).str.strip()
    
    # Cria colunas auxiliares para o filtro
    df['Mes'] = df['Data'].dt.month
    df['Ano'] = df['Data'].dt.year

st.markdown("<h1 style='color: #00ffcc;'>📊 Painel de Controle - Arte Criativa</h1>", unsafe_allow_html=True)

# --- FILTROS DE MÊS E ANO ---
st.subheader("🔍 Filtro de Referência")
col_mes, col_ano = st.columns(2)

meses_nome = {1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho", 
              7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"}

with col_mes:
    mes_selecionado = st.selectbox("Mês", options=list(meses_nome.keys()), format_func=lambda x: meses_nome[x], index=datetime.now().month - 1)

with col_ano:
    anos_disponiveis = sorted(df['Ano'].dropna().unique().astype(int).tolist())
    if not anos_disponiveis: anos_disponiveis = [datetime.now().year]
    ano_selecionado = st.selectbox("Ano", options=anos_disponiveis, index=len(anos_disponiveis)-1)

# Filtrando os dados com base na escolha
df_filtrado = df[(df['Mes'] == mes_selecionado) & (df['Ano'] == ano_selecionado)]

# --- EXIBIÇÃO DOS TOTAIS FILTRADOS ---
if not df_filtrado.empty:
    receitas = df_filtrado[df_filtrado['Tipo'].str.contains('Entrada', case=False, na=False)]['Valor'].sum()
    despesas = df_filtrado[df_filtrado['Tipo'].str.contains('Saíd|Said', case=False, na=False)]['Valor'].sum()
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Receitas", f"R$ {receitas:,.2f}")
    c2.metric("Despesas", f"R$ {despesas:,.2f}")
    c3.metric("Saldo", f"R$ {receitas-despesas:,.2f}")
else:
    st.warning("Nenhum registro encontrado para este mês/ano.")

st.divider()

# --- FORMULÁRIO DE CADASTRO ---
st.subheader("➕ Cadastrar Novo Registro")
with st.form("novo_registro", clear_on_submit=True):
    c1, c2 = st.columns(2)
    with c1:
        data_input = st.date_input("Data", datetime.now())
        desc_input = st.text_input("Descrição")
    with c2:
        valor_input = st.number_input("Valor", min_value=0.0, format="%.2f")
        tipo_input = st.selectbox("Tipo", ["Entrada", "Saída"])
    
    status_input = st.selectbox("Status", ["Pago", "Pendente"])
    if st.form_submit_button("Salvar no Sistema"):
        nova_linha = pd.DataFrame([{
            "Data": data_input.strftime("%Y/%m/%d"),
            "Descrição": desc_input,
            "Tipo": tipo_input,
            "Valor": valor_input,
            "Status": status_input
        }])
        df_final = pd.concat([df.drop(columns=['Mes', 'Ano']), nova_linha], ignore_index=True)
        conn.update(spreadsheet=url, data=df_final)
        st.success("Dados salvos!")
        st.rerun()

st.divider()
st.subheader("📝 Histórico Selecionado")
st.dataframe(df_filtrado.drop(columns=['Mes', 'Ano']), use_container_width=True)
