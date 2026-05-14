import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# Configuração da página para celular
st.set_page_config(page_title="Arte Criativa", layout="centered")

# URL da sua planilha
url = "https://docs.google.com/spreadsheets/d/13Qqqr2IgjZKsUzGSEBcZl3OWWeXc4NIW0QoWw2X4ktE/edit?usp=sharing"

# Conexão direta
conn = st.connection("gsheets", type=GSheetsConnection)

def carregar():
    try:
        # Lê os dados
        df = conn.read(spreadsheet=url, ttl=0)
        if df is not None:
            df.columns = [str(c).strip() for c in df.columns]
            return df.dropna(subset=['Data'], how='any').copy()
    except:
        return pd.DataFrame(columns=["Data", "Descrição", "Tipo", "Valor", "Status"])

df = carregar()

st.markdown("<h2 style='text-align: center; color: #00ffcc;'>🎨 Arte Criativa</h2>", unsafe_allow_html=True)

# Formulário simplificado para tela de celular
with st.container():
    st.subheader("➕ Novo Lançamento")
    data_f = st.date_input("Data", datetime.now())
    desc_f = st.text_input("Descrição (Ex: Xerox)")
    val_f = st.number_input("Valor (R$)", min_value=0.0, step=0.50, format="%.2f")
    tipo_f = st.radio("Tipo", ["Entrada", "Saída"], horizontal=True)
    
    if st.button("SALVAR AGORA", use_container_width=True):
        if desc_f and val_f > 0:
            # Prepara a linha
            nova = pd.DataFrame([{
                "Data": data_f.strftime("%Y-%m-%d"),
                "Descrição": desc_f,
                "Tipo": tipo_f,
                "Valor": val_f,
                "Status": "Pago"
            }])
            
            # Tenta o método de atualização simples
            try:
                df_atualizado = pd.concat([df[["Data", "Descrição", "Tipo", "Valor", "Status"]], nova], ignore_index=True)
                
                # AQUI ESTÁ O TRUQUE:
                conn.update(spreadsheet=url, data=df_atualizado)
                
                st.success("✅ Salvo!")
                st.cache_data.clear()
                st.rerun()
            except Exception as e:
                st.error("O Google ainda está bloqueando o acesso direto.")
                st.info("Dica: No seu navegador do celular, abra a planilha, clique nos 3 pontinhos -> Compartilhar -> Verifique se 'Qualquer pessoa com o link' está mesmo como 'EDITOR'.")
        else:
            st.warning("Preencha os campos!")

st.divider()
st.subheader("📝 Últimos 5")
if not df.empty:
    st.dataframe(df[["Data", "Descrição", "Valor"]].tail(5), use_container_width=True)
            
