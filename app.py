import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

st.set_page_config(page_title="Arte Criativa - Gestão", layout="wide")

# Link da planilha
url = "https://docs.google.com/spreadsheets/d/13Qqqr2IgjZKsUzGSEBcZl3OWWeXc4NIW0QoWw2X4ktE/edit?usp=sharing"

conn = st.connection("gsheets", type=GSheetsConnection)
df_raw = conn.read(spreadsheet=url)

# Função para limpar os valores
def limpar_valor(val):
    if pd.isna(val): return 0.0
    val_str = str(val).replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
    try: return float(val_str)
    except: return 0.0

# Limpeza para remover linhas vazias da visualização
df = df_raw.dropna(subset=['Data', 'Descrição'], how='all').copy()

if not df.empty:
    df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
    df['Valor'] = df['Valor'].apply(limpar_valor)
    df['Tipo'] = df['Tipo'].astype(str).str.strip()
    df['Mes'] = df['Data'].dt.month
    df['Ano'] = df['Data'].dt.year

st.markdown("<h1 style='color: #00ffcc;'>📊 Painel de Controle - Arte Criativa</h1>", unsafe_allow_html=True)

# --- INFORMAÇÕES SUPERIORES (MÊS ATUAL) ---
if not df.empty:
    mes_atual = datetime.now().month
    ano_atual = datetime.now().year
    df_topo = df[(df['Mes'] == mes_atual) & (df['Ano'] == ano_atual)]
    
    if df_topo.empty: df_topo = df

    rec = df_topo[df_topo['Tipo'].str.contains('Entrada', case=False, na=False)]['Valor'].sum()
    des = df_topo[df_topo['Tipo'].str.contains('Saíd|Said', case=False, na=False)]['Valor'].sum()
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Receitas", f"R$ {rec:,.2f}")
    c2.metric("Despesas", f"R$ {des:,.2f}")
    c3.metric("Saldo", f"R$ {rec-des:,.2f}")

st.divider()

# --- NOVO LANÇAMENTO ---
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
        df_base = df_raw.dropna(subset=['Data', 'Descrição'], how='all')
        conn.update(spreadsheet=url, data=pd.concat([df_base, nova], ignore_index=True))
        st.success("Salvo!")
        st.rerun()

st.divider()

# --- HISTÓRICO ---
st.subheader("📝 Histórico Recente")
if not df.empty:
    st.dataframe(df.drop(columns=['Mes', 'Ano']).tail(10), use_container_width=True)

st.divider()

# --- CONSULTA E FECHAMENTO (CORRIGIDO PARA MOSTRAR TUDO) ---
with st.expander("🔍 Consultar outros meses e Fechamento"):
    meses_nome = {1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho", 
                  7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"}
    
    cm, ca = st.columns(2)
    with cm:
        m_sel = st.selectbox("Mês", options=list(meses_nome.keys()), format_func=lambda x: meses_nome[x], index=datetime.now().month - 1)
    with ca:
        anos_list = sorted(df['Ano'].dropna().unique().astype(int).tolist()) if not df.empty else [datetime.now().year]
        a_sel = st.selectbox("Ano", options=anos_list, index=len(anos_list)-1)
    
    df_f = df[(df['Mes'] == m_sel) & (df['Ano'] == a_sel)]
    
    if not df_f.empty:
        rec_f = df_f[df_f['Tipo'].str.contains('Entrada', case=False, na=False)]['Valor'].sum()
        des_f = df_f[df_f['Tipo'].str.contains('Saíd|Said', case=False, na=False)]['Valor'].sum()
        
        # Aqui ele mostra o detalhamento completo igual você queria
        st.markdown(f"### Detalhes de {meses_nome[m_sel]}/{a_sel}")
        col_r, col_d, col_s = st.columns(3)
        col_r.write(f"**Entradas:** R$ {rec_f:,.2f}")
        col_d.write(f"**Saídas:** R$ {des_f:,.2f}")
        col_s.write(f"**Saldo Final:** R$ {rec_f-des_f:,.2f}")
        
        st.dataframe(df_f.drop(columns=['Mes', 'Ano']), use_container_width=True)
    else:
        st.warning("Sem dados para este período.")
        
