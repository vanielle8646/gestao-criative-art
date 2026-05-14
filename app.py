import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

st.set_page_config(page_title="Arte Criativa - Gestão", layout="centered")

# URL da planilha Arte Criativa
url = "https://docs.google.com/spreadsheets/d/13Qqqr2IgjZKsUzGSEBcZl3OWWeXc4NIW0QoWw2X4ktE/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

def carregar_dados():
    try:
        df = conn.read(spreadsheet=url, ttl=0)
        if df is not None:
            df.columns = [str(c).strip() for c in df.columns]
            return df.dropna(subset=['Data']).copy()
    except:
        return pd.DataFrame()

df = carregar_dados()

def para_float(val):
    if pd.isna(val) or val == "": return 0.0
    try:
        return float(str(val).replace('R$', '').replace('.', '').replace(',', '.').strip())
    except: return 0.0

st.markdown("<h2 style='text-align: center; color: #00ffcc;'>🎨 Arte Criativa</h2>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📊 Resumo", "⚠️ Pendentes", "🔒 Fechamento"])

# --- ABA 1: RESUMO ---
with tab1:
    st.subheader("Histórico Recente")
    if not df.empty:
        st.dataframe(df.tail(10), use_container_width=True)
    else:
        st.info("Nenhum dado encontrado.")

# --- ABA 2: PENDENTES ---
with tab2:
    st.subheader("💸 Despesas Pendentes")
    if not df.empty and 'Status' in df.columns:
        pendentes = df[df['Status'].str.contains('Pendente|A pagar', case=False, na=False)].copy()
        if not pendentes.empty:
            pendentes['V_num'] = pendentes['Valor'].apply(para_float)
            total_p = pendentes['V_num'].sum()
            st.metric("Total Pendente", f"R$ {total_p:,.2f}")
            st.dataframe(pendentes[['Data', 'Descrição', 'Valor']], use_container_width=True)
        else:
            st.success("Nada pendente!")

# --- ABA 3: FECHAMENTO DO MÊS ---
with tab3:
    st.subheader("🏁 Fechamento do Mês")
    
    if not df.empty:
        df['Data_dt'] = pd.to_datetime(df['Data'], errors='coerce')
        mes_atual = datetime.now().month
        ano_atual = datetime.now().year
        
        df_mes = df[(df['Data_dt'].dt.month == mes_atual) & (df['Data_dt'].dt.year == ano_atual)].copy()
        
        if not df_mes.empty:
            df_mes['V_num'] = df_mes['Valor'].apply(para_float)
            ent = df_mes[df_mes['Tipo'].str.contains('Entrada', case=False, na=False)]['V_num'].sum()
            sai = df_mes[df_mes['Tipo'].str.contains('Saíd|Said', case=False, na=False)]['V_num'].sum()
            saldo = ent - sai
            
            st.write(f"**Relatório de {datetime.now().strftime('%B/%Y')}:**")
            st.info(f"💰 Total Entradas: R$ {ent:,.2f}")
            st.warning(f"📉 Total Saídas: R$ {sai:,.2f}")
            
            cor_saldo = "green" if saldo >= 0 else "red"
            st.markdown(f"### Saldo Final: <span style='color:{cor_saldo}'>R$ {saldo:,.2f}</span>", unsafe_allow_html=True)
            
            if st.button("Confirmar Fechamento", use_container_width=True):
                st.success("Relatório gerado!")
                st.write("Para arquivar estes dados e começar um novo mês, limpe as linhas antigas diretamente na sua planilha.")
                st.markdown(f"[Abrir Planilha para Limpeza]({url})")
        else:
            st.info("Sem lançamentos para o mês atual.")
            
