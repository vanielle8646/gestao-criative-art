import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

st.set_page_config(page_title="Arte Criativa - Gestão", layout="wide")

url = "https://docs.google.com/spreadsheets/d/13Qqqr2IgjZKsUzGSEBcZl3OWWeXc4NIW0QoWw2X4ktE/edit?usp=sharing"

conn = st.connection("gsheets", type=GSheetsConnection)

def carregar_e_limpar():
    # Lê todos os dados
    df_raw = conn.read(spreadsheet=url, ttl=0)
    
    if df_raw is not None and not df_raw.empty:
        # Garante que os nomes das colunas não tenham espaços invisíveis
        df_raw.columns = [str(c).strip() for c in df_raw.columns]
        
        # Filtra para manter apenas linhas que tenham Data E Descrição preenchidos
        # Isso remove aquelas linhas que só tem "Pago" no Status
        df_limpo = df_raw.dropna(subset=['Data', 'Descrição'], how='any').copy()
        return df_limpo
    return pd.DataFrame(columns=["Data", "Descrição", "Tipo", "Valor", "Status"])

df = carregar_e_limpar()

def formatar_moeda(val):
    if pd.isna(val) or val == "": return 0.0
    if isinstance(val, (int, float)): return float(val)
    s = str(val).replace('R$', '').replace('.', '').replace(',', '.').strip()
    try: return float(s)
    except: return 0.0

st.markdown("<h1 style='color: #00ffcc;'>📊 Painel de Controle - Arte Criativa</h1>", unsafe_allow_html=True)

# Só prossegue se a coluna 'Valor' existir após a limpeza
if 'Valor' in df.columns:
    df['V_num'] = df['Valor'].apply(formatar_moeda)
    df['Data_dt'] = pd.to_datetime(df['Data'], errors='coerce')
    
    # Resumo do Mês
    hoje = datetime.now()
    df_mes = df[(df['Data_dt'].dt.month == hoje.month) & (df['Data_dt'].dt.year == hoje.year)]
    
    ent = df_mes[df_mes['Tipo'].str.contains('Entrada', case=False, na=False)]['V_num'].sum()
    sai = df_mes[df_mes['Tipo'].str.contains('Saíd|Said', case=False, na=False)]['V_num'].sum()
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Receitas", f"R$ {ent:,.2f}")
    c2.metric("Despesas", f"R$ {sai:,.2f}")
    c3.metric("Saldo", f"R$ {ent-sai:,.2f}")
else:
    st.error("Coluna 'Valor' não encontrada. Verifique o cabeçalho da sua planilha.")

st.divider()

# --- FORMULÁRIO ---
st.subheader("➕ Novo Lançamento")
with st.form("form_criative", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        data_f = st.date_input("Data", datetime.now())
        desc_f = st.text_input("Descrição")
    with col2:
        val_f = st.number_input("Valor", min_value=0.0, format="%.2f")
        tipo_f = st.selectbox("Tipo", ["Entrada", "Saída"])
    
    if st.form_submit_button("Salvar no Sistema"):
        if desc_f and val_f > 0:
            nova_linha = pd.DataFrame([{
                "Data": data_f.strftime("%Y/%m/%d"),
                "Descrição": desc_f,
                "Tipo": tipo_f,
                "Valor": val_f,
                "Status": "Pago"
            }])
            
            # Pega os dados atuais sem as colunas de cálculo
            colunas_originais = ["Data", "Descrição", "Tipo", "Valor", "Status"]
            df_para_salvar = pd.concat([df[colunas_originais], nova_linha], ignore_index=True)
            
            try:
                conn.update(spreadsheet=url, data=df_para_salvar)
                st.success("Lançamento realizado com sucesso!")
                st.rerun()
            except Exception as e:
                st.error("Erro ao salvar. Verifique se a planilha está como 'Editor' para qualquer pessoa com o link.")
        else:
            st.warning("Preencha todos os campos obrigatórios.")

st.divider()
st.subheader("📝 Histórico Recente")
st.dataframe(df[["Data", "Descrição", "Tipo", "Valor", "Status"]].tail(10), use_container_width=True)
