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

# --- INFORMAÇÕES SUPERIORES (COMO ESTAVA ANTES) ---
if not df.empty:
    # Mostra o total GERAL ou do MÊS ATUAL por padrão no topo
    mes_atual = datetime.now().month
    ano_atual = datetime.now().year
    
    df_topo = df[(df['Mes'] == mes_atual) & (df['Ano'] == ano_atual)]
    
    # Se o mês atual estiver vazio, mostra o total geral para não ficar zerado
    if df_topo.empty:
        df_topo = df

    receitas = df_topo[df_topo['Tipo'].str.contains('Entrada', case=False, na=False)]['Valor'].sum()
    despesas = df_topo[df_topo['Tipo'].str.contains('Saíd|Said', case=False, na=False)]['Valor'].sum()
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Receitas", f"R$ {receitas:,.2f}")
    c2.metric("Despesas", f"R$ {despesas:,.2f}")
    c3.metric("Saldo", f"R$ {receitas-despesas:,.2f}")

st.divider()

# --- FORMULÁRIO DE CADASTRO NO MEIO ---
st.subheader("➕ Novo Lançamento")
with st.form("add", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        d = st.date_input("Data", datetime.now())
        desc = st.text_input("Descrição")
    with col2:
        v = st.number_input("Valor", min_value=0.0, format="%.2f")
        t = st.selectbox("Tipo", ["Entrada", "Saída"])
    if st.form_submit_button("Salvar no Sistema"):
        nova = pd.DataFrame([{"Data": d.strftime("%Y/%m/%d"), "Descrição": desc, "Tipo": t, "Valor": v, "Status": "Pago"}])
        conn.update(spreadsheet=url, data=pd.concat([df.drop(columns=['Mes', 'Ano']), nova], ignore_index=True))
        st.success("Salvo!")
        st.rerun()

st.divider()

# --- HISTÓRICO ---
st.subheader("📝 Histórico Recente")
st.dataframe(df.drop(columns=['Mes', 'Ano']).tail(10), use_container_width=True)

st.divider()

# --- FERRAMENTAS DE CONSULTA NO FINAL DO APP ---
with st.expander("🔍 Consultar outros meses e Fechamento"):
    meses_nome = {1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho", 
                  7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"}
    
    c_m, c_a = st.columns(2)
    with c_m:
        m_sel = st.selectbox("Escolha o Mês", options=list(meses_nome.keys()), format_func=lambda x: meses_nome[x], index=datetime.now().month - 1)
    with c_a:
        anos_disponiveis = sorted(df['Ano'].dropna().unique().astype(int).tolist())
        if not anos_disponiveis: anos_disponiveis = [datetime.now().year]
        a_sel = st.selectbox("Escolha o Ano", options=anos_disponiveis, index=len(anos_disponiveis)-1)
    
    df_f = df[(df['Mes'] == m_sel) & (df['Ano'] == a_sel)]
    rec_f = df_f[df_f['Tipo'].str.contains('Entrada', case=False, na=False)]['Valor'].sum()
    des_f = df_f[df_f['Tipo'].str.contains('Saíd|Said', case=False, na=False)]['Valor'].sum()
    
    st.write(f"**Resumo de {meses_nome[m_sel]}:** Entradas R$ {rec_f:.2f} | Saídas R$ {des_f:.2f} | **Saldo: R$ {rec_f-des_f:.2f}**")
    
    if st.button("Ver Tabela Anual Completa"):
        resumo_anual = []
        for m in range(1, 13):
            temp_df = df[(df['Mes'] == m) & (df['Ano'] == a_sel)]
            ent = temp_df[temp_df['Tipo'].str.contains('Entrada', case=False, na=False)]['Valor'].sum()
            sai = temp_df[temp_df['Tipo'].str.contains('Saíd|Said', case=False, na=False)]['Valor'].sum()
            resumo_anual.append({"Mês": meses_nome[m], "Saldo": ent - sai})
        st.table(pd.DataFrame(resumo_anual))
        
