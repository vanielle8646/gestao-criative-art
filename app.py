import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Arte Criativa", layout="centered")

# URL da planilha
url = "https://docs.google.com/spreadsheets/d/13Qqqr2IgjZKsUzGSEBcZl3OWWeXc4NIW0QoWw2X4ktE/edit?usp=sharing"

conn = st.connection("gsheets", type=GSheetsConnection)

# Tenta ler os dados atuais
try:
    df = conn.read(spreadsheet=url, ttl=0).dropna(subset=['Data']).copy()
except:
    df = pd.DataFrame(columns=["Data", "Descrição", "Tipo", "Valor", "Status"])

st.title("📲 Lançamento Rápido")

with st.form("celular_form"):
    data = st.date_input("Data")
    desc = st.text_input("Descrição")
    valor = st.number_input("Valor", min_value=0.0)
    tipo = st.selectbox("Tipo", ["Entrada", "Saída"])
    
    if st.form_submit_button("SALVAR"):
        if desc:
            nova_linha = pd.DataFrame([{
                "Data": str(data),
                "Descrição": desc,
                "Tipo": tipo,
                "Valor": valor,
                "Status": "Pago"
            }])
            
            # Tenta concatenar e atualizar
            try:
                df_final = pd.concat([df, nova_linha], ignore_index=True)
                conn.update(spreadsheet=url, data=df_final)
                st.success("✅ Sucesso!")
                st.balloons()
            except Exception as e:
                st.error("O Google ainda exige a conta de serviço.")
        else:
            st.warning("Coloque uma descrição.")

st.divider()
st.subheader("Histórico")
st.table(df[['Data', 'Descrição', 'Valor']].tail(3))
