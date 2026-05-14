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

tab1, tab2, tab3 = st.tabs(["📊 Lançamentos", "⚠️ Pendentes", "🔒 Fechamento"])

# --- ABA 1: LANÇAMENTOS (Onde você digita as Entradas/Saídas) ---
with tab1:
    st.subheader("➕ Novo Registro")
    with st.form("form_novo", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            data_f = st.date_input("Data", datetime.now())
            desc_f = st.text_input("Descrição")
        with col2:
            val_f = st.number_input("Valor (R$)", min_value=0.0, step=0.50)
            tipo_f = st.selectbox("Tipo", ["Entrada", "Saída"])
        
        status_f = st.selectbox("Status", ["Pago", "Pendente"])
        
        if st.form_submit_button("Salvar no Sistema", use_container_width=True):
            if desc_f and val_f > 0:
                nova_linha = pd.DataFrame([{
                    "Data": data_f.strftime("%Y/%m/%d"),
                    "Descrição": desc_f,
                    "Tipo": tipo_f,
                    "Valor": val_f,
                    "Status": status_f
                }])
                
                try:
                    df_atualizado = pd.concat([df[["Data", "Descrição", "Tipo", "Valor", "Status"]], nova_linha], ignore_index=True)
                    conn.update(spreadsheet=url, data=df_atualizado)
                    st.success("✅ Gravado!")
                    st.cache_data.clear()
                    st.rerun()
                except:
                    st.error("Erro de permissão do Google.")
                    st.info(f"Clique no link para abrir a planilha e digitar lá: [Abrir Planilha]({url})")
            else:
                st.warning("Preencha Descrição e Valor.")

    st.divider()
    st.subheader("📝 Histórico Recente")
    if not df.empty:
        st.dataframe(df[["Data", "Descrição", "Tipo", "Valor"]].tail(10), use_container_width=True)

# --- ABA 2: PENDENTES ---
with tab2:
    st.subheader("💸 Despesas Pendentes")
    if not df.empty and 'Status' in df.columns:
        pendentes = df[df['Status'].str.contains('Pendente|A pagar', case=False, na=False)].copy()
        if not pendentes.empty:
            pendentes['V_num'] = pendentes['Valor'].apply(para_float)
            st.metric("Total Pendente", f"R$ {pendentes['V_num'].sum():,.2f}")
            st.dataframe(pendentes[['Data', 'Descrição', 'Valor']], use_container_width=True)
        else:
            st.success("Tudo pago!")

# --- ABA 3: FECHAMENTO ---
with tab3:
    st.subheader("🏁 Balanço do Mês")
    if not df.empty:
        df['V_num'] = df['Valor'].apply(para_float)
        # Filtra entradas e saídas (simplificado)
        ent = df[df['Tipo'].str.contains('Entrada', case=False, na=False)]['V_num'].sum()
        sai = df[df['Tipo'].str.contains('Saíd|Said', case=False, na=False)]['V_num'].sum()
        
        c1, c2 = st.columns(2)
        c1.metric("Total Entradas", f"R$ {ent:,.2f}")
        c2.metric("Total Saídas", f"R$ {sai:,.2f}")
        st.metric("Saldo Líquido", f"R$ {ent-sai:,.2f}")
                                 
